import re

from machine import Pin, PWM, Timer

from secrets import topics
#import utime
import time

MAX_VALUE = 99999
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 10000 # ~10% 
HALF_MODE  = 50000 # ~50% 
SHOWEROUT_MODE = 70000
SHOWERIN_MODE  = 15000


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
#freq_last_time =utime.ticks_ms()
freq_value =-1


FLOW_SWITCHER_REVERSE_DELAY = 5
FLOW_SWITCHER_SECONDS = 90
SHOWEROUT_SECONDS = 30*60 # ~30 min
SHOWERIN_SECONDS = 90*60 # ~1h 30 min

#SHOWEROUT_SECONDS = 3*60 # ~30 min
#SHOWERIN_SECONDS = 5*60 # ~1h 30 min



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
    topic_pub_mode_showerIn  = topics['topic_pub_switch']+'_showerin'
    topic_pub_mode_showerOut  = topics['topic_pub_switch']+'_showerout'
    # topic_pub_mode_in   = topics['topic_pub_switch']+'_in'
    topic_pub_mode_inout   = topics['topic_pub_switch']+'_inout'
    topic_pub_mode_freq   = topics['topic_pub_switch']+'_freq'
    topic_pub_pwm = topics['topic_pub_pwm']
    topic_sub_switch = topics['topic_sub_switch'] # ON/OFF/SETOUT/SETINOUT/SETIN
    topic_sub_pwm = topics['topic_sub_pwm']
    topic_APP_ID = topics.get('APP_ID','bath')

    pwm_val:int=NIGHT_MODE
    switch_val:str = 'ON'
    fan_prog_mode:str = 'SETIN'
    flow_switch_time:int = time.time()
    switch_mode_current:str = 'SETIN'
    switch_mode_prev:str = 'UNK'
    switch_mode_desire:str = 'DESIRED'
    switch_mode_time_desire:int = time.time()
    debugmode = 0
    client = None # mqtt
    
    #fan_freq_Timer = Timer()
    # initialize the timer object to tick every 10 seconds
    #fan_freq_Timer.init(period=10000, mode=Timer.PERIODIC, callback=timer_cb)
        


    def __init__(self):
        global freq_counter , freq_value
        self.client = None
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
        print('bath inited')
    
    def client_setter(self, client):
        self.client = client

    def debugmode_setter(self):
        self.debugmode = 1

    def no_debugmode_setter(self):
        self.debugmode = 0

    def state_app(self):
        return (self.pwm_val, self.switch_val)
    
    def open_fan_window(self, value:int):
        print('open fan window',value)
       
        self.fan_window=value
        if self.fan_window == 1:
            self.pin_fan_window.high()
        else:
           self.pin_fan_window.low()
        msg = b'%d'%(self.fan_window,)
        if self.client is not None:
           self.client.publish(self.topic_pub_fan_window, msg)
    
                
    

 

    
    def topic_getter(self):
        topics = (self.topic_sub_switch, self.topic_sub_pwm)
        return topics



        
    def stopFan(self):
        self.pwm.deinit()
        self.pwm.duty_u16(0)
        self.pin_fan_pwm.init(mode=Pin.OUT)
        self.pin_fan_pwm.value(1) # or full stop
        print('\napplyPWM: pwm full stop self.pin_fan_pwm=',self.pin_fan_pwm.value())
        

    def applyPWM(self):
        #pub=False
        if self.switch_mode_prev != self.switch_mode_current and self.pwm_val>=PWM_VAL2STOP:
            self.stopFan()
            self.switch_mode_desire = self.switch_mode_current
            self.switch_mode_time_desire = time.time()
            return

        self.switch_mode_prev = self.switch_mode_current
        self.switch_mode_desire = 'DESIRED'
        if self.pwm_val<PWM_VAL2STOP:
            self.stopFan()
            self.fan_window=0
            if self.switch_val is None or self.switch_val=="ON":
                self.switch_val="OFF"
                if self.client is not None  :
                    self.client.publish(self.topic_pub_switch, self.switch_val)
            self.open_fan_window(self.fan_window)
            return
        else:
            self.fan_window=1
            self.open_fan_window(self.fan_window)
            if self.switch_val is None or self.switch_val=="OFF":
                self.switch_val="ON"
                if self.client is not None:
                    self.client.publish(self.topic_pub_switch, self.switch_val)
            
            if self.pwm.duty_u16()==0:
                self.pwm = PWM(self.pin_fan_pwm)          # create a PWM object on a pin
                self.pwm.freq(FREQ)  # 100
                print('\napplyPWM: pwm starts ',self.pwm_val,(),self.pin_fan_pwm)
        
        dif= (PWM_DIVIDER_MAX-PWM_DIVIDER_MIN)/2 * (1-(self.pwm_val/PWM_SCALE))
        if self.switch_mode_current=='SETIN':
            # val1=int(PWM_DIVIDER_MIN+dif)
            val1=int(PWM_DIVIDER_MIN-dif)
        else:
            #val1=int(PWM_DIVIDER_MAX-dif)    
            val1=int(PWM_DIVIDER_MAX+dif)    


        self.pwm.duty_u16(val1)
        
        if self.client is not None:
            msgpub=f'%d'%(self.pwm_val,)              
            self.client.publish(self.topic_pub_pwm, msgpub)


    def publishFanProgMode(self):
        if self.client is None:
            print('publishFanProgMode: empty client')
            return

        if self.fan_prog_mode=='SETOUT':
            self.client.publish(self.topic_pub_mode_out, self.fan_prog_mode)
            self.client.publish(self.topic_pub_mode_inout, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerIn, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerOut, 'SETIN')
        elif self.fan_prog_mode=='SETINOUT':
            self.client.publish(self.topic_pub_mode_out, 'SETIN')
            self.client.publish(self.topic_pub_mode_inout, self.fan_prog_mode)
            self.client.publish(self.topic_pub_mode_showerIn, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerOut, 'SETIN')
        elif self.fan_prog_mode=='SETIN':
            self.client.publish(self.topic_pub_mode_out, 'SETIN')
            self.client.publish(self.topic_pub_mode_inout, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerIn, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerOut, 'SETIN')
        elif self.fan_prog_mode=='SHOWERIN':
            self.client.publish(self.topic_pub_mode_out, 'SETIN')
            self.client.publish(self.topic_pub_mode_inout, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerIn, self.fan_prog_mode)
            self.client.publish(self.topic_pub_mode_showerOut, 'SETIN')

        elif self.fan_prog_mode=='SHOWEROUT':
            self.client.publish(self.topic_pub_mode_out, 'SETIN')
            self.client.publish(self.topic_pub_mode_inout, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerIn, 'SETIN')
            self.client.publish(self.topic_pub_mode_showerOut, self.fan_prog_mode)




    def setFanState(self,  val0):
        
        val = val0.upper()
        if val != 'ON' and  val != 'OFF' and  val != 'SETOUT' and val != 'SETINOUT' and  val != 'SETIN' and  val!='SHOWERIN' and val!='SHOWEROUT':
            print("setFanState: bad command ",val0)
            return
        
        if val.startswith('SET') or val == 'SHOWERIN' or val == 'SHOWEROUT':
            if self.fan_prog_mode==val:
                print("switchMode: already ",self.fan_prog_mode)
                self.publishFanProgMode()
                return
            
            self.fan_prog_mode=val
            self.flow_switch_time=time.time() # time when mode started
            if val=='SETOUT':
                self.switch_mode_current = val
            elif val.startswith('SET') and val!='SETOUT': 
                self.switch_mode_current = 'SETIN'
            elif val == 'SHOWEROUT':
                self.switch_mode_current = 'SETOUT'
                self.pwm_val =  SHOWEROUT_MODE
            else:
                self.switch_mode_current = 'SETOUT'
                self.pwm_val =  SHOWERIN_MODE
    
            print("setFanState: ", self.fan_prog_mode)
            self.publishFanProgMode( )
            self.applyPWM()


        elif val == 'ON' or  val == 'OFF':
            if self.switch_val==val:
                print("setFanState: already ",self.switch_val)
                if self.client is not None:
                    self.client.publish(self.topic_pub_switch, self.switch_val)
                return
            
            print("setFanState: ", self.switch_val)
            if self.client is not None:
                self.client.publish(self.topic_pub_switch, self.switch_val)
            self.applyPWM()
                




            
        

    def get_state(self, client):
        if client is not None:
            self.client = client
        global freq_counter , freq_value
        self.freq_value= freq_value
        msg = b'%d'%(self.pwm_val,)
        print('process_get_state:',self.switch_val, self.pwm_val)
        client.publish(self.topic_pub_pwm, msg)
        # msg = b'%d'%(self.switch_val,)
        client.publish(self.topic_pub_switch, b''+self.switch_val)
        msg = b'%d'%(self.fan_window,)
        client.publish(self.topic_pub_fan_window, msg)
        self.publishFanProgMode()
        msg = b'%d'%(int(self.freq_value),)
        client.publish(self.topic_pub_mode_freq, msg)


    def applyDefaultMode(self):
        self.switch_mode_current = 'SETIN'
        self.fan_prog_mode='SETIN'
        self.pwm_val = QUARTER_MODE
        self.applyPWM()      
        self.publishFanProgMode()
        
    def app_cb(self, client, topic0, msg0):
        
        try:
            msg =  msg0.decode("utf-8")
            topic = topic0.decode("utf-8")
            val = None
            print('app_cb:',msg,topic)
            if client is not None:
                self.client= client
            if topic == self.topic_sub_pwm:
               if re.search("\D", msg)  is None:
                   val0=int(msg)
                   if not (val0 <MIN_VALUE or val0 >MAX_VALUE):
                       val = val0
                       self.pwm_val=val
                       if self.pwm_val<PWM_VAL2STOP:
                           client.publish(self.topic_pub_switch, 'OFF')
                       elif self.pwm_val >=PWM_VAL2STOP:    
                           client.publish(self.topic_pub_switch, 'ON')
                   else: 
                       print('bad value %s'%(msg,))
               elif  msg.upper()=='ON':
                   if self.pwm_val>=PWM_VAL2STOP:
                       val = self.pwm_val
                   else:
                       val = QUARTER_MODE
                   self.pwm_val=val
                   self.switch_val = msg.upper()
                   client.publish(self.topic_pub_switch, self.switch_val)
               elif msg.upper()=='OFF':
                   val = PWM_VAL2STOP/10
                   self.pwm_val=val
                   self.switch_val = msg.upper()
                   client.publish(self.topic_pub_switch, self.switch_val)
            elif topic == self.topic_sub_switch:
                if msg.upper()=='ON':
                   val = QUARTER_MODE
                   self.switch_val = msg.upper()
                   self.setFanState( self.switch_val)
                elif msg.upper()=='OFF':
                   val = OFF_MODE
                   self.switch_val = msg.upper()
                   self.setFanState(  self.switch_val)
                elif msg.upper()=='SETOUT' or msg.upper()=='SETINOUT' or msg.upper()=='SETIN' or msg.upper()=='SHOWERIN' or msg.upper()=='SHOWEROUT':
                   val = self.switch_val
                   self.setFanState(  msg.upper())
            elif topic == self.topic_sub_switch or  self.topic == self.topic_sub_pwm:
               msgpub=f'Pico received unknown %s'%(msg,)              
               client.publish(self.topic_pub_info, msgpub)
               return
            if val is not None: 
                #print('app_cb: point2',self.pwm_val,self.switch_val)
                self.applyPWM()

                   
               
        except Exception as e:
            print('Exception in app_cb ', e)


        
      
    def flow_switcher(self):
        print('flow_switcher: [1]')
        if self.switch_mode_desire != 'DESIRED' and self.switch_mode_time_desire+FLOW_SWITCHER_REVERSE_DELAY <time.time():
            self.switch_mode_current= self.switch_mode_desire
            self.switch_mode_prev   = self.switch_mode_desire
            self.applyPWM()
            return


        if self.fan_prog_mode=='SETINOUT':
            if self.flow_switch_time+FLOW_SWITCHER_SECONDS <time.time():
                print('flow_switcher: [2]')
                self.flow_switch_time=time.time()
                if self.switch_mode_current == 'SETIN':
                    self.switch_mode_current = 'SETOUT'
                else:
                    self.switch_mode_current = 'SETIN'
                self.applyPWM()

        elif self.fan_prog_mode=='SHOWEROUT':
            if self.flow_switch_time+SHOWEROUT_SECONDS <time.time():
                print('flow_switcher: [3]')
                self.flow_switch_time=time.time()
                self.applyDefaultMode()
        elif self.fan_prog_mode=='SHOWERIN':
            if self.flow_switch_time+SHOWERIN_SECONDS <time.time():
                print('flow_switcher: [4]')
                self.flow_switch_time=time.time()
                self.applyDefaultMode()

    # def set_additional_proc(self, rt):    
    #     self.rt =  rt
    #     return self.rt
        
    def set_additional_proc(self, rt):    
        self.rt =  rt
        self.rt['FLOWSWITCHER'] = {'last_start': time.time (), 'interval': 4, 'proc': self.flow_switcher , 'last_error': 0}
        return self.rt         
        


# TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()




