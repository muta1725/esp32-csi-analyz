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
    
    # 各サブキャリアごとに平均を引き算（平均を0にする）
    csi_mean_subtracted = csi_amplitude.apply(lambda row: row - np.mean(row))
    
    # 固定するスペクトル（776番目のデータ）
    S1 = csi_mean_subtracted.iloc[599]  # インデックス776
    
    # 他のスペクトルと固定スペクトルの相関を計算
    results = []
    
    for idx, Sn in enumerate(csi_mean_subtracted):
        if idx == 776:  # 固定スペクトル自体はスキップ
            continue
    
        # 相関係数を計算
        correlation = np.corrcoef(S1, Sn)[0, 1]
    
        # 結果をタイムスタンプと紐付け
        results.append((timestamp.iloc[idx], correlation))
    
    # 結果をデータフレームに変換
    results_df = pd.DataFrame(results, columns=['timestamp', 'correlation'])
    
    # タイムスタンプを日時型に変換
    results_df['timestamp'] = pd.to_datetime(results_df['timestamp'])
    
    # プロットを作成
    fig = px.scatter(results_df, x='timestamp', y='correlation', title=f'CSI相関係数の時間変化（基準：599番目のデータ）\nファイル: {file_path}')
    
    # プロットの点を小さくする
    fig.update_traces(marker=dict(size=4))
    
    # 縦軸の範囲を0から1に固定し、0.1刻みに設定
    fig.update_yaxes(range=[0, 1], dtick=0.1)
    
    # x軸の目盛りを1秒間隔に設定
    fig.update_xaxes(
        tickformat='%M:%S',
        dtick=1000  # 1秒 = 1000ミリ秒
    )
    
    # レイアウトを調整
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
    
    # グラフを表示
    fig.show()

def main():
    # コマンドライン引数を処理する
    parser = argparse.ArgumentParser(description='CSIデータファイルを処理します。')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='処理するCSVファイルのパス')
    args = parser.parse_args()
    
    # 指定された各ファイルを処理
    for file_path in args.files:
        print(f'ファイルを処理中: {file_path}')
        process_file(file_path)

if __name__ == '__main__':
    main()
