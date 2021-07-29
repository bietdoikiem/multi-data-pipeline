from datetime import datetime
from time import time
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from maindash import app
import dash
from plotly import graph_objects as go
from plotly.missing_ipywidgets import FigureWidget
import pandas as pd
from utils.cassandrautils import KrakenQueryUtils, CryptoPanicQueryUtils, SortingType
import json

# Connect to Query
kraken_utils = KrakenQueryUtils()
cryptopanic_utils = CryptoPanicQueryUtils()


def render_kraken():
  return html.Div([
      dbc.Row(children=[
          dbc.Col([
              html.Div(children=[
                  html.H2("Top Headlines"),
                  dbc.Card(dbc.ListGroup(id="news-list", flush=True),
                           color="rgba(72, 72, 72, 1)")
              ],
                       className="col-elem")
          ],
                  width=3,
                  md=12,
                  lg=3,
                  xs=12),
          dbc.Col([
              html.Div([
                  html.H2("TradingView"),
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
                                style={"display": "none"},
                                config={'displayModeBar': False}),
                      dcc.Store(id='intermediate-pair'),
                      dcc.Store(id='intermediate-pair-value-json'),
                      dcc.Store(id="intermediate-cryptopanic-value"),
                      dcc.Store(id="prev-index-time"),
                      dcc.Interval(id='news-interval',
                                   interval=60 * 1000,
                                   n_intervals=0),
                      dcc.Interval(
                          id='chart-interval', interval=5 * 1000, n_intervals=0)
                  ],
                           className="inner-box"),
              ],
                       className="col-elem")
          ],
                  width=7,
                  md=12,
                  lg=7,
                  xs=12),
          dbc.Col([html.Div([html.H2("Bid/Ask")], className="col-elem")],
                  width=2,
                  md=12,
                  lg=2,
                  xs=12)
      ],
              no_gutters=True)
  ])


def candlestick_chart(x_series, open, high, low, close):
  fig: FigureWidget = go.Figure(data=[
      go.Candlestick(x=x_series, open=open, high=high, low=low, close=close)
  ])
  fig.update_layout(width=1100,
                    height=500,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f0f0f0"),
                    yaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=20, r=20, b=10, t=10))
  return fig


def headline_news(top: str = 10):
  print("=> News fetching...")
  return cryptopanic_utils.query(limit=top)


def create_list_item(title, url, source_title):
  return dcc.Link(dbc.ListGroupItem(dcc.Markdown(f'''
  {title} - _{source_title}_
  '''),
                                    color="#000000",
                                    style={
                                        "border-width": "0.5px",
                                        "border-color": "rgba(72, 72, 72, 1)",
                                    }),
                  href=url,
                  target='_blank')


@app.callback(Output("intermediate-cryptopanic-value", "data"),
              Input("news-interval", "n_intervals"))
def live_update_news(n):
  news_data = headline_news(15)
  if (n > 0):
    print("News Live Update no.", n)
  else:
    print("Initial CryptoPanic fetch!")
  # print(news_data, flush=True)
  return json.dumps(news_data, default=str)


@app.callback([Output("news-list", "children")],
              [Input("intermediate-cryptopanic-value", "data")])
def create_live_news_list(json_data):
  data = json.loads(json_data)
  return [[
      create_list_item(news['title'], news['url'], news['source_title'])
      for news in data
  ]]


# Define callback for XBT/USD and ETH/USD dropdown selection
@app.callback(Output("intermediate-pair", "data"),
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
              Input("intermediate-pair", "data"))
def display_dynamic_dropdown(label):
  return label


# @app.callback([Output("graph", "extendData")],
#               [Input("chart-interval", "n_intervals")])
# def test_live_update(n):
#   current_datetime = datetime.now().isoformat()
#   print("updating")
#   return [
#       dict(close=[[396000.5 + n]],
#            high=[[39700.5 + n]],
#            low=[[39500.0 + n]],
#            open=[[39550.5 + n]],
#            x=[[current_datetime]])
#   ]


# Define callback for changing trading view to different pairs
@app.callback([
    Output("graph", "figure"),
    Output("graph", "style"),
], [
    Input("intermediate-pair", "data"),
    Input("intermediate-pair-value-json", "data"),
    State("chart-interval", "n_intervals"),
])
def display_candlestick_by_pair(label, json_value, n):
  ctx = dash.callback_context
  trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
  # If update
  if (trigger_id == "intermediate-pair-value-json"):
    df_closed = pd.DataFrame(
        json.loads(json_value))    #.reset_index().set_index('datetime')
    df_closed['datetime'] = pd.to_datetime(df_closed['datetime'])
    df_closed = df_closed.reset_index().set_index('datetime')
    df_closed_ohlc = df_closed['closed_value'].resample('1Min').ohlc()
    fig = candlestick_chart(x_series=df_closed_ohlc.index,
                            open=df_closed_ohlc['open'],
                            high=df_closed_ohlc['high'],
                            low=df_closed_ohlc['low'],
                            close=df_closed_ohlc['close'])
    print("Successfully updated {} chart".format(label))
    return fig, {"margin-top": "10px", "display": "inline"}
  # If initial fetch on pair
  df_closed = kraken_utils.queryByPair(limit=500,
                                       pair=label,
                                       col_order="datetime",
                                       sort=SortingType.DESCENDING,
                                       to_dataframe=True)
  print("=> Switched to chart {}".format(label))
  df_closed['datetime'] = pd.to_datetime(df_closed['datetime'])
  df_closed = df_closed.reset_index().set_index('datetime')
  df_closed_ohlc = df_closed['closed_value'].resample('1Min').ohlc()
  fig = candlestick_chart(x_series=df_closed_ohlc.index,
                          open=df_closed_ohlc['open'],
                          high=df_closed_ohlc['high'],
                          low=df_closed_ohlc['low'],
                          close=df_closed_ohlc['close'])
  return fig, {"margin-top": "10px", "display": "inline"}


# TODO: Map interval component to chart! create another layer call intermediate-pair and intermediate-value-json (for holding JSON value)
# Define callback for live-update data in a specific interval
@app.callback([
    Output("intermediate-pair-value-json", "data"),
    Output("prev-index-time", "data")
], [
    Input("chart-interval", "n_intervals"),
    State("intermediate-pair", "data"),
    State("prev-index-time", "data")
])
def live_update_pair(n, pair, prev_time):
  if (n == 0):
    return dash.no_update, dash.no_update
  kraken_data = kraken_utils.queryByPair(limit=500,
                                         pair=pair,
                                         col_order="datetime",
                                         sort=SortingType.DESCENDING,
                                         to_dataframe=False)
  # print(kraken_data, flush=True)
  # print("Prev Time:", prev_time)
  if (prev_time is not None):
    if (datetime.fromisoformat(str(prev_time)) == kraken_data[0]['datetime']):
      print("Nothing to Update!")
      return dash.no_update, prev_time
  print("Live Update {} of iteration no.".format(pair), n)
  # print(kraken_data)
  return [json.dumps(kraken_data, default=str), kraken_data[0]['datetime']]


# TODO: Tomorrow please Test real-time data stream again