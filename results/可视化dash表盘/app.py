from dash import Dash, html, dcc, Input, Output
import dash
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[
        dbc.themes.FLATLY,
        "/assets/style.css"  # 添加自定义CSS
    ],
    suppress_callback_exceptions=True
)
server = app.server

# 主布局：新增底部背景容器
app.layout = html.Div([
    # 1. 原有内容：标题 + 导航栏
    html.H1("南京多源情感融合分析仪表盘", style={'marginTop': 20}),
    dbc.NavbarSimple(
        id="main-nav",
        children=[
            dbc.NavItem(dbc.NavLink("🏠 首页", href="/", id="nav-home")),
            dbc.NavItem(dbc.NavLink("🗺 地图分布", href="/map_view", id="nav-map")),
            dbc.NavItem(dbc.NavLink("💬 情绪分析", href="/emotion_view", id="nav-emotion")),
            dbc.NavItem(dbc.NavLink("🌤 气象-情感-景区-三维交叉分析", href="/weather_view", id="nav-weather")),
        ],
        brand="数据可视化导航",
        color="primary",
        dark=True,
        className="mb-4"
    ),
    dcc.Location(id="url", refresh=False),

    # 2. 原有内容：所有页面的容器
    html.Div(dash.page_container, id="page-container"),

    # 3. 新增：全局底部背景（所有页面下方都会显示）
    html.Div(id="global-footer-bg")  # 背景容器，样式在CSS中定义
])

# 原有导航栏激活态回调（不变）
@app.callback(
    [Output(f"nav-{page}", "active") for page in ["home", "map", "emotion", "weather"]],
    Input("url", "pathname")
)
def update_nav_active(pathname):
    return [pathname == "/", pathname == "/map_view", pathname == "/emotion_view", pathname == "/weather_view"]

if __name__ == '__main__':
    app.run(debug=True)