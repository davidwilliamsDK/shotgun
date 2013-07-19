'''
Created on 11/07/2013

@author: admin
'''

import re,sgTools,sys,os

def sgPublishFrameStack():
    if len(sys.argv) == 2:
        filePath = str(sys.argv[1])
    
        if re.search("compOut",filePath):
            match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/(?P<dsShot>\w*)\/comp\/compOut\/(?P<dsVersion>\w*)\/(?P<fileName>\w*)', filePath)
            match = match.groupdict()
            fileNameDict = match['fileName'].split("_")
            Step = "comp"
            
            print filePath

            version = match['dsVersion']
        
            fileDirList = filePath.split("/")
            compOutVer = filePath.replace("/" + fileDirList[-1],"")
            
            fileInfo = getUserNK(compOutVer)
            frameInfo = sgTools.sgGetFrameInfo(filePath)
            icon = filePath
            
            proj = sgTools.sgGetProject(str(match['dsProject']),[])
            epiObj = sgTools.sgGetEpisode(str(match['dsEpisode']),str(match['dsProject']),[])
            seqObj = sgTools.sgGetSequence(str(match['dsSeq']),str(match['dsProject']),str(match['dsEpisode']),[])
            taskObj = sgTools.sgGetTasks(str(match['dsProject']),str(match['dsSeq']),str(match['dsShot']),str(Step),['content','id','entity'])
            userObj = sgTools.sgGetUser(str(fileInfo['user']))
            
            renderFile = compOutVer + "/" + fileInfo['nkScript']
            frame_count = int(frameInfo['frame_count'])
            sg_first_frame = int(frameInfo['sg_start_frame'])
            sg_last_frame = int(frameInfo['sg_end_frame'])
            startFrame = frameInfo['startFrame']
            endFrame = frameInfo['endFrame']
            
            publishPath = match['dsRelative'] + "/" + match['dsProject'] + "/film/" + match['dsEpisode'] + "/" + match['dsSeq'] + "/" + match['dsShot'] + "/published2D/compOut/"
            QtPath = publishPath + "QT/"+ match['dsEpisode']+"_"+match['dsSeq']+"_"+match['dsShot']+"_comp.mov"
            
            print QtPath
            
            if os.path.isfile(QtPath):
               print "match" 
            
            #print version, compOutVer, proj, epiObj, seqObj, taskObj, userObj
            #print frame_count, sg_first_frame, sg_last_frame, startFrame, endFrame, renderFile
            
            """
            +Version
            +user
            +proj
            +seq
            +myShot
            +taskObj
            +frame_count
            +sg_first_frame
            +sg_last_frame
            +sg_file_name
            +renderFile
            +icon
            
            
            pubPath
            sg_uploaded_movie
            
            """
            #data = {'code':str(version),'user':usObj,'project':proj,'sg_sequence':[mySeq],'sg_file_name':sg_file_name,'sg_task':taskObj,'sg_path_to_frames':pubPath,'sg_path':renderFile,'entity':myShot,'image':str(icon),'frame_count':frame_count,'sg_first_frame':sg_first_frame,'sg_last_frame':sg_last_frame}
        
def getUserNK(compOutVer):
    tmpDict = {}
    tmpList = os.listdir(compOutVer)
    for t in tmpList:
        if re.search(".nk",t):
            nkScript = t
            break
    tmpSplit = nkScript.split("_")
    user = tmpSplit[-1][:-3]
    nn = tmpSplit[-2]
    ver = tmpSplit[-4]
    tmpDict['user'] = user
    tmpDict['nkScript'] = nkScript
    
    return tmpDict
    

sgPublishFrameStack()


'''
if re.search("s[0-9][0-9][0-9][0-9]/3D",filePath):
    print "shot based"
    match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/(?P<dsShot>\w*)\/3D\/(?P<dsStep>\w*)\/(?P<fileName>\w*)', filePath)
    match = match.groupdict()
    fileNameDict = match['fileName'].split("_")

if re.search("q[0-9][0-9][0-9][0-9]/3D",filePath):
    print "seq based"
    match = re.search('(?P<dsRelative>.*)\/(?P<dsProject>\w*)\/film\/(?P<dsEpisode>\w*)\/(?P<dsSeq>\w*)\/3D\/(?P<dsStep>\w*)\/(?P<fileName>\w*)', filePath)
    match = match.groupdict()
    fileNameDict = match['fileName'].split("_")
'''