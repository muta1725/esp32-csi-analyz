# 振幅を出力するプログラム

import pandas as pd
import numpy as np

# Excelファイルを読み込む
file_path = ''  # 入力ファイルパス
data = pd.read_excel(file_path)

# 時間列とCSIデータ列を抽出
time_col = data.iloc[:, 0]  # 時間列の抽出
csi_data = data.iloc[:, 1:]  # CSIデータ列の抽出

# CSI列の数が偶数であることを確認します（実部と虚部のペア）
assert csi_data.shape[1] % 2 == 0, "The number of CSI columns should be even."

# 各サブキャリアペアの振幅を計算します
num_subcarriers = csi_data.shape[1] // 2  # サブキャリア数
amplitude_data = pd.DataFrame()  # 振幅データ格納用

for i in range(num_subcarriers):
    real_part = csi_data.iloc[:, 2 * i]  # 実部
    imag_part = csi_data.iloc[:, 2 * i + 1]  # 虚部
    amplitude = np.sqrt(real_part**2 + imag_part**2)  # 振幅の計算
    amplitude_data[f'{i + 1}'] = amplitude  # 列名に番号を付けて格納

# 時間列と振幅データを結合
output_data = pd.concat([time_col, amplitude_data], axis=1)

# 出力を新しいExcelファイルに保存
output_file_path = '/mnt/data/CSI_Amplitude_Output.xlsx'  # 出力ファイルパス
output_data.to_excel(output_file_path, index=False)
