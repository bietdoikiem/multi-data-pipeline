from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from maindash import app
import dash
from plotly import graph_objects as go
from plotly.missing_ipywidgets import FigureWidget
import pandas as pd
from utils.cassandrautils import KrakenQueryUtils, CryptoPanicQueryUtils

currency_pairs = ["XBT/USD", "ETH/USD"]

DF = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
)


def render_kraken():
  return html.Div([
      dbc.Row(children=[
          dbc.Col([html.Div(children=["Headline View"], className="col-elem")],
                  width=3,
                  md=12,
                  lg=3,
                  xs=12),
          dbc.Col([
              html.Div([
                  html.P("Trading View"),
                  html.Div(children=[
                      dbc.DropdownMenu(
                          id="chart-dropdown",
                          label="XBT/USD",
                          color="dark",
                          children=[
                              dbc.DropdownMenuItem(id="XBT/USD-pair",
                                                   children="XBT/USD",
                                                   className="dropdown-item"),
                              dbc.DropdownMenuItem(id="ETH/USD-pair",
                                                   children="ETH/USD")
                          ]),
                      dcc.Graph(id="graph",
                                style={"margin-top": "10px"},
                                config={'displayModeBar': False}),
                      dcc.Store(id='intermediate-pair-value'),
                      dcc.Interval(id='chart-interval',
                                   interval=10 * 1000,
                                   n_intervals=0)
                  ],
                           className="inner-box"),
              ],
                       className="col-elem")
          ],
                  width=7,
                  md=12,
                  lg=7,
                  xs=12),
          dbc.Col([html.Div(["Bid/Ask View"], className="col-elem")],
                  width=2,
                  md=12,
                  lg=2,
                  xs=12)
      ],
              no_gutters=True)
  ])


def candlestick_chart():
  fig: FigureWidget = go.Figure(data=[
      go.Candlestick(x=DF['Date'],
                     open=DF['AAPL.Open'],
                     high=DF['AAPL.High'],
                     low=DF['AAPL.Low'],
                     close=DF['AAPL.Close'])
  ])
  fig.update_layout(width=1100,
                    height=700,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f0f0f0"),
                    yaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis_rangeslider_visible=False)
  return fig


# Define callback for XBT/USD and ETH/USD dropdown selection
@app.callback(Output("intermediate-pair-value", "data"),
              Input("XBT/USD-pair", "n_clicks"),
              Input("ETH/USD-pair", "n_clicks"))
def store_dropdown_value(*_):
  ctx = dash.callback_context
  if not ctx.triggered:
    button_id = "XBT/USD"
  else:
    button_id: str = ctx.triggered[0]['prop_id'].split('.')[0]
    # Remove the pair word
    button_id = button_id.split("-")[0]
  return button_id


# Define callback for XBT/USD and ETH/USD dropdown selection
@app.callback(Output("chart-dropdown", "label"),
              Input("intermediate-pair-value", "data"))
def display_dynamic_dropdown(label):
  return label


# Define callback for changing trading view to different pairs
@app.callback(Output("graph", "figure"),
              [Input("intermediate-pair-value", "data")])
def display_candlestick_by_pair(label):
  fig = candlestick_chart()
  kraken_utils = KrakenQueryUtils(pair=label)
  print(kraken_utils.queryByPair(limit=30,
                                 col_order="datetime",
                                 to_dataframe=True),
        flush=True)
  # elif label == "ETH/USD":
  #   fig = candlestick_chart()
  #   kraken_utils = KrakenQueryUtils(pair=label)
  #   print(kraken_utils.queryByPair(limit=30,
  #                                  col_order="datetime",
  #                                  to_dataframe=True),
  #         flush=True)

  return fig


# TODO: Map interval component to chart! create another layer call intermediate-pair and intermediate-value-df (for holding dataframe value)
# Define callback for live-update data in a specific interval
@app.callback(Output("intermediate-pair-value", "data"), [
    Input("chart-interval", "n_intervals"),
    Input("intermediate-pair-value", "data")
])
def live_update_pair(n, pair):
  kraken_utils = KrakenQueryUtils(pair=pair)
  kraken_data = kraken_utils.queryByPair(limit=30,
                                         col_order="datetime",
                                         to_dataframe=True)
  print(kraken_data, flush=True)
  return kraken_data