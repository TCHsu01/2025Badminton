import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd

# 讀取比賽數據
file_path = "match.xlsx"
df = pd.read_excel(file_path)

# 初始化 Dash 應用程式
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("2025小地盃比賽查詢系統"),
    
    # 篩選條件輸入框
    html.Label("開始時間"),
    dcc.Input(id='filter-time', type='text', placeholder='輸入開始時間'),
    
    html.Label("場地"),
    dcc.Input(id='filter-location', type='text', placeholder='輸入場地'),
    
    html.Label("組別"),
    dcc.Input(id='filter-group', type='text', placeholder='輸入組別'),
    
    html.Label("關鍵字"),
    dcc.Input(id='filter-keyword', type='text', placeholder='輸入關鍵字 (選手或裁判)'),
    
    html.Button('搜尋', id='search-button', n_clicks=0),
    html.Button('重置', id='reset-button', n_clicks=0),
    
    # 顯示比賽結果表格
    dash_table.DataTable(
        id='match-table',
        columns=[
            {"name": col, "id": col} for col in df.columns
        ],
        data=df.to_dict('records'),
        page_size=10,
        style_data_conditional=[]
    )
])

@app.callback(
    [Output('match-table', 'data'),
     Output('match-table', 'style_data_conditional')],
    [Input('search-button', 'n_clicks'),
     Input('reset-button', 'n_clicks'),
     Input('filter-time', 'value'),
     Input('filter-location', 'value'),
     Input('filter-group', 'value'),
     Input('filter-keyword', 'value')]
)
def update_table(search_clicks, reset_clicks, time_filter, location_filter, group_filter, keyword_filter):
    ctx = dash.callback_context
    if not ctx.triggered or ctx.triggered[0]['prop_id'].split('.')[0] == 'reset-button':
        return df.to_dict('records'), []
    
    filtered_df = df.copy()
    style_conditions = []
    
    if time_filter:
        filtered_df = filtered_df[filtered_df['開始時間'].astype(str).str.contains(time_filter, case=False, na=False)]
    if location_filter:
        filtered_df = filtered_df[filtered_df['場地'].astype(str).str.contains(location_filter, case=False, na=False)]
    if group_filter:
        filtered_df = filtered_df[filtered_df['組別'].astype(str).str.contains(group_filter, case=False, na=False)]
    if keyword_filter:
        filtered_df = filtered_df[
            filtered_df['選手1'].astype(str).str.contains(keyword_filter, case=False, na=False) |
            filtered_df['選手2'].astype(str).str.contains(keyword_filter, case=False, na=False) |
            filtered_df['裁判'].astype(str).str.contains(keyword_filter, case=False, na=False)
        ]
        # 設定醒目的顏色標示搜尋到的選手和裁判
        style_conditions = []
        for col in ['選手1', '選手2', '裁判']:
            style_conditions.append(
                {'if': {'column_id': col, 'filter_query': f'{{{col}}} contains "{keyword_filter}"'}, 'backgroundColor': '#FFDD57', 'color': 'black'}
            )
    
    return filtered_df.to_dict('records'), style_conditions

server = app.server  # 讓 gunicorn 能識別 Flask 伺服器
if __name__ == "__main__":
    app.run_server(debug=True, port=10000)
