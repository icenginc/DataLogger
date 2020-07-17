import os,sys

def checkProcess(processName):
    output = os.popen("pgrep -af python").read()
    if output.find(processName) != -1:
        return 1
    else:
        return 0
    
processName1 = "sudo python main.py"
processName2 = "python /home/pi/Documents/DataLogger/_software/main.py"
check1 = checkProcess(processName1)
check2 = checkProcess(processName2)

if (check1 | check2):
    print("Running")
else:
    print("Stopped")
