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

VERSION = '1.0.5'

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
        self.uart_pop_data=b'\x00\x00\x00\x00'
        print('jkbms inited')
    
    def debugmode_setter(self):
        self.debugmode = 1

    def no_debugmode_setter(self):
        self.debugmode = 0


    
    # def client_setter(self, client):
    #     self.client = client
    #     print('client_setter',self.client)

    def client_setter(self, client):
        self.client = client
        msg = b'version is '+VERSION
        print('client_setter',self.client)
        client.publish(self.topic_pub_info, msg)        

    def process_pop_msg(self):
        global answer_uart
        try:
            ii=0  
            while len(answer_uart)>0 and ii<100:
                ii+=1
                self.uart_pop_data=answer_uart.pop(0)[1]
                answerLst=self.readBMS2()
                for answerItem in answerLst:
                    v=answerLst[answerItem]
                    if isinstance(v,(int,float)):
                        v=str(v)
                    publish(self.topic_pub+'/'+answerItem,v,self.client)


        except Exception as e:
            print('process_pop_msg',e)
            return -6
        else:
            return 0

    def set_additional_proc(self, rt):    
        self.rt =  rt
        self.rt['POP']       = {'last_start': time.time (), 'interval': 4, 'proc': self.process_pop_msg , 'last_error': 0}
        self.rt['ED'] = {'last_start': time.time ()-860, 'interval': 17, 'proc': self.process_ed , 'last_error': 0}
        return self.rt


        


    
    def topic_getter(self):
        topics = (self.topic_sub, self.topic_sub)
        return topics
        
    def state_app(self):
        errs=self.error_reded+0
        self.error_reded =0
        return {"answer_uart":answer_uart, "error_cnt": self.error_cnt,"error_readed":errs,"debugmode": self.debugmode}
    
    # This script reads the data from a JB BMS over RS-485 and formats
    # it for use with https://github.com/BarkinSpider/SolarShed/
    # https://github.com/PurpleAlien/jk-bms_grafana/blob/main/data_bms.py
    def readBMS2(self):
        res={}
        try: 
            data = self.uart_pop_data
            length = data[2]*256+data[3]-2
            
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
            data = data[11:length-19] # at location 0 we have 0x79
            
            # The byte at location 1 is the length count for the cell data bytes
            # Each cell has 3 bytes representing the voltage per cell in mV
            self.bytecount = data[1]
            
            # We can use this number to determine the total amount of cells we have
            self.cell_count = int(self.bytecount/3)
            res['cell_count'] =self.cell_count
            self.cells =[]        

            # Voltages start at index 2, in groups of 3
            for i in range(self.cell_count) :
                v=struct.unpack_from('>xH', data, i * 3 + 2)[0]/1000
                res['cell_'+str(i+1)] =v
                self.cells.append(v)
                
            # Temperatures are in the next nine bytes (MOSFET, Probe 1 and Probe 2), register id + two bytes each for data
            # Anything over 100 is negative, so 110 == -10
            #62-63(59+3)
            #Температура силових транзисторів °С (00 1С переводимо в десяткову, отримуємо 28 °С)
            self.temp_fet = struct.unpack_from('>H', data, self.bytecount + 3)[0]
            if self.temp_fet > 100 :
                self.temp_fet = -(self.temp_fet - 100)
            res['temp_fet'] =self.temp_fet
            #65-66(59+6)
            #Температура плати балансування °С ( 00 1A = 26°С)
            self.temp_1 = struct.unpack_from('>H', data, self.bytecount + 6)[0]
            if self.temp_1 > 100 :
                self.temp_1 = -(self.temp_1 - 100)
            res['temp_1'] =self.temp_1
            #68-69(59+9)
            # Температура акумулятора °С
            self.temp_2 = struct.unpack_from('>H', data, self.bytecount + 9)[0]
            if self.temp_2 > 100 :
                self.temp_2 = -(self.temp_2 - 100)
            res['temp_2'] =self.temp_2


                    
            # Battery voltage
            #71-72(59+12)
            self.voltage = struct.unpack_from('>H', data, self.bytecount + 12)[0]/100
            res['voltage'] =self.voltage

            # Current
            #74-75(59+15) Струм акумулятора (два байта формують слово,
            # 15 біт цього слова передає значення, 16-тий (рахуємо починаючи з нуля
            # тому номер біта 15) передає знак. Плюс - струм іде в акумулятор, мінус - 
            current=struct.unpack_from('>H', data, self.bytecount + 15)[0]
            if current>=32768:
               current=-(current-32768)/100
            else:
                current=current/100
                   


            self.current = current
            res['current'] =self.current
                
            # Remaining capacity, %
            # 85 (номер байта 77) 
            # Рівень заряда акумулятора % (63 переводимо в десяткову, отримуємо 99%)
            #(59+18)
            self.capacity = struct.unpack_from('>B', data, self.bytecount + 18)[0]                   
            res['capacity'] =self.capacity


            # cycles count
            #(59+22) (номер байта 81, 82)Кількість циклів заряд розряд (00 06 = 6 повних циклів заряд розряд) 
            self.cycles=struct.unpack_from('>H', data, self.bytecount + 22)[0]
            res['cycles'] =self.cycles

            # energy count
            #(59+25) (номер байта 84, 87)Кількість енергії яку віддав акумулятор А год(00 00 02 96 = 662 Ампер годин)
            self.energy=struct.unpack_from('>L', data, self.bytecount + 25)[0]
            res['energy'] =self.energy

            # 89 B6 (номер байта 228, 231) Час роботи БМС в хвилинах (00 00 AD AF=44463хв



            return res
                        
        except Exception as e :
            print(e)
            return res



    
  
 

    
    def get_state(self, client):
        publish(self.topic_sub, 'MAIN', client) # why topic_sub?
        return 0

    # get stats from jk bms modbus
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
            #publish(self.topic_sub, 'DS',self.client)
            self.sub_cb2Uart('DS')
        except Exception as e:
            print('process_ed',e)
            return -3
        else:
            return 0        


    def sub_cb2Uart(self,msg):
        try:
            cmd =''
            if msg=='MAIN' or msg=='DS':
                #https://github.com/syssi/esphome-jk-bms/blob/main/components/jk_modbus/jk_modbus.cpp
                # static const uint8_t FUNCTION_WRITE_REGISTER = 0x02;
                # static const uint8_t FUNCTION_READ_REGISTER = 0x03;
                # static const uint8_t FUNCTION_PASSWORD = 0x05;
                # static const uint8_t FUNCTION_READ_ALL_REGISTERS = 0x06;

                # static const uint8_t ADDRESS_READ_ALL = 0x00;

                # static const uint8_t FRAME_SOURCE_GPS = 0x02;
                # read all registers
                # uint8_t frame[21];
                # frame[0] = 0x4E;                         // start sequence
                # frame[1] = 0x57;                         // start sequence
                # frame[2] = 0x00;                         // data length lb
                # frame[3] = 0x13;                         // data length hb
                # frame[4] = 0x00;                         // bms terminal number
                # frame[5] = 0x00;                         // bms terminal number
                # frame[6] = 0x00;                         // bms terminal number
                # frame[7] = 0x00;                         // bms terminal number
                # frame[8] = FUNCTION_READ_ALL_REGISTERS;  // command word: 0x01 (activation), 0x02 (write), 0x03 (read), 0x05
                #                                         // (password), 0x06 (read all)
                # frame[9] = FRAME_SOURCE_GPS;             // frame source: 0x00 (bms), 0x01 (bluetooth), 0x02 (gps), 0x03 (computer)
                # frame[10] = 0x00;                        // frame type: 0x00 (read data), 0x01 (reply frame), 0x02 (BMS active upload)
                # frame[11] = ADDRESS_READ_ALL;            // register: 0x00 (read all registers), 0x8E...0xBF (holding registers)
                # frame[12] = 0x00;                        // record number
                # frame[13] = 0x00;                        // record number
                # frame[14] = 0x00;                        // record number
                # frame[15] = 0x00;                        // record number
                # frame[16] = 0x68;                        // end sequence
                # auto crc = chksum(frame, 17);
                # frame[17] = 0x00;  // crc unused
                # frame[18] = 0x00;  // crc unused
                # frame[19] = crc >> 8;
                # frame[20] = crc >> 0; 
                # read only one register by address
                # uint8_t frame[22];
                # frame[0] = 0x4E;      // start sequence
                # frame[1] = 0x57;      // start sequence
                # frame[2] = 0x00;      // data length lb
                # frame[3] = 0x14;      // data length hb
                # frame[4] = 0x00;      // bms terminal number
                # frame[5] = 0x00;      // bms terminal number
                # frame[6] = 0x00;      // bms terminal number
                # frame[7] = 0x00;      // bms terminal number
                # frame[8] = function;  // command word: 0x01 (activation), 0x02 (write), 0x03 (read), 0x05 (password), 0x06 (read all)
                # frame[9] = FRAME_SOURCE_GPS;  // frame source: 0x00 (bms), 0x01 (bluetooth), 0x02 (gps), 0x03 (computer)
                # frame[10] = 0x00;             // frame type: 0x00 (read data), 0x01 (reply frame), 0x02 (BMS active upload)
                # frame[11] = address;          // register: 0x00 (read all registers), 0x8E...0xBF (holding registers)
                # frame[12] = value;            // data
                # frame[13] = 0x00;             // record number
                # frame[14] = 0x00;             // record number
                # frame[15] = 0x00;             // record number
                # frame[16] = 0x00;             // record number
                # frame[17] = 0x68;             // end sequence
                # auto crc = chksum(frame, 18);
                # frame[18] = 0x00;  // crc unused
                # frame[19] = 0x00;  // crc unused
                # frame[20] = crc >> 8;
                # frame[21] = crc >> 0;               
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
 





