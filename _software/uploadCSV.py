import os,sys
import sqlite3
import subprocess
from subprocess import check_output
import glob
from datetime import datetime, timedelta

lastUploadDate = ""
filePathLocal = "/home/pi/Documents/DataLogger/_logs/"

def doesCSVFileExist(filePath, filename):
    value = False
    if os.path.isdir(filePath):
        #print(filePath)
        tempIndex = filename.rfind("_")
        if tempIndex != -1:
            baseFilename = filename[:tempIndex]
        foundAnyFiles = glob.glob(filePath + baseFilename + "*.csv")
        if os.path.exists(filePath + filename):
            #print("File Exists")
            #print(filePath + filename)
            value = True
        else:
            print("File Doesn't Exist")
    else:
        print("Path Doesn't exist")
        print(filePath)
    return value

def doesSubFolderExist(filePath):
    value = False
    if os.path.isdir(filePath):
        print("SubFolder Exists")
        value = True
    else:
        print("Creating SubFolder - " + filePath)
        os.makedirs(filePath)

def canAccessServer(filePath):
    value = False
    if os.path.isdir(filePath):
        value = True
    return value

def getDataLine(dictionaryData):
    dataLine = dictionaryData['date'] + "," + dictionaryData['time'] + ","
    channelArray = []
    maxChannel = 0
    for x in range(0,5): #took out 6, that is for the combined measure of temp:humid (dont't want in log file)
        if dictionaryData['enabled' + str(x+1)] == "Yes":
            #print dictionaryData
            if x == 1:
                tempData = dictionaryData['data62']
            else:
                tempData = dictionaryData['data' + str(x+1)]
            tempUnit = dictionaryData['unit' + str(x+1)]
            tempLogChannel = dictionaryData['logChannelA' + str(x+1)]
            if tempLogChannel.find(",") != -1 and tempData.find(":") != -1 and tempUnit.find(",") != -1:
                tempArray = tempLogChannel.split(",")
                tempD = tempData.split(":")
                tempU = tempUnit.split(",")
                for i in range(0, len(tempArray)):
                    channelDictionary = {}
                    channelDictionary['logChannelA'] = int(tempArray[i])
                    channelDictionary['data'] = tempD[i]
                    channelDictionary['unit'] = tempU[i]
                    channelArray.append(channelDictionary)
            else:
                #print(tempLogChannel)
                #channelArray.append(int(tempLogChannel))
                channelDictionary = {}
                if tempLogChannel.find(",") == -1:
                    channelDictionary['logChannelA'] = int(tempLogChannel)
                else:
                    channelDictionary['logChannelA'] = tempLogChannel.split(",")[0]
                channelDictionary['data'] = tempData
                channelDictionary['unit'] = tempUnit
                channelArray.append(channelDictionary)
    newArray = sorted(channelArray, key=lambda k: k['logChannelA'])
    maxChannel = int(newArray[-1]['logChannelA'])
    tempCounter = 0
    for x in range(1, maxChannel + 1):
        #print("Row" + str(x))
        found = False
        for y in range(0,len(newArray)):
            #print(newArray[y]['logChannelA'])
            if x == newArray[y]['logChannelA']:
                found = True
                #print(str(x) + ":" + str(y))
                if x == maxChannel:
                    dataLine = dataLine + newArray[y]['data'] + "," + newArray[y]['unit'] + "\n"
                else:
                    dataLine = dataLine + newArray[y]['data'] + "," + newArray[y]['unit'] + ","
        if not found:
            dataLine = dataLine + ",," 
    #print(dataLine)
    dataLine = dataLine.strip("\n")
    dataLine = dataLine + "\n"
    return dataLine

