# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from maindash import app
from pages import kraken, analysis, twitter, wc_analysis_dynamic

# app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

# add some padding.
CONTENT_STYLE = {"background-color": "#000000"}

# page's content
content = html.Div(id='page-content', style=CONTENT_STYLE)

# Horizontal Navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Kraken", href="/kraken"),
                    className="navlink-item"),
    # dbc.NavItem(dbc.NavLink("Twitter", href="/twitter")),
        dbc.NavItem(dbc.NavLink("Analysis", href="/analysis")),
    ],
    brand="XtremeOLAP",
    brand_href="/",
    color="rgba(88,75,170,1.00)",
    dark=True,
    fluid=True,
)

# App overall layout
# app.layout = html.Div([dcc.Location(id="url"), navbar, content])


def make_layout():
  return html.Div(
      [html.Div(id="blank-output"),
       dcc.Location(id="url"), navbar, content])


# Route navigation callback
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname: str):
  if pathname == "/" or pathname == "/kraken":
    return kraken.render_kraken()
  elif pathname == "/twitter":
    return twitter.render_twitter()
  elif pathname == "/analysis":
    return analysis.render_analysis()
  elif pathname.startswith("/analysis/wordcloud/"):
    id = pathname.split('/')[-1]
    return wc_analysis_dynamic.render_wc_analysis(id)
  # If the user tries to navigate to invalid page, return a 404 message
  return dbc.Jumbotron([
      html.H1("404: Not found", className="text-danger"),
      html.Hr(),
      html.P(f"The path {pathname} was not recognized...")
  ],
                       style={"background-color": "#000000"})


# if __name__ == '__main__':
#   app.run_server(host='0.0.0.0', debug=True, port=8050)
