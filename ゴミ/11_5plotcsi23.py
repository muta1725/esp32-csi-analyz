import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Load the CSV file
file_path = '03/csi_data_C03.csv'
df = pd.read_csv(file_path)

# Extract 'timestamp' and 'data' columns
timestamps = pd.to_datetime(df['timestamp'], format='%H:%M:%S.%f')
data_column = df['data']

# Parse 'data' column into complex numbers and calculate amplitude and phase
num_subcarriers = len(data_column[0].strip('[]').split(',')) // 2  # Assuming each pair (real, imag) represents a subcarrier
amplitudes = []
phases = []

for row in data_column:
    # Convert data into complex pairs
    data_values = np.fromstring(row.strip('[]'), sep=',').reshape(-1, 2)
    complex_values = data_values[:, 0] + 1j * data_values[:, 1]
    
    # Calculate amplitude and phase
    amplitude = np.abs(complex_values)
    phase = np.angle(complex_values)
    
    amplitudes.append(amplitude)
    phases.append(phase)

# Convert lists to numpy arrays for easier indexing
amplitudes = np.array(amplitudes)
phases = np.array(phases)

# Initialize plot for amplitudes with a slider
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.3)  # Adjust to prevent overlap with slider
line, = ax.plot(range(num_subcarriers), amplitudes[0], label="Amplitude Spectrum")
ax.set_xlabel('Subcarrier Index')
ax.set_ylabel('Amplitude')
ax.set_title('Subcarrier Amplitude Spectrum', loc='left')  # Move title to the left
ax.set_ylim(0, 110)  # Set y-axis limit to 90

# Display initial timestamp
current_index = 0
timestamp_text = ax.text(0.5, -0.2, f'Time: {timestamps[current_index].strftime("%H:%M:%S.%f")[:-3]}', 
                         transform=ax.transAxes, ha='center', fontsize=10)

# Set up the slider
ax_slider = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Time', 0, len(timestamps) - 1, valinit=0, valstep=1)

# Update function for slider and arrow key navigation
def update(val):
    index = int(slider.val)
    update_plot(index)

def update_plot(index):
    global current_index
    current_index = index
    line.set_ydata(amplitudes[current_index])
    timestamp_text.set_text(f'Time: {timestamps[current_index].strftime("%H:%M:%S.%f")[:-3]}')
    fig.canvas.draw_idle()

# Key event handler for arrow keys
def on_key(event):
    global current_index
    if event.key == 'right' and current_index < len(timestamps) - 1:
        update_plot(current_index + 1)
        slider.set_val(current_index)
    elif event.key == 'left' and current_index > 0:
        update_plot(current_index - 1)
        slider.set_val(current_index)

# Link slider and key press event
slider.on_changed(update)
fig.canvas.mpl_connect('key_press_event', on_key)

plt.legend(loc='upper left')  # Move legend to the upper left
plt.show()
