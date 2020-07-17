import os, sys
from shutil import copyfile

args = sys.argv
unitType = ""
tempChannel = 0

def checkInputs():
    #print("updateWebsiteSettings.py:checkInputs()")
    if len(args) == 4:
        channel = args[1]
        inputType = args[2]
        value = args[3]
        #print(channel)
        #print(inputType)
        #print(value)
        return channel, inputType, value
    else:
        #print(str(len(args)))
        print("Error not enough arguments")
        exit()

def changeLine(line, channel, inputType, value):
    """Single Conversion"""
    global tempChannel
    global unitType
    edited = 0
    outLine = line
    #print(outLine)
    if line.find("ID:") != -1:
        tempChannel = line[line.find("ID:")+3:].strip()
    #if str(tempChannel) == channel:
    #    print("TempChannel: [" + str(tempChannel) + "], Channel: [" + str(channel) + "]")
    if line.find(inputType) != -1 and (str(tempChannel) == str(channel)):
        tempLine = line[:line.find(":")+1].strip()
        tempLine = tempLine + " " + value + "\n"
        outLine = tempLine
        edited = 1
        # if inputType == "Gain":
        #     print("Gain" + tempLine)
    if line.find("SensorUnit:") != -1 and(str(tempChannel) == str(channel)):
        unitType = line[line.find(":")+1:].strip()
    return outLine, edited

def updateFile(channel, inputType, value):
    #print("updateWebsiteSettings.py:updateFile()")
    filePath = "/home/pi/Documents/DataLogger/_settings/"
    fileName = "SystemConfig.txt"
    backup = fileName.replace(".txt","_temp.txt")
    try:
        if len(filePath) > 0 and len(backup) > 0 and len(fileName) > 0:
            os.system("sudo chmod 777 " + filePath + backup)
            os.system("sudo chmod 777 " + filePath + fileName)
        copyfile(filePath + fileName, filePath + backup)
        #print("Copied File: " + filePath + backup)
        openFiles(filePath, backup, fileName, channel, inputType, value)
    except IOError as e:
        #print("Error - Could not copy file")
        #print(e.errno)
        print(e)

def openFiles(filePath, backup, fileName, channel, inputType, value):
    readFile = open(filePath + backup, "r")
    writeFile = open(filePath + fileName, "w")
    #print("File")
    tempLine = ""
    inputArray = inputType.split("?")
    valueArray = value.split("?")
    settingIndex = 0
    for line in readFile:
        editedLine = ""
        if inputType.find("?") != -1:
            #print("Multiple Settings")
            #print(inputArray)
            #print(valueArray)
            #print(len(valueArray))
            sInputType = str(inputArray[settingIndex]).replace('"',"")
            if sInputType == "channel":
                sInputType = "ID"
            sValue = valueArray[settingIndex].replace('"',"")
            editedLine, edited = changeLine(line, channel, sInputType, sValue)
            if edited == 1:
                #print("Edited")
                settingIndex += 1
                if settingIndex >= len(inputArray):
                    settingIndex = 0
        else:
            editedLine, edited = changeLine(line, channel, inputType, value)
            #print(editedLine)
        writeFile.write(editedLine)
    readFile.close()
    writeFile.close()

def main():
    channel, inputType, value = checkInputs()
    #print(channel)
    #print(inputType)
    #print(value)
    updateFile(channel, inputType, value)
    print("Finished>" + str(channel) + ">" + str(inputType) + ">" + str(value) + ">" + str(unitType))

main()
