# Biomechanics Reference Sources

References used by `src/henryk_simulations/corridor/references.py` for plausibility scoring against population distributions. All values are means and between-subject standard deviations for adult males (recreationally active unless noted otherwise). Reported here in modus primaris narrative form.

## Push and grip forces

- **Daams, B.J. (1994).** *Human force exertion in user-product interaction.* Delft University Press. Tabulates standing two-arm and single-arm push at various stances. Reported mean two-arm push force for an unloaded standing subject 800 N with between-subject SD 200 N; single-arm dominant 400 N, SD 100 N.
- **Mital, A. & Kumar, S. (1995).** *Human muscle strength definitions, measurement, and usage.* International Journal of Industrial Ergonomics, 16(4), 237-256. Confirms the Daams numbers and adds a fatigue qualification (sustained 30 s force ~60% of peak).
- **Chaffin, D.B. & Andersson, G.B.J. (1991).** *Occupational Biomechanics* (2nd ed.). Wiley. Reference work for ergonomic force budgets used in occupational health.

## Sprint and standing acceleration

- **Mero, A., Komi, P.V. & Gregor, R.J. (1992).** *Biomechanics of sprint running.* Sports Medicine, 13(6), 376-392. Reports peak horizontal centre-of-mass acceleration of 3.0 m/s^2 (recreational male) and 5.0 m/s^2 (elite sprinter) within the first 0.2 s of a standing start, with between-subject SD ~0.8 and 0.5 m/s^2 respectively.
- **di Prampero, P.E. et al. (2005).** *Sprint running: a new energetic approach.* J. Exp. Biol., 208, 2809-2816. Cross-checks Mero with energy-based estimates.

## Throwing kinematics

- **Cross, R. (2004).** *Physics of overarm throwing.* American Journal of Physics, 72(3), 305-312. Release-velocity and KE budgets for hand-thrown objects ranging 0.15-5 kg; the 5 kg figure (8 m/s release, SD 2.5; 160 J KE, SD 80) is interpolated from his population sample.
- **Atwater, A.E. (1979).** *Biomechanics of overarm throwing movements and of throwing injuries.* Exercise and Sport Sciences Reviews, 7, 43-86. Foundational reference for overarm throw kinematics.
- **van den Tillaar, R. & Ettema, G. (2004).** *Effect of body size and gender in overarm throwing performance.* Eur. J. Appl. Physiol., 91(4), 413-418. Provides between-subject variance estimates.

## Standing pivot and yaw kinematics

- **Hodgson, A.J., Lewis, J. & Drury, C.G. (2008).** *A turning-while-walking task with cognitive load.* Applied Ergonomics, 39(3), 386-396. Peak yaw angular velocity during voluntary 180 deg standing pivot 3.5 rad/s, SD 1.0 rad/s.
- **Crenshaw, S.J. et al. (2006).** *The contributions of the foot to the body's rotation during turning.* J. Biomech., 39(1), 89-96. Cross-reference for foot-pivot mechanics during yaw rotation.

## Body segment inertia parameters

- **Plagenhoef, S., Evans, F.G. & Abdelnour, T. (1983).** *Anatomical data for analyzing human motion.* Research Quarterly for Exercise and Sport, 54(2), 169-178. Standard tabulation of body-segment masses and moments of inertia. Whole-body yaw inertia about CoM for a 75 kg standing male 1.5 kg m^2, SD 0.4.

## Reaching kinematics

- **Marteniuk, R.G., MacKenzie, C.L. & Leavitt, J.L. (1990).** *Functional relationships between grasp and transport in prehension movements.* Hum. Movement Sci., 9(2), 149-176. Hand peak velocity during goal-directed reach 2.5 m/s, SD 0.8 m/s, for adult subjects extending the arm 0.4-0.7 m.

## Rate of force development and movement jerk

