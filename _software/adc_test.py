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

	print adcReading
	#adcReading = adcReading.replace('\n', '') #take out newline
	#adc_int = int(adcReading, 16)
	#print adc_int
	
	inputShifted = int(binascii.hexlify(adcReading), 16) >> 6
	print ("Input shifted:" + str(inputShifted))
	maskedOutput = 0xFFFFFF & inputShifted
    #6 bit shift, 24 bit mask?
	print(maskedOutput)


	voltageAcrossRTD = float(float(maskedOutput) / float(16777216)) #fpr 24 bit adc
	toVoltage = (voltageAcrossRTD * FS) / opAmpGain

    #print("FS: " + str(FS))
	print(voltageAcrossRTD)
	print("ADC Voltage: " + str(toVoltage))


	RTDResistance = toVoltage / current  + offset
	print ("RTD Resistance: " + str(RTDResistance))
	
#output = check_output(["i2cget", "-y", "1", "0x16", "0x00", "w"])
convert_ADC(binascii.unhexlify("ab8ed4bc"))