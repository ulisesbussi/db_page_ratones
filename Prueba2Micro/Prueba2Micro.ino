#include "MyMQTT.h"
#include <Ticker.h>
#define MSG_BUFFER_SIZE (50)

const int interruptPin = D1; // Pin de interrupción conectado al FC-03
volatile unsigned long pulseCount = 0; // Variable para almacenar el conteo de pulsos total
volatile  long pulsesPerSecond = 0; // Variable para almacenar el conteo de pulsos por segundo
char msg[MSG_BUFFER_SIZE];
Ticker pulseTicker; // Objeto Ticker para medir el tiempo transcurrido
MyMQTT mqtt("RATONES", "ratones123", "192.168.4.1", 1883);

void IRAM_ATTR handleInterrupt()
{
  pulseCount++; // Incrementar el contador de pulsos
}

void updatePulsesPerSecond()
{
  pulsesPerSecond = pulseCount; // Guardar el conteo de pulsos en el último segundo
  pulseCount = 0; // Reiniciar el conteo total de pulsos
}

void setup() {
  pinMode(interruptPin, INPUT_PULLUP);
  Serial.begin(115200);
  delay(10);
  mqtt.connect();
  attachInterrupt(digitalPinToInterrupt(interruptPin), handleInterrupt, RISING);
  pulseTicker.attach(1.0, updatePulsesPerSecond); // Llamar a updatePulsesPerSecond cada segundo
  pulsesPerSecond =-1;
}

void loop() {
 
    mqtt.loop();
     if (pulsesPerSecond>=0){
  //}
    //snprintf(msg, MSG_BUFFER_SIZE, "{'t':%1d, 'v':%2d}", millis(), pulsesPerSecond);
    snprintf(msg, MSG_BUFFER_SIZE, "{'v':%2d}", pulsesPerSecond);
    Serial.print("Pulsos por segundo: ");
    Serial.println(msg);
    mqtt.publish("sensor/datos_0", msg);
    pulsesPerSecond =-1;
}
}
