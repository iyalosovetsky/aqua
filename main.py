import mip
import network
import socket
import time
try:
    from secrets import secrets
except:
    print('File secrets not exist')

rt={}
error_cnt = 0
error_cnt_others = 0

def update():
    secrets.codeImport()
    time.sleep(10)
    machine.reset()

# restart function 
def restart_and_reconnect():  
    print('Too many errors. Reconnecting...')
    time.sleep(10)
    error_cnt = 0
    machine.reset()

# ekraning self.process_show_error()
def publish_error(class_low):
    try:
        class_low.process_show_error()
    except Exception as e:
        print("in function process_show_error() occur error", e)

# OS worker 
def p_RTLoop():
    for key, value in rt.items ():
        l_time = time.time ()
        l_timeprev = value['last_start']
        if value['proc'] is not None:
            if (((l_time - l_timeprev) > value['interval'])) :
                value['last_start'] = l_time
                try:  
                    value['last_error'] = value['proc'] ()
                    if value['last_error'] is None:
                        value['last_error'] = 0
                except Exception as e:
                    value['last_error'] = -97
                    print ('error rt ' + key, e)

# ekraning RTLoop into exceptions
def OSProceed(class_low, station):
    
    while True:
        try:
            p_RTLoop()
        except OSError as e:
            error_cnt +=1
            print('OSError error_cnt',error_cnt, e)
            try:
                publish_error(class_low)
            except Exception as e:
                print('cant broadcast error', e)
            if error_cnt>10: 
                print('OSError restart_and_reconnect()')
                restart_and_reconnect()
        except Exception as e:
            error_cnt_others +=1
            print('Exception error_cnt',error_cnt_others, e)
            if error_cnt>100:
               print('Exception restart_and_reconnect()')
               restart_and_reconnect()


#check wifi connection 
if station.isconnected() == False:
    while station.isconnected() == False:
      pass

    print('Connection successful')
    
print(station.ifconfig())
print('----------')

#add callback to OS
#TODO change last.start
rt['UPDATE'] = {'last_start': time.time (), 'interval': 86400, 'proc': update , 'last_error': 0}

# run app
try:
    import secrets
    print("app successful imported")
except:
    try:
        update()
        print("code successful downloaded")
        mqtt = secrets.app.m_mqtt(rt, station)
        OSProceed(mqtt, station)
    except:
        print("problem with downloaded code")