def updateUploadedBool(dictionaryData):
    date = dictionaryData['date']
    time = dictionaryData['time']
    #print("Upload Date: " + date)
    #print("Upload Time: " + time)
    dateString = date + " " + time
    conn = sqlite3.connect('/home/pi/Documents/DataLogger/_database/temperatures.db')
    cur = conn.cursor()
    beforeDate = datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=-15)
    afterDate = datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S') + timedelta(seconds=15)
    #print("Before Date: " + str(beforeDate))
    #print("After Date: " + str(afterDate))
    statement = "SELECT * FROM dataTable WHERE date BETWEEN datetime('" + str(beforeDate) + "') AND datetime('" + str(afterDate) + "');" 
    #print(statement)
    cur.execute(statement)
    rows = cur.fetchall()
    tempArrayString = ""
    for line in rows:
        #print(line)
        tempArrayString += str(line[0]) + ","
    tempArrayString = tempArrayString.rstrip(",")
    print(tempArrayString)
    statement = "UPDATE dataTable SET uploaded=1 WHERE primeIndex IN (" + tempArrayString + ");"
    #print(statement)
    conn.execute(statement)
    conn.commit()
    conn.close()

def checkUnsavedData(fileName, filePath, logGenerationInterval):
    global lastUploadDate
    print("checkUnsavedData")
    # Find date of non uploaded records
    # Check to see if a log file for that day already exists
    # Create a new one if already not created, Append if already exists (hopefully temperature log reader only graphs the data per time)
    # Read all non uploaded records first and store in an array (dictionaryData to array)
    foundData = True
    while foundData:
        dictionary1 = getRaspberryPiInfo()
        dictionary2 = getSensorInfo(1)
        tempSystemName = dictionary2['system'].replace("System:","").strip()
        dictionary2 = getSensorInfo(1)
        dictionary21 = getSensorInfo(2)
        dictionary22 = getSensorInfo(3)
        dictionary23 = getSensorInfo(4)
        dictionary24 = getSensorInfo(5)
        dictionary25 = getSensorInfo(6)
        dictionary3 = getMissedUploadedFiles(tempSystemName, "ADC 1", 1) # System, inputType
        dictionary4 = getMissedUploadedFiles(tempSystemName, "ADC 2", 1) # System, inputType
        dictionary5 = getMissedUploadedFiles(tempSystemName, "ADC 3", 1) # System, inputType
        dictionary6 = getMissedUploadedFiles(tempSystemName, "ADC 4", 1) # System, inputType
        dictionary7 = getMissedUploadedFiles(tempSystemName, "I2C 1", 1) # System, inputType
        dictionary8 = getMissedUploadedFiles(tempSystemName, "I2C 2", 1) # System, inputType
        tempDictionaryData = mergeDictionaries(dictionary1, dictionary2)
        tempDictionaryData1 = mergeDictionaries(tempDictionaryData, dictionary3)
        tempDictionaryData2 = mergeDictionaries(tempDictionaryData1, dictionary4)
        tempDictionaryData3 = mergeDictionaries(tempDictionaryData2, dictionary5)
        tempDictionaryData4 = mergeDictionaries(tempDictionaryData3, dictionary6)
        tempDictionaryData5 = mergeDictionaries(tempDictionaryData4, dictionary7)
        tempDictionaryData6 = mergeDictionaries(tempDictionaryData5, dictionary8)
        tempDictionaryData7 = mergeDictionaries(tempDictionaryData6, dictionary21)
        tempDictionaryData8 = mergeDictionaries(tempDictionaryData7, dictionary22)
        tempDictionaryData9 = mergeDictionaries(tempDictionaryData8, dictionary23)
        tempDictionaryData10 = mergeDictionaries(tempDictionaryData9, dictionary24)
        dictionaryData = mergeDictionaries(tempDictionaryData10, dictionary25)
        dictionaryData['RP_Name'] = dictionaryData['system']
        #for item in dictionaryData:
        #    print(item + " -> " + dictionaryData[item])
        tempDictionaryDataFinal = checkDictionaryDataKeys(dictionaryData)
        #dataLine = getDataLine(tempDictionaryDataFinal)
        #print(dataLine)
        if 'date' not in tempDictionaryDataFinal:
            # Did not find any unsaved data
            print("No unsaved data found")
            foundData = False
            break
        editedTime = "0000"
        if logGenerationInterval == "Daily":
            fileName = tempDictionaryDataFinal['system'].replace("System:","") + "_" + \
                tempDictionaryDataFinal['date'].replace("-","") + "_" + \
                editedTime[:4] + ".csv"
        elif logGenerationInterval == "Weekly":
            sunday = getBeginningOfWeek()
            fileName = tempDictionaryDataFinal['system'].replace("System:","") + "_" + \
                sunday + "_" + \
                editedTime[:4] + ".csv"
        try:
            saveCSVFile(tempDictionaryDataFinal, filePath, fileName)
        except:
            print("Could not save to database. Saving to local drive.")
            saveCSVFile(tempDictionaryDataFinal, filePathLocal, fileName)
            
        lastUploadDate = tempDictionaryDataFinal['date'] + " " + tempDictionaryDataFinal['time']

