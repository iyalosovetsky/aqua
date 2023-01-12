# Complete project details at https://RandomNerdTutorials.com

#from umqttsimple import MQTTClient
import micropython
import network
#import esp
#esp.osdebug(None)
import gc
gc.collect()
from secrets import secrets

ssid = secrets['ssid']
password = secrets['password']



rtc=machine.RTC()

station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass
 

print('Connection successful',station.ifconfig())
print('---------------------')


