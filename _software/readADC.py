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
opAmpGain = 101.0
current = 100 / 1000000.0
#offset = - 3.40
offset = 0
twoToTheTwentyFour = 16777216 # 2^24


#-----------------7/22/2020 Removed RTD table, and no longer using CDV_Equation function.

#def CVD_equation(resistance):
#    c = 1 - (resistance/100) #100 resistance at 0 degrees
#    a = -.00000057365 #calc from constants
#    b = 0.00392
#    d = b**2-4*a*c # discriminant
#    if d < 0:
#        print ("This equation has no real solution")
#        return 0;
#    elif d == 0:
#        x = (-b+math.sqrt(b**2-4*a*c))/2*a
#        #print ("This equation has one solutions: "), x
#        return x;
#    else:
#        x1 = (-b+math.sqrt((b**2)-(4*(a*c))))/(2*a)
#        x2 = (-b-math.sqrt((b**2)-(4*(a*c))))/(2*a)
#        #print ("This equation has two solutions: ", x1, " or", x2)
#        if (x1 > 0):
#            return x1
#        elif(x2 > 0):
#            return x2

def resistancetotemp(resistance):
    a = 0.00392 #standard coeff
    r0 = 100 #resistance at 0C
    
    numer = (resistance/r0) -1
    temper = numer/a
    #derived from equation: RTemp=R0(1+(a*temperature))
    return temper

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
    RTDResistance = (toVoltage / current)  + offset
    #temperature = CVD_equation(RTDResistance)
    temperature=resistancetotemp(RTDResistance)
    print("Raw Temperature: " + str(temperature) + "C")
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
        print("Adjusted Temperature: " + str(temperature) + "C")
    except Exception as e:
        print("Adjusted Temperature: 0C")
        print(e)
        #os.system("python /home/pi/Documents/DataLogger/_software/restartI2C.py")
    #print("END")
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