def saveCSVFile(dictionaryData, filePath, fileName):
    #Raspberry Pi Name
    #Mac Address
    #Raspberry Pi Firmware/Other ID Info
    #System Number
    #Sensor Type
    #Min
    #Max
    #Measure Interval
    #Save File Duration
    
    #Date, Time, Data, Unit
    
    # CSV File already exists, APPEND
    if doesCSVFileExist(filePath, fileName):
        try:
            writeFile = open(filePath + fileName, "a")
        except IOError as e:
            output = check_output(["sudo", "chmod", "+777", filePath+fileName])
            writeFile = open(filePath + fileName, "a")
        dataLine = getDataLine(dictionaryData)
        print("Appending: " + dataLine)
        writeFile.write(dataLine)
        writeFile.close()
        # CSV File doesn't exist, CREATE NEW
    else:
        print("Creating New File")
        print(filePath + fileName)
        writeFile = open(filePath + fileName, "w")
        piinfo = dictionaryData['RP_Name'] + ",MAC Address:" + dictionaryData['RP_MacAddress'] + ",RP Version:" + dictionaryData['RP_Version'] + "\n"
        systeminfo = "SensorType:" + dictionaryData['sensorType'] + ",Min:" + dictionaryData['min1'] + ",Max:" + \
            dictionaryData['max1'] + ",Log Interval:" + dictionaryData['logIntervalMain'] + ",Save File Duration:" + dictionaryData['saveDuration'] + "\n"
        dataheader = "Date,Time,ADC 1,,ADC 2,,ADC 3,,ADC 4,,I2C1,,I2C2" + "\n"
        dataLine = getDataLine(dictionaryData)
        writeFile.write(piinfo)
        writeFile.write(systeminfo)
        writeFile.write(dataheader)
        writeFile.write(dataLine)
        writeFile.close()
    updateUploadedBool(dictionaryData)

def checkDictionaryDataKeys(dictionaryData):
    for x in range(1,7):
        if "data"+str(x) not in dictionaryData:
            dictionaryData["data"+str(x)] = ""
            if x > 4:
                for y in range (1,3):
                    dictionaryData["data"+str(x)+str(y)] = ""
                    
    for x in range(1,7):
        if "unit"+str(x) not in dictionaryData:
            dictionaryData["unit"+str(x)] = ""
            if x > 4:
                for y in range (1,3):
                    dictionaryData["unit"+str(x)+str(y)] = ""
                    
    for x in range(1,7):
        if "enabled"+str(x) not in dictionaryData:
            dictionaryData["enabled"+str(x)] = ""
            if x > 4:
                for y in range (1,3):
                    dictionaryData["enabled"+str(x)+str(y)] = ""
    
    if dictionaryData['data5'].find(":") != -1:
        location = dictionaryData['data5'].find(":")
        dictionaryData['data51'] = dictionaryData['data5'][:location]
        dictionaryData['data52'] = dictionaryData['data5'][location + 1:]
    
    if dictionaryData['unit5'].find(":") != -1:
        location = dictionaryData['unit5'].find(":")
        dictionaryData['unit51'] = dictionaryData['unit5'][:location]
        dictionaryData['unit52'] = dictionaryData['unit5'][location + 1:]
    
    if dictionaryData['data6'].find(":") != -1:
        location = dictionaryData['data6'].find(":")
        dictionaryData['data61'] = dictionaryData['data6'][:location]
        dictionaryData['data62'] = dictionaryData['data6'][location + 1:]
    
    if dictionaryData['unit6'].find(":") != -1:
        location = dictionaryData['unit6'].find(":")
        dictionaryData['unit61'] = dictionaryData['unit6'][:location]
        dictionaryData['unit62'] = dictionaryData['unit6'][location + 1:]
    return dictionaryData

