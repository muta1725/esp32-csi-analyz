# 空白の行を無視するように修正

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import datetime
import matplotlib.dates as mdates
import argparse

def calculate_amplitude(data_str):
    # データがfloat型の場合は文字列に変換
    if pd.isna(data_str):
        return np.array([])  # 欠損値の場合は空の配列を返す
    if isinstance(data_str, float):
        data_str = str(data_str)
        
    # 振幅の計算
    data_list = np.fromstring(data_str[1:-1], sep=',', dtype=int)
    real = data_list[::2]
    imaginary = data_list[1::2]
    amplitude = np.sqrt(real**2 + imaginary**2)
    return amplitude

def smooth_data(data, window_size):
    """移動平均を使用してデータを平滑化"""
    return pd.Series(data).rolling(window=window_size, min_periods=1).mean().values

def plot_csi_data(file_path, ax, fixed_width=1000, smooth_interval=10):
    # CSVファイルを読み込み、空白行を無視
    csi_data = pd.read_csv(file_path, skip_blank_lines=True)

    # 完全に空白の行を削除
    csi_data = csi_data.dropna(how='all')

    # 'timestamp'列を "HH:MM:SS.%f" 形式で読み込み
    csi_data['timestamp'] = pd.to_datetime(csi_data['timestamp'], format='%H:%M:%S.%f', errors='coerce')

    # timestampの変換エラーを確認
    if csi_data['timestamp'].isnull().any():
        print(f"エラー: {file_path} の一部のtimestampの変換に失敗しました。フォーマットを確認してください。")

    csi_data['amplitudes'] = csi_data['data'].apply(calculate_amplitude)
    amplitudes_df = pd.DataFrame(csi_data['amplitudes'].tolist(), index=csi_data.index)

    # 時間の範囲を取得
    times = (csi_data['timestamp'] - csi_data['timestamp'].min()).dt.total_seconds()

    # 幅を固定するためにインデックスを調整
    num_points = len(times)
    fixed_times = np.linspace(0, times.max(), fixed_width)

    # データをリサンプリング
    resampled_amplitudes = np.array([np.interp(fixed_times, times, amplitudes_df.iloc[:, i]) for i in range(amplitudes_df.shape[1])]).T

    # 平滑化を適用
    smoothed_amplitudes = np.array([smooth_data(resampled_amplitudes[:, i], smooth_interval) for i in range(resampled_amplitudes.shape[1])]).T

    # 3Dグラフのデータを準備
    subcarrier_indices = range(smoothed_amplitudes.shape[1])
    X, Y = np.meshgrid(subcarrier_indices, fixed_times)
    Z = smoothed_amplitudes

    # グラフ描画
    ax.plot_surface(X, Y, Z, cmap='viridis')

    # ラベルとタイトルの設定
    ax.set_xlabel('Subcarrier Index')
    ax.set_ylabel('Time (s)')
    ax.set_zlabel('Amplitude')
    ax.set_title(f'{file_path} (Fixed Width & Smoothed)')

def main(file_paths, smooth_interval=1000):
    num_files = len(file_paths)
    # 行数と列数を決定（最大3列）
    ncols = 3
    nrows = (num_files + ncols - 1) // ncols

    fig = plt.figure(figsize=(10 * ncols, 8 * nrows))

    # 各ファイルに対して個別の3Dグラフを作成
    for i, file_path in enumerate(file_paths):
        ax = fig.add_subplot(nrows, ncols, i + 1, projection='3d')
        plot_csi_data(file_path, ax, smooth_interval=smooth_interval)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WiFi CSI Data Visualizer with Fixed Width & Smoothing')
    parser.add_argument('file_paths', nargs='+', type=str, help='Paths to the CSV files')
    parser.add_argument('--smooth_interval', type=int, default=50, help='Smoothing interval for amplitude')
    args = parser.parse_args()
    main(args.file_paths, smooth_interval=args.smooth_interval)