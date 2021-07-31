from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_html_components.H2 import H2
from maindash import app
import json
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO
import base64
from utils.cassandrautils import CryptoPanicQueryUtils
import os
from datetime import datetime
import boto3

# Setup query tool for CryptoPanic
cryptopanic_utils_analysis = CryptoPanicQueryUtils()
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
                  dbc.InputGroup(
                      [
                          dbc.Textarea(placeholder="Type your analysis here...",
                                       style={"height": "300px"}),
                          dbc.InputGroupAddon(
                              children=[dbc.Button("Submit", color="dark")],
                              addon_type="append")
                      ],
                      className="mb-3",
                  )
              ],
                       className="mt-3"),
          ]),
          dcc.Store(id="all-cryptopanic-data"),
          dcc.Interval(
              "all-cryptopanic-interval", interval=3600 * 1000, n_intervals=0)
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


@app.callback(Output("word-cloud", "src"), [
    Input("all-cryptopanic-data", "data"),
])
def draw_word_cloud_news(json_data):
  data = json.loads(json_data)
  all_titles = " ".join([sub_data['title'] for sub_data in data])
  clean_titles = " ".join(all_titles.split()).lower()
  # print(clean_titles)
  word_cloud = wc.generate(clean_titles)
  # Save the file to temporatory folder before loading to S3 Bucket
  # image_name = f"word-cloud-{current_timestamp}.png"
  # wc.to_file(os.path.join(dirname, f'../s3-temp/{image_name}'))
  # Save temp file to AWS S3

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
  data = open(os.path.join(dirname, f'../s3-temp/{img_name}'), 'rb')
  s3.Bucket(bucket_name).put_object(Key=img_name, Body=data)
  print("=> Done uploading to AWS S3.")