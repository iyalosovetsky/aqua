import re

from machine import UART, Pin
import machine

from secrets import topics
import time 
from picozero import pico_temp_sensor, pico_led

# from time import ticks_ms
import json 
import os
# import rp2
import array
# import pi18
from pi18 import pi18 as pi18

import math

prot=pi18.pi18()
uart0 = UART(0, baudrate=2400, parity=None, stop=1, tx=Pin(0), rx=Pin(1))
app_self = None


R_INTERNAL=0.0012
KOEF=[]
KOEF.append({'v': 40.0, 'prc':0})
KOEF.append({'v': 48.0, 'prc':9})
KOEF.append({'v': 50.0, 'prc':14})
KOEF.append({'v': 51.2, 'prc':17})
KOEF.append({'v': 51.6, 'prc':20})
KOEF.append({'v': 52.0, 'prc':30})
KOEF.append({'v': 52.4, 'prc':40})
KOEF.append({'v': 52.8, 'prc':70})
KOEF.append({'v': 53.2, 'prc':90})
KOEF.append({'v': 53.6, 'prc':99})
 
counter = 0







rtc=machine.RTC()


def fprc(voltage,power):
    v1=voltage+math.sqrt(power*R_INTERNAL)
    vprev=None
    res=None
    if v1<=KOEF[0]['v']:
      return 0.1
    elif v1>KOEF[len(KOEF)-1]['v']:
      return 100.0
    for v in KOEF:
        if vprev is not None:
          if v1<=v['v']:
              res=v
              break
        vprev=v    
    if res is not None and  vprev is not None:
        vd=v1-vprev['v']
        if vd>0:
          k=vd/(res['v']-vprev['v'])
        elif vd==0:  
          k=0.0  
        else:
          k=0.5
        return  vprev['prc']+(res['prc']-vprev['prc'])*k
    else:
          return 0.0

def sendCmd0(connector, request):
    connector.write(request[:8])
    if len(request) > 8:
        connector.write(request[8:])

answer_uart = []



def publish(topic, value, client):
    if client is not None:
        client.publish(topic, value)



