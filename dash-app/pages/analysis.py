from dash.dependencies import Input, Output
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
from utils.cassandrautils import CryptoPanicQueryUtils
import os

cryptopanic_utils_analysis = CryptoPanicQueryUtils()
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../assets/btc-mask.png')
# Setup WordCloud pre-requirements
bitcoin_mask = np.array(Image.open(filename))
stopwords = set(STOPWORDS)
stopwords.add("said")
wc = WordCloud(background_color="white",
               max_words=2000,
               mask=bitcoin_mask,
               stopwords=stopwords,
               contour_width=3,
               contour_color='steelblue')


def render_analysis():
  return html.Div(children=[
      dbc.Container(children=[
          html.H2("Word Cloud"),
          html.Div(children=[html.Img(id="word-cloud")]),
          dcc.Store(id="all-cryptopanic-data"),
          dcc.Interval(
              "all-cryptopanic-interval", interval=1800 * 1000, n_intervals=0)
      ])
  ])


#### CryptoPanic Utility functions & callbacks ####
def all_news(top: str = 200):
  print("=> All News fetching...")
  return cryptopanic_utils_analysis.query(limit=top)


@app.callback(Output("all-cryptopanic-data", "data"),
              Input("all-cryptopanic-interval", "n_intervals"))
def live_update_news(n):
  news_data = all_news(200)
  if (n > 0):
    print("All News Live Update no.", n)
  else:
    print("Initial CryptoPanic fetch!")
  # print(news_data, flush=True)
  return json.dumps(news_data, default=str)


# FIXME: ERROR embedding wordcloud images to web
# @app.callback([Output("word-cloud", "src")],
#               [Input("all-cryptopanic-data", "data")])
# def draw_word_cloud_news(json_data):
#   data = json.loads(json_data)
#   all_titles = " ".join([sub_data['title'] for sub_data in data])
#   word_cloud = wc.generate(all_titles)
#   img = BytesIO()
#   word_cloud.to_image().save(img, format='PNG')
#   return 'data:image/png;base64,{}'.format(
#       base64.b64encode(img.getvalue()).decode())