def getCurrentReading(systemName, inputType, selectedTable=1):
    conn = sqlite3.connect('/home/pi/Documents/DataLogger/_database/temperatures.db')
    #print("uploadCSV.py:getCurrentReading(), systemName:" + systemName + ", inputType:" + inputType + ", selectedTable:" + str(selectedTable) )
    cur = conn.cursor()
    statement = ""
    if selectedTable == 2:
        statement = "SELECT * FROM tempData WHERE system LIKE '" + str(systemName) + "' AND inputType LIKE '" + str(inputType) + "' ORDER BY primeIndex DESC LIMIT 1"
    else:
        statement = "SELECT * FROM dataTable WHERE system LIKE '" + str(systemName) + "' AND inputType LIKE '" + str(inputType) + "' ORDER BY primeIndex DESC LIMIT 1"
    #print(statement)
    cur.execute(statement)
    rows = cur.fetchall()
    #print("uploadCSV.py:getCurrentReading(), Result Length:" + str(len(rows)))
    dictionary = {}
    for line in rows:
        tempCounter = 0
        if len(line) > 0:
            for item in line:
                if tempCounter == 4:
                    if (inputType == "ADC 1"):
                        dictionary['data1'] = str(line[4])
                    elif (inputType == "ADC 2"):
                        dictionary['data2'] = str(line[4])
                    elif (inputType == "ADC 3"):
                        dictionary['data3'] = str(line[4])
                    elif (inputType == "ADC 4"):
                        dictionary['data4'] = str(line[4])
                    elif (inputType == "I2C 1"):
                        dictionary['data5'] = str(line[4])
                    elif (inputType == "I2C 2"):
                        dictionary['data6'] = str(line[4])
                elif tempCounter == 5:
                    tempString = line[5]
                    dictionary['date'] = tempString[:10]
                elif tempCounter == 6:
                    tempString = line[6]
                    dictionary['time'] = tempString[:8]
                tempCounter += 1
    conn.close()
    return dictionary

def getMissedUploadedFiles(systemName, inputType, selectedTable=1):
    conn = sqlite3.connect('/home/pi/Documents/DataLogger/_database/temperatures.db')
    #print("uploadCSV.py:getCurrentReading(), systemName:" + systemName + ", inputType:" + inputType + ", selectedTable:" + str(selectedTable) )
    cur = conn.cursor()
    statement = ""
    if selectedTable == 2:
        statement = "SELECT * FROM tempData WHERE system LIKE '" + str(systemName) + "' AND inputType LIKE '" + str(inputType) + "' ORDER BY primeIndex ASC LIMIT 1"
    else:
        statement = "SELECT * FROM dataTable WHERE system LIKE '" + str(systemName) + "' AND inputType LIKE '" + str(inputType) + "' AND (uploaded=0 OR uploaded IS NULL) ORDER BY primeIndex ASC LIMIT 1"
    #print(statement)
    cur.execute(statement)
    rows = cur.fetchall()
    #print("uploadCSV.py:getCurrentReading(), Result Length:" + str(len(rows)))
    dictionary = {}
    for line in rows:
        tempCounter = 0
        if len(line) > 0:
            for item in line:
                if tempCounter == 4:
                    if (inputType == "ADC 1"):
                        dictionary['data1'] = str(line[4])
                    elif (inputType == "ADC 2"):
                        dictionary['data2'] = str(line[4])
                    elif (inputType == "ADC 3"):
                        dictionary['data3'] = str(line[4])
                    elif (inputType == "ADC 4"):
                        dictionary['data4'] = str(line[4])
                    elif (inputType == "I2C 1"):
                        dictionary['data5'] = str(line[4])
                    elif (inputType == "I2C 2"):
                        dictionary['data6'] = str(line[4])
                elif tempCounter == 5:
                    tempString = line[5]
                    dictionary['date'] = tempString[:10]
                elif tempCounter == 6:
                    tempString = line[6]
                    dictionary['time'] = tempString[:8]
                tempCounter += 1
    conn.close()
    return dictionary

