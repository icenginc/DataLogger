import pigpio
import binascii
import datetime, time
import os, sys
import subprocess
from subprocess import check_output

FS = .015625 * 3.3 #vref
opAmpGain = 100.0 #gain in schematic
current = 100/1000000.0 #current source, 100microamps
offset = 0#-3.40

def convert_ADC(adcReading):
    print(adcReading)
    inputShifted = int(binascii.hexlify(adcReading), 16) >> 6
    print ("Input shifted:" + str(inputShifted))
    maskedOutput = 0xFFFFFF & inputShifted
    print(maskedOutput)
    voltageAcrossRTD = float(float(maskedOutput) / float(16777216)) #fpr 24 bit adc
    toVoltage = (voltageAcrossRTD * FS) / opAmpGain
    print(voltageAcrossRTD)
    print("ADC Voltage: " + str(toVoltage))
    RTDResistance = toVoltage / current  + offset
    print ("RTD Resistance: " + str(RTDResistance))
##-----------------------------------------------------Main
convert_ADC(binascii.unhexlify("ab8ed4bc"))
