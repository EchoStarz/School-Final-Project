# School Final Project

A simple monthly budgeting program written in Python. It stores income, expenses, and category budgets in a local JSON file and provides both a command-line interface and a lightweight Tkinter GUI for quick updates and summaries.

## Features
- Record income and expenses with descriptions, dates, and optional categories.
- Set monthly budgets per category.
- View monthly summaries including totals, category spending, and remaining budget.

## Getting Started
The tool uses only the Python standard library and works with Python 3.9+.

### Graphical interface
Use the GUI to add income/expenses, set budgets, and view monthly summaries without typing commands.

```bash
python -m budget.gui
```

On Windows, you can also double-click the bundled `run_gui.bat` to launch the app using your default Python installation.

### Running commands
Use the CLI via `python -m budget.cli` and choose a data file location (defaults to `~/.budget/budget_data.json`).

```bash
# Add income
python -m budget.cli add-income 2000 "Paycheck" --date 2024-05-31

# Add an expense with a category
python -m budget.cli add-expense 80 "Groceries at Market" --category groceries

# Set a budget for a category
python -m budget.cli set-budget groceries 350

# View a monthly summary
python -m budget.cli summary 2024-05
```

The data file will be created automatically if it does not exist.
