from dash import Dash, html
import dash_bootstrap_components as dbc
import webbrowser
from dash_bootstrap_templates import load_figure_template
import page_utils

last_exp_data= page_utils.read_exp_file()
last_exp_data["Running"] = 578
app = Dash(__name__,
           use_pages=True, 
           external_stylesheets=[dbc.themes.SLATE, '/assets/style.css'],
           
           #suppress_callback_exceptions=True)
        )
from layout import get_layout #esto tiene que ir si o si después de definir
#la app




app.layout = get_layout()


if __name__ == '__main__':
    #webbrowser.open('http://127.0.0.1:8080/')
    #comente esto el 12 dic 2023 (ulises)
    app.run_server(port=8080,debug=True, host= '0.0.0.0')
