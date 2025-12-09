"""Command-line interface for the budgeting tool."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Optional

from .models import BudgetData, Entry
from .storage import load_data, save_data


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Monthly budgeting helper")
    parser.add_argument(
        "--data-file",
        default=Path.home() / ".budget" / "budget_data.json",
        help="Path to the JSON data file",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_income_parser = subparsers.add_parser("add-income", help="Record an income entry")
    _add_entry_arguments(add_income_parser)

    add_expense_parser = subparsers.add_parser("add-expense", help="Record an expense entry")
    _add_entry_arguments(add_expense_parser, include_category=True)

    set_budget_parser = subparsers.add_parser("set-budget", help="Set monthly budget for a category")
    set_budget_parser.add_argument("category", help="Budget category name")
    set_budget_parser.add_argument("amount", type=float, help="Monthly budget amount")

    summary_parser = subparsers.add_parser("summary", help="Show summary for a month")
    summary_parser.add_argument("month", help="Month in YYYY-MM format")

    return parser.parse_args(args=args)


def _add_entry_arguments(parser: argparse.ArgumentParser, include_category: bool = False) -> None:
    parser.add_argument("amount", type=float, help="Amount of the entry")
    parser.add_argument("description", help="Short description")
    parser.add_argument(
        "--date",
        dest="entry_date",
        default=date.today().isoformat(),
        help="Entry date in YYYY-MM-DD (defaults to today)",
    )
    if include_category:
        parser.add_argument("--category", help="Expense category", default=None)


def main(raw_args: Optional[list[str]] = None) -> None:
    args = parse_args(raw_args)
    data_file = Path(args.data_file)
    data = load_data(data_file)

    if args.command == "add-income":
        entry = Entry(amount=args.amount, description=args.description, entry_date=date.fromisoformat(args.entry_date))
        data.add_income(entry)
        save_data(data_file, data)
        print(f"Saved income: {entry.amount:.2f} on {entry.entry_date} ({entry.description})")
    elif args.command == "add-expense":
        entry = Entry(
            amount=args.amount,
            description=args.description,
            entry_date=date.fromisoformat(args.entry_date),
            category=args.category,
        )
        data.add_expense(entry)
        save_data(data_file, data)
        category_info = f" [{entry.category}]" if entry.category else ""
        print(f"Saved expense: {entry.amount:.2f} on {entry.entry_date}{category_info} ({entry.description})")
    elif args.command == "set-budget":
        data.set_budget(args.category, args.amount)
        save_data(data_file, data)
        print(f"Budget for '{args.category}' set to {args.amount:.2f}")
    elif args.command == "summary":
        summary = data.monthly_summary(args.month)
        _print_summary(args.month, summary)


def _print_summary(month: str, summary: dict[str, object]) -> None:
    print(f"Summary for {month}\n{'-' * 32}")
    print(f"Total income:  {summary['income_total']:.2f}")
    print(f"Total expense: {summary['expense_total']:.2f}")
    print(f"Net:           {summary['net']:.2f}\n")

    if summary["category_spend"]:
        print("Category spending:")
        for category, total in summary["category_spend"].items():
            print(f"  - {category}: {total:.2f}")
        print()

    if summary["remaining_by_category"]:
        print("Remaining by category:")
        for category, remaining in summary["remaining_by_category"].items():
            status = "within" if remaining >= 0 else "over"
            print(f"  - {category}: {remaining:.2f} ({status})")


if __name__ == "__main__":
    main()
