import time
import pigpio
import binascii
import lcdtest

adcAddress = 0x16
pi = pigpio.pi()
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
    if lowerIndex < len(rtdResistance):
        lowerResistance = rtdResistance[lowerIndex]
        upperResistance = rtdResistance[lowerIndex+1]
        lowerTemp = rtdTemperature[lowerIndex]
        upperTemp = rtdTemperature[lowerIndex+1]
        temperature = ( (float(resistance) - float(lowerResistance)) / (float(upperResistance) - float(lowerResistance)) ) * (float(upperTemp) - float(lowerTemp)) + float(lowerTemp)
        return temperature
    return 0

def convertADC(adcReading):

    mask = 0xFFFFFF
    inputShifted = int(binascii.hexlify(adcReading), 16) >> 6
    maskedOutput = mask & inputShifted
    voltageAcrossRTD = float(float(maskedOutput) / float(twoToTheTwentyFour))
    toVoltage = (voltageAcrossRTD * FS) / opAmpGain
    RTDResistance = toVoltage / current  + offset
    temperature = readRTDTable(RTDResistance)
    return temperature

def readADC():

    handle = pi.i2c_open(1, adcAddress)
    time.sleep(.02)
    pi.i2c_write_byte(handle, 0xA0)
    time.sleep(0.2)
    (count, data) = pi.i2c_read_device(handle, 4)
    time.sleep(0.2)
    temperature = convertADC(data)
    pi.i2c_close(handle)
    return temperature

####------------------------------------------------------- MAIN

temperature = readADC()
tempFormatted = "{0:.2f}".format(temperature)
print(tempFormatted)
lcdtest.initLCD()
lcdtest.writeText("TTemp: " + str(tempFormatted) + " C")
