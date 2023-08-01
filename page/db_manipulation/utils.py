import sqlite3
import json
import time
import pandas as pd
""" Acá voy a agregar todas las funciones que tengan que ver con modificacion
de la base de datos, de esta forma tengo programas más cortos e independientes.
Si quiero cambiar algo de formato de base de datos, será trasparente para el
resto del programa (o debería)"""

#aca cambie la notación 
#utilizando lo que se conoce como typing hints, basicamente
#es solo para el programador.
def write_meas_to_db(database_file :str, 
                     topic         :str, 
                     medicion      :float):
    """esta función toma una medición de sensor y la escribe
    en la base de datos en la tabla correspondiente."""
    try:
        conn = sqlite3.connect(database_file) #me conecto a la base de datos
        cursor = conn.cursor() #me paro en el ulitmo valor
    
        table_name = topic.replace("/", "_").replace("sensor_", "")
        cursor.execute(
                    f"CREATE TABLE IF NOT EXISTS {table_name} " +\
                    "(tiempo REAL, valor REAL)"
                )
        
        tiempo_actual = time.time()
        cursor.execute(
                    f"INSERT INTO {table_name} (tiempo, valor) VALUES (?, ?)",
                    (tiempo_actual, medicion),
                )
        conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        print("Error al guardar el dato:", e)    
    
def guardar_estado_programa(database_file  : str, 
                            tiempo_deseado : float, 
                            tiempo_actual  : float):
    # Conectar a la base de datos
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Crear tabla de estado si no existe
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS estado_programa "+\
        "(tiempo_deseado REAL, tiempo_actual REAL)"
    )

    # Insertar información sobre el estado actual
    cursor.execute("DELETE FROM estado_programa")  # Solo guardamos el último estado
    cursor.execute("INSERT INTO estado_programa "+\
                    "(tiempo_deseado, tiempo_actual) VALUES (?, ?)", 
                    (tiempo_deseado, tiempo_actual))

    conn.commit()
    cursor.close()
    conn.close()

# Obtener información sobre el estado del programa desde la tabla adicional
def obtener_estado_programa(database_file : str) : #que retorno?
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM estado_programa ORDER BY ROWID DESC LIMIT 1")
    estado = cursor.fetchone()
    cursor.close()
    conn.close()
    return estado


def obtener_datos_desde_tabla(database_file: str,
                           table_name: str,
                           step: int = 1) -> dict:
    """Lee los datos de la tabla seleccionada, 
    con un paso de step. Devuelve un diccionario con los datos

    Args:
        database_file (str): _description_
        table_name (str): _description_
        step (int, optional): _description_. Defaults to 1.
    """
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    largo_tabla = cursor.fetchone()[0]
    
    query = f"SELECT * FROM {table_name} WHERE (ROWID-1) % {step} = 0"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df.to_dict()


