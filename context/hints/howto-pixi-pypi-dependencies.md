# How to Handle PyPI Dependencies in Pixi: Extra Index URLs and Git Repositories

This guide covers how to properly configure PyPI dependencies in pixi environments, specifically dealing with `--extra-index-url` and `git+https://` installations that you might have used with traditional pip.

## Overview

Pixi uses `uv` under the hood for PyPI package resolution and installation, which provides better performance and stricter dependency resolution than traditional pip. This requires a different approach for handling custom package indices and git-based dependencies.

## Configuring Extra Index URLs

### Global PyPI Options (Recommended)

Add a `[pypi-options]` section at the project level to apply to all environments:

```toml
[project]
name = "my-project"
channels = ["conda-forge"]
platforms = ["win-64", "linux-64"]

[pypi-options]
# Main PyPI index (optional, defaults to https://pypi.org/simple)
index-url = "https://pypi.org/simple"
# Additional PyPI indices - order matters (first found wins)
extra-index-urls = [
    "https://custom-index.example.com/simple",
    "https://private-repo.company.com/simple"
]
```

**PyTorch Example** (as a concrete use case):
```toml
[pypi-options]
extra-index-urls = [
    "https://download.pytorch.org/whl/cu117"  # PyTorch CUDA wheels
]
```

### Environment-Specific PyPI Options

For environment-specific configurations:

```toml
[environments.special-env]
features = ["custom-packages"]
pypi-options = { extra-index-urls = ["https://custom-index.example.com/simple"] }

[environments.default] 
features = ["base"]
# Uses default PyPI only
```

**PyTorch Example** (GPU vs CPU environments):
```toml
[environments.gpu]
features = ["cuda"]
pypi-options = { extra-index-urls = ["https://download.pytorch.org/whl/cu117"] }

[environments.cpu] 
features = ["base"]
# Uses default PyPI only
```

### Feature-Specific PyPI Options

For feature-specific configurations:

```toml
[feature.special-feature.pypi-options]
extra-index-urls = ["https://custom-index.example.com/simple"]

[feature.special-feature.pypi-dependencies]
custom-package = ">=1.0.0"
specialized-tool = ">=2.0.0"
```

**PyTorch Example** (CUDA-specific feature):
```toml
[feature.cuda.pypi-options]
extra-index-urls = ["https://download.pytorch.org/whl/cu117"]

[feature.cuda.pypi-dependencies]
torch = "2.0.0+cu117"
torchvision = "0.15.0+cu117"
```

## Git Dependencies

### Basic Git Dependency Syntax

Convert `pip install git+https://...` to pixi format:

```toml
[pypi-dependencies]
# Generic examples
package-from-git = { git = "https://github.com/user/repo.git" }
another-package = { git = "https://github.com/organization/project.git" }

# From: pip install git+https://github.com/user/repo.git
my-custom-package = { git = "https://github.com/user/repo.git" }
```

**Common Real-World Examples**:
```toml
[pypi-dependencies]
# From: pip install git+https://github.com/openai/CLIP.git
clip-by-openai = { git = "https://github.com/openai/CLIP.git" }

# From: pip install git+https://github.com/company/internal-tool.git
internal-tool = { git = "https://github.com/company/internal-tool.git" }
```

### Advanced Git Options

```toml
[pypi-dependencies]
# Specific commit/revision
stable-package = { git = "https://github.com/user/repo.git", rev = "abc123def456" }

# Specific branch (limited support in some pixi versions)
dev-package = { git = "https://github.com/user/repo.git", branch = "develop" }

# Specific tag (limited support in some pixi versions)  
release-package = { git = "https://github.com/user/repo.git", tag = "v1.0.0" }

# SSH URLs for private repositories
private-package = { git = "ssh://git@github.com/company/private-repo.git" }

# Subdirectory within repository
sub-package = { git = "https://github.com/user/monorepo.git", subdirectory = "packages/subproject" }
```

## Real-World Migration Example

**Note: This example uses PyTorch as a concrete case study, but the same principles apply to any package requiring custom indices or git dependencies.**

### Before: Traditional pip approach

```bash
# Example setup script or requirements
pip install torch==1.13.0+cu117 torchvision==0.14.0+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
pip install git+https://github.com/openai/CLIP.git
pip install git+https://github.com/user/custom-library.git
```

### After: Pixi configuration

```toml
[project]
name = "example-project"
channels = ["conda-forge"]
platforms = ["win-64", "linux-64"]

[pypi-options]
# PyTorch example: CUDA wheels require custom index
extra-index-urls = [
    "https://download.pytorch.org/whl/cu117"
]

[feature.ml-workflow.pypi-dependencies]
# PyTorch example: Packages from custom index
torch = "1.13.0+cu117"
torchvision = "0.14.0+cu117"

# Git-based dependencies (common pattern for research libraries)
clip-by-openai = { git = "https://github.com/openai/CLIP.git" }
custom-library = { git = "https://github.com/user/custom-library.git" }

# Regular PyPI packages
numpy = ">=1.23.0,<1.25"
matplotlib = ">=3.1.0"
```

## Important Differences from Pip

### Strict Index Priority