def mergeDictionaries(dictionaryOne, dictionaryTwo):
    finalDictionary = dictionaryOne.copy()
    finalDictionary.update(dictionaryTwo)
    return finalDictionary

def getMAC(interface):
    try:
        str = open('/sys/class/net/' + interface + '/address').read()
    except:
        str = "00:00:00:00:00:00"
    
    return str[0:17]

def getRaspberryPiInfo():
    dictionary = {}
    dictionary['RP_Name'] = "RPI_001"
    dictionary['RP_MacAddress'] = "MAC Address:" + getMAC("wlan0")
    dictionary['RP_Version'] = "RP Version:" + subprocess.check_output(['uname', '-a']).strip()
    
    return dictionary

def findInLine(line, findThis):
    if line.find(findThis) != -1:
        tempString = line[line.find(findThis) + len(findThis) + 2:].strip()
        #print(tempString)
        
        return tempString
    else:
        return ""

def getSensorInfo(channel):
    filePath = "/home/pi/Documents/DataLogger/_settings/"
    fileName = "SystemConfig.txt"
    readFile = open(filePath + fileName, "r")
    dictionary = {}
    tempID = 0
    for line in readFile:
        if line.find("ID: ") != -1:
            tempID += 1
        if len(findInLine(line, "SystemName")) > 0:
            dictionary['system'] = findInLine(line, "SystemName").strip()
        if len(findInLine(line, "LogGenerationInterval")) > 0: # and channel == tempID:
            dictionary['saveDuration'] = findInLine(line, "LogGenerationInterval").strip()
        if len(findInLine(line, "LogInterval")) > 0 and tempID == 0:
            dictionary['logIntervalMain'] = findInLine(line, "LogInterval").strip()
        if len(findInLine(line, "LogInterval")) > 0 and channel == tempID:
            dictionary['logInterval'] = findInLine(line, "LogInterval").strip()
        if len(findInLine(line, "SensorType")) > 0 and channel == tempID:
            dictionary['sensorType'] = findInLine(line, "SensorType").strip()
        if len(findInLine(line, "MinSetting")) > 0 and channel == tempID:
            dictionary['min'+str(channel)] = findInLine(line, "MinSetting").strip()
        if len(findInLine(line, "MaxSetting")) > 0 and channel == tempID:
            dictionary['max'+str(channel)] = findInLine(line, "MaxSetting").strip()
        if len(findInLine(line, "SensorUnit")) > 0 and channel == tempID:
            dictionary['unit'+str(channel)] = findInLine(line, "SensorUnit").strip()
        if len(findInLine(line, "Gain")) > 0 and channel == tempID:
            dictionary['gain'+str(channel)] = findInLine(line, "Gain").strip()
        if len(findInLine(line, "Offset")) > 0 and channel == tempID:
            dictionary['offset'+str(channel)] = findInLine(line, "Offset").strip()
        if len(findInLine(line, "LogFileChannelAssignment")) > 0 and channel == tempID:
            dictionary['logChannelA'+str(channel)] = findInLine(line, "LogFileChannelAssignment").strip()
        if len(findInLine(line, "Enabled")) > 0 and channel == tempID:
            dictionary['enabled'+str(channel)] = findInLine(line, "Enabled").strip()

    readFile.close()
    return dictionary

