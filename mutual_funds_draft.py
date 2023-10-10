from mftool import Mftool
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.dates import date2num
from datetime import datetime

obj = Mftool()


def display_scheme_growth_rate(): 
    scheme_code = scheme_entry.get() 
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    
    
    scheme_quote = obj.get_scheme_quote(scheme_code)
    scheme_name = scheme_quote.get('scheme_name', 'N/A')
    last_updated = scheme_quote.get('last_updated', 'N/A')
    nav = scheme_quote.get('nav', 'N/A')
    
    
    scheme_details_label.config(text=f"Scheme Code: {scheme_code}\n"
                                     f"Scheme Name: {scheme_name}\n"
                                     f"Last Updated: {last_updated}\n"
                                     f"NAV: {nav}")
    
    
    historical_nav_data = obj.get_scheme_historical_nav(scheme_code)
    #print("Historical NAV Data:")
    #print(historical_nav_data)
    
    
    dates = [datetime.strptime(entry['date'], "%d-%m-%Y") for entry in historical_nav_data['data']]
    nav_values = [float(entry['nav']) for entry in historical_nav_data['data']]
    
    
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    end_date = datetime.strptime(end_date, "%d-%m-%Y")
    
  
    filtered_dates = []  
    filtered_nav_values = []
    for i in range(len(dates)):
        if start_date <= dates[i] <= end_date:
            filtered_dates.append(dates[i])
            filtered_nav_values.append(nav_values[i])
    
   
    datewise_growth_data = []
    for i in range(1, len(filtered_nav_values)):
        growth_rate = ((filtered_nav_values[i] - filtered_nav_values[i-1]) / filtered_nav_values[i-1]) * 100
        datewise_growth_data.append((date2num(filtered_dates[i]), growth_rate))
    
  
    fig, ax = plt.subplots(figsize=(10, 5))  
    dates, growth_rates = zip(*datewise_growth_data)
    ax.plot_date(dates, growth_rates, marker='o', linestyle='-', color='b')
    ax.set_xlabel('Date')
    ax.set_ylabel('NAV Growth Rate (%)')
    ax.set_title('Scheme NAV Growth Rate Within Date Range')
    
    
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=6, column=0, columnspan=2, pady=10)
    
    
    toolbar_frame = tk.Frame(window)
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    toolbar.grid(row=0, column=0)
    toolbar_frame.grid(row=7, column=0, columnspan=2, pady=10)


def on_display_button_click():
    try:
        display_scheme_growth_rate()
    except Exception as e:
        messagebox.showerror("Error", str(e))


window = tk.Tk()
window.title("Scheme NAV Growth Rate ")


scheme_label = tk.Label(window, text="Enter Scheme Code:")
scheme_label.grid(row=0, column=0, sticky='w', padx=10, pady=10)
scheme_entry = tk.Entry(window)
scheme_entry.grid(row=0, column=1, padx=10, pady=10)

start_date_label = tk.Label(window, text="Enter Start Date (DD-MM-YYYY):")
start_date_label.grid(row=1, column=0, sticky='w', padx=10, pady=10)
start_date_entry = tk.Entry(window)
start_date_entry.grid(row=1, column=1, padx=10, pady=10)

end_date_label = tk.Label(window, text="Enter End Date (DD-MM-YYYY):")
end_date_label.grid(row=2, column=0, sticky='w', padx=10, pady=10)
end_date_entry = tk.Entry(window)
end_date_entry.grid(row=2, column=1, padx=10, pady=10)

# display button
display_button = tk.Button(window, text="Display Graph", command=on_display_button_click)
display_button.grid(row=3, column=0, columnspan=2, pady=10)


scheme_details_label = tk.Label(window, text="", justify='left')
scheme_details_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)


window.mainloop()
