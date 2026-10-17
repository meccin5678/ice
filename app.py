from pathlib import Path

import pandas as pd
import streamlit as st


# このPythonファイルがあるフォルダを基準にCSVの場所を指定する
project_folder = Path(__file__).parent
csv_path = project_folder / "output" / "sales_summary.csv"

st.title("アイス売上ダッシュボード")

sales_data = pd.read_csv(csv_path)
st.dataframe(sales_data)

st.subheader("フレーバー別の売上")
st.bar_chart(sales_data, x="フレーバー", y="合計売上")
