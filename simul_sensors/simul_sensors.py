from numpy import random
import time
import paho.mqtt.client as mqtt
import json

# los # sirven para hacer comentarios, pero si son muy largos se puede
# poner tres de estas para abrir " y tres para cerrar

# Configuración del broker MQTT
#broker_address = "192.168.0.9"  # Reemplaza con la dirección IP 
#broker_port = 1883
broker_address = "192.168.0.9"
broker_port = 1883
topic = "sensor/datos_"



def on_connect(client, userdata, flags, rc):
    print(f"Connected with flags [{flags}] rtn code [{rc}]" )

def on_disconnect(client, userdata, rc):
    print(f"disconnected with rtn code [{rc}]" )
    print("intentando reconectar")
    client.reconnect() 

def on_publish(client, userdata, msgID):
    print(f"Published with MsgID [{msgID}]" )


client = mqtt.Client(client_id="python00")
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

# Función para generar datos aleatorios y publicarlos en el broker
def publish_simulated_data(topic):
    cont = 0

    client.connect(broker_address, broker_port,keepalive=60) # #me conecto
    t0 =  time.time()
    while True: #voy a correr esto siempre o sea enviar msj constantemente
        valor_medicion = random.randint(0, 100,10)  
        for i in range(10): # envio por los 10 sensores
            # Genera un valor aleatorio para la medición
            
            cont = cont+1
            mensaje = {"medicion":1.0*cont} # 1.0*valor_medicion[i]}
            tp = topic+str(i)
            client.publish(tp, json.dumps(mensaje))
    
        time.sleep(1)

if __name__ == "__main__":
    publish_simulated_data(topic)
