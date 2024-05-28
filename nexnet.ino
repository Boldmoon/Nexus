#include <ESP8266WiFi.h>
#include <PubSubClient.h>

class NexusNetwork
{
private:
  WiFiClient espClient;
  PubSubClient mqttClient;
  bool kill = false;

  const char *wifiSSID;
  const char *wifiPassword;
  const char *mqttServer;
  const char *mqttUsername;
  const char *mqttPassword;
  const char *mqttClientId;
  const char *subscribedTopic;

public:
  String subscribeLoad;

  NexusNetwork(const char *ssid, const char *password, const char *server, const char *username, const char *pwd, const char *clientId) : mqttClient(espClient),
                                                                                                                                          wifiSSID(ssid),
                                                                                                                                          wifiPassword(password),
                                                                                                                                          mqttServer(server),
                                                                                                                                          mqttUsername(username),
                                                                                                                                          mqttPassword(pwd),
                                                                                                                                          mqttClientId(clientId) {}

  bool wifiConnect()
  {
    WiFi.begin(wifiSSID, wifiPassword);
    Serial.print("Connecting to WiFi...");
    unsigned long startAttemptTime = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 30000)
    {
      delay(1000);
      Serial.print(".");
    }
    if (WiFi.status() == WL_CONNECTED)
    {
      Serial.println("\nConnected to WiFi");
      return true;
    }
    else
    {
      Serial.println("\nFailed to connect to WiFi");
      return false;
    }
  }

  bool wifiStatus()
  {
    return WiFi.status() == WL_CONNECTED;
  }

  bool mqttInit()
  {
    mqttClient.setServer(mqttServer, 1883);
    mqttClient.setCallback([this](char *topic, byte *payload, unsigned int length)
                           { this->mqttCallback(topic, payload, length); });
    if (mqttClient.connect(mqttClientId, mqttUsername, mqttPassword))
    {
      Serial.println("Connected to MQTT server");
      if (subscribedTopic != nullptr)
      {
        mqttSubscribeInit(subscribedTopic);
      }
      return true;
    }
    else
    {
      Serial.println("Waiting for MQTT server connection");
      return false;
    }
  }

  bool mqttStatus()
  {
    return mqttClient.connected();
  }

  void autoReconnect()
  {
    Serial.println("\nEntering auto reconnect");
    int retryDelay = 1000;
    while (!kill)
    {
      if (wifiStatus())
      {
        if (mqttStatus())
        {
          Serial.println("\nAll protocols connected\n");
          break;
        }
        else
        {
          Serial.println("\nReconnecting to MQTT server");
          if (!mqttInit())
          {
            delay(retryDelay);
            retryDelay = min(retryDelay * 2, 60000);
          }
          else
          {
            retryDelay = 1000;
          }
        }
      }
      else
      {
        Serial.println("\nReconnecting to WiFi");
        if (!wifiConnect())
        {
          delay(retryDelay);
          retryDelay = min(retryDelay * 2, 60000);
        }
        else
        {
          retryDelay = 1000;
        }
      }
    }
  }

  void mqttPublish(const char *topic, const char *load)
  {
    if (!mqttClient.connected())
    {
      Serial.println("MQTT client not connected, attempting to reconnect");
      autoReconnect();
    }
    if (mqttClient.publish(topic, load))
    {
      Serial.println("Message published");
    }
    else
    {
      Serial.println("Failed to publish message, attempting to reconnect");
      autoReconnect();
    }
  }

  void mqttSubscribeInit(const char *top)
  {
    subscribedTopic = top;
    if (!mqttClient.connected())
    {
      Serial.println("MQTT client not connected, attempting to reconnect");
      autoReconnect();
    }
    if (mqttClient.subscribe(top))
    {
      Serial.println("Subscribed to topic");
    }
    else
    {
      Serial.println("Error occurred while subscribing to MQTT topic, attempting to reconnect");
      autoReconnect();
    }
  }

  void mqttSubscribeBuffer()
  {
    if (!mqttClient.connected())
    {
      Serial.println("MQTT client not connected, attempting to reconnect");
      autoReconnect();
    }
    mqttClient.loop();
  }

  void deactivate()
  {
    kill = true;
    if (wifiStatus())
    {
      WiFi.disconnect();
    }
    if (mqttStatus())
    {
      mqttClient.disconnect();
    }
    Serial.println("All protocols disconnected");
  }

private:
  void mqttCallback(char *topic, byte *payload, unsigned int length)
  {
    char message[length + 1];
    memcpy(message, payload, length);
    message[length] = '\0';
    subscribeLoad = String(message);
    Serial.print("Message received: ");
    Serial.println(subscribeLoad);
  }
};

const char *wifiSSID = "--";
const char *wifiPassword = "--";
const char *mqttServer = "--";
const char *mqttUsername = "--";
const char *mqttPassword = "--";
const char *mqttClientId = "--";

NexusNetwork nexus(wifiSSID, wifiPassword, mqttServer, mqttUsername, mqttPassword, mqttClientId);

void setup()
{
  Serial.begin(115200);
  if (!nexus.wifiConnect())
  {
    Serial.println("Failed to connect to WiFi during setup");
  }
  if (!nexus.mqttInit())
  {
    Serial.println("Failed to connect to MQTT server during setup");
  }
  nexus.mqttSubscribeInit("gold");
}

void loop()
{
  nexus.mqttPublish("test", "Hell1o, MQTT!");
  nexus.mqttSubscribeBuffer();
  delay(1000);
}
