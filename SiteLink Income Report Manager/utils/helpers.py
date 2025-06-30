"""
Utility functions for SiteLink Financial Manager
"""
import pandas as pd
from datetime import datetime

def validate_date_range(start_date, end_date):
    """Validate date range inputs"""
    try:
        start = datetime.strptime(start_date, "%Y-%m")
        end = datetime.strptime(end_date, "%Y-%m")
        return start <= end
    except ValueError:
        return False

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def export_to_excel(df, filename):
    """Export DataFrame to Excel with formatting"""
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='SiteLink_Data', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['SiteLink_Data']
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

def get_month_name(month_number):
    """Convert month number to name"""
    months = {
        '01': 'January', '02': 'February', '03': 'March',
        '04': 'April', '05': 'May', '06': 'June',
        '07': 'July', '08': 'August', '09': 'September',
        '10': 'October', '11': 'November', '12': 'December'
    }
    return months.get(month_number, 'Unknown')
