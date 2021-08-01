from datetime import datetime
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
                          dbc.DropdownMenu(
                              id="timeframe-dropdown",
                              label="1Min",
                              color="dark",
                              style={
                                  "display": "inline",
                                  "margin-right": "10px"
                              },
                              children=[
                                  dbc.DropdownMenuItem(
                                      id="1Min",
                                      children="1Min",
                                      className="dropdown-item"),
                                  dbc.DropdownMenuItem(id="5Min",
                                                       children="5Min"),
                                  dbc.DropdownMenuItem(id="30Min",
                                                       children="30Min"),
                                  dbc.DropdownMenuItem(id="1Hour",
                                                       children="1Hour"),
                              ]),
                          dbc.DropdownMenu(
                              id="study-dropdown",
                              label="Study 📉",
                              color="dark",
                              style={"display": "inline"},
                              children=[
                                  dcc.Checklist(id="studies-checklist",
                                                options=[
                                                    {
                                                        'label': 'MA',
                                                        'value': 'ma'
                                                    },
                                                    {
                                                        'label': 'EMA',
                                                        'value': 'ema'
                                                    },
                                                    {
                                                        'label': 'Bollinger',
                                                        'value': 'bollinger'
                                                    },
                                                    {
                                                        'label': 'Ichimoku',
                                                        'value': 'ichimoku'
                                                    },
                                                ],
                                                value=[],
                                                style={
                                                    "margin-left": "10px",
                                                    "color": "#f0f0f0",
                                                },
                                                labelStyle={"display": "block"})
                              ])
                      ],
                               style={"display": "inline"}),
                      dcc.Graph(id="graph",
                                style={"display": "none"},
                                config={'displayModeBar': False}),
                      dcc.Store(id='intermediate-pair'),
                      dcc.Store(id='intermediate-timeframe'),
                      dcc.Store(id='intermediate-pair-value-json'),
                      dcc.Store(id="intermediate-cryptopanic-value"),
                      dcc.Store(id="prev-index-time"),
                      dcc.Store(id="latest-price"),
                      dcc.Store(id="last-ask"),
                      dcc.Store(id="last-bid"),
                      dcc.Interval(id='news-interval',
                                   interval=3600 * 1000,
                                   n_intervals=0),
                      dcc.Interval(
                          id='chart-interval', interval=3 * 1000, n_intervals=0)
                  ],
                           className="inner-box"),
              ],
                       className="col-elem")
          ],
                  width=7,
                  md=12,
                  lg=7,
                  xs=12),
          dbc.Col(children=[
              html.Div(children=[
                  html.H2("Ask/Bid 🏷️"),
                  dbc.Row(children=[
                      dbc.Col(html.H4("💱"), width=4),
                      dbc.Col(html.H4("Ask ❓"), width=4),
                      dbc.Col(html.H4("Bid 🙏"), width=4)
                  ],
                          className="mb-2"),
                  dbc.Row(children=[
                      dbc.Col(html.P(id="ask-bid-pair", children=""), width=4),
                      dbc.Col(html.P(id="ask-price", children=""), width=4),
                      dbc.Col(html.P(id="bid-price", children=""), width=4)
                  ])
              ],
                       className="col-elem")
          ],
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
  return cryptopanic_utils.query(limit=top, categories=["news"])


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
    return moving_average_trace(df, window_size=5)
  elif (study_type == "ema"):
    return exponential_moving_average_trace(df, window_size=20)
  elif (study_type == "bollinger"):
    return bollinger_trace(df, window_size=10, num_of_std=5)
  elif (study_type == "ichimoku"):
    return ichimoku_cloud_trace(df)
  else:
    raise "Please provide a valid chart study type!"


# Chart Creator
def chart_factory(df: DataFrame,
                  chart_type="candlestick",
                  studies: list = None,
                  pair=None):
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
                       close=df['close'],
                       showlegend=False,
                       name="Chart")
    ]
    if (len(traces) > 0):
      for trace in traces:
        # Check if one trace contain multiple sub-traces
        if (isinstance(trace, list)):
          for subtrace in trace:
            chart_data.append(subtrace)
        else:
          chart_data.append(trace)
    return candlestick_chart(chart_data, pair=pair)
  return None


