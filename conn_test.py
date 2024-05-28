from nexnet import NexusNetwork
import time

nexus = NexusNetwork() 

nexus.wifi_connect()

while True:
    if nexus.mqtt_init():
        break
    else:
        nexus.auto_reconnect()

nexus.mqtt_subscribe_init("gold")

count = 0

while count < 20:
    if nexus.wifi_status():
        pass
    else:
        nexus.auto_reconnect()
    nexus.mqtt_publish("test", count)
    count += 1
    nexus.mqtt_subscribe_buffer()
    if nexus.subscribe_load:
        print(nexus.subscribe_load)
    time.sleep(1)

nexus.deactivate()
