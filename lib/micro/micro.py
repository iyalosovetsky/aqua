import re
import time
from machine import Pin, PWM
from machine import I2S, Pin
from ulab import numpy as np
from picozero import pico_led
from secrets import topics
import array

MAX_VALUE = 100000
MIN_VALUE = 3
OFF_MODE   = 8000
QUARTER_MODE  = 18000 # ~40% 
HALF_MODE  = 38000 # ~40% 
ON_MODE    = HALF_MODE # ~80% 
NIGHT_MODE = QUARTER_MODE # ~10% 
FREQ = 10_000

NUM_CONST = 1024
FREQ_S = 22050
WINDOW_NUMS = 1

class app:

    topic_pub_info = topics['topic_pub_info']
    topic_pub_status = topics['topic_pub_status']
    topic_pub_pwm = topics['topic_pub_pwm']
    topic_sub_switch = topics['topic_sub_switch']
    topic_sub_pwm = topics['topic_sub_pwm']
    topic_APP_ID = topics.get('APP_ID','aqua')

    debugmode = 0
    
    def __init__(self):
        self.sinNum = 16
        c = array.array('L',[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
        self.equalizer = self.tresholdConstr(self.sinNum, c)
        self.last_status = False
        self.last_time = time.ticks_ms()
        buf = array.array("H", [21845 for x in range(NUM_CONST)])
        audio_in = I2S(1, sck=Pin(0), ws=Pin(1), sd=Pin(2), mode=I2S.RX, bits=16, format=I2S.MONO, rate=FREQ_S, ibuf=NUM_CONST) # create I2S object //23ms
        n = audio_in.readinto(buf)          # fill buffer with audio samples from I2S device
        audio_in.deinit()
        x = (65535 - np.array(buf))/32768
        a = np.fft.fft(x)[0][0:NUM_CONST]
    
    def debugmode_setter(self):
        self.debugmode = 1

    def no_debugmode_setter(self):
        self.debugmode = 0

    def state_app(self):
        return (self.last_status, self.last_time)
    
    def client_setter(self, client):
        self.client = client

    def led(self, state):
        try:
            if state is not None and state:
                pico_led.on() 
            else:    
                pico_led.off() 
        except Exception as e:
            print('pico_led FAIL',state)

    def tresholdConstr(self, num, buf):
        sins = int(1024/num)
        treshold = (np.ones(NUM_CONST))
        treshold[0:40] = 0.0

        for j in range(num):
            for i in range(sins):
                treshold[sins*j+i] = buf[j]*treshold[sins*j+i]*num*0.002
        return treshold
    
    def FFTPrint(self, arr, arr_w, num):
        Noise = False
        l = int(len(arr)/2)
        sins = 16
        wide = int(NUM_CONST /sins/2)
        
        treshold = np.zeros(sins,dtype = np.bool)
        treshold_v = (np.ones(NUM_CONST))*sins*0.002
        
        treshold_v[0:40] = 0
        final = np.zeros(sins*2)
        
        for i in range(sins - 1):
            final[i] = np.max(arr[wide*i:wide*i+wide]*arr[wide*i:wide*i+wide]*arr_w[wide*i:wide*i+wide])
        m=int(wide/2)
        for k in range(sins):
            if final[k] > 120:
                final[k] = 120
            if((final[k]) > 50):
                treshold[k] = True
            if (treshold[k]):
                Noise = True
            if Noise:
                return treshold[k]
            else:
                None

    def i2sForFFT(self, NUM = NUM_CONST):
        buf = array.array("H", [21845 for x in range(NUM)])
        audio_in = I2S(1, sck=Pin(0), ws=Pin(1), sd=Pin(2), mode=I2S.RX, bits=16, format=I2S.MONO, rate=FREQ_S, ibuf=NUM) # create I2S object //23ms
        n = audio_in.readinto(buf)          # fill buffer with audio samples from I2S device

        audio_in.deinit()
        x = (65535 - np.array(buf))/32768
        a = np.fft.fft(x)[0][0:NUM_CONST]
        return a

    def microphone_check(self):
        t = time.ticks_ms()+500

        while(time.ticks_ms() < t):
            r = self.i2sForFFT(NUM_CONST)
            self.result = self.FFTPrint(r ,self.equalizer, self.sinNum)
            if self.result is not None:
                self.last_status = True
                self.last_time = time.ticks_ms()
                self.led(1)
                self.send_status()
                break
            else:
                self.led(0)
                


    def send_status(self):
        if(self.last_status):
            print("test")
            msg = b'ON'
            test = b'house/picoa/command/switch'
            self.client.publish(self.topic_pub_status, msg)
            self.client.publish(test, msg)
            self.last_status = False
            self.last_time = time.ticks_ms()
        elif( time.ticks_ms() > (self.last_time + 300_000) ):
            print("hrest")
            self.last_status = False
            self.last_time = time.ticks_ms()
            msg = b'OFF'
            test = b'house/picoa/command/switch'
            self.client.publish(self.topic_pub_status, msg)
            self.client.publish(test, msg)
            

    def set_additional_proc(self, rt):
        self.rt = rt
        self.rt['MICROPHONE'] = {'last_start': time.time (), 'interval': 1, 'proc': self.microphone_check , 'last_error': 0}
        self.rt['SEND_STATUS'] = {'last_start': time.time (), 'interval': 1, 'proc': self.send_status , 'last_error': 0}
        return self.rt

    
    def topic_getter(self):
        topics = (self.topic_sub_switch, self.topic_sub_pwm)
        return topics
        
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
                   
            elif topic == self.topic_sub_switch or  self.topic == topic_sub_pwm:
               msgpub=f'Pico received unknown %s'%(msg,)              
               client.publish(self.topic_pub_info, msgpub)
               return
            else :
               print('Pico received ???',topic, msg)
               return
               
        except Exception as e:
            print('Exception in app_cb ', e)
      

      
        


#TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    mqtt.microphone_check()
    mqtt.send_status()
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()






