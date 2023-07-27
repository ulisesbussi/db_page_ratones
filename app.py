import dash
from dash import dcc, html, Patch, Input, Output, State
import pandas as pd

import sqlite3

import time
from plotly import graph_objs as go
import plotly.io as pio

""" Aca serialize la lectura de datos (esto es importante para ulises).
este script es el encargado de crear una página para visualizar los datos
la idea, es un poco complejo porque tiene varias partes, pero con tiempo
se puede entender.

"""


#%% ----------- Funciones de utilidad personal ------------
# aca puse algunas funciones que me sirven para entender qué está pasando

_debug = True
def debug(val): #hace un print que se activa solo si la variable _debug es true
    if _debug: #esto es para ahorrame tener que sacar los prints si quiero
        #no imprimir nada
        print(val)
        
def check_db_size(): #miro el tamaño en la memoria ram de la bd.
    dfs = obtener_datos_desde_bd()
    "use special library to read dict of dataframes"
    from pympler import asizeof
    n = len(dfs['datos_0']['valor'])
    s = asizeof.asizeof(dfs)/1024/1024
    print(f"tamaño en memoria: {s}MB")
    print(f"cantidad de datos en cad df: {n}")
    print(f"estimacion mb/h:  {s*3600/n}")
    print(f"hotas de datos: {n/3600}")
        
#----------------------------------------------------------
#%% --------- funciones de procesamiento de datos ---------

def obtener_datos_desde_bd(i, n=30):
    """Lee los datos de la tabla datos_i de la bd, cargando solo una cada n filas"""
    conn = sqlite3.connect("datos_sensores.db")
    
     # Obtenemos el largo de la tabla
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM datos_{i};")
    largo_tabla = cursor.fetchone()[0]
    print(f"largo tabla {i}: {largo_tabla}")
    
    query = f"SELECT * FROM datos_{i} WHERE (rowid - 1) % {n} = 0;"  # Selecciona una cada n filas
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict()

# def obtener_datos_desde_bd(i):
#     """Leo los datos de la tabla datos_i de la bd
#     y devuelvo dict de dataFrames"""
#     conn = sqlite3.connect("datos_sensores.db")
#     df = pd.read_sql_query(f"SELECT * FROM datos_{i}", conn)  # Tablas para los canales sensor/datos_0 a sensor/datos_9
#     conn.close()
#     return df.to_dict()


def trace_from_df(df_dict,i):
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
    fig["layout"] = {"title": "Datos de Sensores",
                        "xaxis_title": "Tiempo",
                        "yaxis_title": "Valor"}
    return fig

#----------------------------------------------------------

# Configuración del intervalo de actualización
intervalo_actualizacion = 50 * 1000  # 50 segundos en milisegundos

# Crear la aplicación Dash
app = dash.Dash(__name__)


""" Esto es el esqueleto de la página. Digo que va a tener en ppio 3 partes:
1- un gradfico
2- un objeto que se va a encargar de actualizar con cierto tiempo ( una
especie de timer )
3- un botón para actualizar a mano (porque soy ansioso y no puedo esperar)
"""
app.layout = html.Div(
    [        
        dcc.Graph(id="sensor-graph", figure=create_fig()),
        dcc.Interval(id="interval-component",
                     interval=intervalo_actualizacion,
                     n_intervals=0),
        html.Button("Actualizar Gráfico",
                    id="boton-actualizar",
                    n_clicks=0),
    ]
)

