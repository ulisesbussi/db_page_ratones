from dash import (
                Dash, dcc, html, Input, 
                Output, State ,callback, ALL,
                register_page,
    )
import dash_bootstrap_components as dbc


#---------------------------register--------------------------------
register_page(__name__, path="/to_csv",name='Exportar a csv')
#-------------------------------------------------------------------


import page_utils
last_exp_data= page_utils.read_exp_file()





""" en to_csv.py hay un script que hace la conversión habría que construirlo
como una página.
"""
layout = html.Div([
     
    html.Div([ html.H2([ 'aca como convertir la base de datos a archivos csv'])
        ],
        
    ),
])

