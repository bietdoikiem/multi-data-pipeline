from datetime import datetime
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from maindash import app
from utils.cassandrautils import AnalysisQueryUtils
import math
from utils.dateutils import format_ms_time

analysis_utils_dynamic = AnalysisQueryUtils()


def render_wc_analysis(id):
  return html.Div(children=[
      dbc.Container(children=[
          html.H2("Word Cloud ☁️"),
          html.Div(children=[
              html.Div(children=[
                  dcc.Loading(id="loading-img-dynamic",
                              children=[
                                  html.Img(id="word-cloud-analysis-img",
                                           src="",
                                           style={
                                               "height": "90vh",
                                               "margin-bottom": "10px"
                                           })
                              ])
              ],
                       style={
                           "display": "block",
                           "marginLeft": "auto",
                           "marginRight": "auto",
                           "width": "60%"
                       }),
              html.Div(children=[
                  html.H2("Analysis 📝"),
                  dcc.Loading(html.Div(id="analysis")),
                  html.I(id="datetime-analysis",
                         style={
                             "fontSize": "10px",
                             "color": "#cecece"
                         })
              ],
                       className="mt-3"),
          ]),
          dcc.Store("wc-analysis-id", data=id)
      ])
  ])


@app.callback([
    Output("analysis", "children"),
    Output("word-cloud-analysis-img", "src"),
    Output("datetime-analysis", "children")
], [Input("wc-analysis-id", "data")])
def dynamic_wc_analysis(id):
  actual_datetime = format_ms_time(datetime.fromtimestamp(float(id)))
  result = analysis_utils_dynamic.query_one_by_timestamp(key=actual_datetime)
  # print(result)
  actual_result = result[0]
  # print("URL:", actual_result['url'])
  return [
      actual_result['analysis'], actual_result['url'], "At " + actual_datetime
  ]



