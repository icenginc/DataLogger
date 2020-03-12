from __future__ import print_function
import os, sys
import subprocess
import time


majorRevNum = "0."


os.chdir("/home/pi/Documents/DataLogger/_software")

revision = subprocess.check_output(["git", "rev-list", "--count", "HEAD"])

print(majorRevNum + str(revision).strip())

