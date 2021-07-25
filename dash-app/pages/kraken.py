from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.Div import Div


def render_kraken():
  return dbc.Row(children=[
      dbc.Col([html.Div(children=["Headline View"], className="col-elem")],
              width=3),
      dbc.Col([
          html.Div([
              html.P("Trading View"),
              html.Div(children=[
                  dbc.DropdownMenu(id="chart-dropdown",
                                   label="XBT/USD",
                                   color="dark",
                                   children=[
                                       dbc.DropdownMenuItem("XBT/USD"),
                                       dbc.DropdownMenuItem("ETH/USD")
                                   ]),
                  dcc.Graph(id="graph", style={"margin-top": "10px"})
              ],
                       className="inner-box"),
          ],
                   className="col-elem")
      ],
              width=6),
      dbc.Col([html.Div(["Bid/Ask View"], className="col-elem")], width=3)
  ])