
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

    if table_name in tablas: #la tabla ya existe, no la creo
        return conn
    else:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} "+\
                "(tiempo REAL PRIMARY KEY, velocidad REAL, distancia REAL)")
        #create_index_command = f"CREATE INDEX idx_tiempo ON {table_name} (tiempo);"
        #aca cada tabla tiene que tener su indice con diferente valor
        create_index_command = f"CREATE INDEX idx_tiempo_{idx} ON {table_name} (tiempo);"
        conn.execute(create_index_command)

    return conn


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
        print("Error al leer los dato:", e)
        

#----------------------------------------------------------------------
#------------------ Funciones externas --------------------------------
    
def write_meas_to_db(database_file :str, 
                     topic         :str, 
                     medicion      :float):
    """esta función toma una medición de sensor y la escribe
    en la base de datos en la tabla correspondiente."""
    try:
        conn = sqlite3.connect(database_file) #me conecto a la base de datos
        cursor = conn.cursor() #me paro en el ulitmo valor
    
        table_name = topic.replace("/", "_").replace("sensor_", "")
       
        conn = _create_datatable_if_not_exists(conn,table_name)
        #aca cree una función para crear la tabla, ahora tiene una col distancia
        #además de un índice que va a optimizar la velocidad de las consultas.
        
        tiempo_actual = time.time()
        
        max_t_meass = 0.9 #10*60 # tiempo entre mediciones
        
        d1, d2 = _get_last_two_meas_from_db(conn, table_name)
        query_insert_into = f"INSERT INTO {table_name} (tiempo, velocidad, distancia) VALUES (?, ?, ?)"
        
        if d1 is None:
            cursor.execute(query_insert_into,(tiempo_actual, medicion, 0))
        else:            
            t1,v1,di1 = d1
            t2,v2,di2 = d2
            new_dist = di2 + v2*(tiempo_actual-t2)
            #last_t1,last_v1,last_t2,last_v2 = _get_last_two_meas_from_db(conn, topic)
    #        print("")
    #        print("")
    #        print(f"last_t1: {last_t1}, last_v1: {last_v1}, last_t2: {last_t2}, last_v2: {last_v2}")
    #        print(f"medicion: {medicion}, tiempo_actual: {tiempo_actual}")
    #        print("")
            
            if (v1 == v2 == 0):
                if medicion==0:
                    if tiempo_actual - t1 >= max_t_meass: # cinco min
                        print("paso el tiempo mat_t")
                        cursor.execute(
                            query_insert_into,
                            (tiempo_actual, 0, di2),
                                )
                        #conn.commit()....
                    else: #no paso el x tiempo
                        pass
                else: #tenemos nueva medicion
                    """escribir un 0 adicional"""
                    cursor.execute( #forzamos un 0 el segundo anterior
                            query_insert_into,
                            (tiempo_actual-1, 0, di2),
                          ) 
                    print("no es 0")
                    cursor.execute( #escribimos valor actual
                                query_insert_into,
                                (tiempo_actual, medicion, new_dist),
                           ) 
            else: #si las dos mediciones anteriores no son cero, sigo escribiendo normal
                cursor.execute(
                            query_insert_into,
                            (tiempo_actual, medicion, new_dist),
                       ) 
        conn.commit()

#        if (last_v1 == 0 and last_v2 == 0 and medicion == 0):
#            print("Son 0")
#            if tiempo_actual - last_t1 >= max_t_meass: # cinco min
#                print("paso el tiempo mat_t")
#                cursor.execute(
#                    f"INSERT INTO {table_name} (tiempo, valor) VALUES (?, ?)",
#                    (tiempo_actual, medicion),
#                                )
#                conn.commit()
#            else: #son 0 pero paso menos de x tiempo
#                pass
#        else:
#            print("no es 0")
#            cursor.execute(
#                    f"INSERT INTO {table_name} (tiempo, valor) VALUES (?, ?)",
#                    (tiempo_actual, medicion),
#                            )
#            conn.commit()
#        print("")
#        print("")

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



def obtener_dias_guardados(database_file: str,
                           table_name: str):
    
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()
    try: 
        
        first_row = cursor.execute(f"SELECT * FROM {table_name} ORDER BY tiempo ASC LIMIT 1;").fetchone()
        last_row  = cursor.execute(f"SELECT * FROM {table_name} ORDER BY tiempo DESC LIMIT 1;").fetchone()
        t0 = first_row[0]
        tf = last_row[0]
        days = int(np.ceil((tf-t0)/(3600*24)))
    except Exception as e:
        print(f"Error al calcular dias :{e=}")    
        t0   = -1
        tf   = -1
        days = -1
    finally:
        conn.close()    

    return t0, tf, days
        
        
def obtener_datos_desde_tabla(database_file: str,
                           table_name: str,
                           dia: int = -1) -> dict:
    """Lee los datos de la tabla seleccionada, 
    con un paso de step. Devuelve un diccionario con los datos

    Args:
        database_file (str): _description_
        table_name (str): _description_
        dia : el dia del cual quiero los datos
    """
   conn = sqlite3.connect(database_file)
    try:
        if dia ==-1: #toma todos los datos
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, conn)
        else:
            t0,tf,n_dias = obtener_dias_guardados(database_file, table_name)
            if dia>=0:                
                if dia>=n_dias:
                    print("seleccionando dia mayor que el ultimo")
                    dia=n_dias -1  #creo que le tengo que restar 1
            else:
                ValueError('Se seleccionó un día negativo no se puede calcular')
                
            t_init = t0 + 86400*dia # segundos en un dia 86400
            t_fin  = t0 + 86400*(dia+1)
            query = f"SELECT * FROM {table_name} WHERE tiempo BETWEEN {t_init} AND {t_fin}"
            df = pd.read_sql_query(query, conn)
        
    except:
        df = pd.DataFrame({'tiempo':[], 'velocidad':[], 'distancia':[]})
    conn.close()
    return df.to_dict()



