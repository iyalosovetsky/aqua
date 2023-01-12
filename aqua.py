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
from secrets import secrets

MAX_VALUE = 100000
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 18000 # ~40% 
HALF_MODE  = 38000 # ~40% 
ON_MODE    = HALF_MODE # ~80% 
NIGHT_MODE = QUARTER_MODE # ~10% 

def test_cb(topic0, msg0):
    print("test_cb", topic0, msg0 )
class m_mqtt:
    mqtt_server = secrets['mqtt_server']
    mqtt_user = secrets['mqtt_user']
    mqtt_password = secrets['mqtt_password'] 
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
    counter = 0
    error_mqtt = 0

    debugmode = 0


    pwm_val=NIGHT_MODE
    switch_val = 'ON'
    def __init__(self, rt, station):
        #wifi class
        self.station = station
        
        #NTP init
        self.rtc=machine.RTC()
        self.ntp_secure()
        print(self.time_collect())
        
        #PWM init
        self.p0 = Pin(0, Pin.OUT)    # create output pin on GPIO0
        self.pwm = PWM(self.p0)          # create a PWM object on a pin
        self.pwm.duty_ns(self.pwm_val)     # set duty to 50%
        self.pwm.freq(10_000)  # 100_000
    
        #OS init

        rt['MQTTIN'] = {'last_start': time.time (), 'interval': 0.5, 'proc': self.process_in_msg , 'last_error': 0}
        rt['HELLO'] = {'last_start': time.time ()-90, 'interval': 121, 'proc': self.process_get_state , 'last_error': 0}
        rt['NTP'] = {'last_start': time.time ()-3590, 'interval': 3601, 'proc': self.process_ntp , 'last_error': 0}
        rt['HEALTH'] = {'last_start': time.time (), 'interval': 181, 'proc': self.process_mqtt_isconnected , 'last_error': 0}
        
        
        #MQTT init
        try:
            print('try to connect to MQTT broker')
            self.client = self.connect_and_subscribe()
        except OSError as e:
            self.restart_and_reconnect()

        self.publish(self.topic_pub+b'/ip',station.ifconfig()[0])


    def restart_and_reconnect(self):  
      print('Too many errors. Reconnecting...')
      time.sleep(10)
      self.error_cnt = 0
      machine.reset()

    def connect_and_subscribe(self):
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
        
        
    def showLed(self, val, pub=True):

        print("showLed: ",val, pub) 
        self.pwm.duty_ns(MAX_VALUE-val)
        if pub:
            self.pwm_val=val
            msgpub=f'%d'%(self.pwm_val,)              
            self.publish(self.topic_pub_pwm, msgpub)



    def switchLed(self, val0):
        
        val = val0.upper()
        if val != 'ON' and  val != 'OFF':
            print("switchLed: bad command ",val0)
            return
        
        if self.switch_val==val:
           print("switchLed: already ",self.switch_val) 
           return
            
        self.switch_val=val
        print("switchLed: ", self.switch_val)
        self.publish(self.topic_pub_switch, self.switch_val)
        
        if val=='ON':
            self.showLed(self.pwm_val, False)
            pico_led.on()
            
        if val=='OFF':
            self.showLed(OFF_MODE, False)
            pico_led.off()


    def sub_cb(self,topic0, msg0):

        print(msg0,topic0)
        try:
           msg =  msg0.decode("utf-8")
           topic = topic0.decode("utf-8")
           val = None
           sw = None
           is_command = False
           if topic == self.topic_sub_pwm:
               if re.search("\D", msg)  is None:
                   val0=int(msg)
                   if not (val0 <MIN_VALUE or val0 >MAX_VALUE):
                       val = val0
                   else: 
                       print('bad value %s'%(msg,))
               elif msg.upper()=='ON' or msg.upper()=='OFF':
                   self.switchLed(msg)
                   return
                   
               
           elif topic == self.topic_sub_switch:
              if msg.upper()=='ON':
                   sw = 'ON'
                   is_command = True
                   val = HALF_MODE
              elif msg.upper()=='OFF':
                   sw = 'OFF'
                   is_command = True
                   val = OFF_MODE
              elif msg.upper()=='NIGHT':
                   val = NIGHT_MODE
                   sw = 'ON'
                   is_command = True
              elif msg.upper()=='HALF':
                   val = HALF_MODE
                   sw = 'ON'
                   is_command = True
              elif msg.upper()=='QUARTER':
                   val = QUARTER_MODE
                   sw = 'ON'
                   is_command = True
              elif msg.startswith('DEBUG'):
                   if msg!='DEBUG' : 
                       self.debugmode=int(msg.replace('DEBUG',''))
                   else:
                       self.debugmode=1
                   msgpub=f'Pico received DEBUG %d'%(self.debugmode,)
                   self.publish(self.topic_pub_info, msgpub)
                   return 
              elif topic == self.topic_sub_switch or  self.topic == topic_sub_pwm:
                   msgpub=f'Pico received unknown %s'%(msg,)              
                   self.publish(self.topic_pub_info, msgpub)
                   return
              else :
                   print('Pico received ???',topic, msg)
                   return
           if val is not None: 
               self.showLed(val)
                   
               
        except Exception as e:
            print('Exception in sub_cb error_cnt', e)
      
    def publish(self, topic, value):
        self.client.publish(topic, value)
        #print("publish", topic, value)
      



    def process_get_state(self):
        self.counter += 1
        try:
            now = self.time_collect()
            msg = b'Hello %s #%d ip %s' % (now, self.counter, self.station.ifconfig()[0])
            self.publish(self.topic_pub_info, msg)
            msg = b'%d'%(self.pwm_val,)
            print('process_get_state:',self.switch_val, self.pwm_val)
            self.publish(self.topic_pub_pwm, msg)
            self.publish(self.topic_pub_switch, self.switch_val)

            
        except Exception as e:
            print('process_ed',e)
            return -4
        else:
            return 0
            


    def process_show_error(self):
        try:
            msg = b'Try to reboot device #%d ip %s' % (self.counter, self.station.ifconfig()[0])
            self.publish(self.topic_pub, msg)
            return 0
        except Exception as e:
            print('process_show_error',e)
            return -2
        
    def time_collect(self):
        updated_time = f'start UTC {self.rtc.datetime()[2]:02}.{self.rtc.datetime()[1]:02}.{self.rtc.datetime()[0]:04} {self.rtc.datetime()[4]:02}:{self.rtc.datetime()[5]:02}'
        return updated_time    
    
    def ntp_secure(self):
        try:
            ntptime.settime()
            return self.rtc
        except Exception as e:
            print('Exception to set ntptime',e)
            return None
        
    def process_ntp(self):
        try:
            ntptime.settime()
            print(self.time_collect())
            return 0
        except Exception as e:
            print('Exception to set ntptime',e)
            return -1

    def process_in_msg(self):
        try:
          self.client.check_msg()
        except Exception as e:
            print('process_in_msg error',e)
            self.process_mqtt_isconnected()
            print('process_in_msg error after')
            
            return -2
        else:
            return 0
       
        


#TODO updated working test code            
if __name__=='__main__':
    ntptime.settime()
    rt = {}
    mqtt = m_mqtt(rt, station)
    #mqtt.connect_and_subscribe()
    mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()

