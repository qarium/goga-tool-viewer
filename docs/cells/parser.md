# Parser

Cell `goga_tool_viewer/parser` — parsing JSON files with cell structure into a model data graph.

Depends on: [models](models.md)

## Functions

### parse_json

```python
parse_json(json_str: str) -> CellGraph
```

Parses a JSON string into `CellGraph`. JSON is an array of root cells at the top level.

- `json_str` — JSON file contents as a string
- Returns the complete project graph with all cells and dependencies

### load_json_file

```python
load_json_file(path: str) -> CellGraph
```

Reads a JSON file by path and passes its contents to `parse_json`.

- `path` — path to the JSON file
- Returns the complete project graph

### load_json_stdin

```python
load_json_stdin() -> CellGraph
```

Reads JSON from stdin and passes its contents to `parse_json`. Used with pipe:

```bash
cat data.json | goga tool viewer
```

- Returns the complete project graph

## Usage

```python
from goga_tool_viewer.parser import parse_json, load_json_file, load_json_stdin

# From string
graph = parse_json(json_string)

# From file
graph = load_json_file("path/to/data.json")

# From stdin
graph = load_json_stdin()
```

All load functions delegate parsing to `parse_json`.