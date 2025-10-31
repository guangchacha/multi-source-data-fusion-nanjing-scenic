from dash import html, dcc, register_page
import pandas as pd

# 注册新页面
register_page(__name__, path="/weather_view", name="气象-情感-景区-三维交叉分析")

layout = html.Div([

    html.H3("气象-情感-景区-三维交叉分析", style={'margin': '20px 0'}),

    # 使用 CSS Grid 创建两栏布局
    html.Div([
        # 第一行左
        html.Div([
            html.H4("降水与景区情感对比", style={'fontSize': 16}),
            html.Img(
                src="/assets/可视化图片/降水-景区情感对比.png",
                style={
                    'width': '100%',
                    'maxWidth': '450px',
                    'height': 'auto',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px'
                }
            )
        ], className="image-card"),

        # 第一行右
        html.Div([
            html.H4("能见度与景区情感对比", style={'fontSize': 16}),
            html.Img(
                src="/assets/可视化图片/能见度-景区情感对比.png",
                style={
                    'width': '100%',
                    'maxWidth': '450px',
                    'height': 'auto',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px'
                }
            )
        ], className="image-card"),

        # 第二行左
        html.Div([
            html.H4("天气情感分布箱线图", style={'fontSize': 16}),
            html.Img(
                src="/assets/可视化图片/天气情感分布箱线图.png",
                style={
                    'width': '100%',
                    'maxWidth': '450px',
                    'height': 'auto',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px'
                }
            )
        ], className="image-card"),

        # 第二行右
        html.Div([
            html.H4("天气-情感类型占比", style={'fontSize': 16}),
            html.Img(
                src="/assets/可视化图片/天气-情感类型占比.png",
                style={
                    'width': '100%',
                    'maxWidth': '450px',
                    'height': 'auto',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px'
                }
            )
        ], className="image-card"),

        # 第三行横跨两列
        html.Div([
            html.H4("天气与景区情感热力图", style={'fontSize': 16}),
            html.Img(
                src="/assets/可视化图片/天气-景区情感热力图.png",
                style={
                    'width': '100%',
                    'maxWidth': '920px',
                    'height': 'auto',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px'
                }
            )
        ], className="image-card wide-card"),

        # 第四行横跨两列
        html.Div([
            html.H4("情感强度三维交叉分析", style={'fontSize': 16}),
            html.Img(
                src="/assets/可视化图片/三维交叉-情感强度.png",
                style={
                    'width': '100%',
                    'maxWidth': '920px',
                    'height': 'auto',
                    'border': '1px solid #ddd',
                    'borderRadius': '8px'
                }
            )
        ], className="image-card wide-card"),
    ], className="two-column-grid")
])
