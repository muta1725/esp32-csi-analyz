# 1秒間隔で平滑化処理を追加

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import datetime
import matplotlib.dates as mdates
import argparse

def calculate_amplitude(data_str):
    data_list = np.fromstring(data_str[1:-1], sep=',', dtype=int)
    real = data_list[::2]
    imaginary = data_list[1::2]
    amplitude = np.sqrt(real**2 + imaginary**2)
    return amplitude

def smooth_data(data, window_size):
    return data.rolling(window=window_size, min_periods=1).mean()

def plot_csi_data(file_path, ax):
    # CSVファイルを読み込む
    csi_data = pd.read_csv(file_path)
    csi_data['amplitudes'] = csi_data['data'].apply(calculate_amplitude)
    amplitudes_df = pd.DataFrame(csi_data['amplitudes'].tolist(), index=csi_data.index)

    # 平滑化の適用（1秒間隔）
    timestamps = pd.to_datetime(csi_data['timestamp'])
    amplitudes_df['timestamp'] = timestamps
    amplitudes_df.set_index('timestamp', inplace=True)

    # 1秒間隔で平滑化（移動平均）
    window_size = '1S'
    smoothed_amplitudes_df = amplitudes_df.resample(window_size).mean()

    # 時間の範囲を取得
    start_time = timestamps.min()
    end_time = timestamps.max()
    duration = (end_time - start_time).total_seconds()

    # 3Dグラフのデータを準備
    times = smoothed_amplitudes_df.index.time
    subcarrier_indices = range(smoothed_amplitudes_df.shape[1])
    X, Y = np.meshgrid(subcarrier_indices, times)
    Z = smoothed_amplitudes_df.values

    # タイムスタンプをmatplotlibの数値形式に変換
    Y_nums = mdates.date2num([datetime.datetime.combine(datetime.date(1, 1, 1), t) for t in times])
    ax.plot_surface(X, Y_nums[:, None], Z, cmap='viridis')

    # ラベルとタイトルの設定
    ax.set_xlabel('Subcarrier Index')
    ax.set_ylabel('Time')
    ax.set_zlabel('Smoothed Amplitude')
    ax.set_title(f'{file_path} ({duration} seconds, Smoothed)')

    # Y軸の時間フォーマットを設定
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: mdates.num2date(x).strftime('%H:%M:%S')))

def main(file_paths):
    num_files = len(file_paths)
    fig = plt.figure(figsize=(10 * num_files, 8))

    # 各ファイルに対して個別の3Dグラフを作成
    for i, file_path in enumerate(file_paths):
        ax = fig.add_subplot(1, num_files, i + 1, projection='3d')
        plot_csi_data(file_path, ax)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WiFi CSI Data Visualizer')
    parser.add_argument('file_paths', nargs='+', type=str, help='Paths to the CSV files')
    args = parser.parse_args()
    main(args.file_paths)
