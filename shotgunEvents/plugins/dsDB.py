# -*- coding: utf-8 -*-
"""
For detailed information please see

http://shotgunsoftware.github.com/shotgunEvents/api.html
"""
import logging
import sys
import sg_utils;reload(sg_utils) 
sys.path.append('//vfx-data-server/dsGlobal/dsCore/Shotgun')

import dsSQLTools as dsSQL
reload(dsSQL)

### Setting up local shotgun hook
apiKey = '114101ed238549f285df856f65e89a089c50d7fa'
scriptName = "eventTrigger_connectingFields"
url = "https://duckling.shotgunstudio.com"

def registerCallbacks(reg):
    """Register all necessary or appropriate callbacks for this plugin."""
    
    reg.registerCallback( scriptName, apiKey, callback_projectUpdate, {'Shotgun_Project_Change': ['*']}, None)
    reg.registerCallback( scriptName, apiKey, callback_episodeUpdate, {'Shotgun_Scene_Change': ['*']}, None)
    reg.registerCallback( scriptName, apiKey, callback_seqUpdate, {'Shotgun_Sequence_Change': ['*']}, None)
    reg.registerCallback( scriptName, apiKey, callback_shotUpdate, {'Shotgun_Shot_Change': ['*']}, None)

    # Set the logging level for this particular plugin. Let error and above
    # messages through but block info and lower. This is particularly usefull
    # for enabling and disabling debugging on a per plugin basis.
    reg.logger.setLevel(logging.ERROR)
    reg.logger.setLevel(logging.INFO)

#------------------------------------------
# change status via the status of parent
#------------------------------------------
def updatePROJECTDB(sg,logger,Obj,args):
    dbName = "//vfx-data-server/dsGlobal/globalProjects"
    PROJECT = Obj['name']
    STATUS = Obj['sg_status']
    ID = Obj['id']
    if dsSQL.getValueDB(dbName,"Projects","Id",ID) == []:
        dbName = "//vfx-data-server/dsGlobal/globalProjects"
        tableName = "Projects"   
        dsSQL.buildProjectDB(dbName,tableName)
        logger.info("REBUILDING GLOBAL PROJECTS ") 
    else:
        dsSQL.modifyDB(dbName,"Projects","Status",str(STATUS),"Id",int(ID))
        logger.info("MODIFY GLOBAL PROJECTS " + str(ID) + " "+ str(STATUS)) 

def rebuildDB(dbName,PROJECT):
    dsSQL.buildFullProjectDB(PROJECT,dbName,PROJECT)
    logger.info("REBUILDING EPISODES ") 
    
def updateEPISODEDB(sg,logger,Obj,args):
    dbName = "//vfx-data-server/dsPipe/" + str(Obj['project']['name']) + "/.local/" + str(Obj['project']['name'])
    PROJECT = Obj['project']['name']
    STATUS = Obj['sg_status_list']
    ID = Obj['id']
    if dsSQL.getValueDB(dbName,"EPISODE","Id",ID) == []:
        rebuildDB(dbName,PROJECT)
    else:
        dsSQL.modifyDB(dbName,"EPISODE","Status",str(STATUS),"Id",int(ID))
        logger.info("MODIFY EPISODE " + str(ID) + " "+ str(STATUS)) 
    
def updateSEQUENCEDB(sg,logger,Obj,args):
    dbName = "//vfx-data-server/dsPipe/" + str(Obj['project']['name']) + "/.local/" + str(Obj['project']['name'])
    PROJECT = Obj['project']['name']
    STATUS = Obj['sg_status_list']
    ID = Obj['id']
    if dsSQL.getValueDB(dbName,"SEQUENCE","Id",ID) == []:
        rebuildDB(dbName,PROJECT)
    else:
        dsSQL.modifyDB(dbName,"SEQUENCE","Status",str(STATUS),"Id",int(ID))
        logger.info("MODIFY SEQUENCE " + str(ID) + " "+ str(STATUS)) 

def updateSHOTDB(sg,logger,Obj,args):
    dbName = "//vfx-data-server/dsPipe/" + str(Obj['project']['name']) + "/.local/" + str(Obj['project']['name'])
    PROJECT = Obj['project']['name']
    STATUS = Obj['sg_status_list']
    ID = Obj['id']
    if dsSQL.getValueDB(dbName,"SHOT","Id",ID) == []:
        rebuildDB(dbName,PROJECT)
    else:
        dsSQL.modifyDB(dbName,"SHOT","Status",str(STATUS),"Id",int(ID))
    logger.info("MODIFY SHOT " + str(ID) + " "+ str(STATUS)) 

def callback_projectUpdate(sg,logger,event,args):
    fields = ['sg_status','id','project','name']
    try:
        sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields) 
        updatePROJECTDB(sg,logger,sgVal,args)
    except:
        pass
    
def callback_episodeUpdate(sg,logger,event,args):
    fields = ['sg_status_list','id','project']
    try:
        sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields) 
        updateEPISODEDB(sg,logger,sgVal,args)
    except:
        pass

def callback_seqUpdate(sg,logger,event,args):
    fields = ['sg_status_list','id','project']
    try:
        sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields) 
        updateSEQUENCEDB(sg,logger,sgVal,args)
    except:
        pass
    
def callback_shotUpdate(sg,logger,event,args):
    fields = ['sg_status_list','id','project']
    try:
        sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields) 
        updateSHOTDB(sg,logger,sgVal,args)
    except:
        pass


