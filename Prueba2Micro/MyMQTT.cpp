#include "MyMQTT.h"

MyMQTT::MyMQTT(const char* ssid, const char* password, const char* mqttServer, int mqttPort)
  : _ssid(ssid), _password(password), _mqttServer(mqttServer), _mqttPort(mqttPort), _wifiClient(), _mqttClient(_wifiClient) {}

IPAddress local_IP(10, 42, 0, 11);//este cambiar el ultimo numero
// Set your Gateway IP address
IPAddress gateway(10, 42, 0, 100);

IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(0, 0, 0, 0);//optional
IPAddress secondaryDNS(0, 0, 0, 0);//optional

void MyMQTT::connect() {

  WiFi.setSleepMode(WIFI_NONE_SLEEP);
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
  Serial.println("STA Failed to configure");
  }

  WiFi.begin(_ssid, _password);
  Serial.print("\nConectando a:\t");
  Serial.println(_ssid);
  while (WiFi.status() != WL_CONNECTED) {
    delay(200);
    Serial.print('.');
  }
  Serial.println();
  Serial.print("Conectado a:\t");
  Serial.println(WiFi.SSID()); 
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());

  _mqttClient.setServer(_mqttServer, _mqttPort);

  while (!_mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (_mqttClient.connect("ESP8266Client_1")) { //"ESP8266Client" es el client ID
      Serial.println("connected");
      // Suscribirse a los temas necesarios después de la conexión (si es necesario)
      //_mqttClient.subscribe("intopic");
      
    }
    else {
      Serial.print("failed, rc=");
      Serial.print(_mqttClient.state());
      Serial.println(" try again in 1 seconds");
      // Wait 5 seconds before retrying
      delay(1000);
    } 
  }
}

void MyMQTT::publish(const char* topic, const char* message) {
  _mqttClient.publish(topic, message);
}

void MyMQTT::subscribe(const char* topic) {
  _mqttClient.subscribe(topic);
}

void MyMQTT::loop() {
  if (!_mqttClient.connected()) {
    connect();
  }
  _mqttClient.loop();
  //unsigned long now = millis();
  //if (now - lastMsg > 1000) {
    //lastMsg = now;
    //++value;
    
}