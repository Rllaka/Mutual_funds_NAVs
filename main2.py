import tkinter as tk
from tkinter import Label, Entry, Button, messagebox, ttk, Frame, Canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from datetime import datetime
from mftool import Mftool
import numpy as np

obj = Mftool()

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(self, canvas, window):
        super().__init__(canvas, window)
        self.init_custom_buttons()

    def init_custom_buttons(self):
        self.save_button = tk.Button(self, text="Save Graph", command=self.save_graph, bg="lightgrey")
        self.save_button.pack(side=tk.LEFT, padx=2)

    def save_graph(self):
        self.canvas.figure.savefig("nav_comparison.png")
        messagebox.showinfo("Saved", "Graph saved as nav_comparison.png")

# Fetch Scheme Data
def fetch_scheme_data(scheme_code):
    scheme_data = obj.get_scheme_historical_nav(scheme_code)
    if not scheme_data or 'data' not in scheme_data:
        messagebox.showerror("Error", f"Failed to fetch data for scheme: {scheme_code}")
        return None, None, None

    dates = [datetime.strptime(entry['date'], "%d-%m-%Y") for entry in scheme_data['data']]
    nav_values = [float(entry['nav']) for entry in scheme_data['data']]
    return dates, nav_values

# Calculate Performance Metrics
def calculate_performance_metrics(nav_values):
    if len(nav_values) < 2:
        return 0, 0, 0
    returns = np.diff(nav_values) / nav_values[:-1]
    cagr = ((nav_values[-1] / nav_values[0]) ** (1 / (len(nav_values) / 365.0)) - 1) * 100
    std_dev = np.std(returns) * np.sqrt(252) * 100
    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
    return round(cagr, 2), round(std_dev, 2), round(sharpe_ratio, 2)

# Compare Schemes
def compare_schemes():
    try:
        common_start_date = datetime.strptime(start_date_entry.get(), "%d-%m-%Y")
        common_end_date = datetime.strptime(end_date_entry.get(), "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Use DD-MM-YYYY.")
        return

    scheme1_code = scheme1_entry.get()
    scheme2_code = scheme2_entry.get()
    
    dates1, nav_values1 = fetch_scheme_data(scheme1_code)
    dates2, nav_values2 = fetch_scheme_data(scheme2_code)
    
    if not dates1 or not dates2:
        return
    
    filtered_dates1 = [date for date in dates1 if common_start_date <= date <= common_end_date]
    filtered_nav_values1 = [nav for date, nav in zip(dates1, nav_values1) if common_start_date <= date <= common_end_date]
    
    filtered_dates2 = [date for date in dates2 if common_start_date <= date <= common_end_date]
    filtered_nav_values2 = [nav for date, nav in zip(dates2, nav_values2) if common_start_date <= date <= common_end_date]

    if not filtered_dates1 or not filtered_dates2:
        messagebox.showerror("Error", "No data available for selected date range.")
        return
    
    # Create Graph
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(filtered_dates1, filtered_nav_values1, '-o', label=f'Scheme {scheme1_code} NAV')
    ax.plot(filtered_dates2, filtered_nav_values2, '-o', label=f'Scheme {scheme2_code} NAV')
    ax.set_xlabel('Date')
    ax.set_ylabel('NAV')
    ax.set_title('NAV Comparison')
    ax.legend()
    ax.xaxis_date()
    ax.grid(True)
    
    # Display Graph in GUI
    for widget in plot_frame.winfo_children():
        widget.destroy()
    
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    toolbar = CustomToolbar(canvas, plot_frame)
    toolbar.update()
    
    # Calculate Performance Metrics
    cagr1, std_dev1, sharpe1 = calculate_performance_metrics(filtered_nav_values1)
    cagr2, std_dev2, sharpe2 = calculate_performance_metrics(filtered_nav_values2)
    
    # Get Scheme Details
    scheme1_details = obj.get_scheme_details(scheme1_code)
    scheme2_details = obj.get_scheme_details(scheme2_code)
    
    details_text = f"""
    Scheme 1: {scheme1_details.get('scheme_name', 'N/A')}
    Fund House: {scheme1_details.get('fund_house', 'N/A')}
    Type: {scheme1_details.get('scheme_type', 'N/A')}
    Category: {scheme1_details.get('scheme_category', 'N/A')}
    CAGR: {cagr1}% | Std Dev: {std_dev1} | Sharpe: {sharpe1}
    
    Scheme 2: {scheme2_details.get('scheme_name', 'N/A')}
    Fund House: {scheme2_details.get('fund_house', 'N/A')}
    Type: {scheme2_details.get('scheme_type', 'N/A')}
    Category: {scheme2_details.get('scheme_category', 'N/A')}
    CAGR: {cagr2}% | Std Dev: {std_dev2} | Sharpe: {sharpe2}
    """
    details_label.config(text=details_text)

# Create Scrollable Frame
def create_scrollable_frame(root):
    canvas = Canvas(root)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    frame = Frame(canvas)
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    return frame

# GUI Setup
root = tk.Tk()
root.title("Mutual Fund Comparison Tool")
scrollable_frame = create_scrollable_frame(root)

Label(scrollable_frame, text="Scheme 1 Code").pack()
scheme1_entry = Entry(scrollable_frame)
scheme1_entry.pack()

Label(scrollable_frame, text="Scheme 2 Code").pack()
scheme2_entry = Entry(scrollable_frame)
scheme2_entry.pack()

Label(scrollable_frame, text="Start Date (DD-MM-YYYY)").pack()
start_date_entry = Entry(scrollable_frame)
start_date_entry.pack()

Label(scrollable_frame, text="End Date (DD-MM-YYYY)").pack()
end_date_entry = Entry(scrollable_frame)
end_date_entry.pack()

Button(scrollable_frame, text="Compare Schemes", command=compare_schemes).pack()
details_label = Label(scrollable_frame, text="", justify="left")
details_label.pack()

plot_frame = Frame(scrollable_frame)
plot_frame.pack(fill='both', expand=True)

root.mainloop()
