import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def calculate_amplitude(data_str):
    data_list = np.fromstring(data_str[1:-1], sep=',', dtype=int)
    real = data_list[::2]
    imaginary = data_list[1::2]
    amplitude = np.sqrt(real**2 + imaginary**2)
    return amplitude

# CSVファイルを読み込む
file_path = '03/csi_data_B03.csv'  # CSVファイルのパスに置き換えてください
csi_data = pd.read_csv(file_path)
csi_data['amplitudes'] = csi_data['data'].apply(calculate_amplitude)
amplitudes_df = pd.DataFrame(csi_data['amplitudes'].tolist(), index=csi_data.index)

# 3Dグラフのデータを準備
timestamp_values = pd.to_datetime(csi_data['timestamp'])
subcarrier_indices = range(amplitudes_df.shape[1])
X, Y = np.meshgrid(subcarrier_indices, timestamp_values)
Z = amplitudes_df.values

# 3Dグラフを作成
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y.astype(int), Z, cmap='viridis')

# ラベルとタイトルの設定
ax.set_xlabel('Subcarrier Index')
ax.set_ylabel('Timestamp')
ax.set_zlabel('Amplitude')
ax.set_title('Amplitude of WiFi CSI Data Over Time and Subcarriers')

# Y軸の日付フォーマットを設定
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%H:%M:%S')))

plt.show()