Unlike pip, pixi (via uv) uses **strict index priority**:
- The first index where a package is found is used
- `extra-index-urls` are checked before `index-url`
- Order in the TOML array matters

```toml
[pypi-options]
extra-index-urls = [
    "https://priority-1.example.com/simple",  # Checked first
    "https://priority-2.example.com/simple"   # Checked second
]
index-url = "https://pypi.org/simple"  # Checked last (default)
```

**PyTorch Example**: Why order matters for CUDA packages:
```toml
[pypi-options]
extra-index-urls = [
    "https://download.pytorch.org/whl/cu117",  # PyTorch CUDA wheels (checked first)
    "https://download.pytorch.org/whl/cpu"     # PyTorch CPU fallback (checked second)
]
# PyPI default index checked last
```

### No Dependency Links

Pixi doesn't support pip's `--find-links` option directly. Use `find-links` in `pypi-options` instead:

```toml
[pypi-options]
find-links = [
    { path = "./local-wheels" },
    { url = "https://example.com/wheels/" }
]
```

## Best Practices

### 1. Prefer Conda Packages When Available

```toml
[dependencies]
# Prefer conda packages for better performance and compatibility
numpy = ">=1.23.0,<1.25"
scipy = ">=1.9.0,<2.0"
matplotlib = ">=3.1.0"

[pypi-dependencies]
# Use PyPI only when necessary or for specialized packages
research-specific-package = ">=1.0.0"
company-internal-tool = ">=2.0.0"
```

**PyTorch Note**: While PyTorch is available via conda, CUDA-specific versions often require PyPI with custom indices.

### 2. Pin Git Dependencies for Reproducibility

```toml
[pypi-dependencies]
# Good: Pinned to specific commit for reproducibility
stable-package = { git = "https://github.com/user/repo.git", rev = "abc123def456" }
production-tool = { git = "https://github.com/org/tool.git", tag = "v2.1.0" }

# Avoid: Unpinned (uses latest commit, not reproducible)
# unstable-package = { git = "https://github.com/user/repo.git" }
```

### 3. Use Environment-Specific Configurations

```toml
# Example: Different package sources for different compute environments
[feature.gpu-computing.pypi-options]
extra-index-urls = ["https://custom-gpu-packages.example.com/simple"]

[feature.gpu-computing.pypi-dependencies]
gpu-accelerated-lib = ">=2.0.0"

[feature.cpu-only.pypi-dependencies]
cpu-optimized-lib = ">=1.0.0"
```

**PyTorch Example**: Separate GPU and CPU environments:
```toml
[feature.gpu.pypi-options]
extra-index-urls = ["https://download.pytorch.org/whl/cu117"]

[feature.gpu.pypi-dependencies]
torch = "2.0.0+cu117"

[feature.cpu.pypi-dependencies]
torch = "2.0.0+cpu"
```

### 4. Test Configuration Changes

```bash
# Test installation in specific environment
pixi install -e your-environment-name

# Verify package sources and versions
pixi info -e your-environment-name

# Check for conflicts
pixi tree -e your-environment-name
```

## Troubleshooting

### Common Issues

1. **Package not found in extra index**
   - Verify URL format (should end with `/simple`)
   - Check index priority order
   - Test URL accessibility

2. **Git authentication issues**
   - Use SSH URLs for private repos
   - Configure SSH keys properly
   - Consider using access tokens in HTTPS URLs

3. **Dependency conflicts**
   - Review pixi's strict resolution rules
   - Check for version conflicts between conda and PyPI packages
   - Use `pixi tree` to inspect dependency graph

### Debugging Commands

```bash
# Show environment information
pixi info -e environment-name

# Show dependency tree
pixi tree -e environment-name

# Install with verbose output
pixi install -e environment-name -v

# Check package installation
pixi run -e environment-name python -c "import package_name; print(package_name.__version__)"
```

## Migration Checklist

- [ ] Identify all `--extra-index-url` usage in scripts
- [ ] Convert to `[pypi-options]` section in pixi.toml
- [ ] Identify all `git+https://` installations
- [ ] Convert to `{ git = "..." }` format in `pypi-dependencies`
- [ ] Pin git dependencies to specific commits/tags
- [ ] Test installation with `pixi install`
- [ ] Update setup scripts to remove manual pip commands
- [ ] Document new installation process

## References

- [Pixi Project Configuration Documentation](https://prefix-dev.github.io/pixi/reference/project_configuration/)
- [PyPI Dependencies in Pixi](https://prefix-dev.github.io/pixi/python/pyproject_toml/)
- [UV Index Configuration](https://docs.astral.sh/uv/pip/index/)
- [Git Dependencies Best Practices](https://prefix-dev.github.io/pixi/tutorials/python/)

## Example Projects

- [PyTorch CUDA Environment Example](https://github.com/prefix-dev/pixi/tree/main/examples/pytorch-cuda) *(PyTorch as concrete example)*
- [Git Dependencies Discussion](https://github.com/prefix-dev/pixi/discussions/1710)
- [Complex PyPI Configuration Examples](https://github.com/prefix-dev/pixi/tree/main/examples)
