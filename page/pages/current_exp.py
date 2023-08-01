from dash import (
                Dash, dcc, html, Input, 
                Output, State ,callback, ALL,
                register_page, Patch,
    )
import dash_bootstrap_components as dbc
import pandas as pd
from plotly import graph_objs as go
from dash_bootstrap_templates import load_figure_template

load_figure_template("cyborg")


from db_manipulation import utils as dbu

#--------------------------------register-----------------------------
register_page(__name__, path="/running",name = "Experimento actual")
#---------------------------------------------------------------------


import page_utils

last_exp_data= page_utils.read_exp_file()

#------------------------Funciones de figuras------------------------------
#esto quizá vaya a utils después
def trace_from_df(df_dict : dict, i : int):
    """ trace es la línea que voy a poner en 
    el plot, lo creo para agregarlo"""
    df = pd.DataFrame(df_dict)
    trace = {
        "x": df["tiempo"],
        "y": df["valor"],
        "type": "scatter",
        "mode": "lines",
        "name": f"Sensor {i}",
    }
    return trace

def create_fig():
    fig = go.Figure(data=[{"x": [], "y": []} for i in range(10)])
    fig["layout"] = {"title" : "Datos de Sensores",
        "xaxis_title" : "Tiempo", 
        "yaxis_title" : "Valor"
    }
    return fig

intervalo_actualiazcion = 50 * 1000  # 50 segundos en milisegundos





layout = html.Div([
    dcc.Interval(id = "interval-component",
        interval    = intervalo_actualiazcion,
        n_intervals = 0,
    ),
    html.Div([
        dbc.Progress(label="25%", value=25,className="progress-bar",
                     animated= True, color="success",
                     ), #aca mostrar progreso
        ],
        className = "running-exp"
    ),
    
    dcc.Graph(id="sensor-graph", figure=create_fig()),
    dbc.Button("Actualizar Gráfico",
        id="boton-actualizar",
        n_clicks=0
    ),
    
    
])
    #mostrar número de jaulas, datos por jaulas y resumen de actividades?
    #además del plot..






#------------------------Callbacks----------------------------------------
#aca lo que vamos a hacer es una función para cada elemento
# y luego que los callbacks llamen a esas funciones, de esta forma
# podremos reutilizar las funciones después poniendolas en otro archivo
# y hacer que un mismo callback llame a varias funciones sin volvernos locos.


""" El objeto patch eprmite modificar una parte de un objeto
existente sin tener que redefinirlo constantemente. vamos a usar esto
para actualizar los elementos que ya existen.

"""




def actualizar_grafico():
    patched_fig = Patch()
    #para cada tabla
    if last_exp_data.get("db_name") is None:
        return patched_fig
    
    for i in range(10):
        table_name = f"datos_{i}"
        data = dbu.obtener_datos_desde_tabla(last_exp_data.get("db_name"),
                                             table_name,
                                             step = 300)
        this_trace = trace_from_df(data,i)
    
        #si la tabla no está vacía agrego los datos    
        if this_trace is not None:
            patched_fig["data"][i]["x"] = this_trace["x"]
            patched_fig["data"][i]["y"] = this_trace["y"]
               
    return  patched_fig




@callback(Output("sensor-graph", "figure"),
              [Input("interval-component", "n_intervals"),
               Input("boton-actualizar", "n_clicks")]
    )
def refresh(n_intervals, 
                       n_clicks, 
                       ):
    "esta funcion refresca la página"

    patched_fig = actualizar_grafico()
    return  patched_fig












