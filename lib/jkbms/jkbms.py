import re

from machine import UART, Pin
import machine

from secrets import topics
import time 
from picozero import pico_temp_sensor, pico_led

import json 

import time
import struct

import math

uart0 = UART(1, baudrate=115200, bits=8, parity=None, stop=1, tx=Pin(4), rx=Pin(5))
app_self = None

moc_data_jkbms=b'NW\x01!\x00\x00\x00\x00\x06\x00\x01y0\x01\r$\x02\r!\x03\r#\x04\r$\x05\r$\x06\r#\x07\r \x08\r#\t\r$\n\r!\x0b\r \x0c\r$\r\r$\x0e\r!\x0f\r$\x10\r\x1e\x80\x00\x17\x81\x00\x16\x82\x00\x16\x83\x15\x04\x84\x00\x14\x85N\x86\x02\x87\x00\x00\x89\x00\x00\x01\x06\x8a\x00\x10\x8b\x00\x00\x8c\x00\x03\x8e\x16\x80\x8f\x10@\x90\x0e\x10\x91\r\xde\x92\x00\x03\x93\n(\x94\nZ\x95\x00\x03\x96\x01,\x97\x00\xc8\x98\x01,\x99\x00<\x9a\x00\x1e\x9b\x0c\xe4\x9c\x00\n\x9d\x01\x9e\x00d\x9f\x00P\xa0\x00F\xa1\x00<\xa2\x00\x14\xa3\x00F\xa4\x00F\xa5\x00\x05\xa6\x00\n\xa7\xff\xec\xa8\xff\xf6\xa9\x10\xaa\x00\x00\x01\x18\xab\x01\xac\x01\xad\x03\xe8\xae\x01\xaf\x00\xb0\x00\n\xb1\x14\xb22904\x00\x00\x00\x00\x00\x00\xb3\x00\xb4Input Us\xb52408\xb6\x00\x00J\xfc\xb711A___S11.52___\xb8\x00\xb9\x00\x00\x01\x18\xbaInput Userdaeve280Ah\x00\x00\x00\x00\xc0\x01\x00\x00\x00\x00h\x00'

def sendBMSCommand(cmd_string):
    cmd_bytes = bytearray.fromhex(cmd_string)
    for cmd_byte in cmd_bytes:
        hex_byte = ("{0:02x}".format(cmd_byte))
        uart0.write(bytearray.fromhex(hex_byte))
    return






 
counter = 0







rtc=machine.RTC()





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
        self.error_reded =0
        app_self = self
        print('jkbms inited')
    
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
        errs=self.error_reded+0
        self.error_reded =0
        return {"answer_uart":answer_uart, "error_cnt": self.error_cnt,"error_readed":errs,"debugmode": self.debugmode}
    

    def readBMS2(self):
        try: 
            data = self.uart_pop_data
            length = data[2]*256+data[3]-2
            res={}
            if len(data)!=length+1 :
                uart0.read()
                return res
                

            
            # # Calculate the CRC sum
            # crc_calc = sum(data[0:-4])
            # # Extract the CRC value from the data
            # crc_lo = struct.unpack_from('>H', data[-2:])[0]
            
            # Exit if CRC doesn't match
            #if crc_calc != crc_lo :
            #    bms.reset_input_buffer()
            #    raise Exception("CRC Wrong")
        
            # The actual data we need
            self.data = self.data[11:length-19] # at location 0 we have 0x79
            
            # The byte at location 1 is the length count for the cell data bytes
            # Each cell has 3 bytes representing the voltage per cell in mV
            self.bytecount = self.data[1]
            
            # We can use this number to determine the total amount of cells we have
            self.cell_count = int(self.bytecount/3)
            res['cells'] =self.cell_count
            self.cells =[]        

            # Voltages start at index 2, in groups of 3
            for i in range(self.cell_count) :
                v=struct.unpack_from('>xH', self.data, i * 3 + 2)[0]/1000
                res['cell_'+str(i+1)] =v
                self.cells.append(v)
                
            # Temperatures are in the next nine bytes (MOSFET, Probe 1 and Probe 2), register id + two bytes each for data
            # Anything over 100 is negative, so 110 == -10
            self.temp_fet = struct.unpack_from('>H', self.data, self.bytecount + 3)[0]
            if self.temp_fet > 100 :
                self.temp_fet = -(self.temp_fet - 100)
            res['temp_fet'] =self.temp_fet
            self.temp_1 = struct.unpack_from('>H', self.data, self.bytecount + 6)[0]
            if self.temp_1 > 100 :
                self.temp_1 = -(self.temp_1 - 100)
            res['temp_1'] =self.temp_1

            self.temp_2 = struct.unpack_from('>H', self.data, self.bytecount + 9)[0]
            if self.temp_2 > 100 :
                self.temp_2 = -(self.temp_2 - 100)
            res['temp_2'] =self.temp_2


                    
            # Battery voltage
            self.voltage = struct.unpack_from('>H', self.data, self.bytecount + 12)[0]/100
            res['voltage'] =self.voltage

            # Current
            self.current = struct.unpack_from('>H', self.data, self.bytecount + 15)[0]/100
            res['current'] =self.current
                
            # Remaining capacity, %
            self.capacity = struct.unpack_from('>B', self.data, self.bytecount + 18)[0]                   
            res['capacity'] =self.capacity

            return res
                        
        except Exception as e :
            print(e)
            return res



    
  
 
    def process_pop_msg(self):
        try:
            ii=0  
            while len(answer_uart)>0 and ii<100:
                ii+=1
                self.uart_pop_data=answer_uart.pop(0)
                answerLst=self.readBMS2()
                for answerItem in answerLst:
                    answer=json.dumps(answerItem[1])
                    publish(answerItem[0],answer,self.client)
                prc=94.0
                if prc is not None:
                    publish(self.topic_pub+b'/Battery_percent',prc,self.client)

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
            msg = b'I will get daily stats %s #%d ' % (now, counter)
            publish(self.topic_pub, msg,self.client)
            publish(self.topic_sub, 'DS',self.client)
        except Exception as e:
            print('process_ed',e)
            return -3
        else:
            return 0        


    def sub_cb2Uart(self,msg):
        try:
            cmd =''
            if msg=='MAIN':
                cmd='4E 57 00 13 00 00 00 00 06 03 00 00 00 00 00 00 68 00 00 01 29'.replace(' ','')
            print(cmd,"to uart0")
            if cmd is None:
                print("break for None cmd")
                #return
            uart_read=""
            uart0.read()
            time.sleep(.1)
            uart0.read()
            time.sleep(.1)
            sendBMSCommand(cmd)

            time.sleep(0.75)
            while uart0.any() > 0:    #Channel 0 is spontaneous and self-collecting
                uart_read=uart0.read()
            if self.debugmode >2:   
                if msg=='MAIN':    
                    uart_read=moc_data_jkbms  
            if uart_read is None or uart_read=='':
                return 
            print("uart:",uart_read)
            while len(answer_uart)>10:
                    answer_uart.pop(0)
            answer_uart.append([msg,uart_read,time.time()])
        except OSError as e:
            self.error_cnt +=1
            self.error_reded +=1
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
                if msg in ['MAIN'] :
                    print('Pico received MAIN COMMAND',msg)
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
            print('General Exception in app_cb ', e)
      

      




if __name__=='__main__':
    mqtt = app()
 





