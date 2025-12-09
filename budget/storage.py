"""Persistence helpers for the budgeting tool."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .models import BudgetData

PathLike = Union[str, Path]


def ensure_data_file(path: PathLike) -> Path:
    """Ensure the parent directory exists and the file is present."""

    file_path = Path(path)
    if not file_path.parent.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        file_path.write_text(json.dumps(BudgetData().to_dict(), indent=2), encoding="utf-8")
    return file_path


def load_data(path: PathLike) -> BudgetData:
    file_path = ensure_data_file(path)
    with file_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return BudgetData.from_dict(payload)


def save_data(path: PathLike, data: BudgetData) -> None:
    file_path = ensure_data_file(path)
    with file_path.open("w", encoding="utf-8") as handle:
        json.dump(data.to_dict(), handle, indent=2)
