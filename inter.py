import machine
import utime
#butt1 = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_DOWN)
butt1 = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin('LED', machine.Pin.OUT)

def int_handler(pin):
    butt1.irq(handler = None)
    print("int_handler ",pin)
    led.on()
    utime.sleep(2)
    led.off()
    butt1.irq(handler = int_handler)
    

butt1.irq(trigger = machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler = int_handler)

while True:
    utime.sleep(0.5)
    