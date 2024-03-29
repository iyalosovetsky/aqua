from secrets import topic_base



sub_base = b'/command'
pub_base = b'/state'

try:
    topics = {
        "topic_sub" : topic_base + sub_base,
        "topic_pub" : topic_base + pub_base,
        "topic_pub_info" : topic_base + pub_base + b'/info',
        "topic_pub_switch" : topic_base + pub_base + b'/switch',
        "topic_pub_pwm" : topic_base + pub_base + b'/pwm',
        "topic_sub_update" : (topic_base + sub_base + b'/update').decode("utf-8"),
        "topic_sub_switch" : (topic_base + sub_base + b'/switch').decode("utf-8"),
        "topic_sub_pwm" : (topic_base + sub_base + b'/pwm').decode("utf-8")
    }
    print("topic downloaded")
    
except Exception as e:
    print("topic have problem ")
    raise NameError('Topic not created')

try:
    if APP_ID == 'aqua':
        from aqua import aqua as app
    elif APP_ID == 'relay':
        from relay import relay as app
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

    
    mip.install("github:iyalosovetsky/aqua/lib/mqtt_bus/package.json")
    mip.install("github:iyalosovetsky/aqua/lib/utelnetserver/package.json")
    print("update---------------------------------------------------------------------------------update")


