import os,sys
import subprocess
from subprocess import check_output
import glob
from datetime import datetime, timedelta

dbpath = "/mnt/EquipmentLogs/"

def doesSubFolderExist(dbpathfull):
    value = False
    if os.path.isdir(dbpathfull):
        print("SubFolder exists.")
        value = True
    else:
        print("Creating SubFolder - " + dbpath)
        os.makedirs(dbpathfull)

def canAccessServer(dbpath):
    value = False
    if os.path.isdir(dbpath):
        print("Can access server.")
        value = True
    return value

def debugfileexists(dbpathfull,dbpathfulldebug,systemName,message):
    try:
        print("Appending error to debuglog.")
        z=open(dbpathfulldebug, "a+")
        z.write("["+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"] "+str(message)+"\r\n")
    except:
        print("Could not update IP text.")


def updatelog(systemName, message):
    dbpathfull=dbpath+systemName
    dbpathfulldebug=dbpathfull+"/"+systemName+"-debuglog.txt"

    if canAccessServer(dbpath):
        doesSubFolderExist(dbpathfull)
        debugfileexists(dbpathfull,dbpathfulldebug,systemName,message)
