from dash import html, dcc, register_page, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

register_page(__name__, path="/map_view", name="地图分布")

# 数据读取与预处理
df = pd.read_csv("data\processed_data\情感分析结果（限制情感大类）.csv")
df["最高气温"] = df["最高气温"].astype(str).str.replace("℃", "").astype(float)
df["最低气温"] = df["最低气温"].astype(str).str.replace("℃", "").astype(float)

# 确保情感分类合法
valid_emotion_types = ['愉悦', '无情绪', '怀旧', '失望', '悲伤', '烦躁']
df['emotion_type'] = df['emotion_type'].where(df['emotion_type'].isin(valid_emotion_types), '中性')

# 确保intensity是数值（0-10范围）
df['intensity'] = pd.to_numeric(df['intensity'], errors='coerce').fillna(0)


# 定义天气映射关系
def map_weather_to_category(weather):
    if pd.isna(weather):
        return None
    weather = str(weather)
    if "雨" in weather:
        return "雨"
    elif "云" in weather or "雾" in weather:
        return "云、雾"
    elif "晴" in weather:
        return "晴"
    else:
        return "其他"

# 创建新的天气分类列
df['天气分类'] = df['天气'].apply(map_weather_to_category)

# 定义天气分类的显示顺序
weather_order = ["晴", "雨", "云、雾"]