#%% CODIGO VIEJO



# def get_last_two_meas_from_db(database_file:str, topic:str):
    
#     try:
#         conn = sqlite3.connect(database_file) 
#         cursor = conn.cursor()
        
#         table_name = topic.replace("/", "_").replace("sensor_", "")
#         cursor.execute(f"SELECT tiempo, valor FROM {table_name} ORDER BY tiempo DESC LIMIT 2")
        
#         rows = cursor.fetchall()
        
#         if len(rows) == 2:
#             tiempo1, valor1 = rows[0]
#             tiempo2, valor2 = rows[1]
#             return tiempo1, valor1, tiempo2, valor2 
#         elif len(rows) == 1:
#             tiempo, valor = rows[0]
#             return tiempo, valor, tiempo, valor 
#         else:
#             print(f"No se encontraron datos para el tema '{topic}'")
#             return None, None, None, None
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         print("Error al leer los dato:", e)
        


# ~ import sqlite3
# ~ import json
# ~ import time
# ~ import pandas as pd
# ~ """ Acá voy a agregar todas las funciones que tengan que ver con modificacion
# ~ de la base de datos, de esta forma tengo programas más cortos e independientes.
# ~ Si quiero cambiar algo de formato de base de datos, será trasparente para el
# ~ resto del programa (o debería)"""

# ~ #aca cambie la notación 
# ~ #utilizando lo que se conoce como typing hints, basicamente
# ~ #es solo para el programador.
# ~ def write_meas_to_db(database_file :str, 
                     # ~ topic         :str, 
                     # ~ medicion      :float):
    # ~ """esta función toma una medición de sensor y la escribe
    # ~ en la base de datos en la tabla correspondiente."""
    # ~ try:
        # ~ conn = sqlite3.connect(database_file) #me conecto a la base de datos
        # ~ cursor = conn.cursor() #me paro en el ulitmo valor
    
        # ~ table_name = topic.replace("/", "_").replace("sensor_", "")
        # ~ cursor.execute(
                    # ~ f"CREATE TABLE IF NOT EXISTS {table_name} " +\
                    # ~ "(tiempo REAL, valor REAL)"
                # ~ )
        
        # ~ tiempo_actual = time.time()
        # ~ cursor.execute(
                    # ~ f"INSERT INTO {table_name} (tiempo, valor) VALUES (?, ?)",
                    # ~ (tiempo_actual, medicion),
                # ~ )
        # ~ conn.commit()

        # ~ cursor.close()
        # ~ conn.close()
    # ~ except Exception as e:
        # ~ print("Error al guardar el dato:", e)    
    
# ~ def guardar_estado_programa(database_file  : str, 
                            # ~ tiempo_deseado : float, 
                            # ~ tiempo_actual  : float):
    # ~ # Conectar a la base de datos
    # ~ conn = sqlite3.connect(database_file)
    # ~ cursor = conn.cursor()

    # ~ # Crear tabla de estado si no existe
    # ~ cursor.execute(
        # ~ "CREATE TABLE IF NOT EXISTS estado_programa "+\
        # ~ "(tiempo_deseado REAL, tiempo_actual REAL)"
    # ~ )

    # ~ # Insertar información sobre el estado actual
    # ~ cursor.execute("DELETE FROM estado_programa")  # Solo guardamos el último estado
    # ~ cursor.execute("INSERT INTO estado_programa "+\
                    # ~ "(tiempo_deseado, tiempo_actual) VALUES (?, ?)", 
                    # ~ (tiempo_deseado, tiempo_actual))

    # ~ conn.commit()
    # ~ cursor.close()
    # ~ conn.close()

# ~ # Obtener información sobre el estado del programa desde la tabla adicional
# ~ def obtener_estado_programa(database_file : str) : #que retorno?
    # ~ conn = sqlite3.connect(database_file)
    # ~ cursor = conn.cursor()
    # ~ cursor.execute("SELECT * FROM estado_programa ORDER BY ROWID DESC LIMIT 1")
    # ~ estado = cursor.fetchone()
    # ~ cursor.close()
    # ~ conn.close()
    # ~ return estado


# ~ def obtener_datos_desde_tabla(database_file: str,
                           # ~ table_name: str,
                           # ~ step: int = 1) -> dict:
    # ~ """Lee los datos de la tabla seleccionada, 
    # ~ con un paso de step. Devuelve un diccionario con los datos

    # ~ Args:
        # ~ database_file (str): _description_
        # ~ table_name (str): _description_
        # ~ step (int, optional): _description_. Defaults to 1.
    # ~ """
    # ~ conn = sqlite3.connect(database_file)
    # ~ try:
        # ~ cursor = conn.cursor()
    
        # ~ cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        # ~ largo_tabla = cursor.fetchone()[0]
    
        # ~ query = f"SELECT * FROM {table_name} WHERE (ROWID-1) % {step} = 0"
        # ~ df = pd.read_sql_query(query, conn)
    # ~ except:
        # ~ df = pd.DataFrame({'tiempo':[], 'valor':[]})
    # ~ conn.close()
    # ~ return df.to_dict()

