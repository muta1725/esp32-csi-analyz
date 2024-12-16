import pandas as pd
import numpy as np
import plotly.express as px
import argparse
import sys

def process_file(file_path):
    # CSVファイルを読み込む
    data = pd.read_csv(file_path)
    
    # timestamp列とdata列を抽出
    timestamp = data['timestamp']
    csi_data = data['data'].apply(lambda x: np.array([float(num) for num in x.strip('[]').split(',')]))
    
    # data列を複素数に変換し、振幅を計算
    csi_complex = csi_data.apply(lambda x: x[::2] + 1j * x[1::2])  # 実部 + 虚部
    csi_amplitude = csi_complex.apply(np.abs)  # 振幅を計算
    
    # 移動平均（ウィンドウサイズ=20など適宜設定）を時系列方向に適用
    amplitude_matrix = np.vstack(csi_amplitude.to_list())  # shape: (time, subcarriers)
    window_size = 20
    smoothed_matrix = pd.DataFrame(amplitude_matrix).rolling(window=window_size, center=True).mean().values
    csi_amplitude_smoothed = pd.Series(list(smoothed_matrix), index=csi_amplitude.index)
    
    # 各サブキャリアごとに平均を引き算（平均を0に）
    csi_mean_subtracted = csi_amplitude_smoothed.apply(lambda row: row - np.mean(row))
    
    # 基準とするスペクトル（599番目のデータを使用する例）
    # （コメント上は776とあるが、コード上は599となっているためそのまま599を使用）
    S1 = csi_mean_subtracted.iloc[599]
    
    results = []
    for idx, Sn in enumerate(csi_mean_subtracted):
        # 基準スペクトル自身はスキップ
        if idx == 599:
            continue
        
        # マスクを作成
        # 1. indexが0〜60番目は除外 -> np.arange(len(S1)) > 60
        # 2. S1またはSnが0のときは除外 -> (S1 != 0) & (Sn != 0)
        mask = (np.arange(len(S1)) > 60) & (S1 != 0) & (Sn != 0)
        
        S1_filtered = S1[mask]
        Sn_filtered = Sn[mask]
        
        # 有効な要素が1点以上ないと相関係数は計算不能
        if len(S1_filtered) > 1:
            correlation = np.corrcoef(S1_filtered, Sn_filtered)[0, 1]
        else:
            correlation = np.nan
        
        results.append((timestamp.iloc[idx], correlation))
    
    # 結果をDataFrame化
    results_df = pd.DataFrame(results, columns=['timestamp', 'correlation'])
    results_df['timestamp'] = pd.to_datetime(results_df['timestamp'])
    
    # 可視化
    fig = px.scatter(results_df, x='timestamp', y='correlation',
                     title=f'CSI相関係数の時間変化（基準：599番目のデータ）\nファイル: {file_path}')
    
    fig.update_traces(marker=dict(size=4))
    fig.update_yaxes(range=[0, 1], dtick=0.1)
    
    fig.update_xaxes(
        tickformat='%M:%S',
        dtick=1000  # 1秒 = 1000ミリ秒
    )
    
    fig.update_layout(
        xaxis_title='タイムスタンプ',
        yaxis_title='相関係数',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=10, label='10秒', step='second', stepmode='backward'),
                    dict(count=30, label='30秒', step='second', stepmode='backward'),
                    dict(count=60, label='60秒', step='second', stepmode='backward'),
                    dict(count=120, label='120秒', step='second', stepmode='backward'),
                    dict(count=180, label='180秒', step='second', stepmode='backward'),
                    dict(count=300, label='300秒', step='second', stepmode='backward'),
                    dict(count=600, label='600秒', step='second', stepmode='backward'),
                    dict(count=1, label='全期間', step='all')
                ])
            ),
            rangeslider=dict(visible=True),
            type='date'
        )
    )
    
    fig.show()

def main():
    # コマンドライン引数を処理
    parser = argparse.ArgumentParser(description='CSIデータファイルを処理します。')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='処理するCSVファイルのパス')
    args = parser.parse_args()
    
    # 指定された各ファイルを処理
    for file_path in args.files:
        print(f'ファイルを処理中: {file_path}')
        process_file(file_path)

if __name__ == '__main__':
    main()