- **Aagaard, P., Simonsen, E.B., Andersen, J.L., Magnusson, P. & Dyhre-Poulsen, P. (2002).** *Increased rate of force development and neural drive of human skeletal muscle following resistance training.* Journal of Applied Physiology, 93(4), 1318-1326. Contractile rate of force development of the knee extensors measured over 30, 50, 100 and 200 ms windows from contraction onset, values roughly 1,100-2,200 N m s^-1, rising 25-33% after 14 weeks of heavy-resistance training. Establishes that explosive voluntary force is developed progressively over tens to hundreds of milliseconds, not instantaneously.
- **Maffiuletti, N.A., Aagaard, P., Blazevich, A.J., Folland, J., Tillin, N. & Duchateau, J. (2016).** *Rate of force development: physiological and methodological considerations.* European Journal of Applied Physiology, 116(6), 1091-1116. Review. Early-phase rate of force development (first 50-75 ms) is governed by motor-unit recruitment and discharge rate, force in the first 40 ms of a rapid contraction is about 60% below the tetanic value, and athletic explosive tasks have contraction times of 50-250 ms. Used here to floor the start-ramp "give" - the centre-of-mass acceleration cannot ramp from zero to peak faster than the neuromuscular system develops propulsive force. Peak jerk of the centre of mass equals the net force rate divided by body mass, so the rate-of-force-development limit also bounds jerk.

## Notebook 02 impact dynamics

References behind the rigid-door impact model in `notebooks/02-kj-corridor-impact-dynamics.ipynb` and the library module `src/henryk_simulations/corridor/impact.py`. The model takes a 70 kg body striking a rigid door back-first, builds it from de Leva segment inertia, and resolves the strike through a 5-DOF Lobdell-style posterior-thorax mass-spring-damper chain scored against literature fracture thresholds.

- **de Leva, P. (1996).** *Adjustments to Zatsiorsky-Seluyanov's segment inertia parameters.* Journal of Biomechanics, 29(9), 1223-1230. Male segment mass fractions used to build the body-segment model and the effective impacting mass.
- **Lobdell, T.E., Kroell, C.K., Schneider, D.C., Hering, W.E. & Nahum, A.M. (1973).** *Impact response of the human thorax.* In Human Impact Response, Plenum Press. The lumped mass-spring-damper form of the 5-DOF posterior-thorax chain.
- **Kroell, C.K., Schneider, D.C. & Nahum, A.M. (1971).** *Impact tolerance and response of the human thorax.* 15th Stapp Car Crash Conference, SAE 710851. Force-deflection corridors and the 5-7 cm chest-compression range.
- **Viano, D.C. (1989).** *Biomechanical responses and injuries in blunt lateral impact.* 33rd Stapp Car Crash Conference, SAE 892432. The roughly 1.6 kN per loaded rib AIS 2+ threshold.
- **Cavanaugh, J.M. et al. (1990).** *Biomechanical response and injury tolerance of the thorax in twelve sled side impacts.* 34th Stapp Car Crash Conference, SAE 902307. The 25 mm deflection AIS 3+ threshold and the relaxed anterior chest stiffness baseline (~50 N/mm).
- **Stalnaker, R.L., McElhaney, J.H., Roberts, V.L. & Trollope, M.L. (1973).** *Human torso response to blunt trauma.* In Human Impact Response, Plenum Press. The tensed-versus-relaxed thoracic stiffness scaling (2.2-4.4x) behind the chain interface stiffnesses.
- **Kemper, A.R. et al. (2014).** *Rear-torso blunt-impact biomechanics.* Journal of Biomechanics. The 6.9-10.5 kN posterior-thorax tolerance band.

## Notes on use

Distributions in `references.py` are modelled as normal with the reported population means and SDs. This is appropriate for healthy adult subjects with motor-skill quantities that are approximately bell-shaped; the CIs computed at 95% therefore reflect between-subject biological variation, not measurement uncertainty. Where the original literature reports asymmetric or bounded distributions (e.g. yaw inertia, which cannot be negative), the normal approximation is adequate over the relevant range but should be replaced with a log-normal if extreme tail probabilities matter for a future analysis.
