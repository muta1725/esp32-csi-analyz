import pandas as pd
import numpy as np
import sys
import os

# コマンドライン引数からファイルパスを取得
if len(sys.argv) < 2:
    print("Usage: python script_name.py <file_path1> <file_path2> ...")
    sys.exit(1)

file_paths = sys.argv[1:]

def process_data(file_path):
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

    # 振幅データをデータフレームに変換
    amplitudes_df = pd.DataFrame(amplitudes, index=timestamps, columns=[f'Subcarrier_{i}' for i in range(num_subcarriers)])

    # 移動平均フィルタ（ウィンドウ100）を適用
    smoothed_amplitudes = amplitudes_df.rolling(window=100, min_periods=1).mean()

    # 小数点第6位で切り捨て
    smoothed_amplitudes = smoothed_amplitudes.round(6)

    # 移動平均後のデータをCSVに出力
    output_file = os.path.splitext(file_path)[0] + '_smoothed.csv'
    smoothed_amplitudes.to_csv(output_file, index_label='timestamp')
    print(f"Processed file saved as {output_file}")

# 各ファイルを処理
for file_path in file_paths:
    process_data(file_path)
