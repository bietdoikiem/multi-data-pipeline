from datetime import datetime
from time import time
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from maindash import app
import dash
from pandas.core.frame import DataFrame
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
                  html.H2("Top Headlines 📰"),
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
                  html.H2("Trading View 📊"),
                  html.Div(children=[
                      html.Div(children=[
                          dbc.DropdownMenu(id="chart-dropdown",
                                           label="XBT/USD",
                                           color="dark",
                                           style={
                                               "display": "inline",
                                               "margin-right": "10px"
                                           },
                                           children=[
                                               dbc.DropdownMenuItem(
                                                   id="XBT/USD-pair",
                                                   children="XBT/USD",
                                                   className="dropdown-item"),
                                               dbc.DropdownMenuItem(
                                                   id="ETH/USD-pair",
                                                   children="ETH/USD")
                                           ]),
                          dbc.DropdownMenu(id="study-dropdown",
                                           label="Study 📉",
                                           color="dark",
                                           style={"display": "inline"},
                                           children=[
                                               dbc.InputGroup([
                                                   dbc.InputGroupAddon(
                                                       dbc.Checkbox(),
                                                       addon_type="prepend"),
                                                   html.P("MA")
                                               ])
                                           ])
                      ],
                               style={"display": "inline"}),
                      dcc.Graph(id="graph",
                                style={"display": "none"},
                                config={'displayModeBar': False}),
                      dcc.Store(id='intermediate-pair'),
                      dcc.Store(id='intermediate-pair-value-json'),
                      dcc.Store(id="intermediate-cryptopanic-value"),
                      dcc.Store(id="prev-index-time"),
                      dcc.Store(id="latest-price"),
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
          dbc.Col([html.Div([html.H2("Bid/Ask 🏷️")], className="col-elem")],
                  width=2,
                  md=12,
                  lg=2,
                  xs=12)
      ],
              no_gutters=True)
  ])


#### CryptoPanic Utility functions & callbacks ####
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
  news_data = headline_news(10)
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


def study_factory(df: DataFrame, study_type: str = None):
  # Check if there is empty list of study provided
  if study_type == None:
    raise "Please provide one study type!"
  # Factory conditions #
  if (study_type == "ma"):
    print("Updating MovingAverage")
    return moving_average_trace(df, days=5)
  elif (study_type == "ema"):
    return exponential_moving_average_trace(df, days=20)
  else:
    raise "Please provide a valid chart study type!"


# Chart Creator
def chart_factory(df: DataFrame,
                  chart_type="candlestick",
                  studies: list = None):
  traces = []
  # Trace of study process
  if (studies != None and len(studies) > 0):
    for study in studies:
      traces.append(study_factory(df, study_type=study))
  # Produce appropriate chart
  if (chart_type == "candlestick"):
    chart_data = [
        go.Candlestick(x=df.index,
                       open=df['open'],
                       high=df['high'],
                       low=df['low'],
                       close=df['close'])
    ]
    if (len(traces) > 0):
      for trace in traces:
        chart_data.append(trace)
    return candlestick_chart(chart_data)
  return None


#### Kraken Utility functions & callbacks ####
def moving_average_trace(df: DataFrame, days=5):
  return go.Scatter(x=df.index,
                    y=df['close'].rolling(days, min_periods=1).mean(),
                    line=dict(color='orange', width=1))


def exponential_moving_average_trace(df: DataFrame, days=20):
  return go.Scatter(x=df.index,
                    y=df['close'].ewm(span=days,
                                      min_periods=0,
                                      adjust=False,
                                      ignore_na=False).mean(),
                    line=dict(color='blue', width=1))


def candlestick_chart(data):
  fig: FigureWidget = go.Figure(data=data)
  fig.update_layout(width=1080,
                    height=550,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f0f0f0"),
                    yaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=20, r=20, b=10, t=10))
  return fig


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


def preprocess_ohlc(df: DataFrame, column=None, parse_datetime=False):
  if (parse_datetime == True):
    df['datetime'] = pd.to_datetime(df['datetime'])
  df_ohlc = df.reset_index().set_index('datetime')
  df_ohlc = df_ohlc[column].resample('1Min').ohlc()
  return df_ohlc


# Define callback for changing trading view to different pairs
@app.callback([Output("graph", "figure"),
               Output("graph", "style")], [
                   Input("intermediate-pair", "data"),
                   Input("intermediate-pair-value-json", "data"),
                   State("chart-interval", "n_intervals"),
               ])
def display_candlestick_by_pair(label, json_value, n):
  ctx = dash.callback_context
  trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
  # If update
  if (trigger_id == "intermediate-pair-value-json"):
    df_closed = pd.DataFrame(json.loads(json_value))
    df_closed_ohlc = preprocess_ohlc(df_closed,
                                     column="closed_value",
                                     parse_datetime=True)
    fig = chart_factory(df=df_closed_ohlc,
                        chart_type="candlestick",
                        studies=["ma", "ema"])
    print("Successfully updated {} chart".format(label))
    return fig, {"margin-top": "10px", "display": "inline"}
  # If initial fetch on pair
  df_closed = kraken_utils.queryByPair(limit=1000,
                                       pair=label,
                                       col_order="datetime",
                                       sort=SortingType.DESCENDING,
                                       to_dataframe=True)
  print("=> Switched to chart {}".format(label))
  df_closed_ohlc = preprocess_ohlc(df_closed,
                                   column="closed_value",
                                   parse_datetime=True)
  fig = chart_factory(df=df_closed_ohlc,
                      chart_type="candlestick",
                      studies=["ma", "ema"])
  return fig, {"margin-top": "10px", "display": "inline"}


# Define callback for live-update data in a specific interval
@app.callback([
    Output("intermediate-pair-value-json", "data"),
    Output("prev-index-time", "data"),
    Output("latest-price", "data")
], [
    Input("chart-interval", "n_intervals"),
    State("intermediate-pair", "data"),
    State("prev-index-time", "data")
])
def live_update_pair(n, pair, prev_time):
  if (n == 0):
    return dash.no_update, dash.no_update, dash.no_update
  kraken_data = kraken_utils.queryByPair(limit=1000,
                                         pair=pair,
                                         col_order="datetime",
                                         sort=SortingType.DESCENDING,
                                         to_dataframe=False)
  if (prev_time is not None):
    if (datetime.fromisoformat(str(prev_time)) == kraken_data[0]['datetime']):
      return dash.no_update, prev_time, dash.no_update
  print("Kraken Live Update {} of iteration no.".format(pair), n)
  last_price = kraken_data[0]['closed_value']
  # print(kraken_data)
  return json.dumps(kraken_data,
                    default=str), kraken_data[0]['datetime'], last_price


app.clientside_callback(
    """
    function(latest_price, pair) {
      if (typeof latest_price === "undefined") {
        document.title = pair
      } else {
        document.title = latest_price + " " + pair
      }
    }
  """, Output("blank-output", "children"), Input("latest-price", "data"),
    Input("intermediate-pair", "data"))

# Test callback for extendData of real-time graph
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