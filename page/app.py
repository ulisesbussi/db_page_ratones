from dash import Dash
import dash_bootstrap_components as dbc
#import page_utils 
import webbrowser
#last_exp_data= page_utils.read_exp_file()
#last_exp_data["Running"] = 578
#page_utils.write_exp_file(last_exp_data)

app = Dash(__name__,
           use_pages=True, 
           external_stylesheets=[dbc.themes.SLATE, '/assets/style.css'],
           
           #suppress_callback_exceptions=True)
        )
from layout import get_layout #esto tiene que ir si o si después de definir
#la app

app.layout = get_layout()


if __name__ == '__main__':
    #app.run_server(host= '0.0.0.0',port=8080,debug=True,)
    # Abre el navegador web con el enlace a la página
    webbrowser.open( 'http://127.0.0.1:8080/')  # Cambia la URL según sea necesario
    #app.run_server(port=8080,debug=True, use_reloader=False)
    app.run_server(port=8080,debug=True,)
