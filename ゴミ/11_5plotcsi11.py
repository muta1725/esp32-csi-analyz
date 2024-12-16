import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# CSVファイルの読み込み
file_path = '03/csi_data_A03.csv'
data_df = pd.read_csv(file_path)

# timestampとdata列を抽出
timestamps = data_df['timestamp']
csi_data = data_df['data']

# 振幅と位相を計算する関数
def calculate_amplitude_phase(data):
    amplitudes = []
    phases = []
    # 2つずつリアル部とイマジナリ部として取り出し、計算
    for i in range(0, len(data), 2):
        real = data[i]
        imag = data[i + 1]
        amplitude = np.sqrt(real**2 + imag**2)
        phase = np.arctan2(imag, real)
        amplitudes.append(amplitude)
        phases.append(phase)
    return amplitudes, phases

# 各行のdata列から振幅と位相を計算
amplitudes_list = []
phases_list = []

for row in csi_data:
    # 文字列を数値リストに変換
    data = list(map(int, row.strip('[]').split(',')))
    amplitudes, phases = calculate_amplitude_phase(data)
    amplitudes_list.append(amplitudes)
    phases_list.append(phases)

# グラフ作成
num_subcarriers = len(amplitudes_list[0])

# 時間ごとにサブキャリアの振幅をプロット
plt.figure(figsize=(10, 6))
for i in range(num_subcarriers):
    amplitude_over_time = [amp[i] for amp in amplitudes_list]
    plt.plot(timestamps, amplitude_over_time, label=f'Subcarrier {i+1}')
plt.xlabel('Timestamp')
plt.ylabel('Amplitude')
plt.title('Amplitude over Time for Each Subcarrier')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 時間ごとにサブキャリアの位相をプロット
plt.figure(figsize=(10, 6))
for i in range(num_subcarriers):
    phase_over_time = [phase[i] for phase in phases_list]
    plt.plot(timestamps, phase_over_time, label=f'Subcarrier {i+1}')
plt.xlabel('Timestamp')
plt.ylabel('Phase (radians)')
plt.title('Phase over Time for Each Subcarrier')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
