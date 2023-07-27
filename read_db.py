import sqlite3
import pandas as pd

# Nombre de la tabla que quieres leer
tabla_a_leer = "datos_0"

def check_db_size():
    dfs = obtener_datos_desde_bd()
    "use special library to read dict of dataframes"
    from pympler import asizeof
    n = len(dfs['datos_0']['valor'])
    s = asizeof.asizeof(dfs)/1024/1024
    print(f"tamaño en memoria: {s}MB")
    print(f"cantidad de datos en cad df: {n}")
    print(f"estimacion mb/h:  {s*3600/n}")
    print(f"hotas de datos: {n/3600}")

def obtener_datos_desde_bd():
    """Leo los datos de la base de datos y devuelvo dict de dataFrames"""
    conn = sqlite3.connect("datos_sensores.db")
    dfs = {}
    for i in range(10):
        df = pd.read_sql_query(f"SELECT * FROM datos_{i}", conn)  # Tablas para los canales sensor/datos_0 a sensor/datos_9
        dfs[f"datos_{i}"] = df.to_dict()
    conn.close()
    return dfs
#---------------------------------------------------

# Función para leer los datos de la tabla y mostrarlos en la consola
def leer_datos_desde_tabla():
    conn = sqlite3.connect("datos_sensores.db")
    cursor = conn.cursor()

    try:
        # Realizar la consulta SQL para obtener los datos de la tabla
        cursor.execute(f"SELECT * FROM {tabla_a_leer}")
        datos = cursor.fetchall()

        if datos:
            # Mostrar los datos en la consola
            print(f"Datos en la tabla '{tabla_a_leer}':")
            for fila in datos:
                tiempo, valor = fila
                print(f"Tiempo: {tiempo}, Valor: {valor}")
        else:
            print(f"La tabla '{tabla_a_leer}' está vacía.")

    except sqlite3.Error as e:
        print("Error al leer los datos:", e)

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    #leer_datos_desde_tabla()
    check_db_size()