def getAllDictionaries(selectedTable=1):
    """This function reads the SystemConfig.txt file to get System and Sensor info.
    It also reads the sensor data written to:
        if selectedTable == 1, dataTable (default)
        if selectedTable == 2, tempData
    """
    dictionary1 = getRaspberryPiInfo()
    dictionary2 = getSensorInfo(1)
    dictionary21 = getSensorInfo(2)
    dictionary22 = getSensorInfo(3)
    dictionary23 = getSensorInfo(4)
    dictionary24 = getSensorInfo(5)
    dictionary25 = getSensorInfo(6)
    tempSystemName = dictionary2['system'].replace("System:","").strip()
    dictionary3 = getCurrentReading(tempSystemName, "ADC 1", selectedTable) # System, inputType
    dictionary4 = getCurrentReading(tempSystemName, "ADC 2", selectedTable) # System, inputType
    dictionary5 = getCurrentReading(tempSystemName, "ADC 3", selectedTable) # System, inputType
    dictionary6 = getCurrentReading(tempSystemName, "ADC 4", selectedTable) # System, inputType
    dictionary7 = getCurrentReading(tempSystemName, "I2C 1", selectedTable) # System, inputType
    dictionary8 = getCurrentReading(tempSystemName, "I2C 2", selectedTable) # System, inputType
    tempDictionaryData = mergeDictionaries(dictionary1, dictionary2)
    tempDictionaryData1 = mergeDictionaries(tempDictionaryData, dictionary3)
    tempDictionaryData2 = mergeDictionaries(tempDictionaryData1, dictionary4)
    tempDictionaryData3 = mergeDictionaries(tempDictionaryData2, dictionary5)
    tempDictionaryData4 = mergeDictionaries(tempDictionaryData3, dictionary6)
    tempDictionaryData5 = mergeDictionaries(tempDictionaryData4, dictionary7)
    tempDictionaryData6 = mergeDictionaries(tempDictionaryData5, dictionary8)
    tempDictionaryData7 = mergeDictionaries(tempDictionaryData6, dictionary21)
    tempDictionaryData8 = mergeDictionaries(tempDictionaryData7, dictionary22)
    tempDictionaryData9 = mergeDictionaries(tempDictionaryData8, dictionary23)
    tempDictionaryData10 = mergeDictionaries(tempDictionaryData9, dictionary24)
    dictionaryData = mergeDictionaries(tempDictionaryData10, dictionary25)
    #dictionaryData = mergeDictionaries(tempDictionaryData5, dictionary8)
    #dictionaryData = mergeDictionaries(tempDictionaryData, dictionaryThree)
    dictionaryData['RP_Name'] = dictionaryData['system']
    return dictionaryData

def getBeginningOfWeek():
    now = datetime.now()
    #print(now.day)
    dayOfWeek = now.weekday()
    #print(dayOfWeek)
    daysAgo = 0
    while dayOfWeek != 6:
        dayOfWeek -= 1
        daysAgo += 1
        if dayOfWeek < 0:
            dayOfWeek = 6
    #print(daysAgo)
    toBeginningOfWeek = now - timedelta(days=daysAgo)
    #print(toBeginningOfWeek)
    sunday = str(toBeginningOfWeek.year) + str(toBeginningOfWeek.month).zfill(2) + str(toBeginningOfWeek.day).zfill(2)
    #print(sunday)
    return sunday

def main(logGenerationInterval):
    filePath = "/mnt/EquipmentLogs/"
    dictionaryData = getAllDictionaries()
    checkDictionaryDataKeys(dictionaryData)
    #for item in dictionaryData:
    #    print(item)
    #    print(item + " -> " + dictionaryData[item])
    #exit()
    editedTime = "0000" #dictionaryData['time'].replace(":","")
    if logGenerationInterval == "Daily":
        fileName = dictionaryData['system'].replace("System:","") + "_" + dictionaryData['date'].replace("-","") + "_" + editedTime[:4] + ".csv"
    elif logGenerationInterval == "Weekly":
        fileName = dictionaryData['system'].replace("System:","") + "_" + getBeginningOfWeek() + "_" + editedTime[:4] + ".csv"
    #print(fileName)
    #exit()
    #filePath = "/mnt/BI_TEST/AndrewC/_DataLogger/_software/_TempCSV/"
    #doesCSVFileExist(filePath, fileName)
    if canAccessServer(filePath):
        filePathWSubfolder = filePath + dictionaryData["system"] + "/"
        doesSubFolderExist(filePathWSubfolder)
        checkUnsavedData(fileName, filePathWSubfolder, logGenerationInterval)
        tempDictionaryDate = dictionaryData['date'] + " " + dictionaryData['time']
        print("Last Uploaded Date: " + lastUploadDate)
        print("Dictionary Date: " + tempDictionaryDate)
        if lastUploadDate != tempDictionaryDate:
            print("Saving to database..")
            saveCSVFile(dictionaryData, filePathWSubfolder, fileName)
        else:
            print("Same Date: No Need to Upload")
    else:
        print("uploadCSV: Could not access network server")
        print("uploadCSV: Will not save (Temprorarily)")

#main("Weekly")
