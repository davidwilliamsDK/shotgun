import sys, os, re, shutil, imp
from time import gmtime, strftime

''' scheduled task running from vfx-render-manager once a day 8:00 
    creates a __lock__ file in dsGlobal\globalTimeSheets
    creates an error log with the date name _errors
    when finished it copies the __lock__ file over to the date of the day.
'''


if sys.platform == "linux2":
    sys.path.append('/mounts/vfxstorage/dsDev/dsCore/shotgun/')
else:
    sys.path.append('//vfx-data-server/dsDev/dsCore/shotgun/')
import sgTools;reload(sgTools)


def writeLog(path,info):
    logFile = open(path, 'a')
    logFile.write(info)
    logFile.close()

def sgTimeLogs(sg, project,path,errPath):
    assetList = []
    shotList = []
    seqList = []
    sceneList = []
    projList = []
    projTLogs = sg.find('TimeLog',[['project.Project.name','is',project]],['id','entity','date','duration','user','entity'])

    for log in projTLogs:
        try:
            entity = log['entity']
            entID = entity['id']
            taskOBJ = sg.find_one("Task",[['id','is',entID]],['entity'])
    
            ID = log['id']
            DATE = log['date']
            DUR = log['duration']
            USR = log['user']['name']
            PROJ = project
            
            if taskOBJ['entity']['type'] == "Asset":
                assetList.append(taskOBJ)
                assetID = taskOBJ['entity']['id']
                assetOBJ = sg.find_one("Asset",[['id','is',assetID]],['sg_episode'])
                epiName = assetOBJ['sg_episode'][0]['name']
                fwTmp = epiName.split("_")
                EPI = epiName
                FW = fwTmp[-1]               
            if taskOBJ['entity']['type'] == "Shot":
                shotList.append(taskOBJ)
                shotID = taskOBJ['entity']['id']
                shotOBJ = sg.find_one("Shot",[['id','is',shotID]],['sg_scene'])
                epiName = shotOBJ['sg_scene']['name']
                fwTmp = epiName.split("_")
                EPI = epiName
                FW = fwTmp[-1]
            if taskOBJ['entity']['type'] == "Sequence":
                seqList.append(taskOBJ)
                seqID = taskOBJ['entity']['id']
                seqOBJ = sg.find_one("Sequence",[['id','is',seqID]],['scene_sg_sequence_1_scenes'])
                epiName = seqOBJ['scene_sg_sequence_1_scenes'][0]['name']
                fwTmp = epiName.split("_")
                EPI = epiName
                FW = fwTmp[-1]
            if taskOBJ['entity']['type'] == "Scene":
                seqList.append(taskOBJ)
                epiName = taskOBJ['entity']['name']
                fwTmp = epiName.split("_")
                EPI = epiName
                FW = fwTmp[-1]
            if taskOBJ['entity']['type'] == "Project":
                projList.append(taskOBJ)
                name = log['entity']['name']
                FW = name
                EPI = name

            info =  '"' + str(ID) + '","' + str(DATE) + '","' + str(DUR) + '","' + str(PROJ) + '","' + str(USR) + '","' + str(FW) + '","' + str(EPI) + '"'  + "\n" 
            writeLog(path,info)
        except:
            info = str(log)
            try:
                writeLog(errPath,taskOBJ['entity']['type'] + "\n")
                writeLog(errPath,project + "\n")
                writeLog(errPath,info + "\n" )
            except:
                writeLog(errPath,str(taskOBJ) + "\n")
                writeLog(errPath,project + "\n")
                writeLog(errPath,info + "\n" )
                print taskOBJ
                pass
            pass

def createLogs():
    
    sg = sgTools.getSG()
    projList = sg.find('Project',[],['name'])

    fileName = strftime("%d-%m-%y", gmtime())
    fileName = fileName 
    lockPath = "//vfx-data-server/dsGlobal/globalTimeSheets/.__lock__"
    path = "//vfx-data-server/dsGlobal/globalTimeSheets/" + fileName + ".txt"
    errPath ="//vfx-data-server/dsGlobal/globalTimeSheets/" + fileName + "_errors.txt"
    if not os.path.isfile(lockPath):logFile = open(lockPath, 'w');logFile.close()
    if not os.path.isfile(errPath):errFile = open(errPath, 'w');errFile.close()
        
    info = '" id "," date"," duration "," project "," user "," farmerswife "," project"' + "\n"
    writeLog(lockPath,info)


    for proj in projList:
        try:
            project = proj['name']
            sgTimeLogs(sg, project,lockPath,errPath)
        except:
            pass
    
    try:
        os.remove(path)
    except:
        pass
    
    shutil.copy(lockPath,path)
    
    os.remove(lockPath)
    #sgTimeLogs(sg,"Lego_City",path,errPath) 
          
createLogs()