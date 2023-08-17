#ifndef MyMQTT_h
#define MyMQTT_h
//#define MSG_BUFFER_SIZE (50)

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <Ticker.h>

class MyMQTT {
public:
  MyMQTT(const char* ssid, const char* password, const char* mqttServer, int mqttPort);
  void connect();
  void publish(const char* topic, const char* message);
  void subscribe(const char* topic);
  void loop();
  //unsigned long lastMsg = 0;
  //char msg[MSG_BUFFER_SIZE];
  //int value = 0;

private:
  const char* _ssid;
  const char* _password;
  const char* _mqttServer;
  int _mqttPort;
  WiFiClient _wifiClient;
  PubSubClient _mqttClient;
};

#endif
