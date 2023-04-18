import machine
import utime
#butt1 = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN)
#butt1 = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin('LED', machine.Pin.OUT)

switches=None

def int_handler(pin):
    global switches
    pin.irq(handler = None)
    id = int(''.join(char for char in str(pin) if char.isdigit()))
    #print("int_handler ",id, pin)
    led.on()
    val1=pin.value()
    utime.sleep(0.1)
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
    def __init__(self,pins):
        self.sw=[]
        for p in pins:
            self.sw.append({"pinN":p,"time": utime.time(), "state": None, "obj": None, 'event': None})
        self.init_sw()    
    
    def init_sw(self): 
        for p in self.sw:
            if p["state"] is None:
                #print(p,"is none")
                if p["pinN"]==12:
                    p["obj"]=machine.Pin(p["pinN"], machine.Pin.IN)
                else:
                    p["obj"]=machine.Pin(p["pinN"], machine.Pin.IN, machine.Pin.PULL_UP)
                p["state"]=p["obj"].value()
                p["obj"].irq(trigger = machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler = int_handler)
                #print(p,"p after init")
            
            
        
        
    
switches=sw([10,11,12])
#butt1.irq(trigger = machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler = int_handler)

while True:
    utime.sleep(0.5)
    