print "SG UTIL"

import sys, re, os, string, shutil
sys.path.append('//vfx-data-server/dsGlobal/globalResources/Shotgun')
from shotgun_api3 import Shotgun
sys.path.append('//vfx-data-server/dsDev/dsCore/maya/')
from dsCommon import dsProjectUtil


server = dsProjectUtil.listShotgunServer()
scriptName = "assetOpenToShotgun"
scriptId = "e932e9c2864c9bcdc3f3ddf8b801cc3d565bf51f"
sg = Shotgun(server, scriptName, scriptId)

def sgCreateAsset(projName, assetName, assetType, assetSubType):
    '''Create assets created with the asset opener in shotgun too'''
    sg = Shotgun(server, scriptName, scriptId)

    proj = sg.find_one("Project", [["name", "is", str(projName)]])
    asset = sg.create("Asset", {"code":str(assetName), "project":proj})

    sg.update("Asset",asset["id"], {"sg_asset_type":str(assetType)})
    sg.update("Asset",asset["id"], {"sg_subtype":str(assetSubType)})
    sg.update("Asset",asset["id"], {"sg_2d_3d":"3D"})
    return asset["id"]

def sgGetAssetID(projName, assetName, assetType, assetSubType):
    filters = [['project.Project.name', 'is', str(projName)], ['code','is', str(assetName)],['sg_asset_type', 'is', str(assetType)], ['sg_subtype', 'is', str(assetSubType)]]
    assetID = sg.find("Asset", filters=filters, fields = ['id'])
    return assetID



def sgRemoveAsset(projName, assetName, assetType, assetSubType):
    '''Delete Asset in Shotgun'''
    sg = Shotgun(server, scriptName, scriptId)

    try:
        #Find asset, that matches these critias
        filters = [['code','is', str(assetName)],['sg_asset_type', 'is', str(assetType)], ['sg_subtype', 'is', str(assetSubType)]]
        asset = sg.find("Asset", filters=filters, fields = ['id'])

        #Delete asset
        sg.delete("Asset", asset[0]['id'])
    except:
        pass

def sgGetTemplate(sgEntity):
    filters = []
    return sg.find(sgEntity, filters=filters, fields = ['id', "code"])

def sgSetAssetStatus(assetID, state):
    print assetID[0]
    sg.update("Asset",assetID[0]["id"], {"sg_status_list":state})

def sgGetAllAssetStatus(project):
    filters = [['project.Project.name', 'is', str(project)]]
    return sg.find('Asset', filters=filters, fields=['code', 'sg_asset_type', 'sg_subtype', 'sg_status_list'])

def setTemplate(assetID, template):
    filters = [['code','is',template]]
    data=sg.find_one("TaskTemplate", filters=filters, fields=['id','code'])
    sg.update("Asset",assetID, {"task_template":data})

def setSequenceTemplate(seqID, template):
    filters = [['code','is',template]]
    data=sg.find_one("TaskTemplate", filters=filters, fields=['id','code'])
    sg.update("Sequence", seqID, {"task_template":data})

##def getSeguenceTasks(taskName):
##    filters = [['Task.content', 'is', taskName]]
##    return sg.find('task', filters=filters, fields=['content', 'entity', 'sg_status_list'])

def sgGetSeqTasks(seqID,fields = []):
    filters = [['entity.Sequence.id','is',seqID]]
    return sg.find('Task', filters, fields)

def sgSetSeqTaskStatus(templateID, status):
    sg.update("Task",templateID, {"sg_status_list":str(status)})

def sgAddSeqNote(subject, content, taskObj, seqObj, projObj):
    data = {'subject':subject,'content':content,'addressings_to':[taskObj], 'note_links':[seqObj], 'project':projObj}
    noteID = sg.create('Note',data)
    return noteID

