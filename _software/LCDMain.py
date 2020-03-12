
import time
import LCDLibrary
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)


button1 = 23
button2 = 24
button3 = 25

GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

tempCounter = 0

LCDLibrary.initLCD()
LCDLibrary.writeText("SSTART")

def action_button1(channel):

    global tempCounter
    tempCounter -= 1

    LCDLibrary.initLCD()
    LCDLibrary.writeText("CCounter: " + str(tempCounter))

    time.sleep(0.5)

def action_button2(channel):
        
    global tempCounter
    tempCounter += 1

    LCDLibrary.initLCD()
    LCDLibrary.writeText("CCounter: " + str(tempCounter))

    time.sleep(0.5)
    
GPIO.add_event_detect(button1, GPIO.FALLING, callback=action_button1)
GPIO.add_event_detect(button2, GPIO.FALLING, callback=action_button2)

try:
    GPIO.wait_for_edge(button3, GPIO.FALLING)
    print("Button " + str(button3) + " Pressed")

except KeyboardInterrupt:

    GPIO.cleanup()

GPIO.cleanup()

LCDLibrary.initLCD()
LCDLibrary.writeText("EEND")




    
