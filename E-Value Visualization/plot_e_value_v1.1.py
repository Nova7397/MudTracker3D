import csv
import re
import matplotlib.pyplot as plt

# List of CSV file paths
csv_files = [
    r"D:\TU Delft\MSc3\Auto Data Recorder\20241007\2024-10-07-14-28-51_output\timelapse_log.csv",
    r"D:\TU Delft\MSc3\Auto Data Recorder\20241007\2024-10-07-14-57-29_output\timelapse_log.csv",
    r"D:\TU Delft\MSc3\Auto Data Recorder\20241007\2024-10-07-15-23-07_output\timelapse_log.csv",
    r"D:\TU Delft\MSc3\Auto Data Recorder\20241007\2024-10-07-15-55-05_output\timelapse_log.csv",
    r"D:\TU Delft\MSc3\Auto Data Recorder\20241007\2024-10-07-16-12-39_output\timelapse_log.csv"
]

# Colors for the different plots
colors = ['b', 'g', 'r', 'c', 'm']

# Loop through each CSV file and plot its E values
for i, csv_file in enumerate(csv_files):
    e_values = []
    
    # Open and read each CSV file
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            gcode = row['gcode']
            
            # Use regular expression to extract the E value
            e_value_match = re.search(r"E([0-9]*\.?[0-9]+)", gcode)
            
            if e_value_match:
                e_value = float(e_value_match.group(1))
                e_values.append(e_value)

    # X-axis will be the sequence number of the data points (1, 2, 3, ...)
    x_values = range(1, len(e_values) + 1)
    
    # Plot the E values for the current file
    plt.plot(x_values, e_values, marker='o', linestyle='-', color=colors[i], label=f'CSV {i+1}')

# Chart title and labels
plt.title('E Values from Multiple CSV Files')
plt.xlabel('Data Point Sequence')
plt.ylabel('E Value')
plt.legend()  # Add a legend to distinguish different files
plt.tight_layout()

# Show the plot
plt.show()
