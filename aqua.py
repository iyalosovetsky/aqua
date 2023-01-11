import network
import socket

from picozero import pico_temp_sensor, pico_led

from machine import Pin, PWM


import time

from umqtt.simple import MQTTClient

import re
import ubinascii
import machine
import ntptime

mqtt_server = '10.80.39.78'
mqtt_user='igor'
mqtt_password='p29041971' 

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'house/picoa/command'
topic_pub = b'house/picoa/state'


topic_pub_info=topic_pub+b'/info'
topic_pub_switch=topic_pub+b'/switch'
topic_pub_pwm=topic_pub+b'/pwm'

topic_sub_switch=(topic_sub+b'/switch').decode("utf-8")
topic_sub_pwm=(topic_sub+b'/pwm').decode("utf-8")


mqtt_keepalive=7200


message_intervalPop = 4
message_intervalGS=120 #2 minute
error_cnt=0






counter = 0
error_cnt = 0
error_cnt_others = 0
error_mqtt = 0

debugmode = 0

MAX_VALUE = 100000
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 18000 # ~40% 
HALF_MODE  = 38000 # ~40% 
ON_MODE    = HALF_MODE # ~80% 
NIGHT_MODE = QUARTER_MODE # ~10% 

pwm_val=NIGHT_MODE


pico_led.on() 
p0 = Pin(0, Pin.OUT)    # create output pin on GPIO0
pwm = PWM(p0)          # create a PWM object on a pin
pwm.duty_ns(pwm_val)     # set duty to 50%
pwm.freq(10_000)  # 100_000


def restart_and_reconnect():
  print('Too many errors. Reconnecting...')
  time.sleep(10)
  error_cnt = 0
  machine.reset()




    
def showLed(val):
    global pwm_val
    print("showLed: ",val) 
    pwm_val=val
    pwm.duty_ns(MAX_VALUE-val)     




def sub_cb(topic0, msg0):
    global error_cnt, debugmode
    global testmode
    print(msg0,topic0)
    try:
       msg =  msg0.decode("utf-8")
       topic = topic0.decode("utf-8")
       val = None
       sw = None
       is_command = False
       
       if re.search("\D", msg)  is None:
           # is digit
           if topic == topic_sub_pwm:
               val0=int(msg)
               if not (val0 <MIN_VALUE or val0 >MAX_VALUE):
                   val = val0
               else:
                   print('bad value %s'%(msg,))
       else:
           # is alpha
          if topic == topic_sub_switch and msg.upper()=='ON':
               if  pwm_val>MAX_VALUE/10:
                   val = pwm_val
                   print('already on')
               else:    
                   val = HALF_MODE
               sw = 'ON'
               is_command = True
               
          elif topic == topic_sub_switch and msg.upper()=='OFF':
               if  pwm_val<=OFF_MODE:
                   val = pwm_val
                   print('already off')
               else:    
                   val = OFF_MODE
               sw = 'OFF'
               is_command = True
          elif topic == topic_sub_switch and msg.upper()=='NIGHT':
               val = NIGHT_MODE
               sw = 'ON'
               is_command = True
          elif topic == topic_sub_switch and msg.upper()=='HALF':
               val = HALF_MODE
               sw = 'ON'
               is_command = True
          elif topic == topic_sub_switch and msg.upper()=='QUARTER':
               val = QUARTER_MODE
               sw = 'ON'
               is_command = True
          elif topic == topic_sub_switch and  msg.startswith('DEBUG'):
            if msg!='DEBUG' : 
              debugmode=int(msg.replace('DEBUG',''))
            else:
              debugmode=1
            msgpub=f'Pico received DEBUG %d'%(debugmode,)
            publish(topic_pub_info, msgpub)
          elif topic == topic_sub_switch or  topic == topic_sub_pwm:
            msgpub=f'Pico received unknown %s'%(msg,)              
            publish(topic_pub_info, msgpub)
          else :
            print('Pico received ???',topic, msg)
       if val is not None: 
           showLed(val)
           msgpub=f'%d'%(pwm_val,)              
           publish(topic_pub_pwm, msgpub)
           if is_command:
               publish(topic_pub_switch, sw)
           
    except Exception as e:
        print('Exception error_cnt',error_cnt, e)

  

