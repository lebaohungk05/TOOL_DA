This project use uv as package manager, do not use pip directly to install package, do not use python directly to run script, instead use:
```bash
uv pip install [package-name]
```
to install package
and use:
```bash
uv run script.py
```
to run script.

If the project do not have .venv, instantiate it with 
```bash
uv venv
```