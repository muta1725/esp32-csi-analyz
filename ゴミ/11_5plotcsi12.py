import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

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
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# 初期の振幅と位相のプロット
lines_amp = [ax1.plot([], [], label=f'Subcarrier {i+1}')[0] for i in range(num_subcarriers)]
lines_phase = [ax2.plot([], [], label=f'Subcarrier {i+1}')[0] for i in range(num_subcarriers)]

# プロット範囲の初期設定
start = 0
window_size = 100  # 表示するデータポイントの範囲

# 振幅と位相の更新関数
def update_plot(val):
    pos = int(slider.val)
    end = pos + window_size
    ax1.set_xlim(timestamps.iloc[pos], timestamps.iloc[end - 1])
    ax2.set_xlim(timestamps.iloc[pos], timestamps.iloc[end - 1])
    for i in range(num_subcarriers):
        lines_amp[i].set_data(timestamps.iloc[pos:end], [amp[i] for amp in amplitudes_list[pos:end]])
        lines_phase[i].set_data(timestamps.iloc[pos:end], [phase[i] for phase in phases_list[pos:end]])
    fig.canvas.draw_idle()

# スライダーの作成
ax_slider = plt.axes([0.2, 0.02, 0.6, 0.03], facecolor="lightgoldenrodyellow")
slider = Slider(ax_slider, 'Scroll', 0, len(timestamps) - window_size, valinit=start, valstep=1)
slider.on_changed(update_plot)

# ラベルとタイトルの設定
ax1.set_ylabel('Amplitude')
ax1.set_title('Amplitude over Time for Each Subcarrier')
ax1.legend()

ax2.set_ylabel('Phase (radians)')
ax2.set_xlabel('Timestamp')
ax2.set_title('Phase over Time for Each Subcarrier')
ax2.legend()

# 初期プロットの更新
update_plot(0)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
