import pandas as pd
import sqlite3
import os



def obtener_datos_desde_bd(name="datos_sensores.db"):
    """Leo los datos de la base de datos y devuelvo dict de dataFrames"""
    conn = sqlite3.connect(name)
    dfs = {}
    for i in range(10):
        df = pd.read_sql_query(f"SELECT * FROM datos_{i}", conn)  # Tablas para los canales sensor/datos_0 a sensor/datos_9
        dfs[f"datos_{i}"] = df.to_dict()
    conn.close()
    return dfs



if __name__ == '__main__':
    output_folder ='out_csv/'
    if os.path.exists(output_folder):
        os.mkdir(output_folder)
    
    dfs = obtener_datos_desde_bd()
    for f,d in dfs.items():
        pd.DataFrame(d).to_csv(f+'.csv',index=False)
    