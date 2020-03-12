#!/usr/bin/env python
import os,sys
import re
import time
#import readADC
#import readHumidifier
import lcdtest
import uploadCSV
import datetime
import subprocess
import threading
import socket
import atexit
import logging
import i2cMux
#import LCDLibrary
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
button1 = 23
button2 = 24
button3 = 25
sensor_Run = 12
sensor_Alarm = 16

# Port 1 -> ADC
# Port 2 -> I2C 1
# Port 3 -> I2C 2
# Port 4 -> LCD Display
portChannels = []
dictionaryData = {}
timer = 0

def getIPAddress():
    s= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
    return ip

def action_button1(empty):
    print("Button 1")
    dictionaryData = uploadCSV.getAllDictionaries(1) # HARD CODED
    ipAddress = getIPAddress()
    systemName = dictionaryData['system']
    lcdtest.writeText(systemName)
    ipAddress = (ipAddress).strip()
    lcdtest.writeText2(ipAddress)
    time.sleep(0.5)

def action_button2(empty):
    print("Action Button 2")
    returnData = lcdtest.readFromDatabase("5")
    temp = returnData[4]
    data = dictionaryData['data5']
    unit = dictionaryData['unit5']
    if temp.find(":") != -1 and unit.find(",") != -1:
        temp2 = temp.split(":")
        tempT = temp2[0]
        tempH = temp2[1]
        temp3 = unit.split(",");
        tempUnitT = temp3[0]
        tempUnitH = temp3[1]
        tempFinal = str("{0:.1f}".format(float(tempT))) + tempUnitT + ", " + str("{0:.1f}".format(float(tempH))) + tempUnitH
    print(tempFinal)
    lcdtest.writeText(tempFinal)
    time.sleep(0.5)

def action_button3(empty):
    lcdtest.initLCD()
    time.sleep(0.5)

