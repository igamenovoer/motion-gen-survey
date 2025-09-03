Key commands (Windows pwsh via pixi):
- Install env: pixi install
- Full setup legacy: pixi run setup
- Full setup latest: pixi run -e latest setup
- Test CUDA: pixi run test-cuda / pixi run -e latest test-cuda
- Generate motion: pixi run generate-motion
- Help: pixi run help
Quality gates (manual for now): run a quick generation then inspect tests/check-flowmdm-result-animation.py via pixi run -e latest python tests/check-flowmdm-result-animation.py (if task adds output).