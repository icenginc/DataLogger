import time
import pigpio
import binascii
import datetime, time
import os, sys
import sqlite3
import uploadCSV
import i2cMux
import math

i2cMuxAddress = 0x75
adcAddress = 0x16
VREF = 3.3
FS = 0.5 * VREF
opAmpGain = 100.0
current = 100 / 1000000.0
offset = - 3.40
twoToTheTwentyFour = 16777216 # 2^24

def readRTDTable(resistance):
    rtdTemperature = ["-55","-50","-45","-40","-35","-30","-25","-20","-15","-10","-5","0","5","10","15","20",
"25","30","35","40","45","50","55","60","65","70","75","80","85","90","95","100","105",
"110","115","120","125","130","135","140","145","150","155"]
    rtdResistance = ["78.32","80.31","82.29","84.27","86.25","88.22","90.19","92.16","94.12","96.09","98.04","100",
"101.95","103.9","105.85","107.79","109.73","111.67","113.61","115.54","117.47","119.4",
"121.32","123.24","125.16","127.08","128.99","130.9","132.8","134.71","136.61","138.51",
"140.4","142.29","144.18","146.07","147.95","149.83","151.71","153.58","155.46","157.33","159.19"]
    tempCounter = 0
    for line in rtdResistance:
        tempCounter += 1
    lowerResistance = 0.0
    upperResistance = 0.0
    lowerTemp = 0.0
    upperTemp = 0.0
    counter = 0
    lowerIndex = 0
    tempCounter = 0
    for resistanceValue in rtdResistance:
        if float(resistance) > float(resistanceValue):
            lowerIndex = tempCounter
        tempCounter += 1
    if lowerIndex < len(rtdResistance) - 1:
        lowerResistance = rtdResistance[lowerIndex]
        upperResistance = rtdResistance[lowerIndex+1]
        lowerTemp = rtdTemperature[lowerIndex]
        upperTemp = rtdTemperature[lowerIndex+1]
        temperature = ( (float(resistance) - float(lowerResistance)) / (float(upperResistance) - float(lowerResistance)) ) * (float(upperTemp) - float(lowerTemp)) + float(lowerTemp)
        return temperature
    return 0

def CVD_equation(resistance):
    c = 1 - (resistance/100) #100 resistance at 0 degrees
    #A = alpha + (alpha*sigma)/100
    #B = -(alpha*sigma)/10000
    #alpha = .00385
    #gamma = 1.49
    a = -.00000057365 #calc from constants
    b = .003907365 #calc from constants
    d = b**2-4*a*c # discriminant
    if d < 0:
        print ("This equation has no real solution")
        return 0;
    elif d == 0:
        x = (-b+math.sqrt(b**2-4*a*c))/2*a
        #print ("This equation has one solutions: "), x
        return x;
    else:
        x1 = (-b+math.sqrt((b**2)-(4*(a*c))))/(2*a)
        x2 = (-b-math.sqrt((b**2)-(4*(a*c))))/(2*a)
        #print ("This equation has two solutions: ", x1, " or", x2)
        if (x1 > 0):
            return x1
        elif(x2 > 0):
            return x2

def convertADC(adcReading):
    #print binascii.hexlify(adcReading)
    #print int(binascii.hexlify(adcReading), 16)
    mask = 0xFFFFFF
    inputShifted = int(binascii.hexlify(adcReading), 16) >> 6
    maskedOutput = mask & inputShifted
    #6 bit shift, 6 byte mask?
    #print(maskedOutput)
    voltageAcrossRTD = float(float(maskedOutput) / float(twoToTheTwentyFour)) #fpr 24 bit adc
    toVoltage = (voltageAcrossRTD * FS) / opAmpGain
    #print("FS: " + str(FS))
    #print(voltageAcrossRTD)
    #print("ADC Voltage: " + str(toVoltage))
    RTDResistance = toVoltage / current  + offset
    #print("RTD Resistance: " + str(RTDResistance))
    #temperature = readRTDTable(RTDResistance)
    #print RTDResistance
    temperature = CVD_equation(RTDResistance)
    print("Temperature: " + str(temperature) + "C")
    return temperature

def getChannel(channel):
    returnValue = 0xA0
    if channel == 1:
        returnValue |= 0b10000
    elif channel == 2:
        returnValue |= 0b11000
    elif channel == 3:
        returnValue |= 0b10001
    elif channel == 4:
        returnValue |= 0b11001
    return returnValue

def getChannelString(channel):
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