def initGPIO():
    print("Initialize GPIO")
    GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(button3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(button1, GPIO.FALLING, callback=action_button1)
    GPIO.add_event_detect(button2, GPIO.FALLING, callback=action_button2)
    GPIO.add_event_detect(button3, GPIO.FALLING, callback=action_button3)
    GPIO.setup(sensor_Run, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(sensor_Alarm, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def checkI2CLibrary():
    """Checks to see if the pigpiod library is running"""
    proc = subprocess.Popen(["pigs pigpv"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    out = out.strip()
    if (out != "socket connect failed" and len(out) > 0):
        print("pigpiod Library Running")
    else:
        logging.debug("Restart I2C")
        os.system("python /home/pi/Documents/DataLogger/_software/restartI2C.py")

def checkGPIOButtons():
    if GPIO.input(button1):
        action_button1(button1)
    elif GPIO.input(button2):
        action_button2(button2)
    elif GPIO.input(button3):
        action_button3(button3)
    time.sleep(0.3)

def startLogger():
    date = datetime.date.today()
    debugFilename = "debug" + str(date.year) + str(date.month) + str(date.day) + ".log"
    if os.path.isdir("/home/pi/Documents/DataLogger/_logs/"):
        logging.info("START LOGGING")
    else:
        os.mkdir("/home/pi/Documents/DataLogger/_logs/")
        logging.info("START LOGGING")
    logging.basicConfig(filename="/home/pi/Documents/DataLogger/_logs/" + debugFilename, filemode="w", level=logging.DEBUG, format="%(asctime)s, %(levelname)s - %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p")

def main():
    """This is the main fuction"""
    global timer
    global bigCounter
    global dictionaryData
    startLogger()
    checkI2CLibrary()
    lcdtest.setupGPIO()
    try:
        lcdtest.initLCD()
    except:
        logging.debug("Failed to Init LCD")
    lcdtest.setLCDBacklight(0) # OFF
    initGPIO()
    print("Finished All Initialization")
    ####----------------------------------------------- GET SystemConfig DATA
    dictionaryData = uploadCSV.getAllDictionaries()
    tempMin = ""
    tempMax = ""
    tempUnit = ""
    for i in range(0,6):
        if ("min" + str(i)) in dictionaryData:
            tempMin = dictionaryData[("min" + str(i))]
        if ("max" + str(i)) in dictionaryData:
            tempMax = dictionaryData[("max" + str(i))]
        if ("unit" + str(i)) in dictionaryData:
            tempUnit = dictionaryData[("unit" + str(i))]
    tempString = "Min:" + tempMin + tempUnit + \
        ", Max:" + tempMax + tempUnit
    
    ipAddress = getIPAddress()
    ipAddress = (ipAddress).strip()
    #print(ipAddress)
    lcdtest.writeText2(ipAddress)
    #logInterval = int(re.findall("\d+.", dictionaryData['logInterval'])[0].replace("s",""))
    logInterval = int(dictionaryData['logIntervalMain'].replace("s",""))
    #print( logInterval )
    ####---------------------------------------------- INITIALIZE TIMERS
    timer5s = 0
    startTimer5s = datetime.datetime.now()
    startTimer30s = datetime.datetime.now()
    startTimer300s = datetime.datetime.now()
    startTargetTime = datetime.datetime.now()
    programStartTime = datetime.datetime.now()
    print("Log Interval: " + str(logInterval))
    print("Save Duration: " + dictionaryData['saveDuration'])
    print("Starting Run Loop")
    print("---------------------------------------------------------")
    while 1:
        if timer == 0:
            startTimer30s = datetime.datetime.now()
        if timer5s == 10:
            startTimer5s = datetime.datetime.now()
        timer5s += 1.0
        timer += 1.0
        timeNow = datetime.datetime.now()
        checkGPIOButtons()
        check_restart(timeNow)
        if (timeNow - startTimer5s).total_seconds() >= 5:
            print(str((timeNow - startTimer5s).total_seconds()) + " Seconds")
            #print(startTimer5s)
            #### ------------------------------------------------------ CHECK IF I2C LIBRARY RUNNING
            checkI2CLibrary()
            #### ------------------------------------------------------ READ ADC and HUMIDIFIER (I2C)
            try:
                print("Read Sensors")
                for x in range(0,4):
                    if dictionaryData['enabled' + str(x+1)] == "Yes":
                        print("ADC Channel #" + str(x+1) + " Enabled")
                        #os.system("python /home/pi/Documents/DataLogger/_software/readADC.py 2 " + str(x+1))
                        #time.sleep(0.2)
                if dictionaryData['enabled' + str(1)] == "Yes" and dictionaryData['enabled' + str(2)] == "Yes":
                    print("Humidity Detection Enabled")
                    os.system("python /home/pi/Documents/DataLogger/_software/readHumidifier.py 2")
                time.sleep(0.1)
            except:
                logging.debug("Restarting I2C Library")
                os.system("python /home/pi/Documents/DataLogger/_software/restartI2C.py")
                #### ------------------------------------------------------ UPDATE LCD
            try:
                print("Update LCD")
                dictionaryData = uploadCSV.getAllDictionaries(2) # 2=> Get from tempData table
                time.sleep(0.1)
                if dictionaryData['enabled5'] == "Yes":
                    lcdtest.repeatThis(5, dictionaryData) #dictionary data -> from library I2C
                else:
                    lcdtest.repeatThis(6, dictionaryData) #dictionary data -> from library ADC
                #print dictionaryData
                lcdtest.writeText2(ipAddress)
                print ("-_-_-_-_-_-_-_-_-_-_-_-_-_-")
            except Exception as e:
                logging.debug("LCD Write Error")
                print("main.py:main(), LCD Error")
                print(e)
                print(threading.active_count())
            #### ------------------------------------------------------ CHECK SENSORS RUN, ALARM
            try:
                if not GPIO.input(sensor_Run):
                    lcdtest.setLCDBacklight(1) # GREEN
                    #print("GREEN")
                else:
                    lcdtest.setLCDBacklight(2) # RED
                    #print("RED")
                if not GPIO.input(sensor_Run) and not GPIO.input(sensor_Alarm):
                    lcdtest.setLCDBacklight(3) # BLUE
                    #print("BLUE")
            except:
                logging.debug("Error Reading GPIO Sensors")
                print("Error Reading Sensor GPIOs")
            timer5s = 0
        time.sleep(0.2)
        timeNow = datetime.datetime.now()
        if (timeNow - startTargetTime).total_seconds() >= logInterval:
            print(str((timeNow - startTargetTime).total_seconds()) + " Seconds")
            startTargetTime = timeNow
            #print(datetime.datetime.now().time())
            # Save to .txt file / database
            for x in range(0,4):
                if dictionaryData['enabled' + str(x+1)] == "Yes":
                    print("ADC Channel #" + str(x+1) + " Enabled")
                    #os.system("python /home/pi/Documents/DataLogger/_software/readADC.py 1 " + str(x+1))
            if dictionaryData['enabled' + str(1)] == "Yes" and dictionaryData['enabled' + str(2)] == "Yes":
                print("Humidity Detection Enabled")
                os.system("python /home/pi/Documents/DataLogger/_software/readHumidifier.py 1")
            uploadCSV.main(dictionaryData['saveDuration'])
            timer = 0
        #print(str((timeNow - programStartTime).total_seconds()) + " Seconds Running")

def check_restart(date_time):
    #print time.hour
    if(date_time.hour == 0 and date_time.minute == 0 and date_time.second < 30):
        print ("SCHEDULED RESTART")
        exitHandler("RESTARTING")
        time.sleep(3)
        os.system("sudo bash /home/pi/Documents/DataLogger/_software/reboot.sh")

def exitHandler(text):
    print("\nExiting script...")
    print("----------------------------------------------------------------")
    try:
        lcdtest.setLCDBacklight(0) # OFF
        lcdtest.initLCD()
        lcdtest.writeText("Shutting Down...")
        time.sleep(1)
        lcdtest.writeText(text)
        time.sleep(1)
    except Exception as e:
        print("Error exiting")
        print(e)
#### -------------------------------------------------- START

atexit.register(exitHandler, "OFF")
main()
