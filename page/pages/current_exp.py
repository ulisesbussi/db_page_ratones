from dash import (
                Dash, dcc, html, Input, 
                Output, State ,callback, ALL,
                register_page,
    )
import dash_bootstrap_components as dbc

#--------------------------------register-----------------------------
register_page(__name__, path="/running",name = "Experimento actual")
#---------------------------------------------------------------------


#from .utils import read_exp_fil, write_exp_file
import page_utils

last_exp_data= page_utils.read_exp_file()






layout = html.Div([
     
    html.Div([
        dbc.Progress( 0.95), #aca mostrar progreso
        ],
        className = "running-exp"
    ),
    
    #mostrar número de jaulas, datos por jaulas y resumen de actividades?
    #además del plot..
    
])