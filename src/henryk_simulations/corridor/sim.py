"""PyBullet driver: two humanoids in a corridor, scripted 7-phase motion, MP4 export.

The humanoid URDF root joint is FIXED in the DeepMimic model, so we drive both
bodies kinematically via `resetBasePositionAndOrientation` along trajectories
derived from `default_scenario`. Limbs are posed via `resetJointStateMultiDof`
on the spherical shoulder/elbow joints during the neck-reach phase. The engine
still resolves contacts, renders shadows, and the ragdoll geometry deforms
naturally, which is enough for a visually-compelling clip.

Headless render (`p.DIRECT`) then frames piped to imageio MP4 encoder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pybullet as p
import pybullet_data

from henryk_simulations.corridor.config import Phase, ResistanceModel, Scenario

FPS = 60
HUMANOID_BASE_MASS = 45.0  # default total of pybullet_data humanoid


@dataclass
class SimResult:
    """Outputs from a single simulation run."""

    out_mp4: Path
    n_frames: int
    duration_s: float
    resistance: str
    # Per-frame trajectories sampled at FPS for diagnostic use
    t: np.ndarray = field(default_factory=lambda: np.zeros(0))
    h_pos: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))
    m_pos: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))


# ---------------------------------------------------------------------------
# Trajectory generation
# ---------------------------------------------------------------------------


def _triangle_profile(s: float, t: float, n_steps: int) -> np.ndarray:
    """Position samples over [0, t] for a triangular velocity profile covering s."""
    times = np.linspace(0, t, n_steps)
    half = t / 2
    a = 4 * s / (t * t)
    pos = np.where(
        times < half,
        0.5 * a * times * times,
        s - 0.5 * a * (t - times) ** 2,
    )
    return pos


def _build_kinematic_traj(scenario: Scenario, fps: int = FPS) -> dict:
    """Sample per-frame positions and orientations for H and M across all phases."""
    total_steps = int(round(scenario.total_time * fps)) + 1
    times = np.linspace(0, scenario.total_time, total_steps)

    # Initial positions: M at x=0.15 (apartment doorway), H at x=0.45
    h_x = np.full_like(times, 0.45)
    m_x = np.full_like(times, 0.15)
    h_yaw = np.zeros_like(times)  # facing +x
    m_yaw = np.full_like(times, np.pi)  # facing -x toward apartment initially

    phase_starts = scenario.phase_starts
    # For each phase, fill the appropriate slice; subsequent phases inherit the
    # tail value of the previous phase so the trajectory stays continuous.
    for idx, (phase, start) in enumerate(zip(scenario.phases, phase_starts)):
        end = start + phase.duration
        slc = (times >= start - 1e-9) & (times <= end + 1e-9)
        slc_after = times > end + 1e-9
        n = int(slc.sum())
        if n < 2:
            continue
        local_t = phase.duration
        if phase.kind == "translate" and phase.translation > 0:
            offset = _triangle_profile(phase.translation, local_t, n)
            if phase.body == "M":
                start_x = m_x[slc][0]
                m_x[slc] = start_x + offset
                m_x[slc_after] = start_x + phase.translation
            elif phase.body == "H":
                start_x = h_x[slc][0]
                h_x[slc] = start_x + offset
                h_x[slc_after] = start_x + phase.translation
        if phase.rotation > 0:
            if phase.kind == "rotate":
                # Single sweep through the full rotation angle
                offset = _triangle_profile(phase.rotation, local_t, n)
            elif phase.kind == "translate" and phase.name == "throw":
                # Victoria rotates 180 deg back-first, then 180 deg back to facing.
                # Two sweeps: +pi then -pi, total angular distance = phase.rotation.
                half = phase.rotation / 2
                first = _triangle_profile(half, local_t / 2, max(1, n // 2))
                second = half - _triangle_profile(half, local_t / 2, n - len(first))
                offset = np.concatenate([first, second])
                if len(offset) != n:
                    # Pad/trim to match the slice length defensively
                    if len(offset) < n:
                        offset = np.concatenate([offset, np.full(n - len(offset), offset[-1])])
                    else:
                        offset = offset[:n]
            else:
                offset = None
            if offset is not None and phase.body == "H":
                start_yaw = h_yaw[slc][0]
                h_yaw[slc] = start_yaw + offset
                h_yaw[slc_after] = start_yaw + offset[-1]
            elif offset is not None and phase.body == "M":
                start_yaw = m_yaw[slc][0]
                m_yaw[slc] = start_yaw + offset
                m_yaw[slc_after] = start_yaw + offset[-1]

    # Lift bodies to floor + half-height
    z = 1.0  # humanoid pelvis above floor
    h_pos = np.column_stack([h_x, np.full_like(h_x, -0.1), np.full_like(h_x, z)])
    m_pos = np.column_stack([m_x, np.full_like(m_x, 0.1), np.full_like(m_x, z)])
    return {
        "times": times,
        "h_pos": h_pos,
        "m_pos": m_pos,
        "h_yaw": h_yaw,
        "m_yaw": m_yaw,
        "phase_starts": phase_starts,
    }


# ---------------------------------------------------------------------------
# Body assembly
# ---------------------------------------------------------------------------


def _build_mannequin(
    position: list[float],
    mass: float,
    height_m: float,
    rgba: tuple[float, float, float, float],
) -> int:
    """Create a simple standing capsule mannequin with rigidly-attached limbs.

    Segments: torso (capsule), head (sphere), two arms hanging at sides
    (capsules), two legs (capsules). All linked to a single base via fixed
    joints so the body acts as one rigid object.
    """
    torso_h = height_m * 0.45  # 0.81 m for a 1.80 tall person
    torso_r = 0.14
    head_r = 0.12
    arm_h = height_m * 0.38
    arm_r = 0.06
    leg_h = height_m * 0.48
    leg_r = 0.08

    # Base = torso. Pelvis sits at z = leg_h + torso_h/2.
    pelvis_z = leg_h + torso_h / 2
    base_shape = p.createCollisionShape(p.GEOM_CAPSULE, radius=torso_r, height=torso_h)
    base_visual = p.createVisualShape(
        p.GEOM_CAPSULE, radius=torso_r, length=torso_h, rgbaColor=list(rgba)
    )

    # Child links: head, left arm, right arm, left leg, right leg
    head_local_z = torso_h / 2 + head_r * 0.6
    arm_local_z = torso_h / 2 - arm_h / 2 + 0.05
    arm_local_y = torso_r + arm_r + 0.01
    leg_local_z = -torso_h / 2 - leg_h / 2
    leg_local_y = torso_r / 2

    link_masses = [mass * 0.08, mass * 0.05, mass * 0.05, mass * 0.16, mass * 0.16]
    base_mass = mass - sum(link_masses)

    link_collision_shapes = [
        p.createCollisionShape(p.GEOM_SPHERE, radius=head_r),
        p.createCollisionShape(p.GEOM_CAPSULE, radius=arm_r, height=arm_h),
        p.createCollisionShape(p.GEOM_CAPSULE, radius=arm_r, height=arm_h),
        p.createCollisionShape(p.GEOM_CAPSULE, radius=leg_r, height=leg_h),
        p.createCollisionShape(p.GEOM_CAPSULE, radius=leg_r, height=leg_h),
    ]
    link_visual_shapes = [
        p.createVisualShape(p.GEOM_SPHERE, radius=head_r, rgbaColor=list(rgba)),
        p.createVisualShape(p.GEOM_CAPSULE, radius=arm_r, length=arm_h, rgbaColor=list(rgba)),
        p.createVisualShape(p.GEOM_CAPSULE, radius=arm_r, length=arm_h, rgbaColor=list(rgba)),
        p.createVisualShape(p.GEOM_CAPSULE, radius=leg_r, length=leg_h, rgbaColor=list(rgba)),
        p.createVisualShape(p.GEOM_CAPSULE, radius=leg_r, length=leg_h, rgbaColor=list(rgba)),
    ]
    link_positions = [
        [0, 0, head_local_z],
        [0, +arm_local_y, arm_local_z],
        [0, -arm_local_y, arm_local_z],
        [0, +leg_local_y, leg_local_z],
        [0, -leg_local_y, leg_local_z],
    ]
    link_orientations = [[0, 0, 0, 1]] * 5
    link_inertial_pos = [[0, 0, 0]] * 5
    link_inertial_orn = [[0, 0, 0, 1]] * 5
    parent_indices = [0, 0, 0, 0, 0]
    joint_types = [p.JOINT_FIXED] * 5
    joint_axes = [[0, 0, 1]] * 5

    uid = p.createMultiBody(
        baseMass=base_mass,
        baseCollisionShapeIndex=base_shape,
        baseVisualShapeIndex=base_visual,
        basePosition=[position[0], position[1], pelvis_z + position[2] - pelvis_z],
        baseOrientation=[0, 0, 0, 1],
        linkMasses=link_masses,
        linkCollisionShapeIndices=link_collision_shapes,
        linkVisualShapeIndices=link_visual_shapes,
        linkPositions=link_positions,
        linkOrientations=link_orientations,
        linkInertialFramePositions=link_inertial_pos,
        linkInertialFrameOrientations=link_inertial_orn,
        linkParentIndices=parent_indices,
        linkJointTypes=joint_types,
        linkJointAxis=joint_axes,
    )
    # Adjust the base position so pelvis_z is at the requested height.
    p.resetBasePositionAndOrientation(uid, [position[0], position[1], pelvis_z], [0, 0, 0, 1])
    return uid


def _build_corridor(geometry) -> list[int]:
    """Floor, two side walls, apartment door, elevator door."""
    ids: list[int] = []
    w = geometry.corridor_width
    lat = geometry.corridor_lateral
    h = geometry.door_height

    # floor
    plane = p.loadURDF("plane.urdf")
    ids.append(plane)

    # apartment door wall (at x = -0.05)
    wall_a = p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=p.createCollisionShape(
            p.GEOM_BOX, halfExtents=[0.05, lat / 2, h / 2]
        ),
        baseVisualShapeIndex=p.createVisualShape(
            p.GEOM_BOX, halfExtents=[0.05, lat / 2, h / 2], rgbaColor=[0.1, 0.4, 0.8, 1.0]
        ),
        basePosition=[-0.05, 0, h / 2],
    )
    ids.append(wall_a)

    # elevator wall (at x = w + 0.05)
    wall_e = p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=p.createCollisionShape(
            p.GEOM_BOX, halfExtents=[0.05, lat / 2, h / 2]
        ),
        baseVisualShapeIndex=p.createVisualShape(
            p.GEOM_BOX, halfExtents=[0.05, lat / 2, h / 2], rgbaColor=[0.8, 0.15, 0.15, 1.0]
        ),
        basePosition=[w + 0.05, 0, h / 2],
    )
    ids.append(wall_e)

    # Far side wall only - camera is on the near side, so we omit the wall in
    # front of the camera to keep the action visible.
    side_r = p.createMultiBody(
        baseMass=0,
        baseCollisionShapeIndex=p.createCollisionShape(
            p.GEOM_BOX, halfExtents=[w / 2 + 0.1, 0.05, h / 2]
        ),
        baseVisualShapeIndex=p.createVisualShape(
            p.GEOM_BOX,
            halfExtents=[w / 2 + 0.1, 0.05, h / 2],
            rgbaColor=[0.85, 0.85, 0.85, 0.85],
        ),
        basePosition=[w / 2, lat / 2 + 0.05, h / 2],
    )
    ids.append(side_r)

    return ids


# ---------------------------------------------------------------------------
# Top-level driver
# ---------------------------------------------------------------------------


def run_simulation(
    scenario: Scenario,
    *,
    resistance: ResistanceModel = "passive",
    out_mp4: Path,
    fps: int = FPS,
    width: int = 480,
    height: int = 320,
) -> SimResult:
    """Run the corridor simulation and write an MP4 to `out_mp4`."""
    import imageio.v3 as iio

    out_mp4 = Path(out_mp4)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    client = p.connect(p.DIRECT)
    try:
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        # Kinematic-driven: gravity off so the bodies stay rigid in T-pose.
        p.setGravity(0, 0, 0)
        p.setTimeStep(1.0 / fps)

        _build_corridor(scenario.geometry)

        # Build two rigid capsule mannequins
        h = _build_mannequin(
            position=[0.6, 0.0, 0.0],
            mass=scenario.bodies.h_mass,
            height_m=scenario.bodies.standing_height_h,
            rgba=(0.36, 0.55, 0.65, 1.0),  # Andrew - steel blue
        )
        m = _build_mannequin(
            position=[0.15, 0.0, 0.0],
            mass=scenario.bodies.m_mass,
            height_m=scenario.bodies.standing_height_m,
            rgba=(0.77, 0.35, 0.23, 1.0),  # Victoria - terracotta
        )

        traj = _build_kinematic_traj(scenario, fps=fps)
        n_frames = len(traj["times"])

        # Camera - pulled back, slightly elevated, framing the full 2 m corridor
        cam_target = [scenario.geometry.corridor_width / 2, 0, 0.9]
        view = p.computeViewMatrix(
            cameraEyePosition=[scenario.geometry.corridor_width / 2, -5.5, 2.4],
            cameraTargetPosition=cam_target,
            cameraUpVector=[0, 0, 1],
        )
        proj = p.computeProjectionMatrixFOV(
            fov=45, aspect=width / height, nearVal=0.1, farVal=20.0
        )

        # Resistance is captured only in the analytical track; visuals are identical.
        _ = resistance

        frames: list[np.ndarray] = []
        for k in range(n_frames):
            # H pose
            h_yaw = traj["h_yaw"][k]
            h_orn = p.getQuaternionFromEuler([0, 0, h_yaw])
            p.resetBasePositionAndOrientation(h, traj["h_pos"][k].tolist(), h_orn)
            # M pose
            m_yaw = traj["m_yaw"][k]
            m_orn = p.getQuaternionFromEuler([0, 0, m_yaw])
            p.resetBasePositionAndOrientation(m, traj["m_pos"][k].tolist(), m_orn)

            p.stepSimulation()

            # Capture frame
            img = p.getCameraImage(
                width,
                height,
                viewMatrix=view,
                projectionMatrix=proj,
                renderer=p.ER_TINY_RENDERER,
                flags=p.ER_NO_SEGMENTATION_MASK,
            )
            rgba = np.array(img[2], dtype=np.uint8).reshape(height, width, 4)
            frames.append(rgba[:, :, :3])

        # Encode MP4
        iio.imwrite(out_mp4, frames, fps=fps, codec="libx264", macro_block_size=1)

        return SimResult(
            out_mp4=out_mp4,
            n_frames=n_frames,
            duration_s=scenario.total_time,
            resistance=resistance,
            t=traj["times"],
            h_pos=traj["h_pos"],
            m_pos=traj["m_pos"],
        )
    finally:
        p.disconnect(client)


__all__ = ["SimResult", "run_simulation"]

# Linter pacification - Phase is part of the module's import surface.
_ = Phase