class app:
    topic_pub_info = topics['topic_pub_info']
    topic_pub = topics['topic_pub']
    topic_sub = topics['topic_sub']

    debugmode = 0
    
    def __init__(self):
        self.client = None
        self.error_cnt =0
        self.error_readed =0
        app_self = self
        print('solar inited')
    
    def debugmode_setter(self):
        self.debugmode = 1

    def no_debugmode_setter(self):
        self.debugmode = 0


    
    def client_setter(self, client):
        self.client = client
        print('client_setter',self.client)

    def set_additional_proc(self, rt):    
        self.rt =  rt
        self.rt['POP']       = {'last_start': time.time (), 'interval': 4, 'proc': self.process_pop_msg , 'last_error': 0}
        self.rt['ED'] = {'last_start': time.time ()-860, 'interval': 901, 'proc': self.process_ed , 'last_error': 0}
        return self.rt


        


    
    def topic_getter(self):
        topics = (self.topic_sub, self.topic_sub)
        return topics
        
    def state_app(self):
        errs=self.error_readed+0
        self.error_readed =0
        return {"answer_uart":answer_uart, "error_cnt": self.error_cnt,"error_readed":errs,"debugmode": self.debugmode}
    
    
    
    def filter_answer (self, answOne):
        res=[]
        if answOne[1] is None or answOne[1]=='':
            return res
        if answOne[0]=='MAIN':
            answer_full =prot.decode(answOne[1],"GS")
        elif answOne[0].startswith('DS'):
            answer_full =prot.decode(answOne[1],'ED'+answOne[0][2:])
        else:    
            answer_full =prot.decode(answOne[1],answOne[0])
        for i, k in enumerate(answer_full):
            if k=='_command':
                continue
            elif k=='_command_description':
                continue
            elif k=='raw_response':
                continue
            elif '2' in k or 'Grid' in k:
                continue
            elif 'parallel' in k:
                continue
            else:
                if answOne[0]=='MAIN':
                    res.append([self.topic_pub+b'/'+k.replace(' ','_'), answer_full[k][0], k.replace(' ','_')])
                elif answOne[0].startswith('DS'):
                    res.append([self.topic_pub+b'/'+k.replace(' ','_'), answer_full[k][0], k.replace(' ','_')])
                else:
                    obj= {}
                    obj[k]=answer_full[k]
                    res.append(obj)
        return res
    
    def get_prc_bat(self, arr):
        v = None
        p = None
        state = None
        Ppv1 = None
        CurrDisch = None
        Capacity = None
        try:
            for answOne in arr:
                if len(answOne)>2 :
                    if answOne[2]=="Battery_voltage":
                        v = float(answOne[1])
                    elif answOne[2]=="AC_output_active_power":
                        p = float(answOne[1])
                    elif answOne[2]=="DC/AC_power_direction":
                        state = answOne[1]
                    elif answOne[2]=="PV1_Input_power":
                        Ppv1 = float(answOne[1])
                    elif answOne[2]=="Battery_discharge_current":
                        CurrDisch = float(answOne[1])    
                    elif answOne[2]=="Battery_capacity":
                        Capacity = float(answOne[1])    
            if v is not None and p is not None and state is not None and Ppv1 is not None:
                if state.startswith('DC') and Ppv1<=50.0:
                    prc = fprc(v,p)
                    print('prc is',prc)
                    return '%d'%(prc)
                else:
                    if (CurrDisch is not None and CurrDisch<1.0) and (Capacity is not None and Capacity>=99) :
                       return 'on net'
                    else:                                                  
                       return 'charging..'
            else:
                print('cant get p, v, Ppv1')
            return None                                                                                     
        except Exception as e:
            print('error get prc ',e)
            return None    
 
    def process_pop_msg(self):
        try:
            ii=0  
            while len(answer_uart)>0 and ii<100:
                ii+=1
                answOne=answer_uart.pop(0)
                answLst=self.filter_answer (answOne)
                if answOne[0]=='MAIN':
                    for answOne in answLst:
                        answ=json.dumps(answOne[1])
                        publish(answOne[0],answ,self.client)
                    prc=self.get_prc_bat(answLst)
                    if prc is not None:
                        publish(self.topic_pub+b'/Battery_percent',prc,self.client)
                elif answOne[0].startswith('DS'):
                    for answOne in answLst:
                        answ=json.dumps(answOne[1])
                        publish(answOne[0],answ,self.client)
                else:
                    for answOne in answLst:
                        answ=json.dumps(answOne)
                        publish(self.topic_pub,answ,self.client)
        except Exception as e:
            print('process_pop_msg',e)
            return -6
        else:
            return 0
    
    def get_state(self, client):
        publish(self.topic_sub, 'MAIN', client) # why topic_sub?
        return 0

    def process_ed(self):
        global app_self
        if self is None and app_self is None:
            print('process_ed: self is None',e)
            return 0
        elif self is None and app_self is not None:
            self = app_self
        
        global counter
        counter += 1
        try:
            now=f'UTC {rtc.datetime()[2]:02}.{rtc.datetime()[1]:02}.{rtc.datetime()[0]:04} {rtc.datetime()[4]:02}:{rtc.datetime()[5]:02}'
            msg = b'I will get dayly stats %s #%d ' % (now, counter)
            publish(self.topic_pub, msg,self.client)
            publish(self.topic_sub, 'DS',self.client)
        except Exception as e:
            print('process_ed',e)
            return -3
        else:
            return 0        


    def sub_cb2Uart(self,msg):
        try:
            if msg=='MAIN':
                cmd=prot.get_full_command('GS')
            elif msg.startswith('DS'):
                cmd=prot.get_full_command('ED'+msg[2:])
            else:
                cmd=prot.get_full_command(msg)
            print(cmd,"to uart0")
            if cmd is None:
                print("break for None cmd")
                #return
            uartr=""
            sendCmd0(uart0, cmd)
            time.sleep(0.75)
            while uart0.any() > 0:    #Channel 0 is spontaneous and self-collecting
                uartr=uart0.read()
            if self.debugmode >2:   
                if msg=='MAIN':    
                    uartr=b'^D1060000,000,2301,500,0437,0292,010,528,000,000,005,000,100,030,000,000,0000,0000,0000,0000,0,0,0,1,2,2,0,0p\xdc\r'        
                elif msg=='GS':    
                    uartr=b'^D1060000,000,2301,500,0437,0292,010,528,000,000,005,000,100,030,000,000,0000,0000,0000,0000,0,0,0,1,2,2,0,0p\xdc\r'        
            if uartr is None or uartr=='':
                return 
            print("uart:",uartr)
            while len(answer_uart)>10:
                    answer_uart.pop(0)
            answer_uart.append([msg,uartr,time.time()])
        except OSError as e:
            self.error_cnt +=1
            self.error_readed +=1
            print('OSError error_cnt',self.error_cnt, e)
        except Exception as e:
            print('Exception error_cnt',self.error_cnt, e)

    def app_cb(self, client, topic0, msg0):
        global rtc
        print(msg0,topic0)
        try:
            msg =  msg0.decode("utf-8")
            topic = topic0.decode("utf-8")
            if topic.startswith(self.topic_sub):
                if msg in  prot.STATUS_COMMANDS :
                    if msg=='ED':
                        msg= 'ED'+f'{rtc.datetime()[0]:04}{rtc.datetime()[1]:02}{rtc.datetime()[2]:02}'
                    if self.debugmode>0 and self.client is not None:
                        publish(self.topic_pub, "change to %s"%msg, client)
                    elif msg=='EM':
                        msg= 'EM'+f'{rtc.datetime()[0]:04}{rtc.datetime()[1]:02}'
                    if self.debugmode>0:
                        publish(self.topic_pub, "change to %s"%msg, client)
                    elif msg=='EY':
                        msg= 'EY'+f'{rtc.datetime()[0]:04}'   
                    if self.debugmode>0:
                        publish(self.topic_pub, "change to %s"%msg, client)
                    print('Pico received STATUS_COMMANDS',msg)
                    self.sub_cb2Uart(msg)
                elif msg[0:2] in  prot.STATUS_COMMANDS :
                    print('Pico received STATUS_COMMANDS',msg)
                    self.sub_cb2Uart(msg)
                elif msg in  prot.SETTINGS_COMMANDS :
                    print('Pico received SETTINGS_COMMANDS',msg)
                    self.sub_cb2Uart(msg)
                elif msg=='MAIN':
                    print('Pico received general query',msg)
                    self.sub_cb2Uart(msg)
                elif msg=='DS':
                    msg= 'DS'+f'{rtc.datetime()[0]:04}{rtc.datetime()[1]:02}{rtc.datetime()[2]:02}'
                    if self.debugmode>0:
                        publish(self.topic_pub, "change to %s"%msg, client)
                    print('Pico received dayly stats query',msg)
                    self.sub_cb2Uart(msg)
                elif msg.startswith('DEBUG'):
                    if msg!='DEBUG' : 
                        self.debugmode=int(msg.replace('DEBUG',''))
                    else:
                        self.debugmode=1
                    msgpub=f'Pico received DEBUG %d'%(self.debugmode,)
                    publish(self.topic_pub, msgpub, client)
                else :
                    msgpub=f'Pico received unknown %s'%(msg,)              
                    publish(self.topic_pub, msgpub, client)
            else: 
                    print('Pico received ???',topic, msg)
                    return
        except Exception as e:
            print('Genelal Exception in app_cb ', e)
      

      



#TODO updated working test code            
if __name__=='__main__':
    mqtt = app()
    #mqtt.connect_and_subscribe()
    #mqtt.aquaProceed(station)
    #mqtt.restart_and_reconnect()





