# csvのエンコードを検出して読み込む機能の追加

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import chardet

def detect_encoding(file_path):
    # ファイルのエンコーディングを検出
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))  # 先頭の一部を読み込み
        return result['encoding']

def calculate_amplitude(data_str):
    # 振幅の計算
    data_list = np.fromstring(data_str[1:-1], sep=',', dtype=int)
    real = data_list[::2]
    imaginary = data_list[1::2]
    amplitude = np.sqrt(real**2 + imaginary**2)
    return amplitude

def plot_csi_data(file_path, ax):
    # ファイルのエンコーディングを検出して指定
    encoding = detect_encoding(file_path)
    print(f"Detected encoding: {encoding}")

    # CSVファイルを指定されたエンコーディングで読み込む
    csi_data = pd.read_csv(file_path, encoding=encoding)
    csi_data['amplitudes'] = csi_data['data'].apply(calculate_amplitude)
    amplitudes_df = pd.DataFrame(csi_data['amplitudes'].tolist(), index=csi_data.index)

    # 3Dグラフのデータを準備
    timestamp_values = pd.to_datetime(csi_data['timestamp'])
    subcarrier_indices = range(amplitudes_df.shape[1])
    X, Y = np.meshgrid(subcarrier_indices, timestamp_values)
    Z = amplitudes_df.values

    # 3Dグラフを作成
    ax.plot_surface(X, Y.astype(int), Z, cmap='viridis')

    # ラベルとタイトルの設定
    ax.set_xlabel('Subcarrier Index')
    ax.set_ylabel('Timestamp')
    ax.set_zlabel('Amplitude')
    ax.set_title('Amplitude of WiFi CSI Data Over Time and Subcarriers')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x).strftime('%Y-%m-%d %H:%M:%S')))

def main(file_paths):
    # プロットの準備
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 各ファイルをプロット
    for file_path in file_paths:
        plot_csi_data(file_path, ax)

    plt.show()

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Plot WiFi CSI Data from CSV files.')
    parser.add_argument('file_paths', nargs='+', help='Paths to the CSV files')
    args = parser.parse_args()

    main(args.file_paths)