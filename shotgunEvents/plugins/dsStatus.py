# -*- coding: utf-8 -*-
"""
For detailed information please see

http://shotgunsoftware.github.com/shotgunEvents/api.html
"""
import logging
import sg_utils;reload(sg_utils) 
import sys
sys.path.append('//vfx-data-server/dsDev/dsCore/Shotgun')

### Setting up local shotgun hook
apiKey = '114101ed238549f285df856f65e89a089c50d7fa'
scriptName = "eventTrigger_connectingFields"
url = "https://duckling.shotgunstudio.com"

def registerCallbacks(reg):
    """Register all necessary or appropriate callbacks for this plugin."""
    
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

def setStatus(sg,entity,entityID,status):
    sg.update(entity,entityID, {'sg_status_list':status})

def getShotTasks(sg,logger,shotID,args):
    logger.info(shotID)
    taskList = sg.find('Task',[['entity.Shot.id','is',shotID]],['content','id'])
    for task in taskList:
        setStatus(sg,"Task",task['id'],"fin")
        print task['id']

def getSeqTasks(sg,logger,shotID,args):
    logger.info(shotID)
    taskList = sg.find('Task',[['entity.Sequence.id','is',shotID]],['content','id'])
    for task in taskList:
        setStatus(sg,"Task",task['id'],"fin")
        print task['id']

def getEpiTasks(sg,logger,epiID,args):
    logger.info(epiID)
    taskList = sg.find('Task',[['entity.Scene.id','is',epiID]],['content','id'])
    for task in taskList:
        setStatus(sg,"Task",task['id'],"fin")
        
def getShots(sg,logger,seqID,args):
    logger.info(seqID)
    shotList = sg.find('Shot',[['sg_sequence.Sequence.id','is',seqID]],['content','id'])
    for shot in shotList:
        setStatus(sg,"Shot",shot['id'],"fin")
        logger.info(shot['id'])
        
def getSeqs(sg,logger,epiID,args):
    logger.info("Get all seq in episode")
    seqList = sg.find('Sequence',[['scene_sg_sequence_1_scenes.Scene.id','is',epiID]],['content','id'])
    for seq in seqList:
        setStatus(sg,"Sequence",seq['id'],"fin")     

def callback_episodeUpdate(sg,logger,event,args):
    logger.info("update Episode")
    try:
        fields = ['sg_status_list','id','project']
        sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
    except:
        pass
    if sgVal != None:
        if sgVal['sg_status_list'] == 'cmpt':
            getSeqs(sg,logger,sgVal['id'],args)
            getEpiTasks(sg,logger,sgVal['id'],args)
  
def callback_shotUpdate(sg,logger,event,args):
    fields = ['sg_status_list','id','project']
    try:
        sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
        logger.info(sgVal['sg_status_list'])
    except:
        pass

    if sgVal != None:
        if sgVal['sg_status_list'] == 'fin':
            getShotTasks(sg,logger,sgVal['id'],args)

def callback_seqUpdate(sg,logger,event,args):
    logger.info("update sequence")
    try:
        fields = ['sg_status_list','id','project']
        sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
    except:
        pass
    if sgVal != None:
        if sgVal['sg_status_list'] == 'fin':
            getShots(sg,logger,sgVal['id'],args)
            getSeqTasks(sg,logger,sgVal['id'],args)
