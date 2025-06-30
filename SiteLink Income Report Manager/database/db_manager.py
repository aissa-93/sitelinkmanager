"""
Database management for SiteLink Financial Data
"""
import sqlite3
import pandas as pd
from datetime import datetime
from config.settings import DATABASE_PATH, EXPECTED_COLUMNS

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
        self.migrate_database()

    def init_database(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create main financial data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_month TEXT NOT NULL,
                report_year INTEGER NOT NULL,
                upload_date TEXT NOT NULL,
                SiteID TEXT,
                ChargeDescID TEXT,
                sChgCategory TEXT,
                sChgDesc TEXT,
                sDefAcctCode TEXT,
                sAcctCode TEXT,
                Price REAL,
                Charge REAL,
                Discount REAL,
                ChargeTax1 REAL,
                ChargeTax2 REAL,
                ChargeTotal REAL,
                Payment REAL,
                PaymentTax1 REAL,
                PaymentTax2 REAL,
                PaymentTotal REAL,
                Credit REAL,
                CreditTax1 REAL,
                CreditTax2 REAL,
                CreditTotal REAL,
                TotalCost REAL,
                iCount INTEGER,
                dcPercent REAL,
                Chg_dDisabled INTEGER DEFAULT 0,
                Chg_dDeleted INTEGER DEFAULT 0,
                UNIQUE(report_month, report_year, SiteID, ChargeDescID, sChgCategory, sChgDesc)
            )
        ''')

        # Create summary table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monthly_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_month TEXT NOT NULL,
                report_year INTEGER NOT NULL,
                total_charges REAL,
                total_payments REAL,
                total_credits REAL,
                net_total REAL,
                record_count INTEGER,
                created_date TEXT,
                UNIQUE(report_month, report_year)
            )
        ''')

        conn.commit()
        conn.close()

    def migrate_database(self):
        """Handle database migrations for schema updates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA table_info(financial_data)")
            columns = [column[1] for column in cursor.fetchall()]

            if 'Chg_dDisabled' not in columns:
                cursor.execute('ALTER TABLE financial_data ADD COLUMN Chg_dDisabled INTEGER DEFAULT 0')
            
            if 'Chg_dDeleted' not in columns:
                cursor.execute('ALTER TABLE financial_data ADD COLUMN Chg_dDeleted INTEGER DEFAULT 0')

            conn.commit()
        except Exception as e:
            print(f"Migration error (this is usually safe to ignore): {e}")
        finally:
            conn.close()

    def store_data(self, df):
        """Store DataFrame in database"""
        conn = sqlite3.connect(self.db_path)
        
        # Define all columns the database expects
        db_columns = [
            'report_month', 'report_year', 'upload_date', 'SiteID', 'ChargeDescID', 'sChgCategory', 
            'sChgDesc', 'sDefAcctCode', 'sAcctCode', 'Price', 'Charge', 'Discount', 'ChargeTax1', 
            'ChargeTax2', 'ChargeTotal', 'Payment', 'PaymentTax1', 'PaymentTax2', 'PaymentTotal', 
            'Credit', 'CreditTax1', 'CreditTax2', 'CreditTotal', 'TotalCost', 'iCount', 
            'dcPercent', 'Chg_dDisabled', 'Chg_dDeleted'
        ]
        
        # Filter the DataFrame to only include columns that exist in the database table
        df_to_store = df[[col for col in db_columns if col in df.columns]]

        try:
            report_month = df_to_store['report_month'].iloc[0]
            report_year = df_to_store['report_year'].iloc[0]

            conn.execute(
                "DELETE FROM financial_data WHERE report_month = ? AND report_year = ?",
                (report_month, report_year)
            )

            df_to_store.to_sql('financial_data', conn, if_exists='append', index=False)
            self.create_monthly_summary(conn, report_month, report_year) # Still useful for later
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise Exception(f"Error storing data: {str(e)}")
        finally:
            conn.close()

    def create_monthly_summary(self, conn, report_month, report_year):
        """Create monthly summary calculations"""
        conn.execute(
            "DELETE FROM monthly_summary WHERE report_month = ? AND report_year = ?",
            (report_month, report_year)
        )
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                SUM(ChargeTotal), SUM(PaymentTotal), SUM(CreditTotal),
                SUM(TotalCost), COUNT(*)
            FROM financial_data
            WHERE report_month = ? AND report_year = ?
        ''', (report_month, report_year))
        
        result = cursor.fetchone()
        
        conn.execute('''
            INSERT INTO monthly_summary
            (report_month, report_year, total_charges, total_payments,
             total_credits, net_total, record_count, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report_month, report_year, result[0] or 0, result[1] or 0,
            result[2] or 0, result[3] or 0, result[4] or 0,
            datetime.now().isoformat()
        ))

    def get_all_data(self):
        """Get all raw data from the financial_data table"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM financial_data ORDER BY id"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_financial_summary(self, report_month=None, report_year=None):
        """Get financial summary with filtering options"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT
                report_month, report_year, sChgCategory, sAcctCode,
                SUM(ChargeTotal) as total_charges,
                SUM(PaymentTotal) as total_payments,
                SUM(CreditTotal) as total_credits,
                SUM(TotalCost) as net_total,
                COUNT(*) as transaction_count,
                SUM(CASE WHEN Chg_dDisabled = 1 THEN 1 ELSE 0 END) as disabled_charges
            FROM financial_data
        '''
        
        params = []
        conditions = []
        if report_month:
            conditions.append("report_month = ?")
            params.append(report_month)
        if report_year:
            conditions.append("report_year = ?")
            params.append(report_year)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " GROUP BY report_month, report_year, sChgCategory, sAcctCode"
        query += " ORDER BY report_year DESC, report_month DESC, sChgCategory"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df

    def get_sage_export_data(self, report_month, report_year):
        """Get data formatted for Sage GLS export"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT
                sChgCategory, sAcctCode, sDefAcctCode,
                SUM(ChargeTotal) as debit_amount,
                SUM(PaymentTotal) as credit_amount
            FROM financial_data
            WHERE report_month = ? AND report_year = ? AND Chg_dDisabled = 0
            GROUP BY sChgCategory, sAcctCode, sDefAcctCode
            HAVING ABS(debit_amount) + ABS(credit_amount) > 0
        '''
        
        df = pd.read_sql_query(query, conn, params=[report_month, report_year])
        conn.close()
        return df

    def reset_database(self):
        """Reset database - use only if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS financial_data")
        cursor.execute("DROP TABLE IF EXISTS monthly_summary")
        conn.commit()
        conn.close()
        self.init_database()
        print("Database reset completed!")
