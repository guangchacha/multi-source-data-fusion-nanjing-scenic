from dash import html, register_page
import pandas as pd

register_page(__name__, path="/emotion_view", name="情绪分析")

df = pd.read_csv("data\processed_data\情感分析结果（限制情感大类）.csv")

layout = html.Div([
    html.H3("💬 情感与景区交叉分析", style={'margin': '20px 0'}),

    # 外层容器：使用 CSS Grid 布局
    html.Div([
        # 各个图片卡片
        html.Div([
            html.H4("各景区情感类型分布"),
            html.Img(src="/assets/可视化图片/不同情绪类型的平均强度.png",
                     style={'width': '100%', 'borderRadius': '8px'})
        ], className="image-card"),

        html.Div([
            html.H4("景区-情感类型占比"),
            html.Img(src="/assets/可视化图片/景区-情感类型占比.png",
                     style={'width': '100%', 'borderRadius': '8px'})
        ], className="image-card"),


        html.Div([
            html.H4("愉悦情感关键词云"),
            html.Img(src="/assets/可视化图片/“愉悦”情感关键词云.png",
                     style={'width': '100%', 'borderRadius': '8px'})
        ], className="image-card"),

        html.Div([
            html.H4("怀旧情感关键词云"),
            html.Img(src="/assets/可视化图片/“怀旧”情感关键词云.png",
                     style={'width': '100%', 'borderRadius': '8px'})
        ], className="image-card")

        
    ], style={
        'display': 'grid',
        'gridTemplateColumns': 'repeat(auto-fit, minmax(450px, 1fr))',
        'gap': '20px',
        'justifyItems': 'center',
        'alignItems': 'start',
        'padding': '10px'
    })
])
