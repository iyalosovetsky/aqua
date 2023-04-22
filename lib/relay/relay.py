import re

from machine import Pin, PWM

from secrets import topics
import time 
from picozero import pico_temp_sensor, pico_led
from time import ticks_ms
import json 
import os
import re


SWITCH_INVERSE = True
SWITCHES = [22,10,11,12]  
RELAYS = [21,20,19,18,17,16,15,14]     
RELAYS_AUTOOFF = [10,20,30,40,0,0,0,0]     
BOUNCE_TIME =  0.02 

switches = []
config_relay=[]

def int_handler(pin):
    global switches
    pin.irq(handler = None)
    last_state = pin.value()

    stop = ticks_ms() + (BOUNCE_TIME * 1000)
    pico_led.on()
    while ticks_ms() < stop:
        # keep checking, reset the stop if the value changes
        if pin.value() != last_state:
            stop = ticks_ms() + (BOUNCE_TIME )
            last_state = pin.value()
    pico_led.off()

    id = int(''.join(char for char in str(pin) if char.isdigit()))
    
    
    if switches is not None:
        event=0
        pp=None
        for p in switches:
            if p["pinN"] == id:
                #print("Found", p)
                if p['state'] != last_state :
                    p['event']=1
                    event=1
                    p['state'] = last_state
                    pp =p
        if event == 1:        
            print( 'switches is ', pp)
    pin.irq(handler = int_handler)

class switch:
    def __init__(self,pins,relays):
        global switches
        self.sw=[]
        self.relay=[]
        switches = self.sw
        for p in pins:
            self.sw.append({"pinN":p,"time": time.time(), "state": None, "obj": None, 'event': None})
        for p in relays:
            self.relay.append({"pinN":p,"time": time.time(), "state": None, "obj": None, 'event': None})
        
        self.update_cfg_from_file()    
        self.init_sw()
        

        
    def Relay_CHx(self,n,value): 
        if value == 1:
            self.relay[n]["obj"].high()
            if self.relay[n]['state'] != 1:
              self.relay[n]['event'] = 1
              self.relay[n]["time"] = time.time()
            self.relay[n]['state'] = 1
        else:
            self.relay[n]["obj"].low()
            if self.relay[n]['state'] != 0:
              self.relay[n]['event'] = 1
              self.relay[n]["time"] = time.time()
            self.relay[n]['state'] = 0
    
    def init_sw(self): 
        for p in self.sw:
            if p["state"] is None:
                p["obj"]=Pin(p["pinN"], Pin.IN, Pin.PULL_UP)
                p["state"]=p["obj"].value()
                p["obj"].irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = int_handler)
        for i, p in enumerate(self.relay):
            if p["state"] is None:
                p["obj"]=Pin(p["pinN"], Pin.OUT)
                p["autoOFFInterval"]=-1 # seconds
                p["OFFAt"]=[] # [5.30,12.40]
                p["ONAt"]= [] # [5.30,12.40]
                self.Relay_CHx(i,0)
                #print(p,"p after init")
        #print(self.relay,"self.relay after init")   
        
    def update_cfg_from_fileOne(self, typeJson):
        files=[ff for ff in os.listdir() if ff.endswith('.json') and ff.startswith('cfg_') ]    
        newcfg = False 
        obj= None
        if typeJson == 'relay':
            obj =self.relay
        elif  typeJson == 'sw':
            obj =self.sw
        else:
            print("update_cfg_from_file: unkn type ",typeJson)           
        if 'cfg_'+typeJson+'.json' in files:
            data=None
            with open('cfg_'+typeJson+'.json', 'r') as f:
                data=json.load(f)
            if isinstance(data,(list,tuple)):
                for i, item in enumerate(data) :
                    if not isinstance(item,dict):
                        print("update_cfg_from_file: pin item is not dict, skip ",i, item)    
                    elif i+1 > len(obj):
                        print("update_cfg_from_file: pin out of range",i)    
                    else:
                        obj[i].update(item)
                        print("update_cfg_from_file: pin ->", i,obj[i])    
                        newcfg = True      
            if newcfg :
                print("update_cfg_from_fileOne: "+typeJson+" is OK")    


    def update_cfg_from_file(self):
        files=[ff for ff in os.listdir() if ff.endswith('.json') and ff.startswith('cfg_') ]    
        newcfgRelay = False      
        if 'cfg_relay.json' in files:
            self.update_cfg_from_fileOne('relay')
        if 'cfg_sw.json' in files:
            self.update_cfg_from_fileOne('sw')



