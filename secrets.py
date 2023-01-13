import mip
#dict with secrets params
secrets = {
    "ssid" : "ssid",
    "password" : "password",
    "mqtt_server" : "mqtt_server",
    "mqtt_user" : "mqtt_user",
    "mqtt_password" : "mqtt_password"
}
#create status of importing code
try:
    from aqua import aqua as app
    code_exist = True
except:
    code_exist = False

# needed libs for custom app write in this function 
def codeImport():
    mip.install("github:RaspberryPiFoundation/picozero/picozero/__init__.py", target="/lib/picozero")
    mip.install("github:RaspberryPiFoundation/picozero/picozero/picozero.py", target="/lib/picozero")
    mip.install("github:iyalosovetsky/aqua/package.json")
    print("update---------------------------------------------------------------------------------update")
