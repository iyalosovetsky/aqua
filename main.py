import network
import socket
import time
import ntptime
from picozero import pico_temp_sensor, pico_led

try:
    from secrets import secrets
except Exception as e:
    print('from secrets import secrets FAIL',e)
    print('File secrets not exist')

try:
    from secrets import topics
except:
    print('File topics not exist')


pico_led.off() 

rt={}
error_cnt = 0
error_cnt_others = 0

def update():
#     secrets.codeImport()
#     time.sleep(10)
#     machine.reset()
    pico_led.on() 
    time.sleep(10)
    return 0

# restart function 
def restart_and_reconnect():  
    print('Too many errors. Reconnecting...')
    time.sleep(10)
    error_cnt = 0
    machine.reset()

# ekraning self.process_show_error()
def publish_error(class_low):
    try:
        class_low.process_show_error()
    except Exception as e:
        print("in function process_show_error() occur error", e)

# OS worker 
def p_RTLoop():
    for key, value in rt.items ():
        l_time = time.time ()
        l_timeprev = value['last_start']
        if value['proc'] is not None:
            if (((l_time - l_timeprev) > value['interval'])) :
                value['last_start'] = l_time
                try:  
                    value['last_error'] = value['proc'] ()
                    if value['last_error'] is None:
                        value['last_error'] = 0
                except Exception as e:
                    value['last_error'] = -97
                    print ('error rt ' + key, e)

# ekraning RTLoop into exceptions
def OSProceed(class_low, station):
    
    while True:
        try:
            p_RTLoop()
        except OSError as e:
            error_cnt +=1
            print('OSError error_cnt',error_cnt, e)
            try:
                publish_error(class_low)
            except Exception as e:
                print('cant broadcast error', e)
            if error_cnt>10: 
                print('OSError restart_and_reconnect()')
                restart_and_reconnect()
        except Exception as e:
            error_cnt_others +=1
            print('Exception error_cnt',error_cnt_others, e)
            if error_cnt>100:
               print('Exception restart_and_reconnect()')
               restart_and_reconnect()


#check wifi connection
ssid = secrets['ssid']
password = secrets['password']


station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

if station.isconnected() == False:
    while station.isconnected() == False:
      pass

    print('Connection successful')
    
print(station.ifconfig())
print('----------')


# delay for initialize ntp
pico_led.on() 
time.sleep(9)
pico_led.off() 
ntptime.settime()

#add callback to OS
#TODO change last.start
rt['UPDATE'] = {'last_start': time.time (), 'interval': 86400, 'proc': update , 'last_error': 0}

# download code if code not exist
try:
    import secrets
    if not secrets.code_exist:
        print("Try download code")
        update()
    else:    
        print("app successful imported")
except Exception as e:
    print("problem with downloading code", e)
    
# run app    
try:
    app_m = secrets.app.app()
    mqtt = secrets.mqtt_bus.m_mqtt(rt, station, app_m)
    print(rt)
    OSProceed(mqtt, station)
except Exception as e:
    print("problem with downloaded code", e)



