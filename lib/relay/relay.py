import re

from machine import Pin, PWM

from secrets import topics
import time 
from picozero import pico_temp_sensor, pico_led
from picozero import Speaker
from time import ticks_ms
import json 
import os
import re
import rp2
import array


BEAT = 0.4 
liten_mus = [ ['d5', BEAT / 2], ['d#5', BEAT / 2], ['f5', BEAT], ['d6', BEAT], ['a#5', BEAT], ['d5', BEAT],
              ['f5', BEAT], ['d#5', BEAT], ['d#5', BEAT], ['c5', BEAT / 2],['d5', BEAT / 2], ['d#5', BEAT],
              ['c6', BEAT], ['a5', BEAT], ['d5', BEAT], ['g5', BEAT], ['f5', BEAT], ['f5', BEAT], ['d5', BEAT / 2],
              ['d#5', BEAT / 2], ['f5', BEAT], ['g5', BEAT], ['a5', BEAT], ['a#5', BEAT], ['a5', BEAT], ['g5', BEAT],
              ['g5', BEAT], ['', BEAT / 2], ['a#5', BEAT / 2], ['c6', BEAT / 2], ['d6', BEAT / 2], ['c6', BEAT / 2],
              ['a#5', BEAT / 2], ['a5', BEAT / 2], ['g5', BEAT / 2], ['a5', BEAT / 2], ['a#5', BEAT / 2], ['c6', BEAT],
              ['f5', BEAT], ['f5', BEAT], ['f5', BEAT / 2], ['d#5', BEAT / 2], ['d5', BEAT], ['f5', BEAT], ['d6', BEAT],
              ['d6', BEAT / 2], ['c6', BEAT / 2], ['b5', BEAT], ['g5', BEAT], ['g5', BEAT], ['c6', BEAT / 2],
              ['a#5', BEAT / 2], ['a5', BEAT], ['f5', BEAT], ['d6', BEAT], ['a5', BEAT], ['a#5', BEAT * 1.5] ]





SWITCH_INVERSE = True

#pins
SWITCHES = [22,10,11,12]  
RELAYS = [21,20,19,18,17,16,15,14]     
SPEAKER_LED = 6
RGB_LED = 13

BOUNCE_TIME =  0.02 

switches = []
config_relay=[]

# Configure the number of WS2812 LEDs, pins and brightness.
NUM_LEDS = 1

brightness = 0.1

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
COLORS = (BLACK, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)



