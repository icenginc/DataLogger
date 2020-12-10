from subprocess import check_output
import os


def main():
    check1=check_output(["python", "/home/pi/Documents/DataLogger/_software/website/checkIfRunning.py"])
    if(check1 == "Stopped\n"):
        print("Rebooting process...")
        os.system('bash /home/pi/Documents/DataLogger/_software/reboot.sh')
    else:
        print("Process currently running..")

main()
