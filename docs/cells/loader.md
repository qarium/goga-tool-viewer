# Loader

Cell `goga_tool_viewer/loader` — project file loader for reading CODEMANIFEST and usage files from the filesystem.

## Functions

### load_codemanifest

```python
load_codemanifest(cell_path: str, project_root: str = '') -> str
```

Reads a CODEMANIFEST file by cell path and returns its contents as a string.

- `cell_path` — relative path to a cell (e.g. `"goga_tool_viewer/parser"`)
- `project_root` — absolute path to the project root. If empty, uses the current working directory
- Returns the text content of the CODEMANIFEST file

Raises `ValueError` if the path contains `..`, starts with `/`, or escapes the project root. Raises `FileNotFoundError` if the file is not found.

### load_usage_file

```python
load_usage_file(usage_path: str, project_root: str = '') -> str
```

Reads a usage `.md` file by relative path from the project root and returns its contents as a string.

- `usage_path` — relative path to a `.md` file from the project root (e.g. `".goga/usages/conventions.md"` or `"goga_tool_viewer/parser/.usages/loading.md"`)
- `project_root` — absolute path to the project root. If empty, uses the current working directory
- Returns the text content of the usage file

Raises `ValueError` if the path contains `..`, starts with `/`, escapes the project root, or does not have a `.md` extension. Raises `FileNotFoundError` if the file is not found.

## Path Traversal Protection

Both functions implement two-level path validation:

1. **String-level check** — rejects `..` and leading `/`
2. **Resolve-based check** — verifies the resolved path stays within the project root

## Usage

```python
from goga_tool_viewer.loader import load_codemanifest, load_usage_file

# Load a CODEMANIFEST
content = load_codemanifest("goga_tool_viewer/parser", "/path/to/project")

# Load a usage file
usage = load_usage_file("goga_tool_viewer/parser/.usages/loading.md", "/path/to/project")
```
