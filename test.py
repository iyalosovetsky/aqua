import mip
import network
import socket
try:
    from secrets import secrets
except:
    print('File secrets not exist')


# mip.install("umqtt.simple")
mip.install("github:RaspberryPiFoundation/picozero/picozero/__init__.py", target="/lib/picozero")
mip.install("github:RaspberryPiFoundation/picozero/picozero/picozero.py", target="/lib/picozero")
# mip.install("github:iyalosovetsky/aqua/aqua.py", target="/lib/aqua")
# mip.install("github:iyalosovetsky/aqua/boot.py", target="/lib/aqua")
mip.install("github:iyalosovetsky/aqua/package.json")

if station.isconnected() == False:
    while station.isconnected() == False:
      pass

    print('Connection successful')
    
print(station.ifconfig())
print('----------')

# try:
print("Code downloaded")
from aqua import aqua
mqtt = aqua.m_mqtt(station)
mqtt.aquaProceed(station)


