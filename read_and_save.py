#---------------------------------
#imports generales
import json
import time
import paho.mqtt.client as mqtt
import argparse
import threading
from pytimeparse.timeparse import timeparse
#---------------------------------
#---------------------------------
# imports locales
from db_manipulation.utils import write_meas_to_db, guardar_estado_programa
#---------------------------------


#---------------------------------
#definición variables broker y topicos
broker_address = "192.168.4.1"  
broker_port = 1883
# creo 10 topicos, uno por sensor (sensor/datos_0 a sensor/datos_9)
topics = ["sensor/datos_" + str(i) for i in range(2)]#(10)
#---------------------------------


#---------------------------------
#Funciones locales de utilidad

# Esta funcion sirve para corregir un problema que se genera
#en el envío de mensaje, tiene que ver con los formastos de diccionarios
#de python y con los de json
# acá pueden chusmear que es un diccionario de python y que es un 
#json . .
def convert_to_double_quotes(json_str):
    try:
        json_str_double_quotes = json.loads(json_str.replace("'", "\""))
        return json_str_double_quotes
    except Exception as e:
        print("Error al convertir a comillas dobles:", e)
        return None


"""Esta funcion es media larga pero no se asusten, hace lo siguiente:
Es una función que se va a ejecutar cuando se reciba algún mensaje del broker
es decir, si me suscribo a un canal y llega mensaje por ahí, se ejecuta 
esta función. Lo mismo pasaba en el micro, recuerdan? 

Esta clase de funciones a veces reciben el nombre de callback, porque
se ejecutan cuando pasa un evento determinado"""
# Función para guardar los datos en la base de datos SQLite
def on_message(database_file, client, userdata, message):
    try:
        topic = message.topic
        #aca pueden jugar un poco si quieren,
        # message es el mensaje recibido con toda la estructura de mqtt
        # payload, es el mensaje que uno manda como usuario, el resto del 
        #mensaje tiene que ver con el protocolo en sí digamos.
        #decode lo convierte a un string de bites y de ahí con la función
        #de arriba lo reformateo y saco el valor de la medición.
        payload = convert_to_double_quotes(message.payload.decode())  # Convertir a comillas dobles
        medicion = payload.get('v')

        #print(f"guardando dato: {medicion} en {topic} en db: {database_file}")
        if medicion is not None: #si tengo medicion
            write_meas_to_db(database_file, topic, medicion)
    except Exception as e:
        print("Error al guardar el dato:", e)
#---------------------------------


#------------- Parse de argumentos----------------
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", type=str, default="datos_sensores.db",
                        help="Nombre de la base de datos")
    parser.add_argument("-t", "--timeduration", type=str, default="3m",
                        help="""Duracion de la medicion, especificando unidaded,
                        por ejemplo 1d, 2h, 3m, 4s o 1d5s""")
    
    args = parser.parse_args()
    timeduration = timeparse(args.timeduration)
    database = args.database + ".db" if ".db" not in args.database else args.database
    print(args.timeduration)
    return database, timeduration
    



update_progress_event = threading.Event()
mqtt_exit_event       = threading.Event()


def programar_actualizacion_tabla_estado(database_file, 
                                         time_duration, 
                                         t0):
    while not update_progress_event.wait(10):#60):  # Espera hasta que el evento esté activo o transcurra 1 minuto (60 segundos)
        guardar_estado_programa(database_file, 
                                time_duration, 
                                time.time()-t0)
        print("guardando progreso")


def mqtt_exit_thread(time_duration):
    # Espera hasta que se alcance el tiempo de duración o se active el evento de salida del cliente MQTT
    time.sleep(time_duration)
    mqtt_exit_event.set()




#database_file = "datos_sensores2.db" #nombre de la base de datos

#esta parte de acá lo que hace es ejecutar el archivo silo si se llama
# de este mismo archivo (es un poco más avanzado, por ahora, quedense
# con que el if no tiene una funcionalidad especial).
def main():
    database_file, time_duration = parse()

    print("Conectando al broker.")
    client = mqtt.Client(client_id = "Raspberry")
    client.connect(broker_address, broker_port)

    on_msg = lambda x,y,z: on_message(database_file, x,y,z)
    client.on_message = on_msg

    for topic in topics:
        client.subscribe(topic)

    t0 = time.time()

    update_progress_thread = threading.Thread(
        target=programar_actualizacion_tabla_estado,
        args=(database_file, time_duration, t0),  # Puedes ajustar el valor inicial de tiempo_actual
        daemon=True    )
    update_exit_thread = threading.Thread(
        target= mqtt_exit_thread,
        args=(time_duration,),
        daemon=True    )
    
    update_progress_thread.start()
    
    # Iniciar el bucle de eventos MQTT en el hilo principal
    
    client.loop_start()

    # Esperar hasta que se alcance el tiempo de duración o se active el evento de salida del cliente MQTT
    #update_progress_event.wait()
    update_exit_thread.start()
    mqtt_exit_event.wait()
    # Activar el evento de salida del cliente MQTT
    #mqtt_exit_event.set()

    # Esperar a que el cliente MQTT termine
    client.loop_stop()
    client.disconnect()
    guardar_estado_programa(database_file, 
                                time_duration, 
                                time_duration)


print(__name__)
if __name__ == "__main__":
    main()
    #python read_and_save.py -t 15s -d asd
