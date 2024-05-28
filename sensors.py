from machine import ADC, Pin
from time import sleep
import json

class Sense:
    def __init__(self):

        self.pot_conv_factor = 100 / 65535
        self.dbsbaseline = 0
        self.gasbaseline = 0

        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            
        dht_pin = config["pin_numbers"]["DHT_PIN"]
        dbs_pin = config["pin_numbers"]["DBS_PIN"]
        ldr_pin = config["pin_numbers"]["LDR_PIN"]
        ir_pin = config["pin_numbers"]["IR_PIN"]
        tlt_pin = config["pin_numbers"]["TLT_PIN"]
        pir_pin = config["pin_numbers"]["PIR_PIN"]
        pot_pin = config["pin_numbers"]["POT_PIN"]
        mq5_pin = config["pin_numbers"]["MQ5_PIN"]
        led1_pin = config["pin_numbers"]["LED1_PIN"]
        led2_pin = config["pin_numbers"]["LED2_PIN"]
        buzz_pin = config["pin_numbers"]["BUZZ_PIN"]

        if config["enable_module"]["DHT_EN"]:
            self.dht = ADC(dht_pin)
        if config["enable_module"]["DBS_EN"]:
            self.dbs = ADC(dbs_pin)        
        if config["enable_module"]["LDR_EN"]:
            self.ldr = Pin(ldr_pin, Pin.IN, Pin.PULL_DOWN)
        if config["enable_module"]["IR_EN"]:
            self.ir = Pin(ir_pin, Pin.IN, Pin.PULL_UP)
        if config["enable_module"]["TLT_EN"]:
            self.tlt = Pin(tlt_pin, Pin.IN, Pin.PULL_UP)
        if config["enable_module"]["PIR_EN"]:
            self.pir = Pin(pir_pin, Pin.IN, Pin.PULL_DOWN)
        if config["enable_module"]["POT_EN"]:
            self.pot = ADC(pot_pin)
        if config["enable_module"]["MQ5_EN"]:
            self.mq5 = ADC(mq5_pin)
        if config["enable_module"]["LED1_EN"]:
            self.led1 = Pin(led1_pin, Pin.OUT)
        if config["enable_module"]["LED2_EN"]:
            self.led2 = Pin(led2_pin, Pin.OUT)
        if config["enable_module"]["BUZZ_EN"]:
            self.buzz = Pin(buzz_pin, Pin.OUT)
        
    def start_light(self):
        for _ in range(3):
            self.led1.value(1)
            self.led2.value(0)
            sleep(0.3)
            self.led1.value(0)
            self.led2.value(1)
            sleep(0.3)
        self.led2.value(0)
        self.led1.value(0)
        for _ in range(3):
            self.led1.value(1)
            self.led2.value(1)
            sleep(0.3)
            self.led1.value(0)
            self.led2.value(0)
            sleep(0.3)

    def mq5_calibration(self):
        baseline = []
        for _ in range(60):
            gas_level = self.mq5.read_u16()
            baseline.append(gas_level)
            sleep(1)          
        self.gasbaseline = sum(baseline) / len(baseline)
        return f'Average baseline: {self.gasbaseline}'    

    def dbs_calibration(self):
        baseline = []
        for _ in range(60):
            sound_level = self.dbs.read_u16()
            baseline.append(sound_level)
            sleep(1)  
        
        self.dbsbaseline = sum(baseline) / len(baseline)
        return f'Average baseline: {self.dbsbaseline}'
    
    def read_dht(self):
            adc_value = self.dht.read_u16()
            volt = (3.3 / 65535) * adc_value
            temperature = 27 - (volt - 0.706) / 0.001721
            return round(temperature, 1)

    def read_dbs(self):
        sound_level = self.dbs.read_u16()
        return abs((self.dbsbaseline - sound_level) / self.dbsbaseline) * 100
    
    def read_mq5(self):
        gas_level = self.mq5.read_u16()
        return abs((self.gasbaseline - gas_level) / self.gasbaseline) * 100
        # try (gas level difference)/(maximum gas level difference under std) * 100
    
    def read_ldr(self):
        if self.ldr.value(): 
            return True   #dark outside
        else:
            return False  #bright outside

    def read_ir(self):
        if self.ir.value():
            return False  #nothing detected
        else:
            return True  #smth detected

    def read_tilt(self):
        if self.tlt.value():
            return False
        else:
            return True

    def read_pir(self):
        if self.pir.value():
            return True
        else:
            return False

    def read_pot(self):
        adc_value = self.pot.read_u16()
        percent = int(round(adc_value * self.pot_conv_factor))
        return percent    
 