def getProjectID(projName):
    return sg.find_one("Project", [["name", "is", projName]])

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setEpisode(assetID, film):
    print film
    filters = [['code','is',str(film)]]
    data=sg.find_one("Scene", filters=filters, fields=['id','code'])
    print data
    sg.update("Asset",assetID, {"sg_episode":[data]})

def sgCreateIcon(projName, assetName, assetType, assetSubType, icon):
    '''Add Icon to Asset in Shotgun'''
    sg = Shotgun(server, scriptName, scriptId)
    filters = [['code','is', str(assetName)],['sg_asset_type', 'is', str(assetType)], ['sg_subtype', 'is', str(assetSubType)]]
    asset = sg.find("Asset", filters=filters, fields = ['id'])
    sg.update("Asset",asset[0]["id"], {"image":str(icon)})

def addTypesToList(list):
    if list:
        for entry in list:
            values = sg.schema_field_read(str(entry[0]), str(entry[1]))[str(entry[1])]["properties"]["valid_values"]["value"]
            if not entry[2] in values:
                print str(entry[2])
                values.append(str(entry[2]))
                properties = {"valid_values" : values}
                sg.schema_field_update(str(entry[0]), str(entry[1]), properties)

def sgTemplate(wf,sg):
    if wf == "shotWF":
        filters = [ ['code','is', 'DucklingShotTemplate' ]]
        template = sg.find_one('TaskTemplate',filters)
        return template
    elif wf == "sequenceWF":
        filters = [ ['code','is', 'DucklingSequenceTemplate' ]]
        template = sg.find_one('TaskTemplate',filters)
        return template

def sgGetShot(shotName,seqName,projName,epiName,sg):
    '''Test and return if Shot exists'''
    try:
        filters = [ ['code','is', shotName], ['project.Project.name','is', str(projName)],['sg_scene.Scene.code','is', str(epiName)],['sg_sequence.Sequence.code','is', str(seqName)] ]
        myShot = sg.find("Shot", filters=filters)
        return myShot
    except:
        pass

def sgGetShotTasks(shotObj,sg):
    try:
        shotID = shotObj[0]['id']
        filter = [['id','is', shotID]]
        infoFromSG = ['tasks']
        myTasks = sg.find_one('Shot',filter,infoFromSG)

        return myTasks
    except:
        pass

def sgGetAssetTask(assetObj,sg):
    try:
        assetID = assetObj['id']
        filter = [['id','is', assetID]]
        infoFromSG = ['tasks']
        myTasks = sg.find_one('Asset',filter,infoFromSG)
        return myTasks
    except:
        pass

def sgGetSeq(seqName,projName,epiName,sg):
    '''Test and return if Sequence exists'''
    try:
        filters = [ ['code','is', seqName], ['project.Project.name','is', str(projName)],['custom_entity01_sg_sequence_custom_entity01s.CustomEntity01.code','is', str(epiName)]]
        mySeq = sg.find("Sequence", filters=filters)
        return mySeq
    except:
        pass

def sgTestEpi(projName,epiName,sg):
    try:
        myEpiList = sg.find("Scene", [['project.Project.name','is', str(projName)]],["code"])
        for epi in myEpiList:
            if re.search(str(epiName),str(epi['code']),):
                epiName = epi['code']
        return epiName
    except:
        pass

def sgGetEpi(projName,epiName,sg):
    '''Test and return if Episode exists'''
    try:
        filters = [ ['code','is', epiName], ['project.Project.name','is', str(projName)]]
        myEpi = sg.find("Scene", filters=filters)
        return myEpi
    except:
        pass

def sgGetUser(userName,sg):
    myPeople = sg.find("HumanUser", [["groups.Group.code","is","ducklings"]], ["name","projects","sg_initials"])
    for user in myPeople:
        if userName == str(user['name']) or userName == str(user['sg_initials']):
            myUser = user
            return myUser

