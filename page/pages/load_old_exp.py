from dash import (
                Dash, dcc, html, Input, 
                Output, State ,callback, ALL,
                register_page,
    )
import dash_bootstrap_components as dbc


#----------------------------register--------------------------
register_page(__name__, path="/load_old",name="Estado actual")
#--------------------------------------------------------------

import page_utils

last_exp_data= page_utils.read_exp_file()






layout = html.Div([
     
    html.Div([ html.H2([ 'acá opción de de cargar un un archivo viejo y mostrar análisis como el otro?'])
        ],
        
    ),
])


# acá opción de de cargar un un archivo viejo y mostrar análisis con este?


