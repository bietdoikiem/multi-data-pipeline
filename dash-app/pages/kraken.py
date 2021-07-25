from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from maindash import app
import dash
from plotly import graph_objects as go
from plotly.missing_ipywidgets import FigureWidget
import pandas as pd

currency_pairs = ["XBT/USD", "ETH/USD"]

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
)


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
                                       dbc.DropdownMenuItem(
                                           id="XBT/USD-pair",
                                           children="XBT/USD",
                                           className="dropdown-item"),
                                       dbc.DropdownMenuItem(id="ETH/USD-pair",
                                                            children="ETH/USD")
                                   ]),
                  dcc.Graph(id="graph", style={"margin-top": "10px"}, config={'displayModeBar': False}),
                  dcc.Store(id='intermediate-pair-value')
              ],
                       className="inner-box"),
          ],
                   className="col-elem")
      ],
              width=7),
      dbc.Col([html.Div(["Bid/Ask View"], className="col-elem")], width=2)
  ],
                 no_gutters=True)


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


@app.callback(Output("graph", "figure"),
              [Input("intermediate-pair-value", "data")])
def display_candlestick_by_pair(label):
  if label == "XBT/USD":
    fig: FigureWidget = go.Figure(data=[
        go.Candlestick(x=df['Date'],
                       open=df['AAPL.Open'],
                       high=df['AAPL.High'],
                       low=df['AAPL.Low'],
                       close=df['AAPL.Close'])
    ])
  elif label == "ETH/USD":
    fig: FigureWidget = go.Figure(data=[
        go.Candlestick(x=df['Date'],
                       open=df['AAPL.Open'],
                       high=df['AAPL.High'],
                       low=df['AAPL.Low'],
                       close=df['AAPL.Close'],
                       increasing_line_color='cyan',
                       decreasing_line_color='gray')
    ])
  fig.update_layout(width=1100,
                    height=700,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#f0f0f0"),
                    yaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis=dict(gridcolor="rgba(72, 72, 72, 1)"),
                    xaxis_rangeslider_visible=False
                    )

  return fig
