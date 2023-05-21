import mip
secrets = {
    "ssid" : "******",
    "password" : "****************",
    "mqtt_server" : "10.80.39.**",
    "mqtt_user" : "**********",
    "mqtt_password" : "**********"
}

APP_ID='solar'
topic_base = b'house/picotest'

if APP_ID == 'aqua':
    topic_base = b'house/picoa'
elif APP_ID == 'relay':
    topic_base = b'house/relay'
elif APP_ID == 'solar':
    topic_base = b'house/pico'


sub_base = b'/command'
pub_base = b'/state'
if APP_ID == 'solar':
    sub_base = b'/in'
    pub_base = b'/out'



try:
   topics = {
        "topic_sub" : topic_base + sub_base,
        "topic_pub" : topic_base + pub_base,
        "topic_pub_info" : topic_base + pub_base + b'/info',
        "topic_pub_switch" : topic_base + pub_base + b'/switch',
        "topic_pub_relay" : (topic_base + pub_base + b'/relay').decode("utf-8"),
        "topic_pub_pwm" : topic_base + pub_base + b'/pwm',
        "topic_sub_update" : (topic_base + sub_base + b'/update').decode("utf-8"),
        "topic_sub_switch" : (topic_base + sub_base + b'/switch').decode("utf-8"),
        "topic_sub_pwm" : (topic_base + sub_base + b'/pwm').decode("utf-8"),
        "topic_sub_relay" : (topic_base + sub_base + b'/relay').decode("utf-8")}
   print("topic downloaded")
    
except Exception as e:
    print("topic have problem ")
    raise NameError('Topic not created')

#try:
#    if APP_ID == 'aqua':
#        from aqua import aqua as app
#    elif APP_ID == 'relay':
#        from relay import relay as app
#    from mqtt_bus import mqtt_bus
#    from utelnetserver import utelnetserver
#    code_exist = True
#except:
#    code_exist = False


try:
    if APP_ID == 'aqua':
        from aqua import aqua as app
    elif APP_ID == 'relay':
        from relay import relay as app
    elif APP_ID == 'solar':
        from solar import solar as app
    from mqtt_bus import mqtt_bus
    from utelnetserver import utelnetserver
    code_exist = True
except:
    code_exist = False


def codeImport():
    mip.install("github:RaspberryPiFoundation/picozero/picozero/__init__.py", target="/lib/picozero")
    mip.install("github:RaspberryPiFoundation/picozero/picozero/picozero.py", target="/lib/picozero")
    
    if APP_ID == 'aqua':
        mip.install("github:iyalosovetsky/aqua/lib/aqua/package.json")
    elif APP_ID == 'relay':
        mip.install("github:iyalosovetsky/aqua/lib/relay/package.json")
    elif APP_ID == 'solar':
        mip.install("github:iyalosovetsky/aqua/lib/pi18/package.json")
        mip.install("github:iyalosovetsky/aqua/lib/solar/package.json")

    mip.install("github:iyalosovetsky/aqua/lib/mqtt_bus/package.json")
    mip.install("github:iyalosovetsky/aqua/lib/utelnetserver/package.json")
    print("update---------------------------------------------------------------------------------update")
    
