import time
import pigpio


LCD_Address = 0x3C

pi = pigpio.pi()

def initLCD():

    handle = pi.i2c_open(1, LCD_Address)
    time.sleep(.01)

    pi.i2c_write_device(handle, [0x00,0x38,0x39,0x14,0x78,0x5E,0x6D,0x0c,0x01,0x06])
    time.sleep(0.01)

    pi.i2c_close(handle)

def writeText(text):

    handle = pi.i2c_open(1, LCD_Address)
    time.sleep(.01)

    pi.i2c_write_byte(handle, 0x40)

    pi.i2c_write_device(handle, text)
    time.sleep(.01)

    pi.i2c_close(handle)
