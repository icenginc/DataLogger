#import RPi.GPIO as GPIO
import pigpio

pi = pigpio.pi()

sensor_Run = 12
sensor_Alarm = 16

def initializeGPIO():
    #print("init")
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setup(sensor_Run, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(sensor_Alarm, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pi.set_mode(sensor_Run, pigpio.INPUT)
    pi.set_mode(sensor_Alarm, pigpio.INPUT)

    pi.set_pull_up_down(sensor_Run, pigpio.PUD_UP)
    pi.set_pull_up_down(sensor_Alarm, pigpio.PUD_UP)


def checkRunStatus():

    returnValue = "Not Running"
    
    if not GPIO.input(sensor_Run):
        returnValue = "Running"
    
    return returnValue

def checkRunStatus2():

    returnValue = "Not Running"

    if not pi.read(sensor_Run):
        returnValue = "Running"

    return returnValue


def checkAlarmStatus2():

    returnValue = "Not Running"

    if pi.read(sensor_Alarm):
        returnValue = "Running"

    return returnValue


def checkAlarmStatus():

    returnValue = "Not Running"

    if not GPIO.input(sensor_Alarm):
        returnValue = "Running"

    return returnValue

def main():


    initializeGPIO()

    #r1 = checkRunStatus().strip()
    #r2 = checkAlarmStatus().strip()

    r1 = checkRunStatus2().strip()
    r2 = checkAlarmStatus2().strip()


    print(r1 + ":" + r2)


main()
pi.stop()
