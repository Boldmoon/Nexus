from umqtt.simple import MQTTClient
import network
import time
import json

class NexusNetwork:
    def __init__(self):
        self.wlan = None
        self.mqtt_client = None
        self.subscribe_load = []
        self.kill = False

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        
        self.wifi_ssid = config["nexus_data"]["wifi_ssid"]
        self.wifi_pwd = config["nexus_data"]["wifi_pwd"]
        self.mqtt_host = config["nexus_data"]["mqtt_host"]
        self.mqtt_uname = config["nexus_data"]["mqtt_uname"]
        self.mqtt_pwd = config["nexus_data"]["mqtt_pwd"]
        self.mqtt_client_id = config["nexus_data"]["mqtt_client_id"]

    def wifi_connect(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self.wlan.connect(self.wifi_ssid, self.wifi_pwd)
        while not self.wlan.isconnected() and not self.kill:
            print('Waiting for WiFi connection...')
            time.sleep(1)
        if self.wlan.isconnected():
            print("Connected to WiFi")
            return True
        else:
            return False

    def wifi_status(self):
        return self.wlan.isconnected()
    
    def mqtt_init(self):
        try:
            self.mqtt_client = MQTTClient(client_id=self.mqtt_client_id, 
                                          server=self.mqtt_host, 
                                          user=self.mqtt_uname, 
                                          password=self.mqtt_pwd)
            self.mqtt_client.connect()
            print("Connected to MQTT broker")
            return True
        except OSError:
            print("Waiting for MQTT broker connection")
            return False
    
    def mqtt_status(self):
        try:
            self.mqtt_client.ping()
            return True
        except OSError:
            return False
    
    def auto_reconnect(self):
        print("\nEntering auto reconnect")
        while not self.kill:
            if self.wifi_status():
                if self.mqtt_status():
                    print("\nAll protocols connected\n")
                    return
                else:
                    print("\nReconnecting to MQTT server")
                    if not self.mqtt_init():
                        time.sleep(5)
            else:
                print("\nReconnecting to WiFi")
                if not self.wifi_connect():
                    time.sleep(5)

    def mqtt_publish(self, topic, load):
        try:
            self.mqtt_client.publish(topic, str(load))
        except Exception as e:
            print(f"\nError occurred while publishing MQTT message: {e}")
            self.auto_reconnect()

    def mqtt_subscribe_init(self, topic):
        def mqtt_subscription_callback(topic, message):
            self.subscribe_load.append(message.decode("utf-8"))

        try:
            self.mqtt_client.set_callback(mqtt_subscription_callback)
            self.mqtt_client.subscribe(topic)
        except Exception as e:
            print(f"\nError occurred while subscribing to MQTT topic: {e}")
            self.auto_reconnect()

    def mqtt_subscribe_buffer(self):
        try:
            self.mqtt_client.check_msg()
        except Exception as e:
            print(f"\nError occurred while checking MQTT messages: {e}")
            self.auto_reconnect()

    def deactivate(self):
        self.kill = True
        if self.wifi_status():
            self.wlan.disconnect()
            self.wlan.active(False)
        if self.mqtt_status():
            self.mqtt_client.disconnect()
        print("All protocols disconnected")
