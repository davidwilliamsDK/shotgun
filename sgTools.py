import sys, re, os, string, shutil, subprocess

if sys.platform == "linux2":
    sys.path.append('/dsGlobal/globalResources/Shotgun')
    sys.path.append('/dsGlobal/dsCore/maya/')
else:
    sys.path.append('//vfx-data-server/dsGlobal/globalResources/Shotgun')
    sys.path.append('//vfx-data-server/dsGlobal/dsCore/maya')

from shotgun_api3 import Shotgun
import dsCommon.dsProjectUtil

try:
    import maya.cmds as cmds
    import maya.OpenMaya as api
    import maya.OpenMayaUI as apiUI
except:
    pass

def getSG():
    server = "https://duckling.shotgunstudio.com"
    scriptName = "assetOpenToShotgun"
    scriptId = "e932e9c2864c9bcdc3f3ddf8b801cc3d565bf51f"
    sg = Shotgun(server, scriptName, scriptId)
    return sg

def getPageDict(projName):
    sg = getSG()
    pageDict = {}
    tmpPages = sg.find('Page',filters=[['project.Project.name','is',projName]],fields=['entity_type','id','name'])

    for tmp in tmpPages:
        if pageDict.has_key((tmp['entity_type'])) == 0:
            #print str(tmp['id']) + " " + str(tmp['entity_type'])
            pageDict[tmp['entity_type']] = tmp['id']
    return pageDict

def sgGetPage(pr,ep,sq,val):
    
    sg = getSG()
    pageDict = getPageDict(pr)
    
    epiObj = sg.find_one("Scene", [['code','is', str(ep)], ['project.Project.name','is', str(pr)]], ['id'])
    seqObj = sg.find_one("Sequence", [['code','is', sq], ['project.Project.name','is', str(pr)],['scene_sg_sequence_1_scenes.Scene.code','is', str(ep)]],['id'])
    #shotObj = sg.find_one("Shot", [['code','is', str(sh)], ['project.Project.name','is', str(pr)],['sg_sequence.Sequence.code','is', str(sq)],['sg_scene.Scene.code','is', str(ep)]],['id'])
    #taskObj = sg.find_one('Task',[['project.Project.name','is',str(pr)],['entity.Sequence.code','is',str(sq)],['step.Step.code','is',str(tk)]],['id'])
    
    globalEpPage = "https://duckling.shotgunstudio.com/page/" + str(pageDict['Scene'])
    globalSqPage = "https://duckling.shotgunstudio.com/page/" + str(pageDict['Sequence'])
    globalShPage = "https://duckling.shotgunstudio.com/page/" + str(pageDict['Shot'])
    #shPage = "https://duckling.shotgunstudio.com/page/" + str(pageDict['Shot']) + "#Shot" + "_" + str(shotObj['id']) + "_" + str(sh)
    #tkPage = "https://duckling.shotgunstudio.com/page/" + str(pageDict['Shot']) + "#Task" + "_" + str(taskObj['id']) + "_" + str(tk)
    #ovPage = "https://duckling.shotgunstudio.com/page/" + str(pageDict['Task'])

    if val =="sq":
        return globalSqPage 

def sgTestProject(projName):
    sg = getSG()
    ###Create Project in shotgun###
    myProj = sgGetProject(projName,[])

    if myProj == None:
        sg.create("Project",{"name":str(projName),"sg_status":"Active"})
        print "created project in shotgun"
    else:
        print "already present"