#### Kraken Utility functions & callbacks ####
# Technical Indicators #
def moving_average_trace(df: DataFrame, window_size=7):
  return go.Scatter(x=df.index,
                    y=df['close'].rolling(window_size, min_periods=1).mean(),
                    showlegend=False,
                    name="MA",
                    line=dict(color='#FFD580', width=1))


def exponential_moving_average_trace(df: DataFrame, window_size=21):
  return go.Scatter(x=df.index,
                    y=df['close'].ewm(span=window_size,
                                      min_periods=1,
                                      adjust=False,
                                      ignore_na=False).mean(),
                    showlegend=False,
                    name="EMA",
                    line=dict(color='#ADD8E6', width=1))


# Bollinger Bands
def bollinger_trace(df: DataFrame, window_size=20, num_of_std=2):
  price = df["close"]
  rolling_mean = price.rolling(window=window_size, min_periods=1).mean()
  rolling_std = price.rolling(window=window_size, min_periods=1).std()
  upper_band = rolling_mean + (rolling_std * num_of_std)
  lower_band = rolling_mean - (rolling_std * num_of_std)

  trace1 = go.Scatter(x=df.index,
                      y=upper_band,
                      mode="lines",
                      showlegend=False,
                      name="BB_upper",
                      line=dict(width=1))

  trace2 = go.Scatter(x=df.index,
                      y=rolling_mean,
                      mode="lines",
                      showlegend=False,
                      name="BB_mean",
                      line=dict(width=1))

  trace3 = go.Scatter(x=df.index,
                      y=lower_band,
                      mode="lines",
                      showlegend=False,
                      name="BB_lower",
                      line=dict(width=1))

  return [trace1, trace2, trace3]


def ichimoku_cloud_trace(df: DataFrame):
  # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
  period9_high = df['high'].rolling(window=9, min_periods=1).max()
  period9_low = df['low'].rolling(window=9, min_periods=1).min()
  tenkan_sen = (period9_high + period9_low) / 2

  # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
  period26_high = df['high'].rolling(window=26, min_periods=1).max()
  period26_low = df['low'].rolling(window=26, min_periods=1).min()
  kijun_sen = (period26_high + period26_low) / 2

  # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
  senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

  # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
  period52_high = df['high'].rolling(window=52, min_periods=1).max()
  period52_low = df['low'].rolling(window=52, min_periods=1).min()
  senkou_span_b = ((period52_high + period52_low) / 2).shift(26)

  # The most current closing price plotted 22 time periods behind (optional)
  chikou_span = df['close'].shift(-22)    # Given at Trading View.

  trace1 = go.Scatter(x=df.index,
                      y=tenkan_sen,
                      mode="lines",
                      showlegend=False,
                      name="Tenkan_Sen",
                      line=dict(color="orange", width=1))

  trace2 = go.Scatter(x=df.index,
                      y=kijun_sen,
                      mode="lines",
                      showlegend=False,
                      name="Kijun_Sen",
                      line=dict(width=1))

  trace3 = go.Scatter(x=df.index,
                      y=senkou_span_a,
                      mode="lines",
                      showlegend=False,
                      name="Senkou_Span_A",
                      line=dict(color="green", width=1))
  trace4 = go.Scatter(x=df.index,
                      y=senkou_span_b,
                      mode="lines",
                      showlegend=False,
                      name="Senkou_Span_B",
                      line=dict(color="red", width=1))
  trace5 = go.Scatter(x=df.index,
                      y=chikou_span,
                      mode="lines",
                      showlegend=False,
                      name="Chikou_Span",
                      line=dict(color="pink", width=1))
  # df['blue_line'] = tenkan_sen
  # df['red_line'] = kijun_sen
  # df['cloud_green_line_a'] = senkou_span_a
  # df['cloud_red_line_b'] = senkou_span_b
  # df['lagging_line'] = chikou_span
  return [trace1, trace2, trace3, trace4, trace5]


def candlestick_chart(data, pair):
  fig: FigureWidget = go.Figure(data=data)
  fig.update_layout(width=1080,
                    height=550,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f0f0f0"),
                    yaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=20, r=20, b=10, t=10),
                    uirevision=pair)
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


