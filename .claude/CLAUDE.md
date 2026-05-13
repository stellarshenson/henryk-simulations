<!-- @import /home/lab/workspace/.claude/CLAUDE.md -->

# Project-Specific Configuration

This file imports workspace-level configuration from `/home/lab/workspace/.claude/CLAUDE.md`.
All workspace rules apply. Project-specific rules below strengthen or extend them.

The workspace `/home/lab/workspace/.claude/` directory contains additional instruction files
(MERMAID.md, NOTEBOOK.md, DATASCIENCE.md, GIT.md, and others) referenced by CLAUDE.md.
Consult workspace CLAUDE.md and the .claude directory to discover all applicable standards.

## Mandatory Bans (Reinforced)

The following workspace rules are STRICTLY ENFORCED for this project:

- **No automatic git tags** - only create tags when user explicitly requests
- **No automatic version changes** - only modify version in `pyproject.toml` when user explicitly requests
- **No automatic publishing** - never run `make publish`, `twine upload`, or similar without explicit user request
- **No manual package installs if Makefile exists** - use `make install` or equivalent Makefile targets, not direct `pip install` / `uv install`
- **No automatic git commits or pushes** - only when user explicitly requests

## Project Context

`henryk-simulations` is a private Python physics simulation project. The scaffold was generated from `copier-data-science` v1.3.5.

**Purpose**: Build numerical and physics-based simulations of specific real-world events to disclose the role of physical laws (forces, accelerations, momenta, energies, biomechanical constraints) in those events. Output is intended for personal analysis and amusement, not for public distribution.

**First simulation target**: A two-body movement sequence in a 2 m corridor over 3 seconds, parameterised by body masses (90 kg, 70 kg), required rotations, and number of sub-phases (pull, swap, throw, neck-reach, reverse). Goal is to compute required velocities, accelerations, G-loads, impulses, kinetic energies, and to evaluate biomechanical plausibility.

**Technology Stack**:
- Python 3.12 managed by `uv` (virtual environment at `.venv`, kernel name `henryk-sim`)
- `ruff` for lint and format (line length 99)
- `pytest` with `pytest-cov` for tests
- `loguru`, `tqdm`, `typer`, `python-dotenv` as runtime dependencies
- Numerical stack (numpy, scipy, matplotlib, pandas) NOT yet declared - to be added when the first simulation lands

**Module layout**: source under `src/henryk_simulations/` (`config.py`, `dataset.py`, `features.py`, `modeling/`, `plots.py`), notebooks under `notebooks/`, reports under `reports/`, figures under `reports/figures/`.

**Working directory boundary**: never reach outside `/home/lab/workspace/private/henryk/henryk-simulations/` unless the user explicitly asks. This is a private project and outputs should stay local unless told otherwise.

## Journal Rules (Project-Specific)

- **APPEND ONLY**: New journal entries MUST be appended at the end of the file, never inserted between existing entries
- Entries maintain strict chronological order by position - the last entry in the file is always the most recent work
- Never reorder, move, or insert entries out of sequence
- The Stellars **journal plugin** is the canonical tool for this file: create via `/journal:create`, append via `/journal:update`, archive via `/journal:archive`. The `journal:journal` skill auto-triggers on any mention of "journal" and runs `journal-tools check` after every write
- Direct edits to `JOURNAL.md` are a last resort - prefer the plugin so modus secundis format, continuous numbering and append-only order are enforced automatically

## Strengthened Rules

- **Simulation outputs must be reproducible**: any numerical simulation produces fixed-seed results, parameters logged inline in the notebook, and figures saved to `reports/figures/` with the notebook number prefix
- **Physics-first, not framework-first**: prefer explicit Newtonian/Lagrangian math written out in markdown cells before reaching for libraries. The point of this project is to expose the physics, not to hide it behind an engine
- **Sensitivity to the subject matter**: simulations describe forces and bodies as physical objects. Code, comments, and documentation stay strictly technical and neutral. No editorialising in source files. Conversational framing happens in chat, not in artefacts
- **Notebook standards mandatory**: follow the `notebook-standards` plugin skill - GPU cell (if applicable) before imports, grouped imports, centralised config, markdown headers per section. Number prefix on notebook filenames (`01-kj-corridor-kinematics.ipynb`)
- **Use the Makefile**: `make install` to set up the env, `make test`, `make lint`, `make format`. Do not bypass with direct `uv pip install`
