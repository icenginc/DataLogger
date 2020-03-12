import time
import pigpio
import sqlite3 as lite
import sys
import threading
import RPi.GPIO as GPIO
import i2cMux
import logging

LCD_Address = 0x3C
maxCharacters = 20
GPIO.setwarnings(False)

def initLCD():
    print("Initializing LCD")
    i2cMux.readI2CMux(4)
    time.sleep(0.1)
    pi = pigpio.pi()
    try:
        handle = pi.i2c_open(1, LCD_Address)
        time.sleep(.5)
        pi.i2c_write_device(handle, [0x00,0x38,0x39,0x14,0x78,0x5E,0x6D,0x0c,0x01,0x06])
        time.sleep(0.5)
        pi.i2c_close(handle)
        time.sleep(.2)
        pi.stop()
    except:
        logging.debug("lcdTest.py:initLCD, Error Initializing LCD")
        print("Error Initializing LCD")

# Write's on second line
def writeText2(text):
    i2cMux.readI2CMux(4)
    time.sleep(0.1)
    pi = pigpio.pi()
    try:
        handle = pi.i2c_open(1, LCD_Address)
        time.sleep(.1)
        pi.i2c_write_device(handle, [0x00,0xC0])
        time.sleep(.1)
        while len(text) < 20:
            text = text + " "
        pi.i2c_write_device(handle, "A" + text)
        time.sleep(.1)
        pi.i2c_close(handle)
        time.sleep(.1)
        pi.stop()
    except Exception as e:
        logging.debug("lcdTest.py:writeText2, Error Writing LCD Text2")
        print("lcdTest.py:writeText2, Error Writing LCD Text2")

def writeText(text):
    i2cMux.readI2CMux(4)
    time.sleep(0.1)
    pi = pigpio.pi()
    try:
        handle = pi.i2c_open(1, LCD_Address)
        time.sleep(.1)
        pi.i2c_write_device(handle, [0x00,0x02])
        time.sleep(.1)
        while len(text) < 20:
            text = text + " "
        pi.i2c_write_device(handle, "A" + text)
        time.sleep(.1)
        pi.i2c_close(handle)
        time.sleep(.1)
        pi.stop()
    except Exception as e:
        logging.debug("lcdTest.py:writeText, Error Writing LCD Text")
        print("lcdTest.py:writeText, Error Writing LCD Text")

def getChannelString(channel):\
    if channel == "1":
        return "ADC 1"
    elif channel == "2":
        return "ADC 2"
    elif channel == "3":
        return "ADC 3"
    elif channel == "4":
        return "ADC 4"
    elif channel == "5":
        return "I2C 1"
    elif channel == "6":
        return "I2C 2"

def readFromDatabase(channel):
    con = None
    data = None
    inputType = getChannelString(channel)
    try:
        con = lite.connect('/home/pi/Documents/DataLogger/_database/temperatures.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM tempData WHERE inputType = '" + inputType + "'")
        data = cur.fetchone()
    except lite.Error, e:
        print("Error: " + e)
    finally:
        if con:
            con.close()
    return data

def repeatThis(channel, dictionaryData):
    data = ""
    minD = ""
    maxD = ""
    unit = ""
    if ('data' + str(channel)) in dictionaryData:
        data = dictionaryData['data' + str(channel)]
    if data.find(":") != -1:
        temp2 = data.split(":")
        tempT = temp2[0]
        tempH = temp2[1]
        tempUnitT = "C"
        tempUnitH = "%H"
        tempFinal = str("{0:.1f}".format(float(tempT))) + tempUnitT + ", " + str("{0:.1f}".format(float(tempH))) + tempUnitH
        print(tempFinal)
        writeText(tempFinal)
    else:
        text = "Temp: " + str(round(data,4)) + unit
        print(text)
        writeText(text)
    time.sleep(0.2)
    if minD.find(",") != -1 and maxD.find(",") != -1:
        minTemp = minD.split(",")
        maxTemp = maxD.split(",")
        tempUnitT = "C"
        tempUnitH = "%H"
        tempString = "Min:" + str("{0:.1f}".format(float(minTemp[0]))) + tempUnitT + \
                     ", Max:" + str("{0:.1f}".format(float(maxTemp[0]))) + tempUnitT
        print(tempString)
    else:
        if len(minD) > 0 and len(maxD) > 0:
            tempString = "Min:" + str("{0:.1f}".format(float(minD))) + \
                     "Max:" + str("{0:.1f}".format(float(maxD)))
            print(tempString)

def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(27, GPIO.OUT)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(22, GPIO.OUT)
    
def setLCDBacklight(setting = 1):   
    if setting == 1: # GREEN
        GPIO.output(27, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(22, GPIO.LOW)
    elif setting == 2: # RED
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(27, GPIO.LOW)
        GPIO.output(22, GPIO.LOW)
    elif setting == 3: # BLUE
        GPIO.output(22, GPIO.HIGH)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
    else:
        GPIO.output(27, GPIO.LOW)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(22, GPIO.LOW)

def startLogger():
    logging.basicConfig(filename="../_logs/LCD_debug.log", filemode="w", level=logging.DEBUG, format="%(asctime)s, %(levelname)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")
    logging.info("START LOGGING")

####--------------------------------------------------------------------

def main():
    print("Main")
    startLogger()
    i2cMux.readI2CMux(4)
    setupGPIO()
    initLCD()
    toggle = 0
    while True:
        repeatThis()
        if toggle == 0:
            setLCDBacklight(1)
            toggle = 1
        else:
            setLCDBacklight(3)
            toggle = 0
        time.sleep(4)

#main()
