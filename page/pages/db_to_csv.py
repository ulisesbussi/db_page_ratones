from dash import (
                Dash, dcc, html, Input, 
                Output, State ,callback, ALL,
                register_page,
    )
import pandas as pd
import dash_bootstrap_components as dbc
import os
import sqlite3
#---------------------------register--------------------------------
register_page(__name__, path="/to_csv",name='Exportar a csv')
#-------------------------------------------------------------------


import page_utils
last_exp_data= page_utils.read_exp_file()

def obtener_datos_desde_bd(name :str ):
    """Leo los datos de la base de datos y devuelvo dict de dataFrames"""
    conn = sqlite3.connect(name)
    dfs = {}
    for i in range(2):
        df = pd.read_sql_query(f"SELECT * FROM datos_{i}", conn)  # Tablas para los canales sensor/datos_0 a sensor/datos_9
        dfs[f"datos_{i}"] = df.to_dict()
    conn.close()
    return dfs

carpeta_archivos = "\\Users\\alefermatulu\\Documents\\Lucas\\db_page_ratones-main\\dbs"

# Obtener la lista de archivos en la carpeta
archivos_en_carpeta = [archivo for archivo in os.listdir(carpeta_archivos) if archivo.endswith(".db")]

#opcion_inicial = archivos_en_carpeta[0] if archivos_en_carpeta else "No hay bases de datos"




""" en to_csv.py hay un script que hace la conversión habría que construirlo
como una página.
"""
layout = dbc.Container([
    html.H1("Conversor de Archivos", className="mt-4"),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='dropdown-archivos',
                options=[{'label': archivo, 'value': archivo} for archivo in archivos_en_carpeta],
                #value=opcion_inicial,
                clearable=False , 
                # Evita que el usuario pueda borrar la opción predeterminada
                placeholder="Seleccione un archivo"
            ),
            width=6
        ),
        dbc.Col(
            dbc.Button('Convertir',
                       id='boton-convertir',
                       n_clicks=0,
                       color="primary",
                       className="ml-2 btn"),
            width=2
        ),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='mensaje-convertido', className="mt-3")),
    ]),
], className="mt-3")


@callback(
    Output('mensaje-convertido', 'children'),
    [Input('boton-convertir', 'n_clicks')],
    [State('dropdown-archivos', 'value')],
    prevent_initial_call=True
)
def convertir_archivo(n_clicks, archivo_seleccionado):
    if n_clicks is None:
        return ""

    if archivo_seleccionado ==  None:
        return "Seleccione un archivo válido antes de convertir."
    else:
        output_folder =r'C:\Users\alefermatulu\Documents\Lucas\db_page_ratones-main\out_csv'
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        
        dfs = obtener_datos_desde_bd(os.path.join(carpeta_archivos,archivo_seleccionado))
        n=archivo_seleccionado.replace(".db", "")+"_"
        for f,d in dfs.items():
            csv_filename = os.path.join(output_folder,n + f + '.csv')
            pd.DataFrame(d).to_csv(csv_filename,index=False)
        mensaje = f"Archivo '{archivo_seleccionado}' convertido exitosamente."
        return mensaje
