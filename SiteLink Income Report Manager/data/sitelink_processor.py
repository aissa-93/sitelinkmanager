"""
SiteLink data processing and management
"""
import pandas as pd
import json
from datetime import datetime
from config.settings import SAGE_MAPPING_PATH, DEFAULT_SAGE_MAPPING
from database.db_manager import DatabaseManager

class SiteLinkProcessor:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.init_sage_mapping()
    
    def init_sage_mapping(self):
        """Initialize Sage GLS mapping configuration"""
        if not SAGE_MAPPING_PATH.exists():
            with open(SAGE_MAPPING_PATH, 'w') as f:
                json.dump(DEFAULT_SAGE_MAPPING, f, indent=4)
    
    def read_excel_file(self, file_path, report_month, report_year):
        """
        Read and process the Excel file.
        """
        try:
            df = pd.read_excel(file_path)
            
            df['report_month'] = report_month
            df['report_year'] = report_year
            df['upload_date'] = datetime.now().isoformat()
            
            db_columns = [
                'SiteID', 'ChargeDescID', 'sChgCategory', 'sChgDesc', 'sDefAcctCode', 'sAcctCode',
                'Price', 'Charge', 'Discount', 'ChargeTax1', 'ChargeTax2', 'ChargeTotal',
                'Payment', 'PaymentTax1', 'PaymentTax2', 'PaymentTotal', 'Credit',
                'CreditTax1', 'CreditTax2', 'CreditTotal', 'TotalCost', 'iCount',
                'dcPercent', 'Chg_dDisabled', 'Chg_dDeleted'
            ]
            
            for col in db_columns:
                if col not in df.columns:
                    df[col] = 0
            
            return df
            
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def store_data(self, df):
        """Store processed data using database manager"""
        try:
            return self.db_manager.store_data(df)
        except Exception as e:
            raise e

    def get_all_data(self):
        """Get all raw data for display"""
        return self.db_manager.get_all_data()

    def get_financial_summary(self, report_month=None, report_year=None):
        """Get financial summary"""
        return self.db_manager.get_financial_summary(report_month, report_year)

    def prepare_sage_export(self, report_month, report_year):
        """Prepare data for Sage GLS export"""
        with open(SAGE_MAPPING_PATH, 'r') as f:
            mapping = json.load(f)
        
        df = self.db_manager.get_sage_export_data(report_month, report_year)
        
        df['sage_account'] = df['sChgCategory'].map(
            mapping.get('category_mappings', {})
        ).fillna(df['sAcctCode'])
        
        sage_export = []
        for _, row in df.iterrows():
            if row['debit_amount'] != 0:
                sage_export.append({
                    'Account': row['sage_account'],
                    'Description': row['sChgCategory'],
                    'Debit': abs(row['debit_amount']),
                    'Credit': 0,
                    'Reference': f"{report_month}-{report_year}"
                })
            
            if row['credit_amount'] != 0:
                sage_export.append({
                    'Account': row['sage_account'],
                    'Description': row['sChgCategory'],
                    'Debit': 0,
                    'Credit': abs(row['credit_amount']),
                    'Reference': f"{report_month}-{report_year}"
                })
        
        return pd.DataFrame(sage_export)