def connect_and_subscribe():
  global client_id, mqtt_server, mqtt_user,mqtt_password, mqtt_keepalive, topic_sub, error_mqtt
  error_mqtt+=1
  client = MQTTClient(client_id=client_id, port=1883,server=mqtt_server,user=mqtt_user, password=mqtt_password,keepalive=mqtt_keepalive)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub_switch)
  client.subscribe(topic_sub_pwm)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client


  
def publish(topic, value):
    client.publish(topic, value)
  



def process_get_state():
    global counter
    counter += 1
    try:
        now=f'UTC {rtc.datetime()[2]:02}.{rtc.datetime()[1]:02}.{rtc.datetime()[0]:04} {rtc.datetime()[4]:02}:{rtc.datetime()[5]:02}'
        msg = b'Hello %s #%d ip %s' % (now, counter, station.ifconfig()[0])
        publish(topic_pub_info, msg)
        msg = b'%d'%(MAX_VALUE-pwm_val,)
        publish(topic_pub_pwm, msg)
        publish(topic_pub_switch, b'ON')

        
    except Exception as e:
        print('process_ed',e)
        return -4
    else:
        return 0
        


def process_show_error():
    try:
        msg = b'Try to reboot device #%d ip %s' % (counter, station.ifconfig()[0])
        publish(topic_pub, msg)
        return 0
    except Exception as e:
        print('process_show_error',e)
        return -2

def process_ntp():
    try:
        ntptime.settime() 
        print(f'start UTC {rtc.datetime()[2]:02}.{rtc.datetime()[1]:02}.{rtc.datetime()[0]:04} {rtc.datetime()[4]:02}:{rtc.datetime()[5]:02}')
        return 0
    except Exception as e:
        print('Exception to set ntptime',e)
        return -1

def process_in_msg():
    try:
      client.check_msg()
    except Exception as e:
        print('process_in_msg error',e)
        process_mqtt_isconnected()
        print('process_in_msg error after')
        
        return -2
    else:
        return 0
   
    
def process_mqtt_isconnected():
    try:
        client.ping()
        client.ping()
    except:
        print("\nlost connection to mqtt broker...")
        try:
          client.disconnect()
        except Exception as e:
            print('process_mqtt_isconnected fail disconnect',e)
        try:
            if error_mqtt>20:
                print('process_mqtt_isconnected will reboot..' )
                restart_and_reconnect()
            connect_and_subscribe()
            return 1
        except Exception as e:
            print('process_mqtt_isconnected fail reconnect',e)
            return -5
    else:
        return 0
    
  




rt={}
rt['MQTTIN'] = {'last_start': time.time (), 'interval': 0.5, 'proc': process_in_msg , 'last_error': 0}
rt['HELLO'] = {'last_start': time.time ()-90, 'interval': 121, 'proc': process_get_state , 'last_error': 0}
rt['NTP'] = {'last_start': time.time ()-3590, 'interval': 3601, 'proc': process_ntp , 'last_error': 0}
rt['HEALTH'] = {'last_start': time.time (), 'interval': 181, 'proc': process_mqtt_isconnected , 'last_error': 0}

 
 

    

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







try:
    print('try to connect to MQTT broker')
    client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

rtc=machine.RTC()
ntptime.settime() 
print(f'start UTC {rtc.datetime()[2]:02}.{rtc.datetime()[1]:02}.{rtc.datetime()[0]:04} {rtc.datetime()[4]:02}:{rtc.datetime()[5]:02}')

pico_led.on()

def aquaProceed(station):
    publish(topic_pub+b'/ip',station.ifconfig()[0])

    while True:
        try:
            p_RTLoop()
        except OSError as e:
            error_cnt +=1
            print('OSError error_cnt',error_cnt, e)
            try:
                process_show_error()
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
        


 






        


# 
