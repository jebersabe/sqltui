# sqltui

A terminal-based SQL client for Alibaba Cloud MaxCompute (ODPS) built with [Textual](https://github.com/Textualize/textual). It provides a split-pane TUI for writing SQL, running queries, and exploring table partitions across multiple configured projects.

## Features

- Textual-based TUI with a query editor and results table
- Project selector backed by a YAML config file
- Execution of SQL queries against MaxCompute / ODPS
- Display of query results in a scrollable table
- Quick partition inspection for a given table
- Keyboard shortcuts for common actions (run, clear, check partitions)

## Requirements

- Python >= 3.11
- An Alibaba Cloud MaxCompute (ODPS) environment
- Valid ODPS credentials available as environment variables
- A `config.yaml` file in the project root defining available projects

The core dependencies (managed via `pyproject.toml`) include:

- `textual[syntax]`
- `pandas`
- `pyodps`
- `python-dotenv`
- `pyyaml`

## Installation

This project is set up for use with [uv](https://github.com/astral-sh/uv) and standard PEP 621 metadata.

### Option 1: Install as a package

From the project root:

```bash
uv sync
uv run sqltui
```

This will install dependencies and run the `sqltui` entry point defined in `pyproject.toml`.

### Option 2: Run directly with Textual dev

From the project root, in development mode:

```bash
uv sync
uv run textual run --dev src/sqltui/__main__.py
```

This runs the app with Textual's dev tools (hot reload, debug console, etc.).

## Configuration

Two configuration layers are used:

1. **Environment variables** for ODPS credentials
2. **`config.yaml`** for project definitions

### Environment variables

Credentials are loaded via `python-dotenv`, so you can either export them in your shell or define them in a `.env` file at the project root.

For each project, the `config.yaml` refers to keys that are the *names* of the environment variables storing the actual secrets. For example:

- `access_key`: the name of the env var holding the ODPS access ID (e.g. `ODPS_ACCESS_ID_DEV`)
- `secret_key`: the name of the env var holding the ODPS secret key (e.g. `ODPS_ACCESS_KEY_DEV`)

Example `.env` file:

```env
ODPS_ACCESS_ID_DEV=your_access_id_here
ODPS_ACCESS_KEY_DEV=your_secret_here
ODPS_ACCESS_ID_PROD=your_access_id_here
ODPS_ACCESS_KEY_PROD=your_secret_here
```

### `config.yaml`

The app expects a `config.yaml` in the project root directory. It must contain a top-level `projects` list. Each project entry should have at least:

- `name`: ODPS project name (also the label in the TUI project selector)
- `access_key`: env var name for the access ID
- `secret_key`: env var name for the secret key

Example `config.yaml`:

```yaml
projects:
  - name: dev_project
    access_key: ODPS_ACCESS_ID_DEV
    secret_key: ODPS_ACCESS_KEY_DEV
  - name: prod_project
    access_key: ODPS_ACCESS_ID_PROD
    secret_key: ODPS_ACCESS_KEY_PROD
```

If `config.yaml` is missing, the app will log an error and raise a `FileNotFoundError` on startup.

## Usage

Once installed and configured:

```bash
uv run sqltui
```

### Layout

- **Top bar**: Textual header and a project selector (`Select`) showing the configured projects.
- **Left panel**: SQL query editor (`TextArea`) with syntax highlighting.
- **Bottom of left panel**: Action buttons: `Run`, `Check Partitions`, `Clear`, and `Exit`.
- **Right panel**: Results table (`DataTable`) showing query results or partition lists.
- **Bottom bar**: Textual footer with helpful key binding hints.

### Keyboard shortcuts

- `Ctrl+Enter` — Run current query
- `Ctrl+T` — Check partitions for the given table
- `Ctrl+L` — Clear the query editor

### Actions

- **Selecting a project**: Use the dropdown at the top to choose an ODPS project. The app uses the corresponding credentials to create an `ODPS` client.
- **Running a query**:
  - Type (or paste) a SQL query into the left-hand editor.
  - Press `Ctrl+Enter` or click **Run**.
  - Results will be loaded into the right-hand `DataTable`.
- **Checking partitions**:
  - Enter a table name (e.g. `my_db.my_table`) in the editor.
  - Press `Ctrl+T` or click **Check Partitions**.
  - The app checks if the table exists and then lists its partitions in the results panel.
- **Clearing**: Press `Ctrl+L` or click **Clear** to clear the editor.
- **Exiting**: Click **Exit** or close the terminal window.

### Error handling

- If no project is selected when you try to run a query, the app shows an in-app warning notification.
- Most ODPS-related issues (invalid credentials, connectivity, missing tables) are caught and displayed as error notifications with truncated messages.

## Development

The main application class is `SqlTUI` in `src/sqltui/main.py`. Supporting pieces include:

- `src/sqltui/__main__.py` — entry point for the Textual app and the `sqltui` console script.
- `src/sqltui/backend.py` — helpers for creating an `ODPS` instance from environment variables and loading YAML config.
- `src/sqltui/sqltui.tcss` — Textual CSS theme and layout configuration.

### Running in dev mode

From the project root:

```bash
uv run textual run --dev src/sqltui/__main__.py
```

You can then modify the app code and see changes reflected live while the dev server is running.

## Troubleshooting

- **`config.yaml not found`**: Ensure that `config.yaml` exists in the project root and matches the expected schema shown above.
- **Credentials not working**: Confirm that the env var names in `config.yaml` match actual variables set in your shell or `.env` file.
- **No projects populated in the selector**: Check that `projects` is a non-empty list in `config.yaml` and that YAML indentation is correct.
- **Connection/ODPS errors**: Inspect the terminal logs and in-app notifications for the underlying `pyodps` error messages.

## License

Apache
