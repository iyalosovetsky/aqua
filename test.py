from umqtt.simple import MQTTClient
from picozero import pico_temp_sensor, pico_led

# https://github.com/RaspberryPiFoundation/picozero
def runTest():
    pico_led.on() 