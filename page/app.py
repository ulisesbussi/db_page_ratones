from dash import Dash
import dash_bootstrap_components as dbc
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
    app.run_server(host= '0.0.0.0',port=8080,debug=True,)
