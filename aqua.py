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

MAX_VALUE = 100000
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 18000 # ~40% 
HALF_MODE  = 38000 # ~40% 
ON_MODE    = HALF_MODE # ~80% 
NIGHT_MODE = QUARTER_MODE # ~10% 


class m_mqtt:
    mqtt_server = '10.80.39.78'
    mqtt_user='igor'
    mqtt_password='p29041971' 
    mqtt_keepalive=7200

    client_id = ubinascii.hexlify(machine.unique_id())

    topic_sub = b'house/picot/command'
    topic_pub = b'house/picot/state'
    topic_pub_info=topic_pub+b'/info'
    topic_pub_switch=topic_pub+b'/switch'
    topic_pub_pwm=topic_pub+b'/pwm'
    topic_sub_switch=(topic_sub+b'/switch').decode("utf-8")
    topic_sub_pwm=(topic_sub+b'/pwm').decode("utf-8")

    message_intervalPop = 4
    message_intervalGS=120 #2 minute
    error_cnt=0
    counter = 0
    error_cnt = 0
    error_cnt_others = 0
    error_mqtt = 0

    debugmode = 0


    pwm_val=NIGHT_MODE
    def __init__(self):
        #pico_led.on() 

        #PWM init
        self.p0 = Pin(0, Pin.OUT)    # create output pin on GPIO0
        self.pwm = PWM(self.p0)          # create a PWM object on a pin
        self.pwm.duty_ns(self.pwm_val)     # set duty to 50%
        self.pwm.freq(10_000)  # 100_000
    
        #OS init
        self.rt={}
        self.rt['MQTTIN'] = {'last_start': time.time (), 'interval': 0.5, 'proc': self.process_in_msg , 'last_error': 0}
        self.rt['HELLO'] = {'last_start': time.time ()-90, 'interval': 121, 'proc': self.process_get_state , 'last_error': 0}
        self.rt['NTP'] = {'last_start': time.time ()-3590, 'interval': 3601, 'proc': self.process_ntp , 'last_error': 0}
        self.rt['HEALTH'] = {'last_start': time.time (), 'interval': 181, 'proc': self.process_mqtt_isconnected , 'last_error': 0}

        #MQTT init
        try:
            print('try to connect to MQTT broker')
            self.client = self.connect_and_subscribe()
        except OSError as e:
            self.restart_and_reconnect()

        #NTP init
        self.rtc=machine.RTC()
        ntptime.settime() 
        print(f'start UTC {self.rtc.datetime()[2]:02}.{self.rtc.datetime()[1]:02}.{self.rtc.datetime()[0]:04} {self.rtc.datetime()[4]:02}:{self.rtc.datetime()[5]:02}')
        

    def restart_and_reconnect(self):
      print('Too many errors. Reconnecting...')
      time.sleep(10)
      self.error_cnt = 0
      machine.reset()

    def connect_and_subscribe(self):
        print("connect_and_subscribe")
        #global client_id, mqtt_server, mqtt_user,mqtt_password, mqtt_keepalive, topic_sub, error_mqtt, client
        self.error_mqtt+=1
        client = MQTTClient(client_id=self.client_id, port=1883,server=self.mqtt_server,user=self.mqtt_user, password=self.mqtt_password,keepalive=self.mqtt_keepalive)
        client.set_callback(self.sub_cb)
        client.connect()
        client.subscribe(self.topic_sub_switch)
        client.subscribe(self.topic_sub_pwm)
        print('Connected to %s MQTT broker, subscribed to %s topic' % (self.mqtt_server, self.topic_sub))
        return client

    def process_mqtt_isconnected(self):
        try:
            self.client.ping()
            self.client.ping()
        except:
            print("\nlost connection to mqtt broker...")
            try:
              self.client.disconnect()
            except Exception as e:
                print('process_mqtt_isconnected fail disconnect',e)
            try:
                if error_mqtt>20:
                    print('process_mqtt_isconnected will reboot..' )
                    self.restart_and_reconnect()
                self.connect_and_subscribe()
                return 1
            except Exception as e:
                print('process_mqtt_isconnected fail reconnect',e)
                return -5
        else:
            return 0
        
        
    def showLed(self,val):
    #     global pwm_val
    #     print("showLed: ",val) 
    #     pwm_val=val
    #     pwm.duty_ns(MAX_VALUE-val)     
        pico_led.on() 




    def sub_cb(self,topic0, msg0):
        print("sub_cb", msg0,topic0)
        try:
            msg =  msg0.decode("utf-8")
            topic = topic0.decode("utf-8")
            val = None
            sw = None
            is_command = False

            if re.search("\D", msg)  is None:
                # is digit
                if topic == self.topic_sub_pwm:
                    val0=int(msg)
                    if not (val0 <MIN_VALUE or val0 >MAX_VALUE):
                        print("sub_cb digit value", val0)
                        self.pwm_val = val0
                    else:
                        print('bad value %s'%(msg,))   
            else:
                # is alpha
                if topic == self.topic_sub_switch and msg.upper()=='ON':
                    print("sub_cb alpha", "ON")
                    sw = 'ON'
                    is_command = True                    
                elif topic == topic_sub_switch and msg.upper()=='OFF':
                    print("sub_cb alpha", "OFF")
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
                        self.debugmode=int(msg.replace('DEBUG',''))
                    else:
                        self.debugmode=1
                    msgpub=f'Pico received DEBUG %d'%(self.debugmode,)
                    self.publish(self.topic_pub_info, msgpub)
                elif topic == self.topic_sub_switch or  topic == self.topic_sub_pwm:
                    msgpub=f'Pico received unknown %s'%(msg,)              
                    self.publish(self.topic_pub_info, msgpub)
                else :
                    print('Pico received ???',topic, msg)
            if val is not None: 
                self.showLed(val)
                msgpub=f'%d'%(self.pwm_val,)              
                self.publish(topic_pub_pwm, msgpub)
                if is_command:
                    self.publish(self.topic_pub_switch, sw)
               
        except Exception as e:
            print('Exception error_cnt',self.error_cnt, e)
      
    def publish(self, topic, value):
        self.client.publish(topic, value)
        print("publish", topic, value)
      



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
       
        

    def p_RTLoop(self):
        for key, value in self.rt.items ():
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


    def aquaProceed(self, station):
        self.publish(self.topic_pub+b'/ip',station.ifconfig()[0])
        print("start")
        while True:
            try:
                self.p_RTLoop()
            except OSError as e:
                self.error_cnt +=1
                print('OSError error_cnt',self.error_cnt, e)
                try:
                    self.process_show_error()
                except Exception as e:
                    print('cant broadcast error', e)
                if self.error_cnt>10: 
                    print('OSError restart_and_reconnect()')
                    self.restart_and_reconnect()
            except Exception as e:
                self.error_cnt_others +=1
                print('Exception error_cnt',self.error_cnt_others, e)
                if self.error_cnt>100:
                   print('Exception restart_and_reconnect()')
                   self.restart_and_reconnect()
            
if __name__=='__main__':
    mqtt = m_mqtt()
    #mqtt.connect_and_subscribe()
    mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()