def readADC(channel, dictionaryData):
    convertedChannel = getChannel(int(channel))
    print(adcAddress)
    print("readADC.py:readADC, channel: " + str(channel))
    print("Converted channel: " + str(convertedChannel) + "  Hex: " + str(hex(convertedChannel)))
    temperature = 0
    pi = pigpio.pi()
    try:
        handle = pi.i2c_open(1, adcAddress)
        time.sleep(.02)
        #print handle
        #print("Try Writing...")
        pi.i2c_write_byte(handle, convertedChannel)
        time.sleep(0.2)
        #print("Try Reading...")
        (count, data) = pi.i2c_read_device(handle, 4)
        time.sleep(0.2)
        #print("Count: " + str(count))
        #print(binascii.hexlify(data))
        #print int(data, 16)
        temperature = convertADC(data)
        gain = dictionaryData['gain' + channel]
        offset = dictionaryData['offset' + channel]
        print("Gain: " + str(gain) + "; Offset: " + str(offset))
        temperature = (float(temperature) - float(offset)) * float(gain)
        #temperature = (float(temperature))
        pi.i2c_close(handle)
        time.sleep(0.1)
        pi.stop()
    except Exception as e:
        print("readADC.py:readADC, Error Reading ADC")
        print(e)
        #os.system("python /home/pi/Documents/DataLogger/_software/restartI2C.py")
    #print("END")
    #print("Temperature: " + str(temperature) + "C")
    return temperature

# For tempData Table
# Checks if a record with 'system' already exists. If not, INSERT, otherwise UPDATE
def checkIfChannelDataExists(channel):
    returnValue = False
    inputType = getChannelString(channel)
    conn = sqlite3.connect('/home/pi/Documents/DataLogger/_database/temperatures.db')
    cur = conn.cursor()
    statement = "SELECT * FROM tempData WHERE inputType LIKE '" + inputType + "'"
    #print(statement)
    cur.execute(statement)
    rows = cur.fetchall()
    #print(len(rows))
    if len(rows) > 0:
        returnValue = True
    #for line in rows:
    #    print(line)
    conn.close()
    return returnValue

# table 2 => TEMP
# table 1 => DATA STORAGE
def insertIntoDatabase(channel, data, table = "2"):
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()
    dateNow = datetime.datetime.now()
    timeNow = dateNow.time()
    #print(dateNow)
    #print(timeNow)
    dictionaryData = uploadCSV.getAllDictionaries()
    system = dictionaryData['system'] #"RPI_001"
    inputType = getChannelString(channel)
    tempDataExistsForChannel = checkIfChannelDataExists(channel)
    conn = sqlite3.connect('/home/pi/Documents/DataLogger/_database/temperatures.db')
    statement = ""
    if table == "1":
        statement = "INSERT INTO dataTable (system, inputType, data, date, time) VALUES ('" + system + "','" + inputType + "','" + str(data) + "','" + str(dateNow) + "','" + str(timeNow) + "')"
    else:
        if tempDataExistsForChannel == True:
            statement = "UPDATE tempData SET system = '" + system + "', data = '" + str(data) + "', date = '" + str(dateNow) + "', time = '" + str(timeNow) + "' WHERE inputType = '" + inputType + "'"
        else:
            statement = "INSERT INTO tempData (system, inputType, data, date, time) VALUES ('" + system + "','" + inputType + "','" + str(data) + "','" + str(dateNow) + "','" + str(timeNow) + "')"
        print ("Inserting Channel " + channel + " data: " + data)
    #print(statement)
    conn.execute(statement)
    conn.commit()
    conn.close()

####------------------------------------------------------- MAIN

def main():
    """This is the main function. It takes 1 argument:
    Ex: python readADC.py 1\t Writes to dataTable in database
    Ex: python readADC.py 2\t Writes to tempTable in database"""
    i2cMux.readI2CMux(1)
    channel = "1"
    # channel min
    # channel max
    # channel units
    # channel interval
    # channel upload ftp link
    #configureI2CMux()
    args = sys.argv
    table = 2
    if len(args) > 2:
        if args[1] == "1" or args[1] == "2":
            #print(args[1])
            table = args[1]
        channel = args[2]
    dictionaryData = uploadCSV.getAllDictionaries()
    temperature = readADC(channel, dictionaryData)
    tempFormatted = "{0:.2f}".format(temperature)
    print("ADC Reading, Channel #" + str(channel) + ": " + "\n" + tempFormatted)
    # Insert data into database
    #print("Inserting into database: " + tempFormatted + "for channel " + channel)
    insertIntoDatabase(channel, tempFormatted, table)
    # If full day reached (12:00am), generate text file from database data and
    # upload to FTP (if file is uploaded daily)

main()
