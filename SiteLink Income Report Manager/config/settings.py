"""
Configuration settings for SiteLink Financial Manager
"""
import os
from pathlib import Path

# Database configuration
DATABASE_NAME = "sitelink_financial_data.db"
DATABASE_PATH = Path.cwd() / DATABASE_NAME

# Sage mapping configuration
SAGE_MAPPING_FILE = "sage_gls_mapping.json"
SAGE_MAPPING_PATH = Path.cwd() / SAGE_MAPPING_FILE

# Expected Excel columns
EXPECTED_COLUMNS = [
    'SiteID', 'ChargeDescID', 'sChgCategory', 'sChgDesc', 
    'sDefAcctCode', 'sAcctCode', 'Price', 'Charge', 'Discount',
    'ChargeTax1', 'ChargeTax2', 'ChargeTotal', 'Payment',
    'PaymentTax1', 'PaymentTax2', 'PaymentTotal', 'Credit',
    'CreditTax1', 'CreditTax2', 'CreditTotal', 'TotalCost',
    'iCount', 'dcPercent', 'Chg_dDisabled'
]

# Numeric columns for data processing
NUMERIC_COLUMNS = [
    'Price', 'Charge', 'Discount', 'ChargeTax1', 'ChargeTax2',
    'ChargeTotal', 'Payment', 'PaymentTax1', 'PaymentTax2',
    'PaymentTotal', 'Credit', 'CreditTax1', 'CreditTax2',
    'CreditTotal', 'TotalCost', 'iCount', 'dcPercent', 'Chg_dDisabled'
]

# Default Sage GLS mapping
DEFAULT_SAGE_MAPPING = {
    "account_mappings": {
        "revenue_accounts": {
            "rental_income": "4000",
            "late_fees": "4010",
            "administrative_fees": "4020"
        },
        "tax_accounts": {
            "sales_tax": "2200",
            "county_tax": "2210"
        }
    },
    "category_mappings": {
        "Rent": "4000",
        "Late Fee": "4010",
        "Admin Fee": "4020",
        "Insurance": "4030"
    }
}

# GUI Settings
WINDOW_TITLE = "SiteLink Financial Data Manager"
WINDOW_SIZE = "800x600"
MONTHS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