# Define callback for Timeframe dropdown selection
@app.callback(Output("intermediate-timeframe", "data"), [
    Input("1Min", "n_clicks"),
    Input("5Min", "n_clicks"),
    Input("30Min", "n_clicks"),
    Input("1Hour", "n_clicks")
])
def store_timeframe_dropdown_value(*_):
  ctx = dash.callback_context
  if not ctx.triggered:
    button_id = "1Min"
  else:
    button_id: str = ctx.triggered[0]['prop_id'].split('.')[0]
    # Since pandas only allow 1H interval for Hourly
    if (button_id == "1Hour"):
      button_id = "1H"
  return button_id


# Define callback for Timeframme dropdown selection
@app.callback(Output("timeframe-dropdown", "label"),
              Input("intermediate-timeframe", "data"))
def display_dynamic_timeframe_dropdown(label):
  return label


def preprocess_ohlc(df: DataFrame,
                    column=None,
                    parse_datetime=False,
                    freq="1Min"):

  if (parse_datetime == True):
    df['datetime'] = pd.to_datetime(df['datetime'])
  df_ohlc = df.reset_index().set_index('datetime')
  df_ohlc = df_ohlc[column].resample(freq).ohlc()
  return df_ohlc


# Define callback for changing trading view to different pairs
@app.callback([Output("graph", "figure"),
               Output("graph", "style")], [
                   Input("intermediate-pair", "data"),
                   Input("intermediate-pair-value-json", "data"),
                   Input("studies-checklist", "value"),
                   Input("intermediate-timeframe", "data"),
                   State("chart-interval", "n_intervals"),
               ])
def display_candlestick_by_pair(label, json_value, studies, timeframe, *_):
  ctx = dash.callback_context
  trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
  # If update
  if (trigger_id == "intermediate-pair-value-json"):
    df_closed = pd.DataFrame(json.loads(json_value))
    df_closed_ohlc = preprocess_ohlc(df_closed,
                                     column="closed_value",
                                     parse_datetime=True,
                                     freq=timeframe)
    fig = chart_factory(df=df_closed_ohlc,
                        chart_type="candlestick",
                        studies=studies,
                        pair=label)
    print("Successfully updated {} chart".format(label))
    return fig, {"margin-top": "10px", "display": "inline"}
  # If initial fetch on pair
  df_closed = kraken_utils.queryByPair(limit=6000,
                                       pair=label,
                                       col_order="datetime",
                                       sort=SortingType.DESCENDING,
                                       to_dataframe=True)
  print("=> Refresh {} chart".format(label))
  df_closed_ohlc = preprocess_ohlc(df_closed,
                                   column="closed_value",
                                   parse_datetime=True,
                                   freq=timeframe)
  fig = chart_factory(df=df_closed_ohlc,
                      chart_type="candlestick",
                      studies=studies,
                      pair=label)
  return fig, {"margin-top": "10px", "display": "inline"}


# Define callback for live-update data in a specific interval
@app.callback([
    Output("intermediate-pair-value-json", "data"),
    Output("prev-index-time", "data"),
    Output("latest-price", "data"),
    Output("ask-bid-pair", "children"),
    Output("ask-price", "children"),
    Output("bid-price", "children"),
], [
    Input("chart-interval", "n_intervals"),
    State("intermediate-pair", "data"),
    State("prev-index-time", "data")
])
def live_update_pair(n, pair, prev_time):
  if (n == 0):
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
  kraken_data = kraken_utils.queryByPair(limit=6000,
                                         pair=pair,
                                         col_order="datetime",
                                         sort=SortingType.DESCENDING,
                                         to_dataframe=False)
  if (prev_time is not None):
    if (datetime.fromisoformat(str(prev_time)) == kraken_data[0]['datetime']):
      return dash.no_update, prev_time, dash.no_update, dash.no_update, dash.no_update, dash.no_update
  print("Kraken Live Update {} of iteration no.".format(pair), n)
  prev_time = kraken_data[0]['datetime']
  last_price = kraken_data[0]['closed_value']
  last_ask_price = kraken_data[0]['ask_value']
  last_bid_price = kraken_data[0]['bid_value']
  # print(kraken_data)
  return json.dumps(
      kraken_data,
      default=str), prev_time, last_price, pair, last_ask_price, last_bid_price


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