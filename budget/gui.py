"""Tkinter-based graphical interface for the budgeting tool."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk
import tkinter as tk

from .models import BudgetData, Entry
from .storage import load_data, save_data


class BudgetApp:
    """Simple GUI for adding entries and viewing summaries."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Budget Helper")

        self.data_path_var = tk.StringVar(value=str(Path.home() / ".budget" / "budget_data.json"))
        self._load_current_data()

        self._build_layout()

    def _load_current_data(self) -> None:
        self.data = load_data(Path(self.data_path_var.get()))

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Data file chooser
        data_row = ttk.Frame(main)
        data_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        data_row.columnconfigure(1, weight=1)
        ttk.Label(data_row, text="Data file:").grid(row=0, column=0, padx=(0, 8))
        ttk.Entry(data_row, textvariable=self.data_path_var).grid(row=0, column=1, sticky="ew")
        ttk.Button(data_row, text="Use file", command=self._reload_data).grid(row=0, column=2, padx=(8, 0))

        # Entry fields
        form = ttk.Labelframe(main, text="Add income or expense", padding=10)
        form.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Amount:").grid(row=0, column=0, sticky="w", pady=2)
        self.amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.amount_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Description:").grid(row=1, column=0, sticky="w", pady=2)
        self.description_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.description_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Date (YYYY-MM-DD):").grid(row=2, column=0, sticky="w", pady=2)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(form, textvariable=self.date_var).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(form, text="Category (expenses):").grid(row=3, column=0, sticky="w", pady=2)
        self.category_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.category_var).grid(row=3, column=1, sticky="ew", pady=2)

        button_row = ttk.Frame(form)
        button_row.grid(row=4, column=0, columnspan=2, pady=(8, 0))
        ttk.Button(button_row, text="Add income", command=self._add_income).grid(row=0, column=0, padx=4)
        ttk.Button(button_row, text="Add expense", command=self._add_expense).grid(row=0, column=1, padx=4)

        # Budgets
        budgets = ttk.Labelframe(main, text="Budgets", padding=10)
        budgets.grid(row=2, column=0, sticky="nsew", padx=(0, 12), pady=(10, 0))
        budgets.columnconfigure(1, weight=1)

        ttk.Label(budgets, text="Category:").grid(row=0, column=0, sticky="w", pady=2)
        self.budget_category_var = tk.StringVar()
        ttk.Entry(budgets, textvariable=self.budget_category_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(budgets, text="Amount:").grid(row=1, column=0, sticky="w", pady=2)
        self.budget_amount_var = tk.StringVar()
        ttk.Entry(budgets, textvariable=self.budget_amount_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Button(budgets, text="Set budget", command=self._set_budget).grid(row=2, column=0, columnspan=2, pady=(8, 0))

        # Summary panel
        summary = ttk.Labelframe(main, text="Monthly summary", padding=10)
        summary.grid(row=1, column=1, rowspan=2, sticky="nsew")
        summary.columnconfigure(1, weight=1)
        summary.rowconfigure(2, weight=1)

        ttk.Label(summary, text="Month (YYYY-MM):").grid(row=0, column=0, sticky="w", pady=2)
        self.summary_month_var = tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(summary, textvariable=self.summary_month_var).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(summary, text="Show summary", command=self._show_summary).grid(row=0, column=2, padx=(8, 0))

        self.summary_text = tk.Text(summary, width=50, height=18, state="disabled")
        self.summary_text.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(8, 0))

        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(main, textvariable=self.status_var, foreground="green")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 0))

    def _set_status(self, message: str, error: bool = False) -> None:
        self.status_var.set(message)
        color = "red" if error else "green"
        self.status_label.configure(foreground=color)
        self.root.update_idletasks()
        if error:
            messagebox.showerror("Budget Helper", message)

    def _reload_data(self) -> None:
        try:
            self._load_current_data()
            self._set_status(f"Loaded data from {self.data_path_var.get()}")
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Failed to load data: {exc}", error=True)

    def _parse_amount(self, value: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise ValueError("Please enter a valid number for the amount")

    def _parse_date(self, value: str) -> date:
        try:
            return date.fromisoformat(value)
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")

    def _add_income(self) -> None:
        try:
            amount = self._parse_amount(self.amount_var.get())
            entry_date = self._parse_date(self.date_var.get())
            description = self.description_var.get().strip()
            if not description:
                raise ValueError("Description cannot be empty")

            entry = Entry(amount=amount, description=description, entry_date=entry_date)
            self.data.add_income(entry)
            save_data(self.data_path_var.get(), self.data)
            self._set_status(f"Saved income: {amount:.2f} on {entry_date}")
        except Exception as exc:  # noqa: BLE001
            self._set_status(str(exc), error=True)

    def _add_expense(self) -> None:
        try:
            amount = self._parse_amount(self.amount_var.get())
            entry_date = self._parse_date(self.date_var.get())
            description = self.description_var.get().strip()
            if not description:
                raise ValueError("Description cannot be empty")

            category = self.category_var.get().strip() or None
            entry = Entry(amount=amount, description=description, entry_date=entry_date, category=category)
            self.data.add_expense(entry)
            save_data(self.data_path_var.get(), self.data)
            label = f" [{category}]" if category else ""
            self._set_status(f"Saved expense: {amount:.2f} on {entry_date}{label}")
        except Exception as exc:  # noqa: BLE001
            self._set_status(str(exc), error=True)

    def _set_budget(self) -> None:
        try:
            category = self.budget_category_var.get().strip()
            if not category:
                raise ValueError("Category cannot be empty")
            amount = self._parse_amount(self.budget_amount_var.get())
            self.data.set_budget(category, amount)
            save_data(self.data_path_var.get(), self.data)
            self._set_status(f"Budget for '{category}' set to {amount:.2f}")
        except Exception as exc:  # noqa: BLE001
            self._set_status(str(exc), error=True)

    def _show_summary(self) -> None:
        try:
            month = self.summary_month_var.get().strip()
            if not month:
                raise ValueError("Month cannot be empty")
            summary = self.data.monthly_summary(month)
            self._display_summary(month, summary)
            self._set_status(f"Summary updated for {month}")
        except Exception as exc:  # noqa: BLE001
            self._set_status(str(exc), error=True)

    def _display_summary(self, month: str, summary: dict[str, object]) -> None:
        lines = [
            f"Summary for {month}",
            "-" * 32,
            f"Total income:  {summary['income_total']:.2f}",
            f"Total expense: {summary['expense_total']:.2f}",
            f"Net:           {summary['net']:.2f}",
            "",
        ]

        if summary["category_spend"]:
            lines.append("Category spending:")
            for category, total in summary["category_spend"].items():
                lines.append(f"  - {category}: {total:.2f}")
            lines.append("")

        if summary["remaining_by_category"]:
            lines.append("Remaining by category:")
            for category, remaining in summary["remaining_by_category"].items():
                status = "within" if remaining >= 0 else "over"
                lines.append(f"  - {category}: {remaining:.2f} ({status})")

        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", "\n".join(lines))
        self.summary_text.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    BudgetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
