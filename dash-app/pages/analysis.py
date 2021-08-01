import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from maindash import app
import json
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO
import base64
from utils.cassandrautils import CryptoPanicQueryUtils, AnalysisQueryUtils, SortingType
import os
from datetime import datetime
import boto3

# Setup query tool for CryptoPanic
cryptopanic_utils_analysis = CryptoPanicQueryUtils()
analysis_utils = AnalysisQueryUtils()
# Path to wordcloud mask image
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../assets/btc-mask.png')
# Setup WordCloud pre-requirements
bitcoin_mask = np.array(Image.open(filename))
stopwords = set(STOPWORDS)
stopwords.add("said")
stopwords.add("will")
stopwords.add("u")
stopwords.add("s")

wc = WordCloud(width=1200,
               height=700,
               background_color="white",
               max_words=1000,
               mask=bitcoin_mask,
               stopwords=stopwords,
               contour_width=3,
               contour_color='steelblue')
# Setup S3 client
s3 = boto3.resource('s3')
BUCKET_NAME = "dash-asm-bucket"
BUCKET_REGION = "us-east-2"


def render_analysis():
  return html.Div(children=[
      dbc.Container(children=[
          html.H2("Word Cloud ☁️"),
          html.Div(children=[
              html.Div(children=[
                  dcc.Loading(id="loading-img",
                              children=[
                                  html.Img(id="word-cloud",
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
                  html.H2("Analysis ✒️"),
                  dcc.Loading(
                      dbc.InputGroup(
                          [
                              dbc.Textarea(
                                  id="analysis-text",
                                  placeholder="Type your analysis here...",
                                  style={"height": "200px"},
                                  value=""),
                              dbc.InputGroupAddon(children=[
                                  dbc.Button(id="submit-analysis",
                                             children="Submit",
                                             color="dark")
                              ],
                                                  addon_type="append")
                          ],
                          className="mb-3",
                      ))
              ],
                       className="mt-3"),
              html.Div(children=[
                  html.H2("History 📜"),
                  dcc.Loading(id="history-loading",
                              children=dbc.Card(dbc.ListGroup(
                                  id="history-list-container", flush=True),
                                                color="rgba(72, 72, 72, 1)")),
              ],
                       className="mt-3"),
          ]),
          dcc.Store(id="all-cryptopanic-data"),
          dcc.Store(id="last-submission"),
          dcc.Store(id="last-submission-modal"),
          dcc.Store(id="history-data"),
          dbc.Button(id="invisible-history-load",
                     n_clicks=0,
                     style={"display": "none"}),
          dcc.Interval(
              "all-cryptopanic-interval", interval=3600 * 1000, n_intervals=0),
          dbc.Modal([
              dbc.ModalHeader("XtremeOLAP"),
              dbc.ModalBody("Saved analysis for Wordcloud successfully! ✍️"),
              dbc.ModalFooter(
                  dbc.Button("Close",
                             id="close-sm",
                             className="ml-auto",
                             n_clicks=0,
                             color="dark")),
          ],
                    id="modal-sm",
                    size="sm",
                    is_open=False,
                    style={"color": "#000000"}),
      ])
  ])


#### CryptoPanic Utility functions & callbacks ####
def all_news(top: str = 1000):
  return cryptopanic_utils_analysis.query(limit=top,
                                          categories=["news", "media"])


@app.callback(Output("all-cryptopanic-data", "data"),
              Input("all-cryptopanic-interval", "n_intervals"))
def live_update_news(_):
  news_data = all_news(1000)
  print("All CryptoPanic news and media fetched!")
  # print(news_data, flush=True)

  return json.dumps(news_data, default=str)


# Submit Analysis callback
@app.callback([
    Output("last-submission", "data"),
    Output("last-submission-modal", "data")
], [Input("submit-analysis", "n_clicks"),
    State("analysis-text", "value")])
def submit_analysis_wordcloud(n_clicks, analysis_text):
  if (n_clicks is not None and n_clicks > 0):
    print("=> Saving analysis...")
    saved_filename = save_wordcloud_png(wc)
    result = s3_upload_wordcloud(img_name=saved_filename,
                                 bucket_name="dash-asm-bucket")
    url = f'https://{BUCKET_NAME}.s3.{BUCKET_REGION}.amazonaws.com/{saved_filename}'
    if (result):
      analysis_utils.insert_one({
          "datetime": datetime.utcnow(),
          "category": "wordcloud",
          "analysis": analysis_text,
          "url": url
      })
      print("Sample added to database")
    return [analysis_text, True]
  return dash.no_update, dash.no_update


@app.callback(Output("word-cloud", "src"), [
    Input("all-cryptopanic-data", "data"),
])
def draw_word_cloud_news(json_data):
  data = json.loads(json_data)
  all_titles = " ".join([sub_data['title'] for sub_data in data])
  clean_titles = " ".join(all_titles.split()).lower()
  word_cloud = wc.generate(clean_titles)
  # Encode base64 image for direct presentation on website
  img = BytesIO()
  word_cloud.to_image().save(img, format='PNG')
  return 'data:image/png;base64,{}'.format(
      base64.b64encode(img.getvalue()).decode())


# WC Utils
def save_wordcloud_png(wc: WordCloud):
  current_timestamp: float = datetime.utcnow().timestamp()
  # Save the file to temporatory folder before loading to S3 Bucket
  img_name = f"word-cloud-{current_timestamp}.png"
  wc.to_file(os.path.join(dirname, f'../s3-temp/{img_name}'))
  return img_name


# S3 Utils
def s3_upload_wordcloud(img_name, bucket_name):
  try:
    data = open(os.path.join(dirname, f'../s3-temp/{img_name}'), 'rb')
    s3.Bucket(bucket_name).put_object(Key=img_name, Body=data)
    print("=> Done uploading to AWS S3.")
  except Exception as error:
    print(error)
    print("FAILED!")
    return False
  return True


def toggle_success_modal(n1, n2, is_open):
  if n1 or n2:
    return not is_open
  return is_open


def query_all_analysis_report(limit=10):
  data = analysis_utils.query(limit=limit,
                              sort=SortingType.DESCENDING,
                              col_order="datetime",
                              categories=["wordcloud"])
  # print(data)
  return data


@app.callback(Output("history-data", "data"), [
    Input("invisible-history-load", "n_clicks"),
    Input("last-submission", "data")
])
def initial_history_load(n, last_submission_data):
  ctx = dash.callback_context
  trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
  if (trigger_id == "invisible-history-load"):
    if (n == 0):
      return json.dumps(query_all_analysis_report(limit=100), default=str)
  print("Updated since last submission!")
  return json.dumps(query_all_analysis_report(limit=100), default=str)


@app.callback([Output("history-list-container", "children")],
              Input("history-data", "data"))
def generate_link_buttons(json_data):
  history_data = json.loads(json_data)
  return [[create_link_button(history_obj) for history_obj in history_data]]


def create_link_button(history_obj):
  return dcc.Link(
      dbc.ListGroupItem(dcc.Markdown(f'''
  WordCloud analysis at _{history_obj['datetime']}_
  '''),
                        color="#000000",
                        style={
                            "border-width": "0.5px",
                            "border-color": "rgba(72, 72, 72, 1)",
                        }),
      href=
      f"/analysis/wordcloud/{datetime.strptime(history_obj['datetime'], '%Y-%m-%d %H:%M:%S.%f').timestamp()}",
      target='_blank')


app.callback(
    Output("modal-sm", "is_open"),
    [Input("last-submission-modal", "data"),
     Input("close-sm", "n_clicks")],
    [State("modal-sm", "is_open")])(toggle_success_modal)
