'''
Created on 28/06/2013

@author: admin
'''


def doIT(self):
    duckUser = self.User_CB.currentText()
    for user in self.myPeople:           
        if str(duckUser) == user['name']:
            self.currentUser = user
            self.duckInitials = user['sg_initials']
            break
        
    thumbPath = sgTools.sgThumbnail(self.filePath,self.check,True)
    description = str(self.description_LE.text())
    
    if description != "":
        self.sgTaskID = cmds.getAttr('dsMetaData.sgTaskID')
        self.versionUp(self.filePath,self.check,False)
        
        cmds.setAttr("dsMetaData.User",str(duckUser),type="string")
        cmds.setAttr("dsMetaData.Version",str(self.version_file_name),type="string")
        
        save = cmds.file(save=True, force=True)
        self.versionUp(self.filePath,self.check,True)
    
        self.path_version_file = self.path_version_file.replace(self.pathDict['dsRelative'] + "/","")
        
        heroName = self.pathDict['fileName']
        self.connect2SG()
        
        if self.wf == "shot":
            data = {'code':self.version_file_name,'project':self.proj,'user':self.currentUser,'sg_task':self.taskObj,'sg_file_name':heroName,'sg_path':self.path_version_file,'description':description,'image':thumbPath,'sg_version_file_name':self.version_file_name,'entity':self.shotObj}
        else:
            data = {'code':self.version_file_name,'project':self.proj,'user':self.currentUser,'sg_task':self.taskObj,'sg_file_name':heroName,'sg_path':self.path_version_file,'description':description,'image':thumbPath,'sg_version_file_name':self.version_file_name,'entity':self.seqObj}
       
        result = sgTools.sgCreateObj('Version',data)
        print "created " + self.version_file_name + " in shotGun"
    
    self.close()
    
    self.check = self.checkLocalVersion(self.filePath,self.pathDict)
    self.versionUp(self.filePath,self.check,False)
    cmds.setAttr("dsMetaData.Version",str(self.version_file_name),type="string")