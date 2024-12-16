import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import sys
import os

# コマンドライン引数からファイルパスを取得
if len(sys.argv) < 2:
    print("Usage: python script_name.py <file_path1> <file_path2> ...")
    sys.exit(1)

file_paths = sys.argv[1:]

def plot_data(file_path):
    # CSVファイルの読み込み
    df = pd.read_csv(file_path)

    # 'timestamp'と'data'列を抽出
    timestamps = pd.to_datetime(df['timestamp'], format='%H:%M:%S.%f')
    data_column = df['data']

    # 複素数として'データ'列を解析し、振幅を計算
    num_subcarriers = len(data_column[0].strip('[]').split(',')) // 2
    amplitudes = []

    for row in data_column:
        # データを複素数のペアに変換
        data_values = np.fromstring(row.strip('[]'), sep=',').reshape(-1, 2)
        complex_values = data_values[:, 0] + 1j * data_values[:, 1]
        
        # 振幅を計算
        amplitude = np.abs(complex_values)
        amplitudes.append(amplitude)

    # 処理を容易にするため、リストをデータフレームに変換
    amplitudes_df = pd.DataFrame(amplitudes, index=timestamps, columns=[f'Subcarrier_{i}' for i in range(num_subcarriers)])

    # 移動平均フィルタ（ウィンドウ100）を適用
    smoothed_amplitudes = amplitudes_df.rolling(window=100, min_periods=1).mean()

    # 平滑化後のデータを用いてMSEを計算
    mse_values = ((smoothed_amplitudes.diff(periods=10))**2).mean(axis=1)

    # 動き検出の閾値を設定
    mse_threshold = 1.0  # 感度に応じて調整

    # スライダー付きのインタラクティブ表示を初期化
    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.3)
    line, = ax.plot(range(num_subcarriers), smoothed_amplitudes.iloc[0], label="Smoothed Amplitude Spectrum")
    ax.set_xlabel('Subcarrier Index')
    ax.set_ylabel('Amplitude')
    ax.set_ylim(0, 110)
    ax.set_title(f'Subcarrier Amplitude Spectrum')

    # ファイル名をウィンドウのタイトルに設定
    fig.canvas.manager.set_window_title(f'File: {os.path.basename(file_path)}')

    # 初期タイムスタンプ、MSE、動き検出テキストを表示
    current_index = 0
    timestamp_text = ax.text(0.5, -0.2, f'Time: {timestamps[current_index].strftime("%H:%M:%S.%f")[:-3]}', 
                             transform=ax.transAxes, ha='center', fontsize=10)
    mse_text = ax.text(0.5, -0.3, f'MSE: {mse_values.iloc[current_index]:.2f}', 
                       transform=ax.transAxes, ha='center', fontsize=10, color='blue')
    movement_text = ax.text(0.5, 1.05, '', transform=ax.transAxes, ha='center', color='red', fontsize=12)

    # スライダーの設定
    ax_slider = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')
    slider = Slider(ax_slider, 'Time', 0, len(timestamps) - 1, valinit=0, valstep=1)

    # スライダーと矢印キー操作用の更新関数
    def update_plot(index):
        nonlocal current_index
        current_index = index
        line.set_ydata(smoothed_amplitudes.iloc[current_index])
        timestamp_text.set_text(f'Time: {timestamps[current_index].strftime("%H:%M:%S.%f")[:-3]}')
        mse_text.set_text(f'MSE: {mse_values.iloc[current_index]:.2f}')
        
        # MSEが閾値を超えたかチェック
        if mse_values.iloc[current_index] > mse_threshold:
            movement_text.set_text("動き検出")
        else:
            movement_text.set_text("")
        
        fig.canvas.draw_idle()

    # スライダーの更新用関数
    def update(val):
        index = int(slider.val)
        update_plot(index)

    # 矢印キーのイベントハンドラ
    def on_key(event):
        nonlocal current_index
        if event.key == 'right' and current_index < len(timestamps) - 1:
            update_plot(current_index + 1)
            slider.set_val(current_index)
        elif event.key == 'left' and current_index > 0:
            update_plot(current_index - 1)
            slider.set_val(current_index)

    # スライダーとキーイベントをリンク
    slider.on_changed(update)
    fig.canvas.mpl_connect('key_press_event', on_key)

    plt.legend(loc='upper left')
    plt.show(block=False)  # 非同期的にウィンドウを開く

# 各ファイルに対して個別にグラフを表示
for file_path in file_paths:
    plot_data(file_path)

plt.show()  # 最後に全てのウィンドウを表示