def sgConvertIcon(frameOne):
    rvio = '"C:/Program Files (x86)/Tweak/RV-3.12.15-32/bin/rvio.exe"'
    cmd = rvio + ' ' + frameOne + ' -o '+ frameOne[:-3] + 'jpg'
    os.system(cmd)
    return frameOne[:-3]+ "jpg"

def sgGetUsers():
    sg = Shotgun(server, scriptName, scriptId)
    '''return list of users'''
    userList = []
    group = {'type': 'Group', 'id': 5}
    myPeople = sg.find("HumanUser", [["groups","is",group]], ["name"])
    for user in myPeople:
        userList.append(user['name'])
    return userList

def sgCreateVersion(path,sgUser):
    sg = Shotgun(server, scriptName, scriptId)
    match = re.search('(?P<relative>.*)\/(?P<project>\w*)\/film\/(?P<episode>\w*)\/(?P<sequence>\w*)\/(?P<shot>\w*)\/comp\/published3D\/(?P<rlLayer>\w*)\/(?P<version>\w*)', path)
    match = match.groupdict()
    if match:
        dsRelativePath = match['relative']
        dsProject = match['project']
        dsEpisode = match['episode']
        dsSeq = match['sequence']
        dsShot = match['shot']
        dsRenderLayer = match['rlLayer']
        dsVersion = match['version']
    else:
        pass
    myUser = sgGetUser(sgUser,sg)
    proj = sg.find_one("Project", [["name", "is", str(dsProject)]])
    myShot = sgGetShot(dsShot,dsSeq,dsProject,dsEpisode,sg)
    myTasks = sgGetShotTasks(myShot,sg)
    for task in myTasks['tasks']:
        if task['name'] == 'published3D':
            taskObj = task
            break
    mySeq = sgGetSeq(dsSeq,dsProject,dsEpisode,sg)
    myEpi = sgGetEpi(dsProject,dsEpisode,sg)
    fileList = os.listdir(path + "/")

    if fileList != []:
        frameOne = path + "/" + fileList[0]
        filter = [['project','is', proj],['entity','is', myShot[0]],['code','is',str(dsVersion)],['sg_task','is',taskObj],['sg_render_layer','is',str(dsRenderLayer)]]
        dictFromSG = sg.find('Version',filter )
        if dictFromSG == []:
            icon = sgConvertIcon(frameOne)
            data = {'code':str(dsVersion),'project':proj,'user':myUser,'sg_episode':myEpi,'sg_sequence':mySeq,'sg_task':taskObj,'sg_path_to_frames':frameOne,'sg_render_layer':dsRenderLayer,'entity':myShot[0],'image':str(icon)}
            result = sg.create('Version', data)
        else:
            print "Version Already present"
    else:
        print "empty layer for " + path

def sgCreateMayaNukeVersion(path,heroName,pathToFile,sg):
    match = re.search('(?P<project>\w*)_(?P<episode>\w*)_(?P<sequence>\w*)_(?P<shot>\w*)_(?P<version>\w*)_(?P<task>\w*)_(?P<nn>\w*)_(?P<user>\w*)', path)
    match = match.groupdict()
    if match:
        dsProject = match['project']
        dsEpisode = match['episode']
        dsSeq = match['sequence']
        dsShot = match['shot']
        dsVersion = match['version']
        dsTask = match['task']
        dsNN = match['nn']
        dsUser = match['user']
    else:
        pass
    versionName = path
    myUser = sgGetUser(dsUser,sg)
    proj = sg.find_one("Project", [["name", "is", str(dsProject)]])
    epiName = sgTestEpi(dsProject,dsEpisode,sg)
    myShot = sgGetShot(dsShot,dsSeq,dsProject,epiName,sg)
    myTasks = sgGetShotTasks(myShot,sg)
    for task in myTasks['tasks']:
        if task['name'].lower() == dsTask.lower():
            taskObj = task
            break
    mySeq = sgGetSeq(dsSeq,dsProject,epiName,sg)
    myEpi = sgGetEpi(dsProject,epiName,sg)

    filter = [['project','is', proj],['entity','is', myShot[0]],['code','is',str(dsVersion)],['sg_task','is',taskObj]]
    dictFromSG = sg.find('Version',filter )

    if dictFromSG == []:
        data = {'code':str(dsVersion),'project':proj,'user':myUser,'sg_task':taskObj,'sg_file_name':heroName,'sg_path':pathToFile,'sg_render_layer':None,'entity':myShot[0]}
        result = sg.create('Version', data)
        print "created shotgun version "
    else:
        print "Version Already present"

