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
plt.subplots_adjust(bottom=0.25)
line, = ax.plot(range(num_subcarriers), amplitudes[0], label="Amplitude Spectrum")
ax.set_xlabel('Subcarrier Index')
ax.set_ylabel('Amplitude')
ax.set_title('Subcarrier Amplitude Spectrum')
ax.set_ylim(0, 100)  # Set y-axis limit

# Set up the slider with time display
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Time', 0, len(timestamps) - 1, valinit=0, valstep=1)

# Update function for the slider
def update(val):
    index = int(slider.val)
    line.set_ydata(amplitudes[index])
    slider.label.set_text(f'Time: {timestamps[index].strftime("%H:%M:%S.%f")[:-3]}')  # Display timestamp
    fig.canvas.draw_idle()

# Link slider to the update function
slider.on_changed(update)

plt.legend()
plt.show()
