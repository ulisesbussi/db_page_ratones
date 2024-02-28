from dash import (
                dcc, html, Input, 
                Output, State ,callback,
                register_page, no_update
    )
import pandas as pd
import dash_bootstrap_components as dbc
import os
import sqlite3
import datetime
#---------------------------register--------------------------------
register_page(__name__, path="/to_csv",name='Exportar o Eliminar')
#-------------------------------------------------------------------


import page_utils
last_exp_data= page_utils.read_exp_file()
#def convert_timestamp(ts):
#    return datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')#('%Y-%m-%d %H:%M:%S.%f')
def convert_timestamp(df):
    df['tiempo']= pd.to_datetime((df.tiempo-df.tiempo[0])*1e9).dt.strftime('%m-%d %H:%M:%S:%f')
    return df

def obtener_datos_desde_bd(name :str ):
    """Leo los datos de la base de datos y devuelvo dict de dataFrames"""
    conn = sqlite3.connect(name)
    dfs = {}
    for i in range(50):
        try: 
            df = pd.read_sql_query(f"SELECT * FROM datos_{i}", conn)  # Tablas para los canales sensor/datos_0 a sensor/datos_9
            #df['tiempo'] = df ['tiempo'].apply(convert_timestamp)
            df = convert_timestamp(df)
            dfs[f"datos_{i}"] = df.to_dict()
        except pd.errors.DatabaseError:
            break #rompo for
       
    conn.close()
    return dfs
def obtener_carpeta_pendrive():
    base_dir = '/media/raspberryunq'
    dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir,d))]
    if dirs:
        first_dir = dirs[0]
        pendrive_dir = os.path.join(base_dir,first_dir)+'/Ratones'
        return pendrive_dir
    else: 
        return None
carpeta_archivos = "/home/raspberryunq/db_page_ratones-main/dbs"

# Obtener la lista de archivos en la carpeta
#archivos_en_carpeta = [archivo for archivo in os.listdir(carpeta_archivos) if archivo.endswith(".db")]

#opcion_inicial = archivos_en_carpeta[0] if archivos_en_carpeta else "No hay bases de datos"




""" en to_csv.py hay un script que hace la conversión habría que construirlo
como una página.
"""
layout = dbc.Container([
    html.H1("Conversor y Eliminador de Archivos", className="mt-4"),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # Actualizar cada 60 segundos
        n_intervals=0
    ),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='dropdown-archivos',
                options=[],
                clearable=False,
                placeholder="Seleccione un archivo"
            ),
            width=6
        ),
        dbc.Col(
            dbc.Button('Convertir',
                       id='boton-convertir',
                       n_clicks=0,
                       color="primary",
                       className="ml-2 btn"
            ),
            width=2
        ),
    ]),
    dbc.Row([
        dbc.Col(html.Div(id='mensaje-convertido', className="mt-3")),
    ]),
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='dropdown-archivos-borrar',
                options=[],
                multi=True,
                placeholder="Seleccione un archivo a borrar",
                style={'color':'red'}
            ),
            width=6
        ),
        dbc.Col(
            dbc.Button('Borrar',
                        id='boton-borrar',
                        n_clicks=0,
                        color="danger",
                        className="ml-2 btn"),
            width=2
        ),
    ]),
    #Modal de confirmacion
    dbc.Modal(
        [
            dbc.ModalHeader("Confirmación"),
            dbc.ModalBody("¿Estas Seguro? Los archivos se borrarán permanentemente"),
            dbc.ModalFooter([
                dbc.Button("Cancelar", id="close",className="ml.auto"),
                dbc.Button("Borrar", color="danger", id="confirm",className="ml.auto"),]
            ),
        ],
        id="modal",
    ),
dbc.Row([
    dbc.Col(html.Div(id='output-message', className="mt-3")),
]),
])


        

@callback(
    Output('mensaje-convertido', 'children'),
    [Input('boton-convertir', 'n_clicks')],
    [State('dropdown-archivos', 'value')],
    prevent_initial_call=True
)
def convertir_archivo(n_clicks, archivo_seleccionado):
    if n_clicks is None:
        return ""

    if archivo_seleccionado is None:
        return "Seleccione un archivo válido antes de convertir."
    else:
        #output_folder =r'/home/raspberryunq1/Documentos/db_page_ratones-main/out_csv'
        output_folder=obtener_carpeta_pendrive()
        if output_folder is None:
            return 'Conecte un Pendrive y vuelva a intentarlo '
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)
        
        dfs = obtener_datos_desde_bd(os.path.join(carpeta_archivos,archivo_seleccionado))
        #n=archivo_seleccionado.replace(".db", "")+"_"
        carpeta_exp = os.path.join(output_folder,
                                    archivo_seleccionado.replace(".db", ""))
        print(carpeta_exp)
        if not os.path.exists(carpeta_exp):
            os.mkdir(carpeta_exp)
        else:
            print("mmm la carpeta del experimento ya existia...")
                
        for f,d in dfs.items():
            #csv_filename = os.path.join(output_folder,n + f + '.csv')
            csv_filename =os.path.join(carpeta_exp,f+'.csv')
            pd.DataFrame(d).to_csv(csv_filename,index=False)
        mensaje = f"Archivo '{archivo_seleccionado}' convertido exitosamente."
        return mensaje

@callback(
    Output('dropdown-archivos', 'options'),
    [Input('interval-component', 'n_intervals'),
    Input('confirm', 'n_clicks')]
)
def update_dropdown_options(n,c):
    archivos_en_carpeta = [archivo for archivo in os.listdir(carpeta_archivos) if archivo.endswith(".db")]
    archivos_ordenados = sorted(archivos_en_carpeta,key = lambda archivo:os.path.getmtime(os.path.join(carpeta_archivos, archivo)), reverse=True)
    dropdown_options = [{'label': archivo, 'value': archivo} for archivo in archivos_ordenados]
    return dropdown_options

@callback(
    Output('dropdown-archivos-borrar', 'options'),
    [Input('interval-component', 'n_intervals'),
    Input('confirm', 'n_clicks')]
)
def update_dropdown_options(n,c):
    archivos_en_carpeta = [archivo for archivo in os.listdir(carpeta_archivos) if archivo.endswith(".db")]
    archivos_ordenados = sorted(archivos_en_carpeta,key = lambda archivo:os.path.getmtime(os.path.join(carpeta_archivos, archivo)), reverse=True)
    dropdown_options = [{'label': archivo, 'value': archivo} for archivo in archivos_ordenados]
    return dropdown_options
    
@callback(
    Output('modal', 'is_open'),
    [Input('boton-borrar', 'n_clicks'),
     Input('close','n_clicks'),
     Input('confirm', 'n_clicks')],
    [State('modal','is_open')],
    prevent_initial_call=True,
)
def toggle_modal(n_borrar, n_close, n_confirm, is_open):
    #if n_borrar or n_close:
    return not is_open
    #return is_open
    
@callback(
    [Output('output-message', 'children'),
    Output('dropdown-archivos-borrar','value')],
    [Input('confirm', 'n_clicks')],
    [State('dropdown-archivos-borrar','value'),
     State('modal', 'is_open')],
     prevent_initial_call=True,
)
def delete_files(n_clicks, selected_files, is_open):
    if selected_files is not None:
        try:
            for file in selected_files:
                file_path = os.path.join(carpeta_archivos,file)
                os.remove(file_path)
            return f"Archivo {', '.join(selected_files)} borrado correctamente", None
        except Exception as e:
            return f"Error al borrar archivo: {str(e)}", None
    return "mmm algo paso", None
