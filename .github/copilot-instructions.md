# AI Coding Agent Instructions

Concise, project-specific guidance to help AI agents work effectively in this repository.

## 0. General Rules
- AVOID running inline python code when using CLI tools, create scripts in `tmp/` instead, and run the script with `pixi run` or `pixi run -e (whatever env) <script>`.

## 1. Repository Purpose & High-Level Layout
This repo is a survey + implementation workspace for human motion generation. Two distinct layers:
- `context/` knowledge system (design docs, roles, tasks, logs) following a strict HEADER metadata convention.
- `model_zoo/` vendor / third‑party model snapshots (e.g. `FlowMDM/`). Treat these as mostly external; limit intrusive refactors.
Other dirs (`tests/`, `scripts/`, `data/`, `tmp/`) provide test harnesses, utility scripts, sample outputs.

## 2. Key Conventions
- All documentation additions in knowledge space must include a HEADER block (see `context/README.md`).
- Do not auto-upgrade dependencies inside third‑party model subtrees unless fixing a clearly scoped bug (add rationale in commit message and doc in `explain/`).
- Use `pixi` for environment + tasks (FlowMDM supplies both legacy (PyTorch 1.13) and `latest` (PyTorch 2.x) envs). Prefer `pixi run -e latest <task>` for new scripts unless reproducing original paper metrics.
- Motion data shape standard: `[batch, 22, 3, seq_len]` (T2M skeleton). Kinematic chains defined in `model_zoo/FlowMDM/data_loaders/humanml/utils/paramUtil.py`.

## 3. Developer Workflows
| Goal | Command (PowerShell / Windows) | Notes |
|------|--------------------------------|-------|
| Install base env | `pixi install` | Creates default (legacy) env. |
| Full setup (default env) | `pixi run setup` | Downloads SpaCy + chumpy (legacy build). |
| Full setup (latest env) | `pixi run -e latest setup` | Modern toolchain (PyTorch 2.7.1 CUDA 12.6). |
| Test CUDA | `pixi run test-cuda` / `pixi run -e latest test-cuda` | Prints GPU info. |
| Generate motion (example) | `pixi run generate-motion` | Uses Babel sample instructions. |
| Show generation help | `pixi run help` | Lists CLI flags. |

When adding new tasks prefer adding to `[tool.pixi.tasks]` in the nearest `pyproject.toml`.

## 4. Visualization & Known Pitfalls
- Preferred interactive viewer: `tests/check-flowmdm-result-animation.py` (PyVista). Fast, in-place point updates.
- Matplotlib video functions live in `data_loaders/humanml/utils/plot_script.py`.
- Known bug (documented in `model_zoo/FlowMDM/explain/BUG-matplotlib-rendering.md`): backend set after `pyplot` import caused blank MP4 output. Future fixes must move `matplotlib.use('Agg')` before importing `pyplot` and optionally switch to `fig.add_subplot(..., projection='3d')`.
- Always verify motion arrays (no NaNs, expected shape) before attributing visualization failures to model output.

## 5. Code Patterns & Architecture (FlowMDM)
Core flow for generation (`runners/generate.py`):
1. Parse args (`utils/parser_util.py`).
2. Load model + diffusion wrapper (`utils/model_util.py`, `diffusion/`).
3. Sample with BPE schedule (`DiffusionWrapper_FlowMDM`).
4. Convert features → joints (`feats_to_xyz`).
5. Save `results.npy` + MP4 via plot utilities.

Important modules:
- `model/FlowMDM.py`: Network definition + blended positional encodings logic.
- `diffusion/diffusion_wrappers.py`: Orchestrates sampling stages.
- `data_loaders/` subpackages: Dataset adapters, feature recovery (`recover_from_ric`).
- `utils/` helpers: seeding, distributed utils, metrics, parsing.

Avoid deep rewrites of these unless adding an isolated feature—prefer extension via new module or wrapper.

## 6. Data & Formats
- Output file: `results.npy` dict keys: `motion`, `text`, `lengths`, `num_samples`, `num_repetitions`.
- Concatenated text segments separated by `" /// "` (split for per‑segment labeling).
- Frame rates: HumanML3D 20 FPS, Babel 30 FPS (`datasets_fps`).
- Coordinate system: Y-up, meters. Root (pelvis) index 0.

## 7. Testing & Quality Gates
- Lightweight syntax test: run any quick script under pixi (no central test suite yet beyond placeholder `tests/`).
- Type checking (legacy tolerant): `mypy` config ignores many third‑party imports; don't enforce strict typing retroactively inside vendor code.
- Lint: `ruff` & `black` (respect target versions: py38/py39). Only apply formatting to new/own modules—avoid churn in vendored sources.

## 8. Making Changes Safely
- For third‑party code modifications: add a short rationale file under `model_zoo/FlowMDM/explain/CHANGELOG-LOCAL.md` (create if missing) or append to existing bug doc.
- Keep patches minimal; prefer function-level overrides in new files rather than editing original heavy modules.
- Document any change affecting output determinism (sampling schedule, guidance, normalization) in `explain/`.

## 9. Adding New Visualization or Analysis
- Reuse joint topology from `paramUtil.t2m_kinematic_chain`.
- Use in-place numpy updates (`np.copyto`) for performance if building interactive tools.
- Provide a fallback pure-matplotlib path only if headless export needed; otherwise PyVista is primary.

## 10. AI Assistant Behavior Guidelines
- Always check `context/` for domain knowledge before answering conceptual questions.
- When generating new docs, include HEADER block unless file lives under `.github/`.
- Propose, then implement: for risky refactors, stage a plan referencing concrete files.
- Prefer environment-specific commands with `pixi run -e latest` unless reproducing paper results.

## 11. Quick Reference Paths
- Model: `model_zoo/FlowMDM/model/FlowMDM.py`
- Diffusion wrapper: `model_zoo/FlowMDM/diffusion/diffusion_wrappers.py`
- Generation script: `model_zoo/FlowMDM/runners/generate.py`
- Visualization util: `model_zoo/FlowMDM/data_loaders/humanml/utils/plot_script.py`
- Output docs: `model_zoo/FlowMDM/explain/about-flowmdm-output-format.md`
- Bug docs: `model_zoo/FlowMDM/explain/BUG-matplotlib-rendering.md`

## 12. Non-Goals
- Do NOT auto-upgrade PyTorch or alter sampling defaults without explicit request.
- Do NOT rewrite vendored academic code styles for aesthetics alone.

---
Feedback welcome—clarify unclear areas and extend sections only when backed by code patterns in the repo.
