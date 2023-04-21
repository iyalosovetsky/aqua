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

class app:

    topic_pub_info = topics['topic_pub_info']
    topic_pub_switch = topics['topic_pub_switch']
    topic_pub_pwm = topics['topic_pub_pwm']
    topic_sub_switch = topics['topic_sub_switch']
    topic_sub_pwm = topics['topic_sub_pwm']

    pwm_val=NIGHT_MODE
    switch_val = 'ON'
    debugmode = 0
    
    def __init__(self):
                
        #PWM init
        self.p0 = Pin(0, Pin.OUT)    # create output pin on GPIO0
        self.pwm = PWM(self.p0)          # create a PWM object on a pin
        self.pwm.duty_ns(self.pwm_val)     # set duty to 50%
        self.pwm.freq(FREQ)  # 10_000
        self.client = None
        print('aqua inited')
    
    def debugmode_setter(self):
        self.debugmode = 1

    def no_debugmode_setter(self):
        self.debugmode = 0

    def state_app(self):
        return (self.pwm_val, self.switch_val)
    
    def client_setter(self, client):
        self.client = client

    def set_additional_proc(self, rt):    
        self.rt =  rt
        return self.rt

    
    def topic_getter(self):
        topics = (self.topic_sub_switch, self.topic_sub_pwm)
        return topics
        
    def showLed(self, client, val, pub=True):

        print("showLed: ",val, pub) 
        self.pwm.duty_ns(MAX_VALUE-val)
        if pub:
            self.pwm_val=val
            msgpub=f'%d'%(self.pwm_val,)              
            client.publish(self.topic_pub_pwm, msgpub)



    def switchLed(self, client, val0):
        
        val = val0.upper()
        if val != 'ON' and  val != 'OFF':
            print("switchLed: bad command ",val0)
            return
        
        if self.switch_val==val:
           print("switchLed: already ",self.switch_val)
           client.publish(self.topic_pub_switch, self.switch_val)
           return
            
        self.switch_val=val
        print("switchLed: ", self.switch_val)
        client.publish(self.topic_pub_switch, self.switch_val)
        
        if val=='ON':
            self.showLed(client, self.pwm_val, False)
            #pico_led.on()
            
        if val=='OFF':
            self.showLed(client, OFF_MODE, False)
            #pico_led.off()

    def get_state(self, client):
        
        msg = b'%d'%(self.pwm_val,)
        print('process_get_state:',self.switch_val, self.pwm_val)
        client.publish(self.topic_pub_pwm, msg)
        client.publish(self.topic_pub_switch, self.switch_val)
        
        
    def app_cb(self, client, topic0, msg0):

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
                   self.switchLed(client, msg)
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
            elif topic == self.topic_sub_switch or  self.topic == topic_sub_pwm:
               msgpub=f'Pico received unknown %s'%(msg,)              
               client.publish(self.topic_pub_info, msgpub)
               return
            else :
               print('Pico received ???',topic, msg)
               return
            if val is not None: 
                self.showLed(client, val)

                   
               
        except Exception as e:
            print('Exception in app_cb ', e)
      

      
        


#TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    #mqtt.connect_and_subscribe()
    mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()




