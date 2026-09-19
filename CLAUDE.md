# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- Run application: `python app.py` (runs on port 5001)
- Run all tests: `pytest`
- Run a specific test file: `pytest path/to/test_file.py`
- Install dependencies: `pip install -r requirements.txt`

## Code Architecture

This is a Flask-based web application for tracking expenses.

### High-Level Structure
- `app.py`: Main entry point. Defines the Flask application and all URL routes.
- `database/`: Contains database logic. `db.py` is the primary location for connection management and schema initialization (currently a placeholder for student implementation).
- `templates/`: Jinja2 HTML templates for the frontend.
- `static/`: Static assets, including CSS (`static/css/style.css`) and JavaScript (`static/js/main.js`).

### Key Patterns
- **Routing**: Routes are defined using `@app.route` decorators in `app.py`.
- **Templating**: Uses `render_template` to serve HTML pages from the `templates/` directory.
- **Database**: Designed to use SQLite (to be implemented in `database/db.py`).
