# Expense Summary

A simple Python script to process and summarize personal expense records from a CSV file, grouping expenses by month and category. It also detects and logs invalid rows for review.

## Features

- Reads expenses from `expenses.csv`.
- Validates and parses each row (category, amount, date, details).
- Supports multiple date formats (`dd-mm-yyyy`, `dd/mm/yyyy`, etc.).
- Outputs a monthly summary of expenses by category to `monthly_expenses_summary.csv`.
- Logs invalid or incomplete rows to `invalid_expenses.csv` for inspection.
- Prints a readable summary to the console.

## Usage

1. **Prepare your CSV file**

   Create an `expenses.csv` file in the same directory as the script, with the following headers:

   ```
   Category,Amount,Details,Date
   ```

   Example:
   ```
   Food,12.50,Lunch,01-09-2025
   Transport,5.00,Bus ticket,01/09/2025
   ```

2. **Run the script**

   ```bash
   python your_script_name.py
   ```

3. **Check the outputs**
   - `monthly_expenses_summary.csv` — category-wise monthly totals.
   - `invalid_expenses.csv` — any rows with missing or invalid data.
   - Console output — formatted summary and any warnings about invalid data.

## Requirements

- Python 3.8+
- No third-party dependencies (uses standard library)

## Customization

- To use a different input file, modify the `SOURCE_FILE` variable in the script.
- Date formats can be adjusted via the `DATE_FORMATS` tuple.

## File Descriptions

- `expenses.csv` — Input file containing raw expense records.
- `monthly_expenses_summary.csv` — Output file with summarized expenses.
- `invalid_expenses.csv` — Output file listing invalid entries and reasons.

## Example Output

```
Category-wise expenses by month:

2025-09
Food, 12.50
Transport, 5.00
    Total: 17.50
```

## License

MIT License

## Author

shank250
