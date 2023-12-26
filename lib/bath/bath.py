import re

from machine import Pin, PWM, Timer

from secrets import topics
import utime

MAX_VALUE = 99999
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 10000 # ~10% 
HALF_MODE  = 50000 # ~50% 
ON_MODE    = HALF_MODE # ~80% 
NIGHT_MODE = QUARTER_MODE # ~10% 
FREQ = 100
PWM_SCALE = 99999
PWM_DIVIDER_MAX = 65000
PWM_DIVIDER_MIN = 0
PWM_VAL2STOP = 3000

PIN_FAN_PWM =0
PIN_FAN_SENSOR = 14
PIN_FAN_WINDOW = 15

freq_counter =0
DELTA_TIME = 10
freq_last_time =utime.ticks_ms()
freq_value =-1




# this function gets called every time the button is pressed
def freq_counter_cb(pin):
    global freq_counter
    freq_counter +=1

def timer_cb(pTimer):
    global freq_counter,  freq_value
    freq_value = freq_counter/DELTA_TIME
    freq_counter = 0



class app:
    topic_pub_info = topics['topic_pub_info']
    topic_pub_switch = topics['topic_pub_switch']
    topic_pub_fan_window = topics['topic_pub_switch']+'_window'
    topic_pub_mode_out  = topics['topic_pub_switch']+'_out'
    # topic_pub_mode_in   = topics['topic_pub_switch']+'_in'
    topic_pub_mode_inout   = topics['topic_pub_switch']+'_inout'
    topic_pub_mode_freq   = topics['topic_pub_switch']+'_freq'
    topic_pub_pwm = topics['topic_pub_pwm']
    topic_sub_switch = topics['topic_sub_switch'] # ON/OFF/SETOUT/SETINOUT/SETIN
    topic_sub_pwm = topics['topic_sub_pwm']
    topic_APP_ID = topics.get('APP_ID','bath')

    pwm_val:int=NIGHT_MODE
    switch_val:str = 'ON'
    switch_mode:str = 'SETIN'
    switch_mode_current:str = 'SETIN'
    debugmode = 0
    
    #fan_freq_Timer = Timer()
    # initialize the timer object to tick every 10 seconds
    #fan_freq_Timer.init(period=10000, mode=Timer.PERIODIC, callback=timer_cb)
        


    def __init__(self):
        global freq_counter , freq_value
        freq_counter =0
        freq_value= 0
        #PWM init
        self.pin_fan_pwm = Pin(PIN_FAN_PWM, Pin.OUT)    # create output pin on GPIO0 for fan pwm
        self.pin_fan_sensor = Pin(PIN_FAN_SENSOR, Pin.IN, Pin.PULL_UP)  #for pwm sensor
        self.pin_fan_sensor.irq(trigger = Pin.IRQ_FALLING  , handler = freq_counter_cb)
        self.pin_fan_window = Pin(PIN_FAN_WINDOW, Pin.OUT)    # create output pin on GPIO0 for fan close open window
        self.fan_window = 0
        self.open_fan_window(self.fan_window)
        self.pin_fan_sensor.high()
        self.fan_freq_Timer = Timer()
        # initialize the timer object to tick every 10 seconds
        self.fan_freq_Timer.init(period=10000, mode=Timer.PERIODIC, callback=timer_cb)


        self.pwm = PWM(self.pin_fan_pwm)          # create a PWM object on a pin
        self.pwm.freq(FREQ)  # 100
        self.applyPWM()
        self.client = None
        print('bath inited')
    

    def debugmode_setter(self):
        self.debugmode = 1

    def no_debugmode_setter(self):
        self.debugmode = 0

    def state_app(self):
        return (self.pwm_val, self.switch_val)
    
    def open_fan_window(self, value:int, client = None):
        print('open fan window',value)
       
        self.fan_window=value
        if self.fan_window == 1:
            self.pin_fan_window.high()
        else:
           self.pin_fan_window.low()
        msg = b'%d'%(self.fan_window,)
        if client is not None:
           client.publish(self.topic_pub_fan_window, msg)
    
                
    
    def client_setter(self, client):
        self.client = client

    def set_additional_proc(self, rt):    
        self.rt =  rt
        return self.rt

    
    def topic_getter(self):
        topics = (self.topic_sub_switch, self.topic_sub_pwm)
        return topics



        
        
        

    def applyPWM(self, client=None, pub=False):
        if self.pwm_val<PWM_VAL2STOP:
            self.pwm.deinit()
            self.pwm.duty_u16(0)
            self.pin_fan_pwm.init(mode=Pin.OUT)
            self.pin_fan_pwm.value(1) # or full stop
            print('\napplyPWM: pwm full stop self.pin_fan_pwm=',self.pin_fan_pwm.value(),self.pin_fan_pwm)
            self.fan_window=0
            if self.switch_val is None or self.switch_val=="ON":
                self.switch_val="OFF"
                client.publish(self.topic_pub_switch, self.switch_val)
            self.open_fan_window(self.fan_window, client)
            return
        else:
            self.fan_window=1
            self.open_fan_window(self.fan_window, client)
            if self.switch_val is None or self.switch_val=="OFF":
                self.switch_val="ON"
                client.publish(self.topic_pub_switch, self.switch_val)
            
            if self.pwm.duty_u16()==0:
                self.pwm = PWM(self.pin_fan_pwm)          # create a PWM object on a pin
                self.pwm.freq(FREQ)  # 100
                print('\napplyPWM: pwm starts ',self.pwm_val,(),self.pin_fan_pwm)
        
        dif= (PWM_DIVIDER_MAX-PWM_DIVIDER_MIN)/2 * (1-(self.pwm_val/PWM_SCALE))
        if self.switch_mode_current=='SETIN':
            val1=int(PWM_DIVIDER_MIN+dif)
        else:
            val1=int(PWM_DIVIDER_MAX-dif)    


        self.pwm.duty_u16(val1)
        
        if pub and client is not None:
            msgpub=f'%d'%(self.pwm_val,)              
            client.publish(self.topic_pub_pwm, msgpub)


    def publishMode(self,client):
        if self.switch_mode=='SETOUT':
            client.publish(self.topic_pub_mode_out, 'SETOUT')
            client.publish(self.topic_pub_mode_inout, 'SETIN')
            # client.publish(self.topic_pub_mode_in, 'SETIN')
        elif self.switch_mode=='SETINOUT':
            client.publish(self.topic_pub_mode_out, 'SETIN')
            client.publish(self.topic_pub_mode_inout, 'SETINOUT')
            # client.publish(self.topic_pub_mode_in, 'SETIN')
        elif self.switch_mode=='SETIN':
            client.publish(self.topic_pub_mode_out, 'SETIN')
            client.publish(self.topic_pub_mode_inout, 'SETIN')
            # client.publish(self.topic_pub_mode_in, 'SETIN')


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
        global freq_counter , freq_value
        self.freq_value= freq_value
        msg = b'%d'%(self.pwm_val,)
        print('process_get_state:',self.switch_val, self.pwm_val)
        client.publish(self.topic_pub_pwm, msg)
        # msg = b'%d'%(self.switch_val,)
        client.publish(self.topic_pub_switch, b''+self.switch_val)
        msg = b'%d'%(self.fan_window,)
        client.publish(self.topic_pub_fan_window, msg)
        self.publishMode(client)
        msg = b'%d'%(int(self.freq_value),)
        client.publish(self.topic_pub_mode_freq, msg)


        
        
    def app_cb(self, client, topic0, msg0):
        
        try:
            msg =  msg0.decode("utf-8")
            topic = topic0.decode("utf-8")
            val = None
            print('app_cb:',msg,topic)
            if topic == self.topic_sub_pwm:
               if re.search("\D", msg)  is None:
                   val0=int(msg)
                   if not (val0 <MIN_VALUE or val0 >MAX_VALUE):
                       val = val0
                       self.pwm_val=val
                       if self.pwm_val<=PWM_VAL2STOP:
                           client.publish(self.topic_pub_switch, 'OFF')
                       elif self.pwm_val >=PWM_VAL2STOP:    
                           client.publish(self.topic_pub_switch, 'ON')
                   else: 
                       print('bad value %s'%(msg,))
               elif  msg.upper()=='ON':
                   val = HALF_MODE
                   self.pwm_val=val
                   self.switch_val = msg.upper()
                   client.publish(self.topic_pub_switch, self.switch_val)
               elif msg.upper()=='OFF':
                   val = OFF_MODE
                   self.pwm_val=val
                   self.switch_val = msg.upper()
            elif topic == self.topic_sub_switch:
                if msg.upper()=='ON':
                   val = HALF_MODE
                   self.switch_val = msg.upper()
                   self.setFanState(client, msg.upper())
                elif msg.upper()=='OFF':
                   val = OFF_MODE
                   self.switch_val = msg.upper()
                   self.setFanState( client, msg.upper())
                elif msg.upper()=='SETOUT' or msg.upper()=='SETINOUT' or msg.upper()=='SETIN':
                   val = self.switch_val
                   self.setFanState( client, msg.upper())
            elif topic == self.topic_sub_switch or  self.topic == self.topic_sub_pwm:
               msgpub=f'Pico received unknown %s'%(msg,)              
               client.publish(self.topic_pub_info, msgpub)
               return
            if val is not None: 
                print('app_cb: point2',self.pwm_val,self.switch_val)
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




