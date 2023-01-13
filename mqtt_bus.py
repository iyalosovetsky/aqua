import machine

import network
import socket
import time
import ntptime

from umqtt.simple import MQTTClient

import re
import ubinascii

from secrets import secrets
from secrets import topics

class m_mqtt:
    mqtt_server = secrets['mqtt_server']
    mqtt_user = secrets['mqtt_user']
    mqtt_password = secrets['mqtt_password'] 
    mqtt_keepalive=7200

    client_id = ubinascii.hexlify(machine.unique_id())

    topic_sub = topics['topic_sub']
    topic_pub = topics['topic_pub']
    topic_pub_info = topics['topic_pub_info']
    topic_pub_switch = topics['topic_pub_switch']
    topic_pub_pwm = topics['topic_pub_pwm']
    topic_sub_switch = topics['topic_sub_switch']
    topic_sub_pwm = topics['topic_sub_pwm']

    message_intervalPop = 4
    message_intervalGS=120 #2 minute
    counter = 0
    error_mqtt = 0

    debugmode = 0

    def __init__(self, rt, station, app_cb, topics_list):
        #wifi class
        self.station = station
        
        #NTP init
        self.rtc=machine.RTC()
        self.ntp_secure()
        print(self.time_collect())
    
        #OS init
        rt['MQTTIN'] = {'last_start': time.time (), 'interval': 0.5, 'proc': self.process_in_msg , 'last_error': 0}
        rt['HELLO'] = {'last_start': time.time ()-90, 'interval': 121, 'proc': self.process_get_state , 'last_error': 0}
        rt['NTP'] = {'last_start': time.time ()-3590, 'interval': 3601, 'proc': self.process_ntp , 'last_error': 0}
        rt['HEALTH'] = {'last_start': time.time (), 'interval': 181, 'proc': self.process_mqtt_isconnected , 'last_error': 0}
        
        #CB
        self.app_cb = app_cb
        self.topics_list = topics_list
        
        
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
        print('Connected to %s MQTT broker' % (self.mqtt_server))
        ######################################
        for t in self.topics_list:
            client.subscribe(t)
            print(' 			subscribed to %s topic' % (t))
        client.subscribe(self.topic_sub_pwm)
        ######################################
        
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
                   self.app_cb(self.client, msg, topic)
                   return
           if val is not None: 
               self.showLed(val)
                   
               
        except Exception as e:
            print('Exception in sub_cb error_cnt', e)
      
    def publish(self, topic, value):
        self.client.publish(topic, value)
      



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
       
def test_cb():
    print("test")

#TODO updated working test code            
if __name__=='__main__':
    rt = {}
    topics = ('topic1', 'topic2')
    mqtt = m_mqtt(rt, station, test_cb, topics)
    #mqtt.connect_and_subscribe()
    mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()