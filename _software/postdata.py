import os,sys
import subprocess
from subprocess import check_output
import glob
from datetime import datetime, timedelta

dbpath = "/mnt/EquipmentLogs/"
loggerpath = dbpath+"RPi_Logger/"

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

def ipfileexists(dbpathfull,dbpathfullip,ipaddress,systemName):
    try:
        print("Creating/updating IP text.")
        z=open(dbpathfullip, "w+")
        z.write("IP Address: ["+ipaddress+"], Date: "+str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    except:
        print("Could not update IP text.")

def datafilewrite(dbpathfull,dbpathfulltxt,dataline):
    try:
        print("Updating master pi text.")
        z=open(dbpathfulltxt, "w+")
        z.write("Running,"+dataline)
    except:
        print("Could not update master pi text.")

def ippost(ipaddress, systemName):
    dbpathfull=dbpath+systemName
    dbpathfullip=dbpathfull+"/"+systemName+"-IP.txt"
    if canAccessServer(dbpath):
        doesSubFolderExist(dbpathfull)
        ipfileexists(dbpathfull,dbpathfullip,ipaddress,systemName)

def datapost(dataline, systemName):
    dbpathfull=loggerpath+systemName
    dbpathfulltxt=dbpathfull+".txt"
    if canAccessServer(loggerpath):
        #doesSubFolderExist(dbpathfull)
        datafilewrite(dbpathfull,dbpathfulltxt,dataline)

def updatestop(systemName):
    dbpathfull=loggerpath+systemName
    dbpathfulltxt=dbpathfull+".txt"
    if canAccessServer(loggerpath):
        #-----Open to read
        z=open(dbpathfulltxt, "r+")
        content=z.readline().split(',')
        content[0]="Stopped"
        z.close()
        #-----Open to write
        z=open(dbpathfulltxt, "w+")
        z.write(",".join(content))
        z.close()
