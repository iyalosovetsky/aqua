import re

from machine import Pin, PWM

from secrets import topics


MAX_VALUE = 99999
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 1000 # ~10% 
HALF_MODE  = 5000 # ~50% 
ON_MODE    = HALF_MODE # ~80% 
NIGHT_MODE = QUARTER_MODE # ~10% 
FREQ = 100
PWM_SCALE = 99999
PWM_MAX = 65000
PWM_MIN = 0

class app:

    topic_pub_info = topics['topic_pub_info']
    topic_pub_switch = topics['topic_pub_switch']
    topic_pub_mode_out  = topics['topic_pub_switch']+'_out'
    topic_pub_mode_in   = topics['topic_pub_switch']+'_in'
    topic_pub_mode_inout   = topics['topic_pub_switch']+'_inout'
    topic_pub_pwm = topics['topic_pub_pwm']
    topic_sub_switch = topics['topic_sub_switch'] # ON/OFF/SETOUT/SETINOUT/SETIN
    topic_sub_pwm = topics['topic_sub_pwm']
    topic_APP_ID = topics.get('APP_ID','bath')

    pwm_val=NIGHT_MODE
    switch_val = 'ON'
    switch_mode = 'SETIN'
    switch_mode_current = 'SETIN'
    debugmode = 0
    
    def __init__(self):
                
        #PWM init
        self.p0 = Pin(0, Pin.OUT)    # create output pin on GPIO0
        self.pwm = PWM(self.p0)          # create a PWM object on a pin
        self.applyPWM()
        self.pwm.freq(FREQ)  # 100
        self.client = None
        print('bath inited')
    
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




    def applyPWM(self, client=None, pub=False):

        print("applyPWM: ",self.pwm_val, self.switch_mode_current,pub) 
        dif= (PWM_MAX-PWM_MIN)/2 * (1-(self.pwm_val/PWM_SCALE))
        if self.switch_mode_current=='SETIN':
            val1=int(PWM_MIN+dif)
        else:
            val1=int(PWM_MAX-dif)    
        self.pwm.duty_u16(val1)
        if pub and client is not None:
            msgpub=f'%d'%(self.pwm_val,)              
            client.publish(self.topic_pub_pwm, msgpub)

    def publishMode(self,client):
        if self.switch_mode=='SETOUT':
            client.publish(self.topic_pub_mode_out, 'ON')
            client.publish(self.topic_pub_mode_inout, 'OFF')
            client.publish(self.topic_pub_mode_in, 'OFF')
        elif self.switch_mode=='SETINOUT':
            client.publish(self.topic_pub_mode_out, 'OFF')
            client.publish(self.topic_pub_mode_inout, 'ON')
            client.publish(self.topic_pub_mode_in, 'OFF')
        elif self.switch_mode=='SETIN':
            client.publish(self.topic_pub_mode_out, 'OFF')
            client.publish(self.topic_pub_mode_inout, 'OFF')
            client.publish(self.topic_pub_mode_in, 'ON')


    def setFanState(self, client, val0):
        
        val = val0.upper()
        if val != 'ON' and  val != 'OFF' and  val != 'SETOUT' and val != 'SETINOUT' and  val != 'SETIN':
            print("setFanState: bad command ",val0)
            return
        
        if val.startswith('SET'):
            if self.switch_mode==val:
                print("switchMode: already ",self.switch_mode)
                self.publishMode(client)
                return
            self.switch_mode=val
            if val=='SETOUT':
                self.switch_mode_current = val
            else: 
                self.switch_mode_current = 'SETIN'
            print("setFanState: ", self.switch_mode)
            self.publishMode(client)
            self.applyPWM(client)

        elif val == 'ON' or  val == 'OFF':
            if self.switch_val==val:
                print("setFanState: already ",self.switch_val)
                client.publish(self.topic_pub_switch, self.switch_val)
                return
            
            print("setFanState: ", self.switch_val)
            client.publish(self.topic_pub_switch, self.switch_val)
            self.applyPWM(client, True)
                




            
        

    def get_state(self, client):
        msg = b'%d'%(self.pwm_val,)
        print('process_get_state:',self.switch_val, self.pwm_val)
        client.publish(self.topic_pub_pwm, msg)
        self.publishMode(client)
        
        
    def app_cb(self, client, topic0, msg0):
        print(msg0,topic0)
        try:
            msg =  msg0.decode("utf-8")
            topic = topic0.decode("utf-8")
            val = None
            if topic == self.topic_sub_pwm:
               if re.search("\D", msg)  is None:
                   val0=int(msg)
                   if not (val0 <MIN_VALUE or val0 >MAX_VALUE):
                       val = val0
                       self.switch_val=val
                   else: 
                       print('bad value %s'%(msg,))
            elif topic == self.topic_sub_switch:
                if msg.upper()=='ON':
                   val = HALF_MODE
                   self.switch_val = val
                   self.setFanState(self, client, msg.upper())
                elif msg.upper()=='OFF':
                   val = OFF_MODE
                   self.switch_val = val
                   self.setFanState(self, client, msg.upper())
                elif msg.upper()=='SETOUT' or msg.upper()=='SETINOUT' or msg.upper()=='SETIN':
                   val = self.switch_val
                   self.setFanState(self, client, msg.upper())
            elif topic == self.topic_sub_switch or  self.topic == self.topic_sub_pwm:
               msgpub=f'Pico received unknown %s'%(msg,)              
               client.publish(self.topic_pub_info, msgpub)
               return
            if val is not None: 
                self.applyPWM(client, True)

                   
               
        except Exception as e:
            print('Exception in app_cb ', e)
      
    def flow_switcher(self):
        if self.switch_mode=='SETINOUT':
            if self.switch_mode_current == 'SETIN':
                self.switch_mode_current = 'SETOUT'
            else:
                self.switch_mode_current = 'SETIN'
            self.applyPWM()        
      
        


# TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()




