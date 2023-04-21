import re

from machine import Pin, PWM

from secrets import topics


MAX_VALUE = 100000
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 18000 # ~40% 
HALF_MODE  = 38000 # ~40% 
ON_MODE    = HALF_MODE # ~80% 
NIGHT_MODE = QUARTER_MODE # ~10% 
FREQ = 10_000



SWITCH_INVERSE = True
SWITCHES = [22,10,11,12]  
RELAYS = [21,20,19,18,17,16,15,14]      





def int_handler(pin):
    global switches
    pin.irq(handler = None)
    id = int(''.join(char for char in str(pin) if char.isdigit()))
    #print("int_handler ",id, pin)
    led.on()
    val1=pin.value()
    time.sleep(0.1)
    val2=pin.value()
    
    
    if val1!=val2:
        pin.irq(handler = int_handler)
        return 
    led.off()
    #print("int_handler ",id, pin)
    
    if switches is not None:
        event=0
        pp=None
        for p in switches.sw:
            if p["pinN"] == id:
                #print("Found", p)
                if p['state'] != val2 :
                    p['event']=1
                    event=1
                    p['state'] = val2
                    pp =p
        if event == 1:        
            print( 'switches is ', pp)
    pin.irq(handler = int_handler)

class switch:
    def __init__(self,pins,relays):
        self.sw=[]
        self.relay=[]
        for p in pins:
            self.sw.append({"pinN":p,"time": time.time(), "state": None, "obj": None, 'event': None})
        for p in relays:
            self.relay.append({"pinN":p,"time": time.time(), "state": None, "obj": None, 'event': None})
            
        self.init_sw()
        
    def Relay_CHx(self,n,value, pub= False): 
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
                p["obj"]=machine.Pin(p["pinN"], machine.Pin.IN, machine.Pin.PULL_UP)
                p["state"]=p["obj"].value()
                p["obj"].irq(trigger = machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler = int_handler)
        print(self.sw,"self.sw after init")
        for i, p in enumerate(self.relay):
            if p["state"] is None:
                p["obj"]=machine.Pin(p["pinN"], machine.Pin.OUT)
                self.Relay_CHx(i,0)
                #print(p,"p after init")
        #print(self.relay,"self.relay after init")   

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
            if val != self.picoRelayB.relay[i]['state'] :
                self.picoRelayB.Relay_CHx(i,val)        
    
    def client_setter(self, client):
        self.client = client
        print('client_setter',self.client)

    def get_state(self, client):
        for i,p in enumerate(self.picoRelayB.sw):
                val = (1-p['state']) if SWITCH_INVERSE else p['state']
                msg = (b'ON' if val else b'OFF')
                client.publish(self.topic_pub_switch, msg)
        for i,p in enumerate(self.picoRelayB.relay):
                val = p['state']
                msg = (b'ON' if val else b'OFF')
                client.publish(self.topic_pub_relay, msg)

    
    def topic_getter(self):
        return [topic_sub_relay+str(n) for n in range(len(RELAYS))]
        
        
    def app_cb(self, client, topic0, msg0):
        print(msg0,topic0)
        try:
            msg =  msg0.decode("utf-8")
            topic = topic0.decode("utf-8")
            val = None
            sw = None
            swN = None
            is_command = False
            if topic.startswith(self.topic_sub_relay):
                swN=int(''.join(char for char in str(topic) if char.isdigit()))
                if swN+1>len(RELAYS):
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
                else :
                    print('Pico received ???',topic, msg)
                    return
                if val is not None: 
                    self.switchRelay(client, swN, val)
                    print("switchRelay: ", swN, val)
                    self.picoRelayB.Relay_CHx(swN,val)
                    client.publish(self.topic_pub_relay+str(swN), val)


        except Exception as e:
            print('Exception in app_cb ', e)
      

      



#TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()




