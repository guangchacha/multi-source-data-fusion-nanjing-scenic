from dash import html, register_page
import dash_bootstrap_components as dbc

register_page(__name__, path="/", name="首页")

layout = html.Div([
    # 页面标题卡片
    dbc.Card([
        html.H3([
            html.Span(" 🧩项目简介", style={'color': "#1C6B83"}),  # 图标+标题，改成黑色
            html.Hr(style={'borderColor': "#BFD2E9", 'margin': '12px 0'})  # 浅蓝分隔线
        ]),
        html.P("""
            本项目基于南京地区微博签到数据、景点POI信息与气象数据，
            融合情感分析结果，构建多维度可视化仪表盘。目标是探索情绪、
            气象与地理位置的耦合特征，揭示城市体验中的情绪空间分布。
        """, className="home-desc"),
        
        # 数据维度卡片（嵌套小卡片，更精致）
        dbc.Card([
            html.H4([html.Span("🧩 数据维度说明")]),
            html.Ul([
                html.Li("地理维度：经纬度、POI景点名称"),
                html.Li("文本维度：微博签到内容（message）"),
                html.Li("气象维度：最高/最低气温、天气、风向"),
                html.Li("情感维度：sentiment（正负面）、intensity（强度）、emotion_type（情绪类型）")
            ], className="feature-list")
        ], style={'backgroundColor': 'var(--primary-light)', 'marginTop': '16px'}),
        
        html.P("👉 点击上方导航栏可进入各个分析页面，支持按日期和天气筛选数据。", 
               style={'color': 'var(--primary)', 'marginTop': '16px', 'fontWeight': 500})
    ], className="card")  # 应用全局卡片样式
])