def sgTestEpisode(projName,epiName,fps,rez):
    sg = getSG()

    myProj = sgGetProject(projName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    if myEpi == None:
        episode = sg.create("Scene", {"code":str(epiName), "project":myProj,'sg_resolution':rez,'sg_fps':fps})
        print "created episode in shotgun"
    else:
        
        print "episode already present"

def sgTestSeq(wf,projName,epiName,seqName):
    sg = getSG()

    myProj = sgGetProject(projName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    mySeq = sgGetSequence(seqName,projName,epiName,[])

    if wf == "SEQUENCE":
        template = sgTemplate(wf,sg)
        if mySeq == None:
            #add asset, that matches these critias
            data = { 'project':myProj,'code': seqName,'scene_sg_sequence_1_scenes':[myEpi,],'sg_sequence_type':'Sequence','task_template': template}
            result = sg.create('Sequence', data)
            print "created seq in shotgun"
        else:
            print "seq already present"

    if wf == "SHOT":
        template = sgTemplate(wf,sg)
        if mySeq == None:
            #add asset, that matches these critias
            data = { 'project':myProj,'code': seqName,'scene_sg_sequence_1_scenes':[myEpi,],'sg_sequence_type':'Shot'}
            result = sg.create('Sequence', data)
            print "created seq in shotgun"
        else:
            print "seq already present"

def sgTestShot(wf,projName,epiName,seqName,shotName):
    sg = getSG()

    myProj = sgGetProject(projName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    mySeq = sgGetSequence(seqName,projName,epiName,[])
    myShot = sgGetShot(sg,shotName,seqName,projName,epiName,[])

    if wf == "SEQUENCE":
        template = sgTemplate(wf,sg)
    if wf == "SHOT":
        template = sgTemplate(wf,sg)

    if myShot == None:
        data = {'code':shotName,'sg_sequence':mySeq,'sg_scene':myEpi,'project':myProj,'task_template': template}
        result = sg.create('Shot', data)
        print "created shot in shotgun"
    else:
        print "shot already present"

def sgTestSeqWF(projName,epiName,seqName):
    sg = getSG()
    mySeq = sgGetSequence(seqName,projName,epiName,['code','sg_sequence_type'])
    return mySeq

def sgTemplate(wf,sg):
    if wf == "SHOT":
        filters = [ ['code','is', 'DucklingShotTemplate' ]]
        template = sg.find_one('TaskTemplate',filters)
        return template
    elif wf == "SEQUENCE":
        filters = [ ['code','is', 'DucklingSequenceTemplate' ]]
        template = sg.find_one('TaskTemplate',filters)
        return template

def sgGetData(sgEntity, fields = []):
    sg = getSG()
    return sg.find_one( sgEntity['type'] ,[['id','is', sgEntity['id']]], fields)

def sgGetObjbyID(entity,objID,fields = []):
    sg = getSG()
    return sg.find_one(entity,[['id','is',objID]],fields)

def sgCreateObj(entity,data):
    sg = getSG()
    return sg.create(entity, data) 

def sgGetProjects(fields = []):
    sg = getSG()
    return sg.find("Project",filters=[['sg_status', 'is_not', 'Archive'],['sg_status', 'is_not', 'Done/Closed'],['sg_status', 'is_not', 'Lost'],['sg_status', 'is_not', 'NotActive'],['sg_status', 'is_not', 'Development']],fields=['name'])

def sgGetProject(projName,fields = []):
    sg = getSG()
    return sg.find_one("Project", [["name", "is", str(projName)]], fields)

def sgGetEpisode(epiName,projName, fields = []):
    sg = getSG()
    return sg.find_one("Scene", [['code','is', str(epiName)], ['project.Project.name','is', str(projName)]], fields)

def sgGetSequence(seqName,projName,epiName,fields = []):
    sg = getSG()
    return sg.find_one("Sequence", [['code','is', seqName], ['project.Project.name','is', str(projName)],['scene_sg_sequence_1_scenes.Scene.code','is', str(epiName)]],fields)

def sgGetShot(sg,shotName,seqName,projName,epiName, fields = []):
    return sg.find_one("Shot", [['code','is', str(shotName)], ['project.Project.name','is', str(projName)],['sg_sequence.Sequence.code','is', str(seqName)],['sg_scene.Scene.code','is', str(epiName)]],fields)

def sgGetShotTasks(shotID,fields = []):
    sg = getSG()
    return sg.find('Task',[['entity.Shot.id','is',shotID]],fields)

def sgGetTasks(pr,sq,sh,step,fields = []):
    sg = getSG()
    return sg.find_one('Task',[['project.Project.name','is',str(pr)],['entity.Shot.sg_sequence.Sequence.code','is',str(sq)],['entity.Shot.code','is',str(sh)],['step.Step.code','is',str(step)]],fields)

def sgGetTask(taskID,fields = []):
    sg = getSG()
    return sg.find_one('Task',[['id','is',taskID]],fields)

def sgGetSeqTasks(seqID,fields = []):
    sg = getSG()
    return sg.find('Task',[['entity.Sequence.id','is',seqID]],fields)

def sgGetAssetTasks(assetID,fields = []):
    sg = getSG()
    return sg.find('Task',[['entity.Asset.id','is',assetID]],fields)

def sgGetAsset(aName,projName,fields = []):
    sg = getSG()
    return sg.find_one('Asset',[['code','is',aName],['project.Project.name','is',str(projName)]],fields )

def sgGetUserObj(userName,fields = []):
    sg = getSG()
    return sg.find_one("HumanUser", [["name","is",str(userName)]], fields)

def sgGetVersion(taskID,fields = []):
    sg = getSG()
    return sg.find('Version',[['sg_task.Task.id','is',taskID]],fields)

def sgSetTaskStatus(taskID, state):
    sg = getSG()
    sg.update("Task",taskID, {"sg_status_list":state})

def sgCreateShotTask(pr,sh,step,name):
    sg = getSG()
    data = {'content':name,'entity':sh,'project':pr,'step':step}
    result = sg.create('Task', data)
    return result

def sgGetVersionID(sg,filePath,version):
    pathDict = sgShotPathParce(filePath)
    proj = sgGetProject(pathDict['dsProject'],['name'])
    projName = proj['name']
    epiObj = sgGetEpisode(pathDict['dsEpisode'],projName,['code','id','sg_status_list','shots','sequence'])
    epiName = epiObj['code']
    seqObj = sgGetSequence(pathDict['dsSeq'],projName,epiName,['code'])
    seqName = seqObj['code']
    shotObj = sgGetShot(sg,pathDict['dsShot'],seqName,projName,epiName,['code','id'])
    shotName = shotObj['code']
    shotID = shotObj['id']
    shotTasks = sgGetShotTasks(shotID,['content','id','step'])
    for task in shotTasks:
        if str(task['step']['name']) == str(pathDict['dsStep']):
            taskObj = task
            break
    taskID = taskObj['id']
    return taskID

def sgGetPeople():
    sg = getSG()
    myPeople = sg.find("HumanUser", [["groups.Group.code","is","ducklings"]], ["name","projects","sg_initials","sg_status_list"])
    return myPeople

def sgGetUser(userName):
    sg = getSG()
    myPeople = sg.find("HumanUser", [["groups.Group.code","is","ducklings"]], ["name","projects","sg_initials"])
    for user in myPeople:
        if userName == str(user['name']) or userName == str(user['sg_initials']):
            myUser = user
            return myUser

def sgShotPathParce(filePath):

    pathDict = {}

    if re.search("s[0-9][0-9][0-9][0-9]/3D",filePath):
    #if re.search("film",filePath) and re.search("3D",filePath) and re.search("s[0-9][0-9][0-9][0-9]",filePath):
        print "shot based"
        match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/(?P<dsShot>\w*)\/3D\/(?P<dsStep>\w*)\/(?P<fileName>\w*)', filePath)
        match = match.groupdict()
        fileNameDict = match['fileName'].split("_")

    if re.search("q[0-9][0-9][0-9][0-9]/3D",filePath):
    #if re.search("film",filePath) and not re.search("s[0-9][0-9][0-9][0-9]",filePath):
        print "seq based"
        match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/3D\/(?P<dsStep>\w*)\/(?P<fileName>\w*)', filePath)
#        match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/(?P<dsStep>\w*)\/(?P<fileName>\w*)', filePath)
        match = match.groupdict()
        fileNameDict = match['fileName'].split("_")

    if re.search("rawRender",filePath):
        match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/(?P<dsShot>\w*)\/(?P<rawRender>\w*)\/(?P<dsRenderLayer>\w*)\/(?P<fileName>\w*)', filePath)
        match = match.groupdict()
        fileNameDict = match['fileName'].split("_")

    if re.search("compOut",filePath):
        match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/(?P<dsShot>\w*)\/comp\/compOut\/(?P<dsVersion>\w*)\/(?P<fileName>\w*)', filePath)
        match = match.groupdict()
        fileNameDict = match['fileName'].split("_")

    if re.search("asset",filePath):
        match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/asset\/3D\/(?P<type>\w*)\/(?P<subType>\w*)\/(?P<aName>\w*)\/dev\/(?P<dsSoftware>\w*)\/(?P<fileName>\w*)', filePath)
        fileNameDict = match['fileName'].split("_")
        match = match.groupdict()

    if match:
        pathDict = match
        if fileNameDict != []:
            for fn in fileNameDict:
                if not re.search("q[0-9][0-9][0-9][0-9]",fn):
                    if not re.search("s[0-9][0-9][0-9][0-9]",fn):
                        dsTask = fn
            try:pathDict['task'] = dsTask
            except:pass
    return pathDict

def sgGetLatestVersion(sg,filePath):
    pathDict = sgShotPathParce(filePath)

    if 'dsEpisode' in pathDict:
        proj = sgGetProject(str(pathDict['dsProject']),['name'])
        projName = proj['name']
        epiObj = sgGetEpisode(str(pathDict['dsEpisode']),projName,['code','id','sg_status_list','shots','sequence'])
        epiName = epiObj['code']
        seqObj = sgGetSequence(str(pathDict['dsSeq']),projName,epiName,['code'])
        seqName = seqObj['code']
        shotObj = sgGetShot(sg,str(pathDict['dsShot']),seqName,projName,epiName,['code','id'])
        shotName = shotObj['code']
        shotID = shotObj['id']
        shotTasks = sgGetShotTasks(shotID,['content','id','step'])

        for task in shotTasks:
            if task['step']['name'] == pathDict['dsStep']:

                taskObj = task
                taskID = taskObj['id']
                taskVersions = sgGetVersion(taskID,['code','id','sg_task'])
                verList = []
                if taskVersions != []:
                    for tv in taskVersions:
                        lVersion = str(tv['code'])[-3:]
                        verList.append(lVersion)
                    verList.sort()
                    val = int(verList[-1]) + 1
                    return 'v%03d' %int(val)
            else:
                pass

    if 'aName' in pathDict:
        proj = sgGetProject(str(pathDict['dsProject']),['name'])
        projName = proj['name']
        aName = pathDict['aName']
        fileName = pathDict['fileName']
        assetObj = sgGetAsset(sg,aName,projName,['id'])
        assetID = assetObj['id']
        assetTasks = sgGetAssetTasks(sg,assetID,['content','id','step'])
        for task in assetTasks:
            fileNameSplit = fileName.split("_")
            dsStep = fileNameSplit[-1].lower()
            if str(task['step']['name']) == str(dsStep):
                taskObj = task
                taskID = taskObj['id']
                taskVersions = sgGetVersion(taskID,['code','id','sg_task'])
                verList = []
                if taskVersions != []:
                    for ver in taskVersions:
                        verList.append(ver['code'])
                    val = len(verList) + 1
                    return 'v%03d' %int(val)

def sgConvertIcon(frameOne):

    if re.search(".jpg",frameOne) or re.search(".jpeg",frameOne):
        return frameOne
    if re.search("dpx",frameOne) or re.search("exr",frameOne):

        pSplit = frameOne.split(".")
        frameOut = frameOne.replace("."+pSplit[-1],"")

        if sys.platform == "linux2":
            rvio = '/usr/local/rv-Linux-x86-64-3.12.20/bin/rvio'
            cmd = rvio + ' ' + frameOne + ' -o '+ frameOut + '.jpg'
            os.system(cmd)
            #subprocess.Popen(cmd,shell=True)
            return frameOut + ".jpg"
        else:
            rvio = '"C:/Program Files (x86)/Tweak/RV-3.12.20-32/bin/rvio.exe"'
            cmd = rvio + ' ' + frameOne + ' -o '+ frameOut + '.jpg'
            os.system(cmd)
            #subprocess.Popen(cmd, creationflags = subprocess.CREATE_NEW_CONSOLE)
            return frameOut + ".jpg"


def sgGetFrameInfo(filePath):
    fileSplit = filePath.split("/")
    extSplit = filePath.split(".")
    renderlayerDir = filePath.replace("/" + fileSplit[-1],"")
    fileList = os.listdir(renderlayerDir)
    fListClean = []
    for file in fileList:
        fileSplit = file.split(".")
        if fileSplit[-1] == extSplit[-1]:
            fListClean.append(file)
    fListClean.sort()
    frame_count = len(fListClean)
    startFrame = fListClean[0]
    startObj = re.search("[0-9][0-9][0-9][0-9]\.",startFrame)
    sg_start_frame = startObj.group()[:-1]
    endFrame = fListClean[-1]
    endObj = re.search("[0-9][0-9][0-9][0-9]\.",endFrame)
    sg_end_frame = endObj.group()[:-1]
    frameInfo = {'frame_count':frame_count,'sg_start_frame':sg_start_frame,'sg_end_frame':sg_end_frame,'startFrame':startFrame,'endFrame':endFrame,'sg_file_name':startObj}
    return frameInfo

def testVersion(taskID,version,projName,epiName,seqName,shotName):
    sg = getSG()

    myProj = sgGetProject(projName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    mySeq = sgGetSequence(seqName,projName,epiName,[])
    myShot = sgGetShot(sg,shotName,seqName,projName,epiName,['id'])
    shotID = myShot['id']
    myTasks = sgGetShotTasks(shotID,['id'])
    for task in myTasks:
        if int(task['id']) == int(taskID):
            match = True

def sgPublish3DFrames(filePath,renderFile,user,pubPath):
    sg = getSG()
    icon = sgConvertIcon(filePath)
    usObj = sgGetUser(user)
    taskObj = None
    versionObj = re.search("v[0-9][0-9][0-9]",renderFile)
    version = versionObj.group()

    pathDict = sgShotPathParce(filePath)
    proj = sgGetProject(str(pathDict['dsProject']),['name'])
    projName = proj['name']
    epiObj = sgGetEpisode(str(pathDict['dsEpisode']),projName,['code','id','sg_status_list','shots','sequence'])
    epiName = epiObj['code']
    seqObj = sgGetSequence(str(pathDict['dsSeq']),projName,epiName,['code'])
    seqName = seqObj['code']
    shotObj = sgGetShot(sg,str(pathDict['dsShot']),seqName,projName,epiName,['code','id'])
    shotName = shotObj['code']
    shotID = shotObj['id']
    shotTasks = sgGetShotTasks(shotID,['content','id','step'])
    dsRenderLayer = pathDict['dsRenderLayer']

    for task in shotTasks:
        if str(task['step']['name']) == 'publish3d':
            taskObj = task
            taskID = task['id']

    if taskObj == None:
        publish3dTask =  {'type': 'Step', 'name': 'publish3d', 'id': 14}
        taskObj = sgCreateShotTask(sg,proj,shotObj,publish3dTask,'publish3d')
        taskID = taskObj['id']

    myProj = sgGetProject(projName,[])
    mySeq = sgGetSequence(seqName,projName,epiName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    myShot = sgGetShot(sg,shotName,seqName,projName,epiName,[])

    fileSplit = filePath.split("/")
    renderlayerDir = filePath.replace("/" + fileSplit[-1],"")
    fileList = os.listdir(renderlayerDir)

    if fileList != []:
        filter = [['sg_task','is',taskObj]]
        dictFromSG = sg.find('Version',filter )

        frameInfo = sgGetFrameInfo(filePath)
        frame_count = int(frameInfo['frame_count'])
        sg_first_frame = int(frameInfo['sg_start_frame'])
        sg_last_frame = int(frameInfo['sg_end_frame'])
        startFrame = frameInfo['startFrame']
        endFrame = frameInfo['endFrame']

        startFrame = re.sub("RL_","RL.",startFrame)
        endFrame = re.sub("RL_","RL.",endFrame)

        filePath = filePath.replace(pathDict['dsRelative'] + "/" ,"")
        renderFile = renderFile.replace(pathDict['dsRelative'] + "/","")
        versions = sgGetVersion(taskID,['code','id','sg_render_layer'])
        match = False

        for ver in versions:
            if ver['code'] == version and ver['sg_render_layer'] == pathDict['dsRenderLayer']:
                match = True
                sg.update('Version',ver['id'], {'sg_path_to_frames':pubPath,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame})
                print "updated " + str(version) + " in shotGun"
                break
            else:
                match = False
        if match != True:
            data = {'code':str(version),'user':usObj,'sg_file_name':startFrame,'project':proj,'sg_sequence':[mySeq],'sg_task':taskObj,'sg_path_to_frames':pubPath,'sg_path':renderFile,'sg_render_layer':dsRenderLayer,'entity':myShot,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame}
            result = sg.create('Version', data)
            print "created " + str(version) + " in shotGun"

            ''' update status's '''
            sgSetTaskStatus(sg,taskID,'3dp')
            print "changed status for 3dPublished " + str(taskID) + " too 3dp"
        updateCuts(shotID,sg_first_frame,sg_last_frame,frame_count,str(icon))

def updateCuts(shotID,ci,co,cd,icon):
    sg = getSG()
    result = sg.update('Shot',shotID,{'sg_cut_in':ci,'sg_cut_out':co,'sg_cut_duration':cd,'image':str(icon)})

def sgGetLatestOnline(pr,ep,sq,sh):
    sg = getSG()

    proj = sgGetProject(str(pr),['name'])
    projName = proj['name']
    epiObj = sgGetEpisode(str(ep),projName,['code','id','sg_status_list','shots','sequence'])
    epiName = epiObj['code']
    seqObj = sgGetSequence(str(sq),projName,epiName,['code'])
    seqName = seqObj['code']
    shotObj = sgGetShot(sg,str(sh),seqName,projName,epiName,['code','id'])
    shotName = shotObj['code']
    shotID = shotObj['id']
    shotTasks = sgGetShotTasks(shotID,['content','id','step'])
    for task in shotTasks:
        if str(task['step']['name']) == 'publish2d':
            taskObj = task
            taskID = task['id']
    return sgGetVersion(taskID,['code'])

def sgPublish2DFrames(filePath,renderFile,user,pubPath):
    sg = getSG()
    usObj = sgGetUser(user)
    icon = sgConvertIcon(filePath)
    versionObj = re.search("v[0-9][0-9][0-9]",renderFile)
    version = versionObj.group()

    fileDirList = filePath.split("/")
    fileDir = filePath.replace("/" + fileDirList[-1],"")

    outPutList = os.listdir(fileDir)
    for file in outPutList:
        if not re.search(".nk",file):
            sg_file_name = file
            break

    pathDict = sgShotPathParce(filePath)
    proj = sgGetProject(str(pathDict['dsProject']),['name'])
    projName = proj['name']
    epiObj = sgGetEpisode(str(pathDict['dsEpisode']),projName,['code','id','sg_status_list','shots','sequence'])
    epiName = epiObj['code']
    seqObj = sgGetSequence(str(pathDict['dsSeq']),projName,epiName,['code'])
    seqName = seqObj['code']
    shotObj = sgGetShot(sg,str(pathDict['dsShot']),seqName,projName,epiName,['code','id'])
    shotName = shotObj['code']
    shotID = shotObj['id']
    shotTasks = sgGetShotTasks(shotID,['content','id','step'])
    dsVersion = pathDict['dsVersion']

    for task in shotTasks:
        if str(task['step']['name']) == 'publish2d':
            taskObj = task
            taskID = task['id']

    myProj = sgGetProject(projName,[])
    mySeq = sgGetSequence(seqName,projName,epiName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    myShot = sgGetShot(sg,shotName,seqName,projName,epiName,[])

    fileSplit = filePath.split("/")
    compOutDir = filePath.replace("/" + fileSplit[-1],"")
    fileList = os.listdir(compOutDir)

    if fileList != []:
        filter = [['sg_task','is',taskObj]]
        dictFromSG = sg.find('Version',filter )


        frameInfo = sgGetFrameInfo(filePath)
        frame_count = int(frameInfo['frame_count'])
        sg_first_frame = int(frameInfo['sg_start_frame'])
        sg_last_frame = int(frameInfo['sg_end_frame'])
        startFrame = frameInfo['startFrame']
        endFrame = frameInfo['endFrame']

        #filePath = filePath.replace(pathDict['dsRelative'] ,"")
        if re.search("dsPipe",str(pathDict['dsRelative'])):filePath = filePath.replace(pathDict['dsRelative'] ,"dsPipe")
        if re.search("dsComp",str(pathDict['dsRelative'])):filePath = filePath.replace(pathDict['dsRelative'] ,"dsComp")

        fnSplit = startFrame.split(".")

        sg_mov = fnSplit[0]
        compOutDir = compOutDir.replace(pathDict['dsRelative'] ,"")
        pathToMov = compOutDir + "/" + sg_mov + ".mov"

        renderFile = renderFile.replace(pathDict['dsRelative'] + "/","")
        versions = sgGetVersion(taskID,['code','id','sg_render_layer'])
        match = False
        for ver in versions:
            if ver['code'] == version :
                match = True
                print "Version Already present"
                pubPath = pubPath + str(version)
                sg.update('Version',ver['id'], {'sg_path_to_frames':pubPath,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame})
                print "updated " + str(version) + " in shotGun"
                break
            else:
                match = False
        if match != True:
            pubPath = pubPath + str(version)
            #data = {'code':str(version),'user':usObj,'sg_path_to_movie':str(pathToMov),'project':proj,'sg_sequence':[mySeq],'sg_file_name':sg_file_name,'sg_task':taskObj,'sg_path_to_frames':filePath,'sg_path':renderFile,'entity':myShot,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame}
            data = {'code':str(version),'user':usObj,'project':proj,'sg_sequence':[mySeq],'sg_file_name':sg_file_name,'sg_task':taskObj,'sg_path_to_frames':pubPath,'sg_path':renderFile,'entity':myShot,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame}
            result = sg.create('Version', data)
            print "created " + str(version) + " in shotGun"

            ''' update status's '''
            sgSetTaskStatus(sg,taskID,'2dp')
            print "changed status for taskID " + str(taskID) + " too 2dp"
        updateCuts(shotID,sg_first_frame,sg_last_frame,frame_count,str(icon))

'''
def sgPublishFrameStack(filePath,renderFile,task,user,version,dsShot):
    sg = getSG()
    usObj = sgGetUser(user)

    fileDirList = filePath.split("/")
    fileDir = filePath.replace("/" + fileDirList[-1],"")

    thumbPath = filePath.replace("/" + fileDirList[0],"")

    outPutList = os.listdir(fileDir)
    for file in outPutList:
        if re.search(".ma",file):
            sg_file_name = file
            break

    dsRelative = str(os.getenv('RELATIVEPATH'))
    dsProject = str(os.getenv('PROJECT'))
    dsEpisode = str(os.getenv('EPISODE'))
    dsSeq = str(os.getenv('SEQUENCE'))

    proj = sgGetProject(str(dsProject),['name'])
    projName = proj['name']
    epiObj = sgGetEpisode(str(dsEpisode),projName,['code','id','sg_status_list','shots','sequence'])
    epiName = epiObj['code']
    seqObj = sgGetSequence(str(dsSeq),projName,epiName,['code','id'])
    seqName = seqObj['code']
    seqID = seqObj['id']
    shotObj = sgGetShot(sg,str(dsShot),seqName,projName,epiName,['code','id'])
    shotName = shotObj['code']
    shotID = shotObj['id']

    shotTasks = sgGetSeqTasks(seqID,['content','id','step'])

    for task in shotTasks:
        if task['step']['name'] == str('anim'):
            taskObj = task
            taskID = task['id']

    myProj = sgGetProject(projName,[])
    mySeq = sgGetSequence(seqName,projName,epiName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    myShot = sgGetShot(sg,shotName,seqName,projName,epiName,[])

    fileSplit = filePath.split("/")
    compOutDir = filePath.replace("/" + fileSplit[-1],"")
    fileList = os.listdir(compOutDir)
    if fileList != []:
        filter = [['sg_task','is',taskObj]]
        dictFromSG = sg.find('Version',filter )

        frameInfo = sgGetFrameInfo(filePath)
        frame_count = int(frameInfo['frame_count'])
        sg_first_frame = int(frameInfo['sg_start_frame'])
        sg_last_frame = int(frameInfo['sg_end_frame'])
        startFrame = frameInfo['startFrame']
        endFrame = frameInfo['endFrame']

        filePath = filePath.replace(dsRelative + "/","dsPipe/")
        renderFile = renderFile.replace(dsRelative + "/","dsPipe/")

        versions = sgGetVersion(sg,taskID,['code','id','sg_render_layer'])
        match = False
        versionName = dsShot + "_" + version
        for ver in versions:
            if ver['code'] == versionName :
                match = True
                print "Version Already present"
                sg.update('Version',ver['id'], {'sg_path_to_frames':filePath,'image':str(thumbPath),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame})
                print "updated " + str(version) + " in shotGun"
                break
            else:
                match = False
        if match != True:
            data = {'code':str(versionName),'user':usObj,'project':proj,'sg_file_name':sg_file_name,'sg_task':taskObj,'sg_path_to_frames':filePath,'sg_path':renderFile,'entity':myShot,'image':str(thumbPath),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame}
            result = sg.create('Version', data)
            print "created " + str(version) + " in shotGun"
        updateCuts(shotID,sg_first_frame,sg_last_frame,frame_count,str(thumbPath))
'''

def sgCreateAssetVersion(sg,filePath,version):
    description=raw_input('Please enter a description:')
    cmds.file(f=True,s=True)
    pathDict = sgShotPathParce(filePath)
    versionUp(filePath,version)

    proj = sgGetProject(str(pathDict['dsProject']),['name'])
    projName = proj['name']
    aName = pathDict['aName']
    fileName = pathDict['fileName']
    assetObj = sgGetAsset(sg,aName,projName,['id'])
    assetID = assetObj['id']
    assetTasks = sgGetAssetTasks(sg,assetID,['content','id','step'])

    for task in assetTasks:
        fileNameSplit = fileName.split("_")
        dsStep = fileNameSplit[-1].lower()
        taskList = []
        if str(task['step']['name']) == str(dsStep):
            taskObj = task

            taskID = taskObj['id']
            taskVersions = sgGetVersion(taskID,['code'])

            filePathList = filePath.split("/")
            pathToFile = filePath.replace("/" + filePathList[-1], "")
            pathToFile = pathToFile.replace(pathDict['dsRelative'] + "/","")
            heroName = filePathList[-1]
            version_file_name = heroName.replace(".ma","_" + version + ".ma")

            testVersion = sg.find('Version',[['code','is',str(version)],['project','is',proj],['sg_task','is',taskObj],['entity','is',assetObj]])
            if testVersion == []:
                data = {'code':str(version),'project':proj,'sg_task':taskObj,'sg_file_name':heroName,'sg_path':pathToFile,'sg_render_layer':None,'description':description,'sg_version_file_name':version_file_name,'entity':assetObj}
                result = sg.create('Version', data)
                print "created " + version + " in shotGun"

def sgCreateShotVersion(sg,filePath,version):
    description=raw_input('Please enter a description:')

    pathDict = sgShotPathParce(filePath)
    thumbPath = sgThumbnail(filePath,version,True)

    proj = sgGetProject(pathDict['dsProject'],['name'])
    projName = proj['name']
    epiObj = sgGetEpisode(pathDict['dsEpisode'],projName,['code','id','sg_status_list','shots','sequence'])
    epiName = epiObj['code']
    seqObj = sgGetSequence(pathDict['dsSeq'],projName,epiName,['code'])
    seqName = seqObj['code']
    shotObj = sgGetShot(sg,pathDict['dsShot'],seqName,projName,epiName,['code','id'])
    shotName = shotObj['code']
    shotID = shotObj['id']
    shotTasks = sgGetShotTasks(shotID,['content','id','step'])

    for task in shotTasks:
        if str(task['step']['name']) == str(pathDict['dsStep']):
            #if str(task['content']) == str(pathDict['task']):
            taskObj = task
            break


    taskID = taskObj['id']
    taskVersions = sgGetVersion(taskID,['code'])
    #myUser = sgGetUser(sg,user)

    filePathList = filePath.split("/")
    pathToFile = filePath.replace("/" + filePathList[-1], "")
    pathToFile = pathToFile.replace(pathDict['dsRelative'] + "/","")
    heroName = filePathList[-1]
    version_file_name = heroName.replace(".ma","_" + version + ".ma")

    testVersion = sg.find('Version',[['code','is',str(version)],['project','is',proj],['sg_task','is',taskObj],['entity','is',shotObj]])
    if testVersion == []:
        data = {'code':str(version),'project':proj,'sg_task':taskObj,'sg_file_name':heroName,'sg_path':pathToFile,'sg_render_layer':None,'description':description,'image':thumbPath,'sg_version_file_name':version_file_name,'entity':shotObj}
        #print data
        result = sg.create('Version', data)
        print "created " + version + " in shotGun"
    else:
        print "version already present"

def sgThumbUpdate(type,obj,thumbPath):
    #print thumbPath
    sg = getSG()
    sg.update(type,obj["id"], {"image":str(thumbPath)})

def versionUp(filePath,version):
    if not re.search("/version/",filePath):
        filePathList = filePath.split("/")
        versionPath = filePath.replace(filePathList[-1],"version")
        versionPath = versionPath + "/" + filePathList[-1]
        if not os.path.isdir(versionPath):
            os.makedirs(versionPath)
        version_file_name = filePathList[-1].replace(".ma","_" + version + ".ma")
        shutil.copy(filePath,versionPath + "/" + version_file_name)

        print "versioned UP"
    else:
        print "your working in a verison and not the hero file "

def sgThumbnail(filePath,version,bool):
    ''' path to maya scene version and bool to create icon or not...'''
    pathDict = sgShotPathParce(filePath)
    try:
        thumbNailPath = pathDict['dsRelative'] + "/" + pathDict['dsProject'] + "/film/" + pathDict['dsEpisode'] + "/" + pathDict['dsSeq'] + "/" + pathDict['dsShot'] + "/3D/data/icon/"
        thumbPath = thumbNailPath + pathDict['dsSeq'] + "_" + pathDict['dsShot'] + "_" + pathDict['dsStep'] + "_" + pathDict['task'] + "_" + version + ".png"
    except:
        thumbNailPath = pathDict['dsRelative'] + "/" + pathDict['dsProject'] + "/film/" + pathDict['dsEpisode'] + "/" + pathDict['dsSeq'] + "/3D/data/icon/"
        thumbPath = thumbNailPath + pathDict['dsSeq'] + "_" + pathDict['dsStep'] + "_" + pathDict['task'] + "_" + version + ".png"

    if not os.path.isdir(thumbNailPath):
        os.makedirs(thumbNailPath)
    if bool == True:
        view = apiUI.M3dView.active3dView()
        image = api.MImage()
        view.readColorBuffer(image, True)
        image.writeToFile(thumbPath , 'png')
    return thumbPath

def sgPublishFrames(filePath,renderFile,task,user,ver,dsShot):
    sg = getSG()
    usObj = sgGetUser(user)
    icon = sgConvertIcon(filePath)
    #versionObj = re.search("v[0-9][0-9][0-9]",renderFile)
    #version = versionObj.group()
    version = ver
    fileDirList = filePath.split("/")
    fileDir = filePath.replace("/" + fileDirList[-1],"")

    outPutList = os.listdir(fileDir)
    for file in outPutList:
        if not re.search(".nk",file):
            sg_file_name = file
            break

    dsRelative = str(os.getenv('RELATIVEPATH'))
    dsProject = str(os.getenv('PROJECT'))
    dsEpisode = str(os.getenv('EPISODE'))
    dsSeq = str(os.getenv('SEQUENCE'))

    proj = sgGetProject(str(dsProject),['name'])
    projName = proj['name']
    epiObj = sgGetEpisode(str(dsEpisode),projName,['code','id','sg_status_list','shots','sequence'])
    epiName = epiObj['code']
    seqObj = sgGetSequence(str(dsSeq),projName,epiName,['code','id'])
    seqName = seqObj['code']
    seqID = seqObj['id']
    shotObj = sgGetShot(sg,str(dsShot),seqName,projName,epiName,['code','id'])
    shotName = shotObj['code']
    shotID = shotObj['id']
    shotTasks = sgGetSeqTasks(seqID,['content','id','step'])

    for step in shotTasks:
        print step['step']['name']
        if str(step['step']['name']) == task:
            taskObj = step
            taskID = step['id']

    myProj = sgGetProject(projName,[])
    mySeq = sgGetSequence(seqName,projName,epiName,[])
    myEpi = sgGetEpisode(epiName,projName,[])
    myShot = sgGetShot(sg,shotName,seqName,projName,epiName,[])

    fileSplit = filePath.split("/")
    compOutDir = filePath.replace("/" + fileSplit[-1],"")
    fileList = os.listdir(compOutDir)

    if fileList != []:
        filter = [['sg_task','is',taskObj]]
        dictFromSG = sg.find('Version',filter )

        frameInfo = sgGetFrameInfo(filePath)
        frame_count = int(frameInfo['frame_count'])
        sg_first_frame = int(frameInfo['sg_start_frame'])
        sg_last_frame = int(frameInfo['sg_end_frame'])
        startFrame = frameInfo['startFrame']
        endFrame = frameInfo['endFrame']

        if sys.platform == "linux2":
            filePath.replace("/dsPipe","P:/")
            filePath.replace("/dsComp","S:/")

        fnSplit = startFrame.split(".")

        sg_mov = fnSplit[0]

        filePath = filePath.replace(dsRelative + "/","dsPipe/")
        renderFile = renderFile.replace(dsRelative + "/","dsPipe/")

        versions = sgGetVersion(taskID,['code','id','sg_render_layer'])
        match = False
        versionName = dsShot + "_" + version
        for ver in versions:
            if ver['code'] == versionName :
                match = True
                print "Version Already present"
                sg.update('Version',ver['id'], {'sg_path_to_frames':filePath,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame})
                print "updated " + str(version) + " in shotGun"
                break
            else:
                match = False
        if match != True:
            data = {'code':str(versionName),'user':usObj,'project':proj,'sg_file_name':sg_file_name,'sg_task':taskObj,'sg_path_to_frames':filePath,'sg_path':renderFile,'entity':myShot,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame}
            result = sg.create('Version', data)
            print "created " + str(version) + " in shotGun"
        updateCuts(shotID,sg_first_frame,sg_last_frame,frame_count,str(icon))
