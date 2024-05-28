from sensors import Sense
import time 

sensor = Sense()

while True:
    light = sensor.read_ldr()
    print(light)
    time.sleep(3)