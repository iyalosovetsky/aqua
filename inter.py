import machine
import array, time

import rp2
import micropython
micropython.alloc_emergency_exception_buf(100)


led = machine.Pin('LED', machine.Pin.OUT)



switches = None
SWITCH_INVERSE = True





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

class sw:
    def __init__(self,pins,relays):
        self.sw=[]
        self.relay=[]
        for p in pins:
            self.sw.append({"pinN":p,"time": time.time(), "state": None, "obj": None, 'event': None})
        for p in relays:
            self.relay.append({"pinN":p,"time": time.time(), "state": None, "obj": None, 'event': None})
            
        self.init_sw()
        
    def Relay_CHx(self,n,switch): 
        if switch == 1:
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
        print(self.relay,"self.relay after init")        
                
        
            
            
     
     
        
        
    
switches=sw([22,10,11,12],[21,20,19,18,17,16,15,14])
#switches=sw([22,10,11,12],[])


time.sleep(0.5)
def applySw(swObj):
  for i,p in enumerate(swObj.sw):
      if i>len(swObj.relay) or  p['event'] != 1:
          continue
        
      val = (1-p['state']) if SWITCH_INVERSE else p['state']
      p['event'] = 0
      
      if val != swObj.relay[i]['state'] :
        swObj.Relay_CHx(i,val)
      
      


    

while True:
    applySw(switches)
    time.sleep(0.5)

    
    
    
    
