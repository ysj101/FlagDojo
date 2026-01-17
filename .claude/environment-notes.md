# FlagDojo Environment Notes

## Shell Configuration

This project uses `uv` command which is wrapped by safechain in `.zshrc`.

### Important: Running uv commands

**Problem**: The Bash tool runs in non-interactive mode and doesn't load `.zshrc`, so the `uv` shell function is not available.

**Solution**: Always use interactive zsh when running uv commands:

```bash
# ❌ This won't work (no output, silent failure)
uv sync

# ✅ Use this instead
zsh -i -c "uv sync"
zsh -i -c "uv pip install <package>"
zsh -i -c "uv run <command>"
```

## Project Structure

- Main package directory: `app/`
- Project name in pyproject.toml: `flagdojo`
- Python version requirement: >=3.11
- Build backend: hatchling

## Build Configuration

The `pyproject.toml` includes:

```toml
[tool.hatch.build.targets.wheel]
packages = ["app"]
```

This is necessary because the project name (`flagdojo`) doesn't match the package directory name (`app`).

## Common Commands

```bash
# Install dependencies
zsh -i -c "uv sync"

# Run the application
zsh -i -c "uv run python run.py"

# Install dev dependencies
zsh -i -c "uv sync --extra dev"
```
