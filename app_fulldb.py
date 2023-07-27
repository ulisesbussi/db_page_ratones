import dash
from dash import dcc, html
import pandas as pd
import sqlite3
from dash.dependencies import Input, Output, State
import time
from plotly import graph_objs as go
import plotly.io as pio

#%% ----------- Funciones de utilidad personal ------------
_debug = True
def debug(val):
    if _debug:
        print(val)
def check_db_size():
    dfs = obtener_datos_desde_bd()
    "use special library to read dict of dataframes"
    from pympler import asizeof
    n = len(dfs['datos_0']['valor'])
    s = asizeof.asizeof(dfs)/1024/1024
    print(f"tamaño en memoria: {s}MB")
    print(f"cantidad de datos en cad df: {n}")
    print(f"estimacion mb/h:  {s*3600/n}")
    
        
#----------------------------------------------------------
#%% --------- funciones de procesamiento de datos ---------

def obtener_datos_desde_bd():
    """Leo los datos de la base de datos y devuelvo dict de dataFrames"""
    conn = sqlite3.connect("datos_sensores.db")
    dfs = {}
    for i in range(10):
        df = pd.read_sql_query(f"SELECT * FROM datos_{i}", conn)  # Tablas para los canales sensor/datos_0 a sensor/datos_9
        dfs[f"datos_{i}"] = df.to_dict()
    conn.close()
    return dfs

def traces_from_dfs(dfs_dict):
    traces = []
    for i in range(10):
        df = pd.DataFrame(dfs_dict[f"datos_{i}"])
        #if estado_lineas[f"datos_{i}"]:  # Verificar si la línea está habilitada o deshabilitada
        trace = {
            "x": df["tiempo"],
            "y": df["valor"],
            "type": "scatter",
            "mode": "lines",
            "name": f"Sensor {i}",
        }
        traces.append(trace)
    return traces
#----------------------------------------------------------

init_data = obtener_datos_desde_bd()
# Configuración del intervalo de actualización
intervalo_actualizacion = 50 * 1000  # 50 segundos en milisegundos

# Crear la aplicación Dash
app = dash.Dash(__name__)


app.layout = html.Div(
    [
        
        dcc.Graph(id="sensor-graph"),
        dcc.Store(id="dbs-store",data=init_data),
        dcc.Interval(id="interval-component",
                     interval=intervalo_actualizacion,
                     n_intervals=0),
        html.Button("Actualizar Gráfico",
                    id="boton-actualizar",
                    n_clicks=0),
    ]
)

#Callback actualizar dbs-store
@app.callback([Output("dbs-store", "data")],
              [Input("interval-component", "n_intervals"),
               Input("boton-actualizar", "n_clicks")],
              )
def actualizar_db(n_intervals,n_clicks):
    dbs = obtener_datos_desde_bd()
    return [dbs]



# Callback para actualizar el gráfico periódicamente o al hacer clic en el botón
@app.callback([Output("sensor-graph", "figure")],
              [Input("interval-component", "n_intervals"),
               Input("boton-actualizar", "n_clicks")],
              [State("sensor-graph", "figure"),
               State("dbs-store", "data")])
def actualizar_grafico(n_intervals, 
                       n_clicks, 
                       fig,
                       data):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]


    traces = traces_from_dfs(data)
    if traces is None:
        return [fig]
    #print(traces)
    if fig is None:
        fig = go.Figure(data=traces)
        fig["layout"] = {"title": "Datos de Sensores",
                        "xaxis_title": "Tiempo",
                        "yaxis_title": "Valor"}
    else:
        for idx,t in enumerate(traces):
            fig["data"][idx]["x"] = t["x"]
            fig["data"][idx]["y"] = t["y"]

    return  [fig]



if __name__ == "__main__":
    app.run_server(debug=True)




