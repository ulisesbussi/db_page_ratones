from dash import (
                dcc, html, Input, 
                Output, callback,
                register_page, Patch, no_update,
    )
import dash_bootstrap_components as dbc
import pandas as pd
#import plotly
from plotly import graph_objs as go
#import time
from dash_bootstrap_templates import load_figure_template
import sqlite3

load_figure_template("cyborg")


from db_manipulation import utils as dbu

#--------------------------------register-----------------------------
register_page(__name__, path="/running",name = "Experimento actual")
#---------------------------------------------------------------------


import page_utils

#last_exp_data= page_utils.read_exp_file()

#------------------------Funciones de figuras------------------------------
#esto quizá vaya a utils después
def trace_from_df(df_dict : dict, i : int):
    """ trace es la línea que voy a poner en 
    el plot, lo creo para agregarlo"""
    df = pd.DataFrame(df_dict)
    # ~ df["dist"] = df["valor"].cumsum()
    # ~ df['tiempo'] = df['tiempo']- df['tiempo'].iloc[0]  #ver si despues se pasa a minutos o que

    if len(df):
        #df["dist"] = df["valor"].cumsum()
        df['tiempo'] = df['tiempo']- df['tiempo'].iloc[0]  #ver si despues se pasa a minutos o que
    else:
        df["distancia"] = []
    
    #df['tiempo'] = df['tiempo'].to_timestamp()
    trace = {
        "x": df["tiempo"],
        "y": df["distancia"], #df["valor"],
        "type": "scatter",
        "mode": "lines",
        "name": f"Sensor {i}",
    }
    return trace

def trace_from_df_v(df_dict : dict, i : int):
    """ trace es la línea que voy a poner en 
    el plot, lo creo para agregarlo"""
    df = pd.DataFrame(df_dict)
    # ~ df['tiempo'] = df['tiempo']- df['tiempo'].iloc[0]  #ver si despues se pasa a minutos o que
    if len(df):
    #df["dist"] = df["valor"].cumsum()
        df['tiempo'] = df['tiempo']- df['tiempo'].iloc[0]  #ver si despues se pasa a minutos o que
    else:
        df["velocidad"] = []
    # ~ #df['tiempo'] = df['tiempo'].to_timestamp()
    trace = {
        "x": df["tiempo"],
        "y": df["velocidad"],
        "type": "scatter",
        "mode": "lines",
        "name": f"Sensor {i}",
    }
    return trace

def create_fig():
    fig = go.Figure(data=[{"x": [], "y": []} for i in range(3)])
    fig["layout"] = {"title" : "Datos de Sensores",
        "xaxis_title" : "Tiempo", 
        "yaxis_title" : "Distancia"
    }
    fig.update_layout(autosize=False,width=800,height=320,
    margin=dict(l=10,r=20,b=30,t=40))
    return fig

def create_fig_v():
    
    custom_colors = ['#1f77b4' , '#ff7f0e', '#2ca02c', '#d62728' , '#9467bd' ,
                    '#8c564b' , '#e377c2' , '#7f7f7f' , '#bcbd22' , '#17becf']
                    
    fig = go.Figure(data=[{"x": [], "y": [] , "line" : {"color" : custom_colors[i %
    len(custom_colors)]}} for i in range(3)])
    fig["layout"] = {"title" : "Datos de Sensores",
        "xaxis_title" : "Tiempo", 
        "yaxis_title" : "Velocidad"
    }
    fig.update_layout(autosize=False,width=800,height=320,
    margin=dict(l=10,r=20,b=30,t=40))
    return fig
intervalo_actualiazcion = 50 * 1000  # 50 segundos en milisegundos






layout = html.Div([
    dcc.Interval(id = "interval-component",
        interval    = intervalo_actualiazcion,
        n_intervals = 0,
    ),
    dbc.Row([
      dbc.Col([
        html.Div([
            dbc.Progress(label="0%", value=0,className="progress-bar",
                         id = "barra_progreso" ,
                         animated= True, color="success",
                            ), #aca mostrar progreso
            ], className = "running-exp"),
         ],width=8),
            
      dbc.Col([
        dbc.Button("Actualizar Gráfico",
                    id="boton-actualizar",
                    n_clicks=0
                    ),
                ],width=4,className='mt-1'),
        
    ]),
    dbc.Tabs([
        dbc.Tab([
            dcc.Graph(id="sensor-graph-vel", figure=create_fig_v()),
            ], label='Velocidad',tab_id='tab_vel'),
        dbc.Tab([
            dcc.Graph(id="sensor-graph-dist", figure=create_fig()),
            ],label='Distancia',tab_id='tab_dist'),
    ], id ="card-tabs",active_tab="tab_vel",),
    
    #dcc.Graph(id="sensor-graph", figure=create_fig()),
   
    
    
])
    #mostrar número de jaulas, datos por jaulas y resumen de actividades?
    #además del plot..






