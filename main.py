from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


BASE_DIR = Path(__file__).resolve().parent
SOURCE_FILE = BASE_DIR / "expenses.csv"
SUMMARY_FILE = BASE_DIR / "monthly_expenses_summary.csv"
INVALID_FILE = BASE_DIR / "invalid_expenses.csv"

DATE_FORMATS: Tuple[str, ...] = (
	"%d-%m-%Y",
	"%d-%m-%y",
	"%d/%m/%Y",
	"%d/%m/%y",
)


@dataclass
class ExpenseRow:
	category: str
	amount: float
	details: str
	date: datetime

	@property
	def month_key(self) -> str:
		return self.date.strftime("%Y-%m")


def normalize_category(value: str | None) -> str:
	if value is None:
		raise ValueError("Missing category")

	cleaned = " ".join(value.strip().split())
	if not cleaned:
		raise ValueError("Missing category")
	return cleaned


def parse_amount(value: str | None) -> float:
	if value is None:
		raise ValueError("Missing amount")

	normalized = value.replace(",", "").strip()
	if not normalized:
		raise ValueError("Missing amount")

	try:
		return float(normalized)
	except ValueError as exc:
		raise ValueError("Invalid amount") from exc


def parse_date(value: str | None) -> datetime:
	if value is None:
		raise ValueError("Missing date")

	cleaned = value.strip()
	if not cleaned:
		raise ValueError("Missing date")

	for fmt in DATE_FORMATS:
		try:
			return datetime.strptime(cleaned, fmt)
		except ValueError:
			continue
	raise ValueError("Invalid date format")


def read_expenses(path: Path) -> Tuple[List[ExpenseRow], List[Dict[str, str]]]:
	valid_rows: List[ExpenseRow] = []
	invalid_rows: List[Dict[str, str]] = []

	if not path.exists():
		raise FileNotFoundError(f"Source file not found: {path}")

	with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
		reader = csv.DictReader(csv_file)
		for index, row in enumerate(reader, start=2):  # Header is row 1
			category_raw = row.get("Category", "")
			amount_raw = row.get("Amount", "")
			date_raw = row.get("Date", "")
			details_raw = row.get("Details", "") or ""

			try:
				category = normalize_category(category_raw)
			except ValueError as exc:
				invalid_rows.append(_invalid_row(row, index, str(exc)))
				continue

			try:
				amount = parse_amount(amount_raw)
			except ValueError as exc:
				invalid_rows.append(_invalid_row(row, index, str(exc)))
				continue

			try:
				date = parse_date(date_raw)
			except ValueError as exc:
				invalid_rows.append(_invalid_row(row, index, str(exc)))
				continue

			valid_rows.append(
				ExpenseRow(
					category=category,
					amount=amount,
					details=details_raw.strip(),
					date=date,
				)
			)

	return valid_rows, invalid_rows


def _invalid_row(row: Dict[str, str], row_number: int, reason: str) -> Dict[str, str]:
	output = {
		"RowNumber": str(row_number),
		"Category": (row.get("Category") or "").strip(),
		"Amount": (row.get("Amount") or "").strip(),
		"Details": (row.get("Details") or "").strip(),
		"Date": (row.get("Date") or "").strip(),
		"Reason": reason,
	}
	return output


def summarize_by_month(expenses: Iterable[ExpenseRow]) -> Dict[str, Dict[str, float]]:
	totals: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
	for expense in expenses:
		totals[expense.month_key][expense.category] += expense.amount
	return totals


def write_monthly_summary(path: Path, summary: Dict[str, Dict[str, float]]) -> None:
	with path.open("w", encoding="utf-8", newline="") as csv_file:
		fieldnames = ["Month", "Category", "TotalAmount"]
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()

		for month in sorted(summary.keys()):
			for category in sorted(summary[month].keys()):
				writer.writerow(
					{
						"Month": month,
						"Category": category,
						"TotalAmount": f"{summary[month][category]:.2f}",
					}
				)


def write_invalid_rows(path: Path, invalid_rows: List[Dict[str, str]]) -> None:
	if not invalid_rows:
		if path.exists():
			path.unlink()
		return

	with path.open("w", encoding="utf-8", newline="") as csv_file:
		fieldnames = ["RowNumber", "Category", "Amount", "Details", "Date", "Reason"]
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(invalid_rows)


def print_summary(summary: Dict[str, Dict[str, float]]) -> None:
	if not summary:
		print("No valid expense rows were found.")
		return

	print("Category-wise expenses by month:\n")
	for month in sorted(summary.keys()):
		print(f"{month}")
		for category, total in sorted(summary[month].items()):
			print(f"{category}, {total:.2f}")
		month_total = sum(summary[month].values())
		print(f"    Total: {month_total:.2f}\n")


def main() -> None:
	expenses, invalid_rows = read_expenses(SOURCE_FILE)
	summary = summarize_by_month(expenses)

	write_monthly_summary(SUMMARY_FILE, summary)
	write_invalid_rows(INVALID_FILE, invalid_rows)
	print_summary(summary)

	if invalid_rows:
		print(f"\n{len(invalid_rows)} row(s) were excluded. See '{INVALID_FILE.name}' for details.")


if __name__ == "__main__":
	main()