layout = html.Div([
    html.H3("🗺 景点评价情感分布地图"),
    
    # 筛选器容器
    html.Div([
        # 天气筛选器
        html.Div([
            #下拉菜单中菜单中的文字改变为黑色字体

            dcc.Dropdown(
                id='weather_filter',
                options=[{'label': w, 'value': w} for w in weather_order],
                value=None,
                placeholder="选择天气类型（空表示全部）",
                clearable=True,
                style={'width': '100%', 'color': 'black'}
            )
        ], style={'width': '32%', 'display': 'inline-block'}),
        
        # 景点类型筛选器
        html.Div([
            dcc.Dropdown(
                id='poi_type_filter',
                options=[{'label': t, 'value': t} for t in sorted(df['tag5'].dropna().unique())],
                value=None,
                placeholder="选择景区类型（空表示全部）",
                clearable=True,
                style={'width': '100%', 'color': 'black'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'margin-left': '2%'}),
        
        # 情感筛选器
        html.Div([
            dcc.Dropdown(
                id='emotion_filter',
                options=[{'label': e, 'value': e} for e in valid_emotion_types],
                value=None,
                placeholder="选择情感类型（空表示全部）",
                clearable=True,
                style={'width': '100%', 'color': 'black'}
            )
        ], style={'width': '32%', 'display': 'inline-block', 'margin-left': '2%'})
    ], style={'margin': '0 auto 30px auto', 'width': '90%'}),
    
    # 主要内容区域 - 左侧地图，右侧两个饼图上下排列
    html.Div([
        # 左侧地图
        html.Div([
            dcc.Graph(id='map_graph')
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        # 右侧图表区域（上下排列两个饼图）
        html.Div([
            # 情感分布饼图
            html.Div([
                dcc.Graph(id='emotion_pie_chart')
            ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'}),
            
            # 景区分布饼图
            html.Div([
                dcc.Graph(id='poi_pie_chart')
            ], style={'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'})
        ], 
        style={'width': '33%', 'display': 'inline-block', 'margin-left': '2%', 'vertical-align': 'top'})
    ], style={'width': '90%', 'margin': '0 auto'})
])


# 回调函数（更新图表）
def update_dashboard(selected_weather, selected_poi_type, selected_emotion):
    # 筛选数据
    filtered_df = df.copy()
    if selected_weather:
        filtered_df = filtered_df[filtered_df['天气分类'] == selected_weather]
    if selected_poi_type:
        filtered_df = filtered_df[filtered_df['tag5'] == selected_poi_type]
    if selected_emotion:
        filtered_df = filtered_df[filtered_df['emotion_type'] == selected_emotion]
    
    # 处理空数据情况
    if filtered_df.empty:
        empty_fig = go.Figure().update_layout(
            annotations=[{'text': '无符合条件的数据', 'xref': 'paper', 'yref': 'paper', 
                         'font': {'size': 16}, 'showarrow': False}],
            title='筛选结果为空'
        )
        return empty_fig, empty_fig, empty_fig

    # ----------------------
    # 1. 地图：景点情感分布
    # ----------------------
    # 添加轻微的随机噪声以防止点重叠
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['lat_jittered'] = filtered_df_copy['lat'] + np.random.normal(0, 0.001, len(filtered_df_copy))
    filtered_df_copy['lon_jittered'] = filtered_df_copy['lon'] + np.random.normal(0, 0.001, len(filtered_df_copy))
    
    map_fig = px.scatter_mapbox(
        filtered_df_copy,
        lat='lat_jittered', lon='lon_jittered',  # 使用添加了抖动的坐标
        color='emotion_type',
        #透明度
        opacity=0.5,
        size='intensity',
        size_max=15,   # 0-10范围（比之前大一点）
        hover_name='name',
        hover_data={
            'message': True, '天气': True, 'emotion_type': True,
            '最高气温': True, '最低气温': True, 'tag5': True,   # 显示景区类型
            'lat': False, 'lon': False, 'lat_jittered': False, 'lon_jittered': False  # 隐藏抖动坐标
        },
        zoom=11, height=600,
        center=dict(lat=32.0603, lon=118.7969),  # 南京市中心坐标
        mapbox_style='carto-positron', #不带颜色的
        color_discrete_map={
            '愉悦': '#43A047',      # 深绿色，代表积极情绪，稳重且充满生机
            '无情绪': '#78909C',    # 蓝灰色，代表中性情绪，平衡且不突兀
            '怀旧': '#1E88E5',      # 皇家蓝，代表怀旧情绪，深沉且有韵味
            '悲伤': '#8E24AA',      # 深紫色，代表悲伤情绪，内敛且有深度
            '烦躁': '#FB8C00',      # 深橙色，代表烦躁情绪，醒目但不过分刺眼
            '失望': '#F4511E'       # 深橙红色，代表失望情绪，温暖中带点冷色调
        },
        title=f"景点情感分布（天气: {selected_weather if selected_weather else '全部'} | 景区: {selected_poi_type if selected_poi_type else '全部'} | 情感: {selected_emotion if selected_emotion else '全部'}）"
    )
    # 限制地图范围为南京市
    map_fig.update_layout(
        margin={'r':0,'t':40,'l':0,'b':0},
        mapbox=dict(
            center=dict(lat=32.0603, lon=118.7969)
            )
        )
    
    # ----------------------
    # 2. 情感分布饼图
    # ----------------------
    emotion_counts = filtered_df['emotion_type'].value_counts().reset_index()
    emotion_counts.columns = ['情感类型', '数量']
    
    # 如果没有数据，创建空的饼图
    if emotion_counts.empty:
        emotion_pie_fig = go.Figure().update_layout(
            annotations=[{'text': '无情感数据', 'xref': 'paper', 'yref': 'paper', 
                         'font': {'size': 16}, 'showarrow': False}],
            title='情感分布'
        )
    else:
        # 使用与地图相同的情感颜色映射
        color_map = {
            '愉悦': '#43A047',      # 深绿色
            '无情绪': '#78909C',    # 蓝灰色
            '怀旧': '#1E88E5',      # 皇家蓝
            '悲伤': '#8E24AA',      # 深紫色
            '烦躁': '#FB8C00',      # 深橙色
            '失望': '#F4511E',      # 深橙红色
            '中性': '#B0BEC5'       # 默认中性色
        }
        
        emotion_pie_fig = px.pie(
            emotion_counts,
            values='数量',
            names='情感类型',
            title='情感分布',
            color='情感类型',
            color_discrete_map=color_map
        )
        emotion_pie_fig.update_traces(textposition='inside', textinfo='percent+label')
        emotion_pie_fig.update_layout(height=300)
    
    # ----------------------
    # 3. 景区分布饼图（使用tag5）
    # ----------------------
    poi_counts = filtered_df['tag5'].value_counts().reset_index()
    poi_counts.columns = ['景区', '数量']
    
    # 如果没有数据，创建空的饼图
    if poi_counts.empty:
        poi_pie_fig = go.Figure().update_layout(
            annotations=[{'text': '无景区数据', 'xref': 'paper', 'yref': 'paper', 
                         'font': {'size': 16}, 'showarrow': False}],
            title='景区分布'
        )
    else:
        poi_pie_fig = px.pie(
            poi_counts,
            values='数量',
            names='景区',
            title='景区分布',
        )
        poi_pie_fig.update_traces(textposition='inside', textinfo='percent+label')
        poi_pie_fig.update_layout(height=300)
    
    return map_fig, emotion_pie_fig, poi_pie_fig


# 注册回调函数
from dash import callback
@callback(
    [Output('map_graph', 'figure'),
     Output('emotion_pie_chart', 'figure'),
     Output('poi_pie_chart', 'figure')],
    [Input('weather_filter', 'value'),
     Input('poi_type_filter', 'value'),
     Input('emotion_filter', 'value')]
)
def update_map(selected_weather, selected_poi_type, selected_emotion):
    return update_dashboard(selected_weather, selected_poi_type, selected_emotion)