class app:
    topic_pub_info = topics['topic_pub_info']
    topic_pub_switch = topics['topic_pub_switch']
    topic_pub_relay = topics['topic_pub_relay']
    topic_sub_relay = topics['topic_sub_relay']
    debugmode = 0
    
    def __init__(self):
        self.client = None
        self.picoRelayB = switch(SWITCHES, RELAYS)
        print('relay inited')
    
    def debugmode_setter(self):
        self.debugmode = 1

    def no_debugmode_setter(self):
        self.debugmode = 0

    def applySw(self):
        for i,p in enumerate(self.picoRelayB.sw):
            if i>len(self.picoRelayB.relay) or  p['event'] != 1:
                continue
            val = (1-p['state']) if SWITCH_INVERSE else p['state']
            p['event'] = 0
            change= False
            if val != self.picoRelayB.relay[i]['state'] :
                self.picoRelayB.Relay_CHx(i,val)
                change = True
            elif val != self.picoRelayB.relay[i]['obj'].value():
                self.picoRelayB.Relay_CHx(i,val)
                change = True
            if change and self.client is not None:    
                self.client.publish(self.topic_pub_relay+str(i), (b'ON' if val else b'OFF'))
    

    
    def client_setter(self, client):
        self.client = client
        print('client_setter',self.client)

    def set_additional_proc(self, rt):    
        self.rt =  rt
        self.rt['APPLYSW'] = {'last_start': time.time (), 'interval': 0.2, 'proc': self.applySw , 'last_error': 0}
        return self.rt


        
    def get_state(self, client):
        for i,p in enumerate(self.picoRelayB.sw):
                val = (1-p['state']) if SWITCH_INVERSE else p['state']
                msg = (b'ON' if val else b'OFF')
                client.publish(self.topic_pub_switch+str(i), msg)
        for i,p in enumerate(self.picoRelayB.relay):
                val = p['state']
                msg = (b'ON' if val else b'OFF')
                client.publish(self.topic_pub_relay+str(i), msg)

    
    def topic_getter(self):
        return [self.topic_sub_relay+str(n) for n in range(len(RELAYS))]
        
    def state_app(self):
        return {"sw":self.picoRelayB.sw,"relay":self.picoRelayB.relay}
    
    def parseConfig(self):
        global config_relay
        print('parseConfig:  config_relay ', config_relay)
        if not isinstance(config_relay,dict):
            config_relay={}
            print('parseConfig:  bad config ')
            return 
        newcfgRelay = False
        newcfgSw = False
        if config_relay.get("relay") is not None and isinstance(config_relay["relay"],(list,tuple)) :
                for i, item in enumerate(config_relay["relay"]) :
                    if not isinstance(item,dict):
                        print("parseConfig: relay item is not dict, skip ",i, item)    
                    elif i+1 > len(self.picoRelayB.relay):
                        print("parseConfig: relay out of range",i)    
                    else:
                        self.picoRelayB.relay[i].update(item)
                        print("parseConfig: relay ->", i,self.picoRelayB.relay[i])    
                        newcfgRelay = True

        if config_relay.get("sw") is not None and isinstance(config_relay["sw"],(list,tuple)):
                for i, item in enumerate(config_relay["sw"]) :
                    if not isinstance(item,dict):
                        print("parseConfig: sw item is not dict, skip ",i, item)    
                    elif i+1 > len(self.picoRelayB.sw):
                        print("parseConfig: sw out of range",i)    
                    else:
                        self.picoRelayB.sw[i].update(item)
                        print("parseConfig: sw ->", i,self.picoRelayB.sw[i])
                        newcfgSw = True
        if newcfgSw :
            str = json.dumps(self.picoRelayB.sw)
            os.remove("cfg_sw.json")
            with open('cfg_sw.json', 'w') as f:
                f.write(re.sub(r'"obj": Pin\(.+?\),',"   ",str))                
        if newcfgRelay :
            str = json.dumps(self.picoRelayB.relay)
            os.remove("cfg_relay.json")
            with open('cfg_relay.json', 'w') as f:
                f.write(re.sub(r'"obj": Pin\(.+?\),',"   ",str))                

        

    def app_cb(self, client, topic0, msg0):
        print(msg0,topic0)
        global config_relay
        try:
            msg =  msg0.decode("utf-8")
            topic = topic0.decode("utf-8")
            val = None
            sw = None
            swN = None
            is_command = False
            is_config = False
            if topic.startswith(self.topic_sub_relay):
                swN=int(''.join(char for char in str(topic) if char.isdigit()))
                if (swN+1)>len(RELAYS):
                    print('Pico received bad relay N ???',topic, msg)
                    return
                if msg.upper()=='ON':
                   sw = 'ON'
                   is_command = True
                   val = 1
                elif msg.upper()=='OFF':
                   sw = 'OFF'
                   is_command = True
                   val = 0
                elif (msg.startswith('{') and msg.endswith('}')) or (msg.startswith('[') and msg.endswith(']')) :
                   is_config = True
                   try:
                     config_relay= json.loads(msg)
                     self.parseConfig()
                   except Exception as e:
                     print('Exception in app_cb  json load ', msg, e)
                else :
                    print('Pico received ???',topic, msg)
                    return
                if val is not None: 
                    self.picoRelayB.Relay_CHx(swN,val)
                    client.publish(self.topic_pub_relay+str(swN), (b'ON' if val else b'OFF'))
                    



        except Exception as e:
            print('Exception in app_cb ', e)
      

      



#TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()




