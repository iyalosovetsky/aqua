import mip
import network
import socket

ssid = 'IGORNET'
password = 'IG0RNET29041971'



# mip.install("umqtt.simple")
# mip.install("github:RaspberryPiFoundation/picozero/picozero/__init__.py", target="/lib/picozero")
# mip.install("github:RaspberryPiFoundation/picozero/picozero/picozero.py", target="/lib/picozero")
mip.install("github:iyalosovetsky/aqua/aqua.py", target="/lib/aqua")
mip.install("github:iyalosovetsky/aqua/boot.py", target="/lib/aqua")
mip.install("github:iyalosovetsky/aqua/test.py", target="/lib/aqua")

#upip.install('picozero','/lib')
if station.isconnected() == False:
    while station.isconnected() == False:
      pass

    print('Connection successful')
    
print(station.ifconfig())
print('----------')

# try:
print("Code downloaded")
from aqua import test
test.runTest()
#aqua.aquaProceed(station)
# except Exception as e:
#     print("Code download failed", e)

