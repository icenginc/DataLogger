import os, sys
import time
import subprocess
restartSuccessfull = False
restartAttempts = 0

while not restartSuccessfull:
    print("Restarting I2C pigpiod - Attempts: " + str(restartAttempts))
    os.system("sudo killall -9 pigpiod")
    proc = subprocess.Popen(["sudo lsof -i TCP:8888"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    outArray = out.split("\n")
    pList = []
    for item in outArray:
        splitString = item.split(" ")
        listOne = []
        for item2 in splitString:
            if len(item2) > 0:
                #print(item2)
                listOne.append(item2)
        if len(listOne) > 0:
            pList.append(listOne)
    pidList = []
    for item in pList:
        #print("START")
        #print(item)
        if item[0] == "python":
            #print(item[1])
            if item[1] not in pidList:
                #print("Appended")
                pidList.append(item[1])
    for pid in pidList:
        print("Killing Process #" + pid)
        os.system("sudo kill -9 " + pid)
    print("Wait for 30 seconds")
    time.sleep(30)
    os.system("sudo pigpiod start")
    time.sleep(1)
    proc = subprocess.Popen(["pigs pigpv"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    out = out.strip()
    #print(out)
    if (out != "socket connect failed"):
        print("Running")
        restartSuccessfull = True
    else:
        print("Restart")
    restartAttempts += 1
    if restartAttempts >= 10:
        os.system("sudo reboot")
print("Finished Restarting I2C pigpiod")
