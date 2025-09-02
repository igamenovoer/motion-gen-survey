# Development Environment Guide

This project includes a comprehensive development environment with testing, type checking, and linting tools.

## Quick Start

### Install Development Environment
```bash
pixi install -e dev
```

### Activate Development Shell
```bash
pixi shell -e dev
```

## Available Development Tools

### 🧪 Testing with pytest

Run all tests:
```bash
pixi run -e dev test
```

Run tests with coverage:
```bash
pixi run -e dev test-cov
```

Run tests in parallel (faster):
```bash
pixi run -e dev test-parallel
```

Run only fast tests (skip slow tests):
```bash
pixi run -e dev test -m "not slow"
```

### 🔍 Type Checking with mypy

Check types in scripts:
```bash
pixi run -e dev typecheck
```

Strict type checking:
```bash
pixi run -e dev typecheck-strict
```

### 🎨 Linting and Formatting with ruff

Check code style:
```bash
pixi run -e dev lint
```

Auto-fix linting issues:
```bash
pixi run -e dev lint-fix
```

Format code:
```bash
pixi run -e dev format
```

Check formatting without changes:
```bash
pixi run -e dev format-check
```

### 🚀 Combined Commands

Run all quality checks (lint + typecheck + test):
```bash
pixi run -e dev check-all
```

Fix all auto-fixable issues (lint + format):
```bash
pixi run -e dev fix-all
```

## Environment Structure

The `dev` environment includes:

### Base Packages (from default)
- PyTorch with CUDA 12.6
- PyVista for 3D visualization
- SMPLX body models
- CLIP vision-language model
- Trimesh for 3D mesh processing

### Development Tools (dev feature)
- **pytest**: Testing framework with plugins
  - pytest-cov: Coverage reporting
  - pytest-xdist: Parallel execution
  - pytest-timeout: Test timeouts
  - pytest-mock: Mocking support
  - hypothesis: Property-based testing

- **mypy**: Static type checker
  - Type stubs for major libraries

- **ruff**: Fast Python linter and formatter
  - Replaces flake8, black, isort
  - Configured in `ruff.toml`

## Configuration Files

- `pyproject.toml`: pytest, mypy, coverage settings
- `ruff.toml`: Linting and formatting rules
- `pixi.toml`: Environment and dependency definitions

## Writing Tests

Tests go in the `tests/` directory. Example test structure:

```python
# tests/test_example.py
import pytest

class TestExample:
    @pytest.fixture
    def sample_data(self):
        return {"key": "value"}
    
    def test_something(self, sample_data):
        assert sample_data["key"] == "value"
    
    @pytest.mark.slow
    def test_slow_operation(self):
        # Long-running test
        pass
    
    @pytest.mark.gpu
    def test_gpu_required(self):
        # GPU-dependent test
        pass
```

## Test Markers

Available pytest markers:
- `@pytest.mark.slow`: Slow tests (can skip with `-m "not slow"`)
- `@pytest.mark.gpu`: Tests requiring GPU
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.unit`: Unit tests

## Type Hints

Add type hints to improve code quality:

```python
from typing import Optional, List, Dict
import numpy as np
from numpy.typing import NDArray

def process_motion(
    data: NDArray[np.float32],
    frame_idx: int,
    normalize: bool = True
) -> Optional[Dict[str, NDArray]]:
    """Process motion data with type hints."""
    if data.ndim != 4:
        return None
    
    result: Dict[str, NDArray] = {
        "joints": data[0, :, :, frame_idx],
        "frame": np.array([frame_idx])
    }
    return result
```

## Pre-commit Workflow

Before committing code:

1. Format code:
   ```bash
   pixi run -e dev format
   ```

2. Fix linting issues:
   ```bash
   pixi run -e dev lint-fix
   ```

3. Run tests:
   ```bash
   pixi run -e dev test
   ```

4. Check types:
   ```bash
   pixi run -e dev typecheck
   ```

Or run everything at once:
```bash
pixi run -e dev check-all
```

## VS Code Integration

Recommended settings for `.vscode/settings.json`:

```json
{
    "python.linting.enabled": false,
    "python.formatting.provider": "none",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll.ruff": true,
            "source.organizeImports.ruff": true
        }
    },
    "ruff.path": ["${workspaceFolder}/.pixi/envs/dev/bin/ruff"],
    "mypy-type-checker.path": ["${workspaceFolder}/.pixi/envs/dev/bin/mypy"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestPath": "${workspaceFolder}/.pixi/envs/dev/bin/pytest"
}
```

## Continuous Integration

For GitHub Actions, use:

```yaml
- name: Install pixi
  uses: prefix-dev/setup-pixi@v0.4.0
  
- name: Install dev environment
  run: pixi install -e dev
  
- name: Run quality checks
  run: pixi run -e dev check-all
```