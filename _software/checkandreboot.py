from subprocess import check_output
import os
import postdata
import uploadCSV
import time

def main():
    check1=check_output(["python", "/home/pi/Documents/DataLogger/_software/website/checkIfRunning.py"])
    if(check1 == "Stopped\n"):
        dictionaryData=uploadCSV.getAllDictionaries()
        postdata.updatestop(dictionaryData['RP_Name'])
        time.sleep(10)
        print("Rebooting process...")
        os.system('bash /home/pi/Documents/DataLogger/_software/reboot.sh')
    else:
        print("Process currently running..")

main()
