import os,sys
import sqlite3
import subprocess
from subprocess import check_output
import glob
from datetime import datetime, timedelta
import shutil
import datetime

#systemName="TestPi-PC"
dbpath = "/mnt/EquipmentLogs/"
filePathLocal = "/home/pi/Documents/DataLogger/_logs/"

def doesSubFolderExist(inputpath):
    value = False
    if os.path.isdir(inputpath):
        print(inputpath+" subfolder exists.")
        value = True
    else:
        print("Creating SubFolder - " + inputpath)
        os.makedirs(inputpath)

def canAccessServer(dbpath):
    value = False
    if os.path.isdir(dbpath):
        print("Can access server.")
        value = True
    return value

def localuploads(dbpathlu,systemName):
    for fname in os.listdir(filePathLocal):
        #print(fname)
        #print(systemName)
        if(fname.find(systemName) > -1):
            info=os.path.getmtime(filePathLocal+"/"+fname)
            from datetime import datetime
            srcinfo=datetime.fromtimestamp(info)#.strftime('%Y-%m-%d %H:%M')
            if(os.path.exists(dbpathlu+"/"+fname)):
                cinfo=os.path.getmtime(dbpathlu+"/"+fname)
                #from datetime import datetime
                desinfo=datetime.fromtimestamp(cinfo)#.strftime('%Y-%m-%d %H:%M')
                #print(srcinfo)
                #print(desinfo)
                if(srcinfo > desinfo):
                    os.remove(dbpathlu+"/"+fname)
                    shutil.copy(filePathLocal+"/"+fname,dbpathlu+"/"+fname)
                    print("Updating - "+fname)
            else:
                shutil.copy(filePathLocal+"/"+fname,dbpathlu+"/"+fname)
                print("Uploading - "+fname)

def main(systemName):
    dbpathsys=dbpath+systemName
    dbpathlu=dbpathsys+"/LocalUploads/"

    if(canAccessServer(dbpath)):
        doesSubFolderExist(dbpathsys)
        doesSubFolderExist(dbpathlu)
        localuploads(dbpathlu,systemName)
