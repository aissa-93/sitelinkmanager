# SiteLink Financial Data Manager

## Description

The SiteLink Financial Data Manager is a desktop application designed to streamline the process of handling financial reports from SiteLink. It allows users to import monthly financial data from Excel files, store it in a local database, and generate summaries and exports for accounting software like Sage GLS.

This tool is built with Python using the `tkinter` library for the graphical user interface, `pandas` for data manipulation, and `sqlite3` for database management.

## Features

  * **Import from Excel**: Import financial data from `.xlsx` or `.xls` files for a specific month and year.
  * **Data Validation**: The application checks for expected columns to ensure data integrity.
  * **Financial Summary**: View a detailed financial summary grouped by month, year, and charge category.
  * **Sage GLS Export**: Export financial data to a CSV file formatted for Sage GLS, based on customizable account mappings.
  * **Local Database**: All imported data is stored in a local SQLite database for persistence and easy access.

## Requirements

The application requires the following Python libraries:

  * pandas
  * openpyxl
  * tkinter
  * sqlite3
  * pathlib

You can install the necessary packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## How to Use

1.  **Launch the application**: Run the `main.py` file to start the SiteLink Financial Data Manager.
    ```bash
    python main.py
    ```
2.  **Import a Monthly Report**:
      * Select the **Month** and **Year** for the report you want to import.
      * Click the **Select & Import Excel File** button to choose the financial summary file from your computer.
      * A success message will confirm that the data has been imported.
3.  **View Financial Summary**:
      * Click the **View Summary** button to see a detailed breakdown of the financial data in the main window.
4.  **Export to Sage GLS**:
      * Select the **Month** and **Year** for the data you want to export.
      * Click the **Export to Sage GLS** button. A CSV file named `sage_export_{month}_{year}.csv` will be saved in the application's directory.

## Database

The application uses a SQLite database named `sitelink_financial_data.db` to store the imported data. It contains two main tables:

  * `financial_data`: Stores the raw, row-level data from the imported Excel files, with added metadata for the report month, year, and upload date.
  * `monthly_summary`: Contains aggregated financial totals for each month and year, including total charges, payments, credits, and net totals.

## Troubleshooting

### Error: "Failed to import file: Error storing data: table financial\_data has no column named Chg\_dDisabled"

This error occurs when the existing database file (`sitelink_financial_data.db`) is based on an older version of the application and is missing the `Chg_dDisabled` column.

**Solution**:

1.  **Close the application.**
2.  **Delete the database file**: Find and delete the `sitelink_financial_data.db` file located in the same directory as the application.
3.  **Restart the application**: When you run the application again, it will automatically create a new database file with the correct and up-to-date structure. You should now be able to import your files without any issues.