def sgCreateAssetVersion(dsUser,aName,type,subType,dsProject,dsVersion,sg):

    myUser = sgGetUser(dsUser,sg)
    proj = sg.find_one("Project", [["name", "is", str(dsProject)]])

    filter = [['code','is',aName],['project','is',proj]]
    myAsset = sg.find_one('Asset',filter,['code','sg_2d_3d','sg_status_list','sg_subtype','sg_asset_type','id','project'] )
    myTasks = sgGetAssetTask(myAsset,sg)
    for task in myTasks['tasks']:
        filter = [['project','is', proj],['code','is',str(dsVersion)],['entity','is', myAsset],['sg_task','is',task]]
        dictFromSG = sg.find('Version',filter )
        if dictFromSG == []:
            fName = aName + "_" + str(task['name']) + ".ma"
            pathToFile = dsProject + "/asset/3D/" + type + "/" + subType + "/" + aName + "/dev/maya/"
            sg_version_file_name = aName + "_" + str(task['name']) + "_v001.ma"
            data = {'code':str(dsVersion),'project':proj,'user':myUser,'sg_task':task,'sg_file_name':fName,'sg_path':pathToFile,'sg_render_layer':None,'sg_version_file_name':sg_version_file_name,'entity':myAsset}
            result = sg.create('Version', data)
            print "created shotgun version "
        else:
            print "Version Already present"

def sgCreateEpisodeVersionOne(task,pipeStep,user,shot,seq,episode,project,WF,file,sg):
    ## do stuff
    myUser = sgGetUser(user,sg)
    user = myUser["sg_initials"]
    epi = episode.split("_")
    relative = "//vfx-data-server/dsPipe/"
    if pipeStep == "effect" or pipeStep == "light" or pipeStep == "anim":
        shotPath = relative + project + "/film/" + episode + "/" + seq + "/" + shot + "/" + "3D/" + pipeStep + "/" + file
        seqPath = relative + project + "/film/" + episode + "/" + seq + "/" + "3D/" + pipeStep + "/" + file
        versionName =  project + "_" + epi[0] + "_" + seq + "_" + shot + "_" + "v001" + "_" + task + "_" + "nn" + "_" + user + ".ma"
        presetMaya = "//vfx-data-server/dsGlobal/globalMaya/Presets/defaultMaya/default.ma"
        if WF == "Shot":
            if not os.path.isfile(shotPath):
                shutil.copy(presetMaya,shotPath)
                print "created file " + shotPath
        elif WF == "Sequence":
            if not os.path.isfile(seqPath):
                shutil.copy(presetMaya,seqPath)
                print "created file " + seqPath
        return versionName

    elif pipeStep == "comp":
        presetNK = "//vfx-data-server/dsGlobal/globalNuke/presetScripts/default.nk"
        nukePath = relative + project + "/film/" + episode + "/" + seq + "/" + shot + "/comp/nukeScripts" + "/" + project + "_" + epi[0] + "_" + seq + "_" + shot + "_" + "v000" + "_" + task + "_" + "nn" + "_" + user + ".nk"
        versionName =  project + "_" + epi[0] + "_" + seq + "_" + shot + "_" + "v001" + "_" + task + "_" + "nn" + "_" + user + ".nk"
        if not os.path.isfile(nukePath):
            shutil.copy(presetNK,nukePath)
        return versionName
    else:
        print "please use one of the pipeline Steps"
