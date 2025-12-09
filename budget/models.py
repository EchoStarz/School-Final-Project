"""Core budgeting data model for tracking income, expenses, and budgets."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


@dataclass
class Entry:
    """Represents a single income or expense entry."""

    amount: float
    description: str
    entry_date: date
    category: Optional[str] = None

    def to_dict(self) -> Dict[str, str]:
        return {
            "amount": self.amount,
            "description": self.description,
            "entry_date": self.entry_date.isoformat(),
            "category": self.category or "",
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Entry":
        return cls(
            amount=float(data["amount"]),
            description=data["description"],
            entry_date=date.fromisoformat(data["entry_date"]),
            category=data.get("category") or None,
        )


@dataclass
class BudgetData:
    """Holds all budgeting information for a household."""

    income: List[Entry] = field(default_factory=list)
    expenses: List[Entry] = field(default_factory=list)
    budgets: Dict[str, float] = field(default_factory=dict)

    def add_income(self, entry: Entry) -> None:
        self.income.append(entry)

    def add_expense(self, entry: Entry) -> None:
        self.expenses.append(entry)

    def set_budget(self, category: str, amount: float) -> None:
        self.budgets[category] = amount

    def monthly_summary(self, month: str) -> Dict[str, float]:
        """Return totals for a given month (YYYY-MM)."""

        income_total = sum(e.amount for e in self._filter_by_month(self.income, month))
        expense_total = sum(e.amount for e in self._filter_by_month(self.expenses, month))
        category_spend: Dict[str, float] = {}

        for entry in self._filter_by_month(self.expenses, month):
            if entry.category:
                category_spend[entry.category] = category_spend.get(entry.category, 0) + entry.amount

        remaining_by_category = {
            category: self.budgets.get(category, 0) - category_spend.get(category, 0)
            for category in self.budgets
        }

        return {
            "income_total": income_total,
            "expense_total": expense_total,
            "net": income_total - expense_total,
            "category_spend": category_spend,
            "remaining_by_category": remaining_by_category,
        }

    @staticmethod
    def _filter_by_month(entries: List[Entry], month: str) -> List[Entry]:
        return [entry for entry in entries if entry.entry_date.strftime("%Y-%m") == month]

    def to_dict(self) -> Dict[str, object]:
        return {
            "income": [entry.to_dict() for entry in self.income],
            "expenses": [entry.to_dict() for entry in self.expenses],
            "budgets": self.budgets,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "BudgetData":
        return cls(
            income=[Entry.from_dict(entry) for entry in data.get("income", [])],
            expenses=[Entry.from_dict(entry) for entry in data.get("expenses", [])],
            budgets={k: float(v) for k, v in data.get("budgets", {}).items()},
        )