speaker = Speaker(SPEAKER_LED) 


 

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

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

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
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(RGB_LED))
        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)
        self.arws2812 = array.array("I", [0 for _ in range(NUM_LEDS)])

        
    
        
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

    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
        for i,c in enumerate(self.arws2812):
            r = int(((c >> 8) & 0xFF) * brightness)
            g = int(((c >> 16) & 0xFF) * brightness)
            b = int((c & 0xFF) * brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)
        time.sleep_ms(10)

    def pixels_set(self,i, color):
        self.arws2812[i] = (color[1]<<16) + (color[0]<<8) + color[2]

    def pixels_fill(self,color):
        for i in range(len(self.arws2812)):
            self.pixels_set(i, color)    

    def showRGB(self,colorStr):
        color = None
        if isinstance(colorStr, (list,tuple)):
            color = colorStr
        elif colorStr.upper()=='BLACK':
            color = (0, 0, 0)
        elif colorStr.upper()=='RED':
            color = RED    
        elif colorStr.upper()=='YELLOW':
            color = YELLOW    
        elif colorStr.upper()=='GREEN':
            color = GREEN    
        elif colorStr.upper()=='CYAN':
            color = CYAN    
        elif colorStr.upper()=='BLUE':
            color = BLUE    
        elif colorStr.upper()=='PURPLE':
            color = PURPLE
        elif colorStr.upper()=='MAGENTA':
            color = MAGENTA
        elif colorStr.upper()=='WHITE':
            color = WHITE  
        elif len(colorStr.split(','))==3:
            try:
              color = (int(colorStr.split(',')[0]), int(colorStr.split(',')[1]), int(colorStr.split(',')[2]))  
            except:
                print("bad color",colorStr) 
        if color is None:
            print("bad color[2]",colorStr) 
            return
        self.pixels_fill(color)
        self.pixels_show()                     

    
    def init_sw(self): 
        for p in self.sw:
            if p.get("obj") is None:
                p["obj"]=Pin(p["pinN"], Pin.IN, Pin.PULL_UP)
                p["state"]=p["obj"].value()
                p["obj"].irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = int_handler)
        for i, p in enumerate(self.relay):
            if p.get("obj") is None:
                p["obj"]=Pin(p["pinN"], Pin.OUT)
                self.Relay_CHx(i,0)
            if p.get("schedule") is None:   
                p["schedule"]=[] # [5.30,-12.40, 17.00, -20.00] "-" mean off, "+" mean on ; [-120] auto off after 120 seconds isinstance(p["ONAt"],float)
                p["schedWork"]=p["schedule"].copy() # init as 


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
        self.picoRelayB.showRGB('BLUE')
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
                self.picoRelayB.showRGB('CYAN')

    def applyRelaySched(self):
        for i,p in enumerate(self.picoRelayB.relay):
            if isinstance(p["schedWork"],list) and isinstance(p["schedule"],list):
                if len(p["schedWork"])<1:
                    p["schedWork"]=p["schedule"].copy() # init if empty from template
                if len(p["schedWork"])>0:
                    valSched=abs(p["schedWork"][0])
                    val2Set=1 if p["schedWork"][0]>0 else 0 #  1 on 0 off
                    now=time.time()
                    nowt=time.gmtime(now)
                    change = False
                    time2go = False
                    if isinstance(valSched,float): # by utc time
                        tm2check=(nowt[0],nowt[1],nowt[2],int(valSched),round((valSched%1)*100),0,0,0)
                        if now>time.mktime(tm2check): # time to make action
                            p["schedWork"].pop(0)
                            time2go = True
                    elif isinstance(valSched,int): # is interval
                        if time.time()>p['time']+valSched:
                            p["schedWork"].pop(0)
                            time2go = True
                    if time2go and self.picoRelayB.relay[i]['state'] != val2Set: 
                        self.picoRelayB.Relay_CHx(i,val2Set)
                        change = True
                    if change and self.client is not None:    
                            self.client.publish(self.topic_pub_relay+str(i), (b'ON' if val2Set else b'OFF'))
                            self.picoRelayB.showRGB('RGB_250,83,03')

    def play_liten_mus(self):
        speaker.play(liten_mus)
    
    def client_setter(self, client):
        self.client = client
        print('client_setter',self.client)

    def set_additional_proc(self, rt):    
        self.rt =  rt
        self.rt['APPLYSW'] = {'last_start': time.time (), 'interval': 0.2, 'proc': self.applySw , 'last_error': 0}
        self.rt['APPLYSHED'] = {'last_start': time.time (), 'interval': 19, 'proc': self.applyRelaySched , 'last_error': 0}
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
            try:
                str = json.dumps(self.picoRelayB.sw)
            except Exception as e:
                print("parseConfig: can not make json from sw", e)
            try:
                os.remove("cfg_sw.json")
            except :
                print("parseConfig: can not remove  cfg_sw.json")
            try:
                with open('cfg_sw.json', 'w') as f:
                    # f.write(re.sub(r'"obj": Pin\(.+?\),',"   ",str))                
                    f.write(re.sub(r'"obj": (Pin\(.+?\)|null),',"   ",str))                
            except Exception as e:
                print("parseConfig: can not write cfg_sw.json", e)

        if newcfgRelay :
            try:
                str = json.dumps(self.picoRelayB.relay)
            except Exception as e:
                print("parseConfig: can not make json from relay", e)
            try:
                os.remove("cfg_relay.json")
            except :
                print("parseConfig: can not remove  cfg_relay.json")
            try:
                with open('cfg_relay.json', 'w') as f:
                    # f.write(re.sub(r'"obj": Pin\(.+?\),',"   ",str))                
                    f.write(re.sub(r'"obj": (Pin\(.+?\)|null),',"   ",str))                
            except Exception as e:
                print("parseConfig: can not write cfg_relay.json", e)

 
 

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
                    print('app_cb: received bad relay N ???',topic, msg)
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
                     self.picoRelayB.showRGB('MAGENTA')
                   except Exception as e:
                     print('Exception in app_cb  json load ', msg, e)
                     self.picoRelayB.showRGB('RED')
                elif msg.upper().startswith('MUSIC') :
                    self.play_liten_mus()
                    self.picoRelayB.showRGB('CYAN')
                elif msg.upper().startswith('RGB_') :
                    self.picoRelayB.showRGB(msg[4:])
                else: 
                    print('Pico received ???',topic, msg)
                    return
                if val is not None: 
                    self.picoRelayB.Relay_CHx(swN,val)
                    client.publish(self.topic_pub_relay+str(swN), (b'ON' if val else b'OFF'))
                    self.picoRelayB.showRGB('GREEN' if val else 'PURPLE')
        except Exception as e:
            print('Genelal Exception in app_cb ', e)
            self.picoRelayB.showRGB('RED')
      

      



#TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()




