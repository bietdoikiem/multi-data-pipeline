from app import make_layout
from flask_failsafe import failsafe


@failsafe
def create_app():
  from maindash import app
  app.layout = make_layout()
  return app.server


if __name__ == "__main__":
  create_app().run(host='0.0.0.0', debug=True, port=8050)