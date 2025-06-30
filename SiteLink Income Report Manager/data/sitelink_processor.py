"""
SiteLink data processing and management
"""
import pandas as pd
import json
from datetime import datetime
from config.settings import (
    EXPECTED_COLUMNS, NUMERIC_COLUMNS, 
    SAGE_MAPPING_PATH, DEFAULT_SAGE_MAPPING
)
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
        """Read and validate Excel file"""
        try:
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Handle Chg_dDisabled column
            if 'Chg_dDisabled' not in df.columns:
                df['Chg_dDisabled'] = 0
            
            # Validate columns
            missing_columns = set(EXPECTED_COLUMNS) - set(df.columns)
            if missing_columns:
                raise ValueError(f"Missing columns: {missing_columns}")
            
            # Add metadata columns
            df['report_month'] = report_month
            df['report_year'] = report_year
            df['upload_date'] = datetime.now().isoformat()
            
            # Clean numeric columns
            for col in NUMERIC_COLUMNS:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            return df
            
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def store_data(self, df):
        """Store processed data using database manager"""
        return self.db_manager.store_data(df)
    
    def get_financial_summary(self, report_month=None, report_year=None):
        """Get financial summary"""
        return self.db_manager.get_financial_summary(report_month, report_year)
    
    def prepare_sage_export(self, report_month, report_year):
        """Prepare data for Sage GLS export"""
        # Load mapping configuration
        with open(SAGE_MAPPING_PATH, 'r') as f:
            mapping = json.load(f)
        
        # Get data from database
        df = self.db_manager.get_sage_export_data(report_month, report_year)
        
        # Apply Sage mapping
        df['sage_account'] = df['sChgCategory'].map(
            mapping.get('category_mappings', {})
        ).fillna(df['sAcctCode'])
        
        # Format for Sage import
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
