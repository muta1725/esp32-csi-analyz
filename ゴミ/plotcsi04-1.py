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

def plot_csi_data(file_path, ax, fixed_width=1000):
    # CSVファイルを読み込む
    csi_data = pd.read_csv(file_path)

    # 'timestamp'列を "mm:ss.0" 形式で読み込み
    csi_data['timestamp'] = pd.to_datetime(csi_data['timestamp'], format='%M:%S.%f', errors='coerce')

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

    # 3Dグラフのデータを準備
    subcarrier_indices = range(resampled_amplitudes.shape[1])
    X, Y = np.meshgrid(subcarrier_indices, fixed_times)
    Z = resampled_amplitudes

    # グラフ描画
    ax.plot_surface(X, Y, Z, cmap='viridis')

    # ラベルとタイトルの設定
    ax.set_xlabel('Subcarrier Index')
    ax.set_ylabel('Time (s)')
    ax.set_zlabel('Amplitude')
    ax.set_title(f'{file_path} (Fixed Width)')

def main(file_paths):
    num_files = len(file_paths)
    fig = plt.figure(figsize=(10 * num_files, 8))

    # 各ファイルに対して個別の3Dグラフを作成
    for i, file_path in enumerate(file_paths):
        ax = fig.add_subplot(1, num_files, i + 1, projection='3d')
        plot_csi_data(file_path, ax)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WiFi CSI Data Visualizer with Fixed Width')
    parser.add_argument('file_paths', nargs='+', type=str, help='Paths to the CSV files')
    args = parser.parse_args()
    main(args.file_paths)
