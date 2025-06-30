"""
Main GUI window for SiteLink Financial Manager
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from config.settings import WINDOW_TITLE, WINDOW_SIZE, MONTHS
from data.sitelink_processor import SiteLinkProcessor

class SiteLinkGUI:
    def __init__(self):
        self.processor = SiteLinkProcessor()
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create and arrange GUI widgets"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(main_frame, text=WINDOW_TITLE, 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        self.create_import_section(main_frame)
        self.create_data_display_section(main_frame)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def create_import_section(self, parent):
        """Create import controls section"""
        import_frame = ttk.LabelFrame(parent, text="Import Monthly Report", padding="10")
        import_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(import_frame, text="Month:").grid(row=0, column=0, sticky=tk.W)
        self.month_var = tk.StringVar()
        month_combo = ttk.Combobox(import_frame, textvariable=self.month_var, values=MONTHS)
        month_combo.grid(row=0, column=1, padx=(5, 10), sticky=(tk.W, tk.E))
        
        ttk.Label(import_frame, text="Year:").grid(row=0, column=2, sticky=tk.W)
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        year_entry = ttk.Entry(import_frame, textvariable=self.year_var, width=10)
        year_entry.grid(row=0, column=3, padx=(5, 10))
        
        ttk.Button(import_frame, text="Select & Import Excel File", 
                  command=self.import_file).grid(row=0, column=4, padx=(10, 0))
    
    def create_data_display_section(self, parent):
        """Create data display section"""
        data_frame = ttk.LabelFrame(parent, text="Stored Data Viewer", padding="10")
        data_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        controls_frame = ttk.Frame(data_frame)
        controls_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="View All Stored Data", 
                  command=self.view_all_data).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(controls_frame, text="Export to Sage GLS", 
                  command=self.export_sage).grid(row=0, column=1, padx=(0, 10))
        
        self.results_text = tk.Text(data_frame, height=20, width=80, wrap=tk.NONE) # Changed width and wrap
        x_scrollbar = ttk.Scrollbar(data_frame, orient="horizontal", command=self.results_text.xview)
        y_scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        y_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        x_scrollbar.grid(row=2, column=0, sticky=(tk.W, tk.E)) # Added horizontal scrollbar
        
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)
    
    def import_file(self):
        """Handle file import"""
        if not self.month_var.get() or not self.year_var.get():
            messagebox.showerror("Error", "Please select month and year")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select SiteLink Financial Summary Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        
        if file_path:
            try:
                df = self.processor.read_excel_file(
                    file_path, self.month_var.get(), int(self.year_var.get())
                )
                self.processor.store_data(df)
                
                messagebox.showinfo("Success", 
                    f"Successfully imported {len(df)} records for {self.month_var.get()}/{self.year_var.get()}")
                
                self.view_all_data()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import file:\n{str(e)}")
    
    def view_all_data(self):
        """Display all raw data from the database"""
        try:
            all_data_df = self.processor.get_all_data()
            
            self.results_text.delete(1.0, tk.END)
            
            if all_data_df.empty:
                self.results_text.insert(tk.END, "No data available. Please import a report first.")
                return
            
            # Display the raw data as a string
            self.results_text.insert(tk.END, all_data_df.to_string())
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
    
    def export_sage(self):
        """Export data for Sage GLS"""
        if not self.month_var.get() or not self.year_var.get():
            messagebox.showerror("Error", "Please select month and year for export")
            return
        
        try:
            sage_df = self.processor.prepare_sage_export(
                self.month_var.get(), int(self.year_var.get())
            )
            
            if sage_df.empty:
                messagebox.showwarning("Warning", "No data available for selected month/year")
                return
            
            filename = f"sage_export_{self.month_var.get()}_{self.year_var.get()}.csv"
            sage_df.to_csv(filename, index=False)
            
            messagebox.showinfo("Success", f"Sage GLS export saved as: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export for Sage:\n{str(e)}")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()
