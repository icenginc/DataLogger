import pigpio
import binascii
import time
import os, sys

I2C_MuxAddress = 0x75
args = sys.argv

def checkInputs():
    """This function checks the user inputs. Inputs are as follows:
    I2C Port Selection: (1, 2, 3, 4)
    Returns selected port"""
    
    if len(args) == 2:
        return args[1]
    else:
        print("Invalid Arguments - Need port number")
        print("Ex: python i2cMux.py 2\tSelects Port #2 on the I2C Multiplexer")
        exit()

def readI2CMux(selectedPort):
    """This function takes the selected Port and sends a configuratio byte
    to the I2C Mux"""
    try:
        try:
            if pi.connected:
                print("Pigpio i2cMux already connected.")
        except:
            pi = pigpio.pi()
        handle = pi.i2c_open(1, I2C_MuxAddress)
        time.sleep(.2)
        controlByte = 0x04
        if (int(selectedPort) == 1):
            #Selects ADC Chip
            controlByte = 0x01 #0x04-RevA,0x01-RevB mux values
        elif (int(selectedPort) == 2):
            #Selects I2C (channel 1 - J5)
            controlByte = 0x02 #0x05-RevA,0x02-RevB mux values
        elif (int(selectedPort) == 3):
            #Selects I2C (channel 2 - J6)
            controlByte = 0x04 #0x06-RevA,0x04-RevB mux values
        elif (int(selectedPort) == 4):
            #Selects LCD Screen
            controlByte = 0x08 #0x07-RevA,0x08-RevB mux values
        pi.i2c_write_byte(handle, controlByte)
        time.sleep(0.1)
        pi.i2c_close(handle)
        time.sleep(.1)
        #print("I2C Mux Sent: " + hex(controlByte))
    except Exception as e:
        print("Error Configuring I2C Mux")
        print(e)
    finally:
        if pi.connected:
            pi.stop()

def main():
    """This is the main function"""
    selectedPort = checkInputs()
    print("Selected Port: " + str(selectedPort))
    readI2CMux(selectedPort)

#main()
