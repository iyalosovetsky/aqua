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
import secrets as secrets0


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
    topic_sub_update = topics['topic_sub_update']

    counter = 0
    #error_mqtt = 0

    debugmode = 0

    def __init__(self, rt, station, app_obj):
        #wifi class
        self.station = station
        self.error_mqtt=0
        #NTP init
        self.rtc=machine.RTC()
        ntptime.settime() 
        print(self.time_collect())
    
        #OS init
        rt['MQTTIN'] = {'last_start': time.time (), 'interval': 0.5, 'proc': self.process_in_msg , 'last_error': 0}
        rt['HELLO'] = {'last_start': time.time ()-90, 'interval': 121, 'proc': self.process_get_state , 'last_error': 0}
        rt['NTP'] = {'last_start': time.time ()-3590, 'interval': 3601, 'proc': self.process_ntp , 'last_error': 0}
        rt['HEALTH'] = {'last_start': time.time (), 'interval': 181, 'proc': self.process_mqtt_isconnected , 'last_error': 0}
        
        #CB
        self.app_obj = app_obj
        try:
            print("Callback input message:", app_obj.app_cb)
            print("Needed topic:", app_obj.topic_getter())
            print("State of app", app_obj.state_app())
            print("Update app", self.update_app())
            try: 
                print("additional_procs:", app_obj.set_additional_proc(rt))
            except Exception as e:
                print("no additional_procs")
        except Exception as e:
            print('Not exist needed resources in app', e)
            
        
        
        #MQTT init
        self.client = None
        try:
            print('try to connect to MQTT broker')
            self.connect_and_subscribe()
        except OSError as e:
            print('mqtt bus not inited')

            self.restart_and_reconnect()

        self.publish(self.topic_pub+b'/ip',station.ifconfig()[0])
        print('mqtt bus inited')
        
    def update_app(self):
        self.publish(self.topic_pub+b'/update', "10 second")
        print("Update in 10 second ...")
        import time
        for i in range(10):
            time.sleep(1)
            print("Nuke in ", 10 - i, "seconds...")
        import _nuke.py
        return 0
    
    def restart_and_reconnect(self):  
      print('Too many errors. Reconnecting...')
      time.sleep(10)
      self.error_cnt = 0
      machine.reset()

    def connect_and_subscribe(self):
        self.error_mqtt+=1
        self.client = MQTTClient(client_id=self.client_id, port=1883,server=self.mqtt_server,user=self.mqtt_user, password=self.mqtt_password,keepalive=self.mqtt_keepalive)
        self.client.set_callback(self.sub_cb)
        self.client.connect()
        print('Connected to %s MQTT broker' % (self.mqtt_server))
        ######################################
        for t in self.app_obj.topic_getter():
            self.client.subscribe(t)
            print(' 			subscribed to %s topic' % (t))
        
        
        self.client.subscribe(self.topic_sub_update)
        print(' 			subscribed to %s topic' % (t))
        
        self.app_obj.client_setter(self.client)    
        ######################################

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
                if  self.error_mqtt>20:
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
        print(self.topic_sub_update, topic0)
        print(msg0,topic0)
        try:
           msg =  msg0.decode("utf-8")
           topic = topic0.decode("utf-8")
           
           if topic0 == self.topic_sub_update:
               print("start update")        
               self.update_app()
               print("exit update")        

               machine.reset()
               
               
           else :
               #print('Pico received ???',topic, msg)
               if self.client is None:
                   print('sub_cb: self.client is None',topic, msg)
               else:    
                   self.app_obj.app_cb(self.client, topic0, msg0)
               return
                   
               
        except Exception as e:
            print('Exception in sub_cb error_cnt', e)
            if topic0 == self.topic_sub_update:    
                machine.reset()
    
    
    def publish(self, topic, value):
        if self.client is not None:
            self.client.publish(topic, value)
      



    def process_get_state(self):
        self.counter += 1
        try:
            now = self.time_collect()
            msg = b'Hello %s #%d ip %s' % (now, self.counter, self.station.ifconfig()[0])
            self.publish(self.topic_pub_info, msg)
            self.app_obj.get_state(self.client)

            
        except Exception as e:
            print('process_get_state',e)
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
        try:
            updated_time = f'start UTC {self.rtc.datetime()[2]:02}.{self.rtc.datetime()[1]:02}.{self.rtc.datetime()[0]:04} {self.rtc.datetime()[4]:02}:{self.rtc.datetime()[5]:02}'
        except Exception as e:
            print('Exception to set ntptime',e)
            return None
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
    
    
    from secrets import secrets
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
    import secrets
    app_m = secrets.app.app()

    mqtt = m_mqtt(rt, station, app_m)
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()
    while(1):
        mqtt.process_in_msg()
        mqtt.process_get_state()
#         process_ntp
#         process_mqtt_isconnected

