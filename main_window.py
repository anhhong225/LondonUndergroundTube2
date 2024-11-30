import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from station_map import TubeMap
import pandas as pd

# Define line colors
tube_line_colors = {
    'Bakerloo': '#a65a2a',
    'Central': '#e1251b',
    'Circle': '#ffcd00',
    'District': '#007934',
    'Hammersmith and City': '#ec9bad',
    'Jubilee': '#7b868c',
    'Metropolitan': '#870f54',
    'Northern': '#000000',
    'Piccadilly': '#000f9f',
    'Victoria': '#00a0df',
    'Waterloo and City': '#6bcdb2'
}

# Initialize TubeMap
tube_map = TubeMap(data_file='StationData/selected_tube_lines.csv', line_colors=tube_line_colors)
tube_map.load_data()

def calculate_line_info(selected_lines):
    """Calculate and return statistics for the selected lines."""
    if not selected_lines:
        return "No line selected."
    
    data = pd.read_csv('StationData/selected_tube_lines.csv')
    filtered_data = data[data['Tube Line'].isin(selected_lines)]
    
    if filtered_data.empty:
        return "No data for selected lines."
    
    total_distance = filtered_data['Distance (km)'].sum()
    average_distance = filtered_data['Distance (km)'].mean()
    std_dev_distance = filtered_data['Distance (km)'].std()
    
    return (f"Selected Lines: {', '.join(selected_lines)}\n"
            f"Total Distance: {total_distance:.2f} km\n"
            f"Average Distance: {average_distance:.2f} km\n"
            f"Std Deviation: {std_dev_distance:.2f} km")

def update_map(selected_lines):
    """Update the displayed map based on selected lines."""
    for widget in map_frame.winfo_children():
        widget.destroy()  # Clear previous canvas
    
    # If no line is selected, show all lines
    if not selected_lines:
        fig = tube_map.plot_all_lines()  # Show all lines
    else:
        # Plot only the selected lines
        fig = tube_map.plot_selected_lines(selected_lines)
    
    # Create the canvas widget only once, and update it when needed
    canvas = FigureCanvasTkAgg(fig, map_frame)
    canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
    canvas.draw()

def update_line_info():
    """Update the information displayed in the bottom panel based on selected lines."""
    selected_lines = [line for line, var in check_vars.items() if var.get()]
    info = calculate_line_info(selected_lines)
    info_text.delete("1.0", tk.END)
    info_text.insert(tk.END, info)
    update_map(selected_lines)

# Main application setup
main_window = tk.Tk()
main_window.geometry("1600x800")  # Set window size
main_window.title("Underground Tube London")
main_window.configure(bg="#344955")

# Top panel - Dynamic Map
map_frame = tk.Frame(main_window, bg="#344955", width=800, height=600)
map_frame.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

# Right panel - Line selection
line_frame = tk.Frame(main_window, width=400, height=600, bg="#f0f0f0")
line_frame.grid(row=0, column=1, padx=10, pady=10, sticky="NS")

header_lbl = tk.Label(line_frame, text="Select Underground Tube Lines", font=("Arial", 14), bg="#f0f0f0")
header_lbl.pack(pady=10)

check_vars = {}
lines = list(tube_line_colors.keys())
for line in lines:
    var = tk.BooleanVar(value=False)
    check_vars[line] = var
    check = tk.Checkbutton(
        line_frame, text=line, variable=var, font=("Arial", 12), command=update_line_info, bg="#f0f0f0"
    )
    check.pack(anchor="w", padx=10)

# Bottom panel - Line information
info_frame = tk.Frame(main_window, width=1200, height=200, bg="#ffffff")
info_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="EW")

info_text = tk.Text(info_frame, wrap="word", font=("Arial", 12), height=6)
info_text.pack(expand=True, fill="both", padx=10, pady=10)

# Configure column and row weights to make panels resize nicely
main_window.grid_rowconfigure(0, weight=1)  # Row with map and line selection
main_window.grid_rowconfigure(1, weight=0)  # Row with information
main_window.grid_columnconfigure(0, weight=3)  # Map area gets more space
main_window.grid_columnconfigure(1, weight=1)  # Line selection area

# Initial map rendering
fig = tube_map.plot_all_lines()
canvas = FigureCanvasTkAgg(fig, map_frame)
canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

def on_close():
    main_window.destroy() 

# Bind the on_close function to the window's close event
main_window.protocol("WM_DELETE_WINDOW", on_close)
# Start Tkinter main loop
main_window.mainloop()