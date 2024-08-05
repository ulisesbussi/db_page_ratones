
import sqlite3
import json
import time
import datetime
import pandas as pd
import numpy as np
""" Acá voy a agregar todas las funciones que tengan que ver con modificacion
de la base de datos, de esta forma tengo programas más cortos e independientes.
Si quiero cambiar algo de formato de base de datos, será trasparente para el
resto del programa (o debería)"""

#aca cambie la notación 
#utilizando lo que se conoce como typing hints, basicamente
#es solo para el programador.

#-------------- Funciones internas -------------------------------------


def _create_datatable_if_not_exists(conn,table_name):
    """Esta funcion se va a encargar de crear la tabla de datos 
    si esta no existe. Si ya existe la tabla devuelve la conexion.

    Args:
        conn (_type_): conexion a la base de datos
        table_name (_type_): nombre de la tabla
    """
    idx = table_name.split('_')[-1]
    resp = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas = [t[0] for t in resp.fetchall()]

    if table_name not in tablas:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} "+\
                "(tiempo REAL PRIMARY KEY, velocidad REAL, distancia REAL)")
        create_index_command = f"CREATE INDEX idx_tiempo_{idx} ON {table_name} (tiempo);"
        conn.execute(create_index_command)
        conn.commit()


def _get_last_two_meas_from_db(conn, table_name):
    """ Esta funcion obtiene las ultimas dos mediciones de la tabla para 
    Ver cuanto tiempo paso entre ellas y si son 0"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT tiempo, velocidad, distancia FROM {table_name} ORDER BY tiempo DESC LIMIT 2")
        rows = cursor.fetchall()
        
        if len(rows) == 2:
            d1,d2 = rows[:2]
        elif len(rows) == 1:
            d1 = d2 = rows[0]
        else:
            print(f"No se encontraron datos para la {table_name=}")
            return None, None
        return d1, d2
    except Exception as e:
        print("Error al leer los dato (en get_last_two_meas):", e)
        

#----------------------------------------------------------------------
#------------------ Funciones externas --------------------------------
    
def write_meas_to_db(database_file :str, 
                     topic         :str, 
                     medicion      :float):
    """esta función toma una medición de sensor y la escribe
    en la base de datos en la tabla correspondiente."""
    
    table_name = topic.replace("/", "_").replace("sensor_", "")
    max_t_meass = 0.9
    try: 
        with sqlite3.connect(database_file) as conn:
            _create_datatable_if_not_exists(conn,table_name)
            tiempo_actual = time.time()
            
            d1, d2 = _get_last_two_meas_from_db(conn, table_name)
            cursor = conn.cursor()
            query_insert_into = f""" INSERT INTO {table_name} 
                    (tiempo, velocidad, distancia) VALUES (?, ?, ?)"""
            if d1 is None:
                cursor.execute(query_insert_into,(tiempo_actual, medicion, 0))
            else:            
                t1,v1,di1 = d1
                t2,v2,di2 = d2
                new_dist = di2 + v1*(tiempo_actual-t1)
                
                if (v1 == v2 == 0):
                    if medicion==0:
                        if tiempo_actual - t1 >= max_t_meass:
                            #print("paso el tiempo max_t")
                            cursor.execute( query_insert_into,
                                (tiempo_actual, 0, di2),
                            )
                    else: #tenemos nueva medicion
                        """escribir un 0 adicional"""
                        cursor.execute( #forzamos un 0 el segundo anterior
                                query_insert_into,
                                (tiempo_actual-1, 0, di2),
                        ) 
                        #print("no es 0")
                        cursor.execute( #escribimos valor actual
                                query_insert_into,
                                (tiempo_actual, medicion, new_dist),
                        )
                else: 
                    cursor.execute(
                            query_insert_into,
                            (tiempo_actual, medicion, new_dist),
                        ) 
    except Exception as e:
        print("Error al escribir dato (write_meas_to_db):", e)    
                
    
    
    

def guardar_estado_programa(database_file  : str, 
                            tiempo_deseado : float, 
                            tiempo_actual  : float):
    # Conectar a la base de datos
    try:
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            # Crear tabla de estado si no existe
            cursor.execute("""CREATE TABLE IF NOT EXISTS estado_programa
                           (tiempo_deseado REAL, tiempo_actual REAL)""")
            # Insertar información sobre el estado actual
            cursor.execute("DELETE FROM estado_programa")
            cursor.execute("""INSERT INTO estado_programa
                           (tiempo_deseado, tiempo_actual) VALUES (?, ?)""",
                           (tiempo_deseado, tiempo_actual))
    except Exception as e:
        print("Error al guardar el estado del programa:", e)
        
        



# Obtener información sobre el estado del programa desde la tabla adicional
def obtener_estado_programa(database_file : str) : #que retorno?
    try:
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM estado_programa 
                           ORDER BY ROWID DESC LIMIT 1""")
            estado = cursor.fetchone()
    except Exception as e:
        print("Error al obtener el estado del programa:", e)
        estado = None
    return estado



def obtener_dias_guardados(database_file: str,
                           table_name: str):
    select_statement = f"SELECT * FROM {table_name} ORDER BY tiempo"
    try:
        # ~ print(f"{select_statement} ASC LIMIT 1")
        with sqlite3.connect(database_file) as conn:
            cursor = conn.cursor()
            first_row = cursor.execute(f"{select_statement} ASC LIMIT 1").fetchone()
            last_row  = cursor.execute(f"{select_statement} DESC LIMIT 1").fetchone() 
            t0 = first_row[0]
            tf = last_row[0]
            days = int(np.ceil((tf-t0)/(3600*24)))
    except Exception as e:
        print(f"Error al calcular dias :{e=}")
        t0 = tf = days = -1
    return t0, tf, days
        
def obtener_datos_desde_tabla(database_file: str,
                           table_name: str,
                           dia: int = -1) -> dict:

    try:
        with sqlite3.connect(database_file) as conn:
            if dia ==-1:
                query = f"SELECT * FROM {table_name}"
                df = pd.read_sql_query(query, conn)
            else:
                t0,tf,n_dias = obtener_dias_guardados(database_file, table_name)
                if dia>=0:                
                    if dia>=n_dias:
                        print("seleccionando dia mayor que el ultimo")
                        dia=n_dias -1
                else:
                    ValueError('Se seleccionó un día negativo no se puede calcular')
                t_init = t0 + 86400*dia # segundos en un dia 86400
                t_fin  = t0 + 86400*(dia+1)
                query = f"""SELECT * FROM {table_name} 
                            WHERE tiempo BETWEEN {t_init} AND {t_fin} AND (ROWID % 4 = 0)"""
                df = pd.read_sql_query(query, conn)     
    except Exception as e:
        print(f"Error al obtener datos desde tabla: {e=}")
        df = pd.DataFrame({'tiempo':[], 'velocidad':[], 'distancia':[]})
    return df.to_dict()                        
