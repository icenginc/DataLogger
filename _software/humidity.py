from subprocess import check_output
import math
import pigpio
import os

def main():
    one = check_output(["python", "/home/pi/Documents/DataLogger/_software/readADC.py", "2", "1"])
    two = check_output(["python", "/home/pi/Documents/DataLogger/_software/readADC.py", "2", "2"])
    one = strip_output(one)
    two = strip_output(two)
    print(one)
    print(two)
    if(float(one) < float(two)): #make one the higher of the two (dry temp)
        temp = one
        one = two
        two = temp
    dry = calculate_const(one)
    wet = calculate_const(two)
    humidity = calculate_humid(one, two, dry, wet)
    print(humidity)

def strip_output(input):
    temparray = input.splitlines()
    for a in temparray:
        if(a.find("Temperature: ") > -1):
            ftemp=a
    ftemp = ftemp.replace("\n", "")
    ftemp = ftemp.replace("C", "")
    ftemp = ftemp.replace("Temperature: ", "")
    return input
    #see link for below 2 equations : https://www.1728.org/relhum.htm

def calculate_const(input):
    numerator = float(input)*17.502
    denominator = float(input)+240.97
    ratio = numerator/denominator
    result = math.exp(ratio)
    return result*6.112

def calculate_humid(temp_dry, temp_wet, coeff_dry, coeff_wet):
    const = .6687451584
    difference = float(temp_dry) - float(temp_wet)
    expression = (const) * (1 + (.00115*float(temp_wet))) * (difference)
    numerator = coeff_wet - expression
    ratio = numerator/coeff_dry
    return ratio*100

main()
