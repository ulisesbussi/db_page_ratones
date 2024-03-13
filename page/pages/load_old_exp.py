from dash import (
                dcc, html, Input, 
                Output,callback,
                register_page,
    )
import dash_bootstrap_components as dbc    
import os
import sqlite3
import page_utils
import pandas as pd
from plotly import graph_objs as go
from db_manipulation import utils as dbu
from dash_bootstrap_components import Modal, ModalHeader, ModalBody, ModalFooter
#----------------------------register--------------------------
register_page(__name__, path="/load_old",name="Experimentos anteriores")
#--------------------------------------------------------------
last_exp_data= page_utils.read_exp_file()


carpeta_archivos = "/home/raspberryunq/db_page_ratones-main/dbs"

def obtener_datos_desde_bd(name :str ):
    """Leo los datos de la base de datos y devuelvo dict de dataFrames"""
    conn = sqlite3.connect(name)
    dfs = {}
    for i in range(10):
        try:
            df = pd.read_sql_query(f"SELECT * FROM datos_{i}", conn)  # Tablas para los canales sensor/datos_0 a sensor/datos_9
            dfs[f"datos_{i}"] = df.to_dict()
        except:
            break
    conn.close()
    return dfs

def trace_from_df(df_dict : dict, i : int):
    """ trace es la línea que voy a poner en 
    el plot, lo creo para agregarlo"""
    df = pd.DataFrame(df_dict)
    #df["dist"] = df["valor"].cumsum()
    df['tiempo'] = df['tiempo']- df['tiempo'].iloc[0]  #ver si despues se pasa a minutos o que
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
    #df["dist"] = df["valor"].cumsum()
    df['tiempo'] = df['tiempo']- df['tiempo'].iloc[0]  #ver si despues se pasa a minutos o que
    #df['tiempo'] = df['tiempo'].to_timestamp()
    trace = {
        "x": df["tiempo"],
        "y": df["velocidad"],
        "type": "scatter",
        "mode": "lines",
        "name": f"Sensor {i}",
    }
    return trace

def create_fig():
    fig = go.Figure(data=[{"x": [], "y": []} for i in range(2)])
    fig["layout"] = {"title" : "Datos de Sensores",
        "xaxis_title" : "Tiempo", 
        "yaxis_title" : "Distancia"
    }
    fig.update_layout(autosize=False,width=800,height=375,
    margin=dict(l=10,r=20,b=30,t=40))
    return fig
    
def create_fig_v():
    fig = go.Figure(data=[{"x": [], "y": []} for i in range(2)])
    fig["layout"] = {"title" : "Datos de Sensores",
        "xaxis_title" : "Tiempo", 
        "yaxis_title" : "Velocidad"
    }
    fig.update_layout(autosize=False,width=800,height=375,
    margin=dict(l=10,r=20,b=30,t=40))
    return fig

layout = html.Div([
    dcc.Interval(
        id='interval-comp',
        interval=30 * 1000,  # Actualizar cada 30 segundos
        n_intervals=0
    ),
    html.Div([
        dcc.Dropdown(
            id='db-dropdown',
            options=[],
            value=None,
            placeholder='Selecciona un archivo de base de datos',
        ),
        dbc.Tabs([
        dbc.Tab([
            dcc.Graph(id="sensor-graph-vel_old", figure=create_fig_v()),
            ], label='Velocidad',tab_id='tab_vel_old'),
        dbc.Tab([
            dcc.Graph(id="sensor-graph-dist_old", figure=create_fig()),
            ],label='Distancia',tab_id='tab_dist_old'),
    ], id ="card-tabs_old",active_tab="tab_vel_old",),
       #dcc.Graph(id="selected-graph", figure=create_fig()),
    ]),
])


@callback(
    Output('db-dropdown', 'options'),
    Input('interval-comp', 'n_intervals')
)
def update_dropdown_options(n):
    archivos_en_carpeta = [archivo for archivo in os.listdir(carpeta_archivos) if archivo.endswith(".db")]
    #archivos_en_carpeta.sort()
    archivos_ordenados = sorted(archivos_en_carpeta,key = lambda archivo:os.path.getmtime(os.path.join(carpeta_archivos, archivo)), reverse=True)
    dropdown_options = [{'label': archivo, 'value': archivo} for archivo in archivos_ordenados]
    return dropdown_options

@callback(
            [Output("sensor-graph-vel_old", "figure"),
            Output("sensor-graph-dist_old", "figure")],
            Input("db-dropdown", "value"),
              )
def load_graph(value):
    if value is None:
        return create_fig_v(), create_fig()
    value=value.replace(".db","")
    patched_fig_v = create_fig_v()
    patched_fig = create_fig()

    for i in range(10):
       table_name = f"datos_{i}"
       data = dbu.obtener_datos_desde_tabla(os.path.join(carpeta_archivos, f"{value}.db"), table_name, step=1)
       this_trace = trace_from_df(data, i)
       this_trace_v = trace_from_df_v(data, i)
        # Si la tabla no está vacía, agrego los datos
       if this_trace is not None and this_trace_v:
            patched_fig.add_trace(this_trace)
            patched_fig_v.add_trace(this_trace_v)

    return  patched_fig_v, patched_fig
"""  hemos creado un dropdown (dbdropdown) que permite
  a los usuarios seleccionar un archivo de base de datos.
  Cuando un archivo se selecciona en el dropdown, el callback load_graph
  se activa y se encarga de conectarse a la base de datos, obtener los 
  datos y crear un gráfico correspondiente."""
