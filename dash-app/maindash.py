import dash
import dash_bootstrap_components as dbc

FA = "https://use.fontawesome.com/releases/v5.12.1/css/all.css"

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, FA],
                update_title=None,
                suppress_callback_exceptions=True)
