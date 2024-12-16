import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import sys

# コマンドライン引数からファイルパスを取得
if len(sys.argv) < 2:
    print("Usage: python script_name.py <file_path>")
    sys.exit(1)

file_path = sys.argv[1]

# CSVファイルを読み込む
df = pd.read_csv(file_path)

# 'timestamp' と 'data' 列を抽出
timestamps = pd.to_datetime(df['timestamp'], format='%H:%M:%S.%f')
data_column = df['data']

# 'data'列を複素数に変換し、振幅と位相を計算
num_subcarriers = len(data_column[0].strip('[]').split(',')) // 2  # 各ペア(real, imag)がサブキャリアを表すと仮定
amplitudes = []
phases = []

for row in data_column:
    # データを複素数のペアに変換
    data_values = np.fromstring(row.strip('[]'), sep=',').reshape(-1, 2)
    complex_values = data_values[:, 0] + 1j * data_values[:, 1]
    
    # 振幅と位相を計算
    amplitude = np.abs(complex_values)
    phase = np.angle(complex_values)
    
    amplitudes.append(amplitude)
    phases.append(phase)

# リストをnumpy配列に変換してインデックス付けを簡単にする
amplitudes = np.array(amplitudes)
phases = np.array(phases)

# 振幅をプロットするための初期化
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.3)  # スライダーとの重なりを防ぐために調整
line, = ax.plot(range(num_subcarriers), amplitudes[0], label="Amplitude Spectrum")
ax.set_xlabel('Subcarrier Index')
ax.set_ylabel('Amplitude')
ax.set_title('Subcarrier Amplitude Spectrum', loc='left')  # タイトルを左に配置
ax.set_ylim(0, 110)  # y軸の上限を110に設定

# 初期のタイムスタンプを表示
current_index = 0
timestamp_text = ax.text(0.5, -0.2, f'Time: {timestamps[current_index].strftime("%H:%M:%S.%f")[:-3]}', 
                         transform=ax.transAxes, ha='center', fontsize=10)

# スライダーの設定
ax_slider = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Time', 0, len(timestamps) - 1, valinit=0, valstep=1)

# スライダーと矢印キーでの移動に対応する更新関数
def update(val):
    index = int(slider.val)
    update_plot(index)

def update_plot(index):
    global current_index
    current_index = index
    line.set_ydata(amplitudes[current_index])
    timestamp_text.set_text(f'Time: {timestamps[current_index].strftime("%H:%M:%S.%f")[:-3]}')
    fig.canvas.draw_idle()

# 矢印キーのイベントハンドラ
def on_key(event):
    global current_index
    if event.key == 'right' and current_index < len(timestamps) - 1:
        update_plot(current_index + 1)
        slider.set_val(current_index)
    elif event.key == 'left' and current_index > 0:
        update_plot(current_index - 1)
        slider.set_val(current_index)

# スライダーとキーイベントのリンク
slider.on_changed(update)
fig.canvas.mpl_connect('key_press_event', on_key)

plt.legend(loc='upper left')  # 凡例を左上に移動
plt.show()