#------------------------Callbacks----------------------------------------
#aca lo que vamos a hacer es una función para cada elemento
# y luego que los callbacks llamen a esas funciones, de esta forma
# podremos reutilizar las funciones después poniendolas en otro archivo
# y hacer que un mismo callback llame a varias funciones sin volvernos locos.


""" El objeto patch permite modificar una parte de un objeto
existente sin tener que redefinirlo constantemente. vamos a usar esto
para actualizar los elementos que ya existen.

"""


def calcular_porcentaje(tiempo_deseado : float, tiempo_actual : float):
    return int((tiempo_actual / tiempo_deseado) * 100)


def actualizar_grafico():
    patched_fig = Patch()
    #para cada tabla
    if last_exp_data.get("db_name") is None:
        return patched_fig
    
    for i in range(10):
        table_name =    f"datos_{i}"
        data = dbu.obtener_datos_desde_tabla(last_exp_data.get("db_name"),
                                              table_name,
                                              step = 1)
        print(f"data {data}")
        this_trace = trace_from_df(data,i)
    
        #si la tabla no está vacía agrego los datos    
        if this_trace is not None:
            patched_fig["data"][i] = this_trace
            
    return  patched_fig


def actualizar_grafico_v():
    patched_fig = Patch()
    #para cada tabla
    if last_exp_data.get("db_name") is None:
        return patched_fig
    
    for i in range(10):
        table_name =    f"datos_{i}"
        data = dbu.obtener_datos_desde_tabla(last_exp_data.get("db_name"),
                                              table_name,
                                              step = 1)
        print(f"data {data}")
        this_trace = trace_from_df_v(data,i)
    
        #si la tabla no está vacía agrego los datos    
        if this_trace is not None:
            patched_fig["data"][i] = this_trace
            
    return  patched_fig


@callback([Output("sensor-graph-vel", "figure"),
            Output("sensor-graph-dist", "figure")],
              [Input("interval-component", "n_intervals"),
                Input("boton-actualizar", "n_clicks")],
               prevent_initial_call = True
    )
def refresh(n_intervals, 
                        n_clicks, 
                        ):
    
    global last_exp_data
    "esta funcion refresca la página"
    last_exp_data = page_utils.read_exp_file()
    if last_exp_data.get("Running") is None:
        patched_fig = actualizar_grafico()
        patched_fig1 = actualizar_grafico_v()
        return  patched_fig1, patched_fig    
    return create_fig_v(),create_fig()


# Actualiza el porcentaje de la barra de progreso
@callback(
    Output("barra_progreso", "value"),
    Output("barra_progreso", "label"),
    Input("interval-component", "n_intervals"),
    Input("boton-actualizar", "n_clicks"),
    prevent_initial_call = True
)

def actualizar_progreso(n_intervals, n_clicks):
    global last_exp_data
    last_exp_data= page_utils.read_exp_file()
    if last_exp_data.get("Running") is None:
        # Conecta a la base de datos
        conn = sqlite3.connect(last_exp_data.get("db_name"))  # Cambia "nombre_de_tu_base_de_datos.db" al nombre de tu base de datos
    
    # Crea un cursor
        cursor = conn.cursor()
    
    # Ejecuta la consulta SQL para obtener el tiempo actual y tiempo total
        cursor.execute("SELECT tiempo_deseado, tiempo_actual FROM estado_programa")
    
    # Obtén el resultado de la consulta
        result = cursor.fetchone()
    
    # Cierra la conexión a la base de datos
        conn.close()
        tiempo_deseado, tiempo_actual = result
        porcentaje = calcular_porcentaje(tiempo_deseado, tiempo_actual)
        return [porcentaje,f"{porcentaje}%"]
    return [0,"0%"]










