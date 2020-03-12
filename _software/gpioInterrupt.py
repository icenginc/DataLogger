import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

button1 = 23
button2 = 24
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def myCallback(channel):
    print("Callback")

GPIO.add_event_detect(button2, GPIO.FALLING, callback=myCallback)
try:
    GPIO.wait_for_edge(button1, GPIO.FALLING)
    print("Button " + str(button1) + " Pressed")
except KeyboardInterrupt:
    GPIO.cleanup()
GPIO.cleanup()
