import pigpio
import binascii
import time
import os, sys
from subprocess import check_output
import datetime
import sqlite3
import uploadCSV
import i2cMux

args = sys.argv
Hum_Address = 0x44

def convertTemp(hexData):
    #print(int("0x" + str(hexData), 16))
    return -45 + float(175 * int("0x" + str(hexData), 16)/(65536.0 - 1))

def convertHumidity(hexData):
    return 100 * (int("0x" + str(hexData), 16)/(65536.0 - 1))

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

def readHum(channel, dictionaryData):
    try:
        if pi.connected:
            print("Pigpio readHum already connected.")
    except:
        pi = pigpio.pi()
    temperature1Formatted = ""
    temperature2Formatted = ""
    humidityFormatted = ""
    try:
        output = check_output(["python", "/home/pi/Documents/DataLogger/_software/humidity.py"])
        temperature1 = float(output.splitlines()[0])
        temperature2 = float(output.splitlines()[1])
        humidity = float(output.splitlines()[2])
        #print temperature
        #print humidity
        gain = dictionaryData['gain' + channel]
        offset = dictionaryData['offset' + channel]
        print("One: " + "{0:.2f}".format(temperature1) + "C, " + "Two: " + "{0:.2f}".format(temperature2) + "C, " + "{0:.2f}".format(humidity) + "%")
        if gain.find(",") != -1 and offset.find(",") != -1:
            gainArray = gain.split(",")
            offsetArray = offset.split(",")
            gain1 = float(gainArray[0])
            gain2 = float(gainArray[1])
            offset1 = float(offsetArray[0])
            offset2 = float(offsetArray[1])
            temperature1 = (float(temperature1) - offset1) * gain1
            temperature2 = (float(temperature2) - offset2) * gain2
        else:
            #print(temperature)
            temperature1 = (float(temperature1) - float(offset)) * float(gain)
            temperature2 = (float(temperature2) - float(offset)) * float(gain)
            humidity = (float(humidity) - float(offset)) * float(gain)
        #print(temperature)
        #print("{0:.2f}".format(temperature) + "C")
        #print("{0:.2f}".format(humidity) + "%")
        temperature1Formatted = "{0:.4f}".format(temperature1)
        temperature2Formatted = "{0:.4f}".format(temperature2)
        humidityFormatted = "{0:.4f}".format(humidity)
        return temperature1Formatted + ":" + temperature2Formatted + ":" + humidityFormatted 
    except Exception as e:
        print("readHumidifier.py:readHum(), Error Reading Humidifer ADC")
        print(e)
    finally:
        if pi.connected:
            pi.stop()
    #return humidityFormatted #save humidity into channel 5 in database
    #return temperature1Formatted + ":" + temperature2Formatted + ":" + humidityFormatted 

def readHum_i2c(channel, dictionaryData):
    try:
        if pi.connected:
            print("Pigpio readHumi2c already connected.")
    except:
        pi = pigpio.pi()
    temperatureFormatted = ""
    humidityFormatted = ""
    try:
        handle = pi.i2c_open(1, Hum_Address)
        time.sleep(.55)
        pi.i2c_write_device(handle, [0x2C,0x06])
        time.sleep(0.2)
        (count, data) = pi.i2c_read_device(handle, 6)
        time.sleep(0.2)
        pi.i2c_close(handle)
        time.sleep(0.1)
        if pi.connected:
            pi.stop()
        print("Count: " + str(count))
        print(binascii.hexlify(data))
        tempString = binascii.hexlify(data)
        temperature = convertTemp(tempString[:4])
        humidity = convertTemp(tempString[6:10])
        print(temperature)
        print(humidity)
        gain = dictionaryData['gain' + channel]
        offset = dictionaryData['offset' + channel]
        print("One: " + "{0:.2f}".format(temperature) + "C, " + "Two: " + "{0:.2f}".format(temperature) + "C, " + "{0:.2f}".format(humidity) + "%")
        #two temps, because the ADC method uses two. Using the same format here so it will parse it out the same
        if gain.find(",") != -1 and offset.find(",") != -1:
            gainArray = gain.split(",")
            offsetArray = offset.split(",")
            gain1 = float(gainArray[0])
            gain2 = float(gainArray[1])
            offset1 = float(offsetArray[0])
            offset2 = float(offsetArray[1])
            temperature = (float(temperature) - offset1) * gain1
        else:
            #print(temperature)
            temperature = (float(temperature) - float(offset)) * float(gain)
            humidity = (float(humidity) - float(offset)) * float(gain)
        #print(temperature)
        #print("{0:.2f}".format(temperature) + "C")
        #print("{0:.2f}".format(humidity) + "%")
        temperatureFormatted = "{0:.4f}".format(temperature)
        humidityFormatted = "{0:.4f}".format(humidity)
        return temperatureFormatted + ":" + temperatureFormatted + ":" + humidityFormatted 
    except Exception as e:
        print("readHumidifier.py:readHum(), Error Reading Humidifer I2C")
        print(e)
        if pi.connected:
            pi.stop()
    
    #return humidityFormatted #save humidity into channel 5 in database
    #return temperatureFormatted + ":" + temperatureFormatted + ":" + humidityFormatted 

# For tempData Table
# Checks if a record with 'system' already exists. If not, INSERT, otherwise UPDATE
def checkIfChannelDataExists(channel):
    returnValue = False
    inputType = getChannelString(channel)
    conn = sqlite3.connect('/home/pi/Documents/DataLogger/_database/temperatures.db')
    #print ("Input Type:" + inputType)
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
def insertIntoDatabase(channel, data, dictionaryData, table="2"):
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()
    dateNow = datetime.datetime.now()
    timeNow = dateNow.time()
    #print(dateNow)
    #print(timeNow)
    system = dictionaryData['system'] #"RPI_001" changed to BIO#
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

def main():
    """This is the main function. It takes 1 argument:
    Ex: python readHumidifier.py 1 X \t Writes to dataTable in database
    Ex: python readHumidifier.py 2 X \t Writes to tempTable in database
    X: 0 for i2c, 1 for ADC
    """
    
    args = sys.argv
    if len(args) > 2:
        table=args[1]
        select=args[2]
        dictionaryData = uploadCSV.getAllDictionaries()
        if args[1] == "1" or args[1] == "2":
            print("Table: "+args[1]+" Port: "+args[2])
            if args[2] == "0":
                i2cMux.readI2CMux(3)
                tempHum = readHum_i2c("5", dictionaryData)
                insertIntoDatabase("5", tempHum.split(":")[0] + ":" + tempHum.split(":")[2], dictionaryData, table)
            elif args[2] == "1":
                i2cMux.readI2CMux(1)
                tempHum = readHum("6", dictionaryData)
                insertIntoDatabase("6", tempHum.split(":")[0] + ":" + tempHum.split(":")[2], dictionaryData, table)
                insertIntoDatabase("1", tempHum.split(":")[0], dictionaryData, table) #happens in readADC
                insertIntoDatabase("2", tempHum.split(":")[1], dictionaryData, table) #happens in readADC
                else:
                    os.system("sudo pkill -9 -f main.py")
            else:
                print("Invalid port to read humidity from.")
        else:
            print("Invalid table to record into.")

main()