""" aca vuelven a aparecer los callbacks. En este caso sobre app (la variable
que representa a la pagina web). estos de nuevo, se van a ejecutar cuando pase 
algo, ese algo se lo definimos nosotros.

La estructura de los calbacks de dash (librería para la página) es la siguiente:
declaración de variables de callback aparece @app.callback( para decir que 
lo estamos declarando, luego aparecen variables de salida del callback:
[Output("id-del-elemento", "varibale-del-elemento"),...] #los puntos porque
podrían ser más. En este caso lo que vamos a modificar con el callback
es la figura correspondiente al objeto gráfico "sensor-graph". Basicamente
vamos a cambiar lo que se muestra en el grafico.

Las variables de entrada [Input("id-del-elemento","variable-que-lo-activa"),...]
acá las variabbles que activan son basicamente partes del objeto que cambien.
En el ejemplo: "interval-component" que aumenta un contador interno "n_intervals"
cada vez que pase el tiempo programado, o 
Input("boton-actualizar", "n_clicks") que es la variable del boton que cuenta
el numero de clicks que recibió. cuando alguna de esas cosas cambie, se 
ejecutará la función asociada al callback (actualizar_grafico).

Por ultimo el callback puede tener asociado un estado, que es una variable de
entrada que voy a usar dentro de la función (por eso se la paso) pero que no
activa el callback, por ejemplo en este caso
[State("sensor-graph","figure")] Esto es porque si realizo manualmente
un cambio en el grafico en la web, quiero que me lo guarde aunque se actualicen 
los datos!

"""

# Callback para actualizar el gráfico periódicamente o al hacer clic en el botón
@app.callback([Output("sensor-graph", "figure")],
              [Input("interval-component", "n_intervals"),
               Input("boton-actualizar", "n_clicks")]
              )
def actualizar_grafico(n_intervals, 
                       n_clicks, 
                       ):
    """esta funcion se encarga de graficar, fijense que tiene 3 entradas,
    que corresponden a los 2 inputs y al state:
    n_intervals es la variable asociada al "n_intervals" del "interval-component
    ... el nombre interno de la funcion no tiene que coincidir con el externo,
    por ejemplo 'fig' es la variable que contiene a "figure" de "sensor-graph".
    """

    #1) si no hay figura creada la creo vacía
    #esto es para cuando arranca la pagina


    patched_fig = Patch()
    #para cada tabla
    for i in range(10):
        data = obtener_datos_desde_bd(i)
        this_trace = trace_from_df(data,i)
    
        #si la tabla no está vacía agrego los datos    
        if this_trace is not None:
            patched_fig["data"][i]["x"] = this_trace["x"]
            patched_fig["data"][i]["y"] = this_trace["y"]
               
    return  [patched_fig]



# # Callback para actualizar el gráfico periódicamente o al hacer clic en el botón
# @app.callback([Output("sensor-graph", "figure")],
#               [Input("interval-component", "n_intervals"),
#                Input("boton-actualizar", "n_clicks")],
#               [State("sensor-graph", "figure")]
#               )
# def actualizar_grafico(n_intervals, 
#                        n_clicks, 
#                        fig,
#                        ):
#     """esta funcion se encarga de graficar, fijense que tiene 3 entradas,
#     que corresponden a los 2 inputs y al state:
#     n_intervals es la variable asociada al "n_intervals" del "interval-component
#     ... el nombre interno de la funcion no tiene que coincidir con el externo,
#     por ejemplo 'fig' es la variable que contiene a "figure" de "sensor-graph".
#     """

#     #1) si no hay figura creada la creo vacía
#     #esto es para cuando arranca la pagina
#     if fig is None:
#         fig = go.Figure(data=[{"x": [], "y": []} for i in range(10)])
#         fig["layout"] = {"title": "Datos de Sensores",
#                         "xaxis_title": "Tiempo",
#                         "yaxis_title": "Valor"}
        

#     #para cada tabla
#     for i in range(10):
#         data = obtener_datos_desde_bd(i)
#         this_trace = trace_from_df(data,i)
    
#         #si la tabla no está vacía agrego los datos    
#         if this_trace is not None:
#             fig["data"][i]["x"] = this_trace["x"]
#             fig["data"][i]["y"] = this_trace["y"]
               
#     return  [fig]



if __name__ == "__main__":
    app.run_server(debug=True)





# %%
