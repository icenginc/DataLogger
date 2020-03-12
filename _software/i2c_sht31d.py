import i2cMux
import pigpio
import time

Hum_Address = 0x44

def enableDisableHeater(onOff):
    i2cMux.readI2CMux(3)
    time.sleep(0.2)
    pi = pigpio.pi()
    try:
        handle = pi.i2c_open(1, Hum_Address)
        time.sleep(.55)
        if onOff == 1:
            pi.i2c_write_device(handle, [0x30,0x6D])
        else:
            pi.i2c_write_device(handle, [0x30,0x66])
        time.sleep(0.2)
        pi.i2c_close(handle)
        time.sleep(0.1)
        pi.stop()
    except Exception as e:
        print("readHumidifier.py:enableDisableHeater(), Error Reading Humidifer")
        print(e)
