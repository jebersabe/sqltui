# SqlTUI

A terminal-based SQL query interface built with [Textual](https://textual.textualize.io/), designed for interactive querying of Alibaba Cloud MaxCompute (ODPS) databases.

## Features

- **Interactive SQL Editor**: Code editor with SQL syntax highlighting
- **Real-time Results**: Execute queries and view results in a data table
- **Dark/Light Mode**: Toggle between themes for comfortable viewing
- **Keyboard Shortcuts**: Efficient query execution with `Ctrl+Enter`
- **Multi-process Data Loading**: Utilizes multiprocessing for faster data retrieval
- **Clean Interface**: Intuitive split-panel layout with query input and result display

## Screenshot

```
┌─────────────────────────────────────────────────────────────┐
│ Query                           │ Result                    │
│ ┌─────────────────────┐         │ ┌───────────────────────┐ │
│ │ SELECT * FROM ...   │         │ │ col1  │ col2  │ col3  │ │
│ │                     │         │ ├───────┼───────┼───────┤ │
│ │                     │         │ │ data  │ data  │ data  │ │
│ └─────────────────────┘         │ └───────────────────────┘ │
│ [Run] [Clear] [Exit]            │                           │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Alibaba Cloud MaxCompute account with credentials

### Install from source

```bash
# Clone the repository
git clone <repository-url>
cd sqltui

# Install the package
pip install -e .
```

### Install dependencies

```bash
pip install sqltui
```

## Configuration

SqlTUI requires environment variables to connect to your MaxCompute instance. Create a `.env` file in your project directory:

```env
ODPS_ID=your_access_id
ODPS_SECRET=your_secret_access_key
ODPS_PROJECT=your_project_name
```

Alternatively, set these environment variables in your shell:

```bash
export ODPS_ID="your_access_id"
export ODPS_SECRET="your_secret_access_key"
export ODPS_PROJECT="your_project_name"
```

**Note**: The default endpoint is configured for the Asia Pacific Southeast 1 region (`https://service.ap-southeast-1.maxcompute.aliyun.com/api`). You can modify this in `backend.py` if you need a different region.

## Usage

### Launch the application

```bash
sqltui
```

Or run directly with Python:

```bash
python -m sqltui
```

### Keyboard Shortcuts

- `Ctrl+Enter` - Execute the current query
- `d` - Toggle dark/light mode
- `q` - Quit the application

### Button Actions

- **Run** - Execute the SQL query in the editor
- **Clear** - Clear the query editor
- **Exit** - Close the application

## Development

### Install development dependencies

```bash
pip install -e ".[dev]"
```

### Run in development mode

For hot-reloading during development:

```bash
textual run --dev src/sqltui/main.py:SqlTUI
```

### Project Structure

```
sqltui/
├── src/
│   └── sqltui/
│       ├── __init__.py
│       ├── __main__.py      # Entry point
│       ├── main.py          # Main application and UI components
│       ├── backend.py       # ODPS connection handling
│       └── sqltui.tcss      # Textual CSS styling
├── pyproject.toml           # Project configuration
└── README.md
```

## Dependencies

- **textual[syntax]** - Terminal UI framework with syntax highlighting
- **pyodps** - Python SDK for Alibaba Cloud MaxCompute
- **pandas** - Data manipulation and analysis
- **python-dotenv** - Environment variable management

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

[Add your license here]

## Acknowledgments

Built with [Textual](https://textual.textualize.io/) by Textualize.io

## Troubleshooting

### Connection Issues

- Verify your ODPS credentials are correct
- Check that your `.env` file is in the correct location
- Ensure you have network access to the MaxCompute endpoint

### Query Errors

- Error messages will appear as notifications in the UI
- Check that your SQL syntax is compatible with MaxCompute
- Verify you have the necessary permissions for the query

### Performance

- Large result sets may take time to load
- The application uses multiprocessing to optimize data retrieval
- Consider limiting result sets with `LIMIT` clauses for faster response
