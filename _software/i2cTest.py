
import smbus
import time
import sys
import subprocess
import pigpio
import binascii

pi = pigpio.pi()


I2C_Address = 0x16 #16
I2C_Bus_Number = 1

I2C_CH0 = 0b00000001
I2C_CH1 = 0b00000010
I2C_CH2 = 0b00000100
I2C_CH3 = 0b00001000
I2C_CH4 = 0b00010000
I2C_CH5 = 0b00100000
I2C_CH6 = 0b01000000
I2C_CH7 = 0b10000000


def read_I2C():

    handle = pi.i2c_open(I2C_Bus_Number, I2C_Address)

    pi.i2c_write_byte(handle, 0x00)
    time.sleep(0.55)
    (count, byteArray) = pi.i2c_read_device(handle, 2)

    #data = pi.i2c_read_byte(handle)
    #print(str(byteArray))

    
    pi.i2c_close(handle)

    print(count)
    print(binascii.hexlify(byteArray))
    

def I2C_Setup(I2C_CH_Setup):
    bus = smbus.SMBus(I2C_Bus_Number)
    print("Address: " + str(I2C_Address) + ", Data: " + str(I2C_CH_Setup))

    try:
        bus.write_byte(I2C_Address, 0x00)
        #bus.write_i2c_block_data(I2C_Address, 0xA0, [0x18])
        time.sleep(0.3)
    except IOError:
        subprocess.call(['i2cdetect', '-y', '1'])
        flag = 1

    #temp = bus.read_byte(I2C_Address)
    temp = bus.read_byte(I2C_Address)

    print("TCA6408 I2C Channel Status: " + str(bin(temp)) )




read_I2C()
#I2C_Setup(0xC)
