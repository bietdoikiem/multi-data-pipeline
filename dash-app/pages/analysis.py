from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


def render_analysis():
  return html.Div(children=[html.H1("Analysis Page")])
