import sys, re, os, shutil, subprocess, stat, string
import sgTools
import dsCommon.dsOsUtil as dsOsUtil
reload(dsOsUtil)
import dsSQLTools as dsSQL
import dsCheck;reload(dsCheck);dsCheck.dsMDCheck()

if sys.platform == "linux2":
    uiFile = '/dsGlobal/dsCore/shotgun/sgVersionUp.ui'
else:
    uiFile = '//vfx-data-server/dsGlobal/dsCore/shotgun/sgVersionUp.ui'

if dsOsUtil.mayaRunning() == True:
    import maya.cmds as cmds
    import maya.OpenMayaUI as mui
    pyVal = dsOsUtil.getPyGUI()
    
if pyVal == "PySide":
    from PySide import QtCore,QtGui
    from shiboken import wrapInstance
    form_class, base_class = dsOsUtil.loadUiType(uiFile)
    
if pyVal == "PyQt":
    from PyQt4 import QtGui, QtCore, uic
    import sip
    form_class, base_class = uic.loadUiType(uiFile)

def getMayaWindow():
    main_window_ptr = mui.MQtUtil.mainWindow()
    if pyVal == "PySide":
        return wrapInstance(long(main_window_ptr), QtGui.QWidget)
    else:
        return sip.wrapinstance(long(main_window_ptr), QtCore.QObject)

class Window(base_class, form_class):
    def __init__(self, parent=getMayaWindow()):
        super(Window, self).__init__(parent)
        self.setupUi(self)

        self.filePath = cmds.file(q=True,sn=True)
        print string.rsplit(self.filePath,"/",1)[1]

        self.home = 'C:%s' % os.getenv("HOMEPATH")
        self.config_dir = '%s/.versionUp' % (self.home)
        self.config_dir = self.config_dir.replace("/","\\")
        self.config_path = '%s/config.ini' % (self.config_dir)
        self.config_path = self.config_path.replace("/","\\")
        
        self.GetUser()
        self.load_config()
        #self.updateVersionName()
        
        sgTask = cmds.getAttr("dsMetaData.sgTask")
        self.testVersion()
        sgVersion = cmds.getAttr("dsMetaData.Version")
        
        self.version_TE.setText(sgVersion)
        self.task_TE.setText(sgTask)
        
        
        """ Test if shot or seq based file"""

        if re.search("s[0-9][0-9][0-9][0-9]/3D.",self.filePath):
            self.wf = "shot"
        if re.search("q[0-9][0-9][0-9][0-9]/3D.",self.filePath):
            self.wf = "seq"

        self.pathDict = sgTools.sgShotPathParce(self.filePath)
        self.check = self.checkLocalVersion(self.filePath,self.pathDict)
        self.updateVersionName()
                
        """ actions """
        
        self.User_CB.currentIndexChanged.connect(self.save_config)
        self.User_CB.currentIndexChanged.connect(self.updateVersionName)
        self.description_LE.returnPressed.connect(self.doIT)
        #self.description_LE.returnPressed.connect(self.sgCreateShotVersion)


    def testVersion(self):
        versionPath = string.rsplit(self.filePath,"/",1)[0] + "/version/" + string.rsplit(self.filePath,"/",1)[1]
        print versionPath
        if not os.path.isdir(versionPath):
            print "no version Created Yet"
            cmds.setAttr("dsMetaData.Version",string.rsplit(self.filePath,"/",1)[1],type="string")
        else:
            print "version Located"
            tmpList = os.listdir(versionPath)
            for t in tmpList:
                cmds.setAttr("dsMetaData.Version",t,type="string")
                
    def GetUser(self):
        ##Test and return if Episode exists
        self.User_CB.clear()
        self.userDict = {}
        
        self.group = {'type': 'Group', 'id': 5}
        self.myPeople = sgTools.sgGetPeople()
        for user in sorted(self.myPeople):
            tmpList = []
            if str(user['sg_status_list']) == "act":
                userName = str(user['name'])
                tmpList.append(user['id'])
                tmpList.append(user['sg_initials'])
                self.userDict[userName] = tmpList
                self.User_CB.addItem(userName)

    def updateVersionName(self):
        us = self.User_CB.currentText()
        self.duckInitials = self.userDict[str(us)][1]
        self.versionUp(self.filePath,self.check,False)
        cmds.setAttr("dsMetaData.Version",str(self.version_file_name),type="string")
        self.version_TE.setText(self.version_file_name)
        
    def doIT(self):
        duckUser = self.User_CB.currentText()
        for user in self.myPeople:           
            if str(duckUser) == user['name']:
                self.currentUser = user
                self.duckInitials = user['sg_initials']
                break
            
        thumbPath = sgTools.sgThumbnail(self.filePath,self.check,True)
        description = str(self.description_LE.text())
        
        if description is not "":
            self.sgTaskID = cmds.getAttr('dsMetaData.sgTaskID')
            self.versionUp(self.filePath,self.check,False)
            
            cmds.setAttr("dsMetaData.User",str(duckUser),type="string")

            save = cmds.file(save=True, force=True)
            self.versionUp(self.filePath,self.check,True)
        
            self.path_version_file = self.path_version_file.replace(self.pathDict['dsRelative'] + "/","")
            
            heroName = self.pathDict['fileName']

            if re.search("s[0-9][0-9][0-9][0-9]",cmds.file(q=True,sn=True,shn=True)):
                sName = re.search("s[0-9][0-9][0-9][0-9]",cmds.file(q=True,sn=True,shn=True))
                sName = sName.group()            
            else:
                shotList = cmds.ls(type = "shot")
                for shot in shotList:
                    """ skips namespaces"""
                    if re.search("s[0-9][0-9][0-9][0-9]",shot):
                        if re.search(":",shot):
                            sSplit = shot.split(":")
                            shot = sSplit[-1]
                        sName = shot
                        break
            try:
                self.connect2SG(sName)
                if self.wf == "shot":
                    data = {'code':self.version_file_name,'project':self.proj,'user':self.currentUser,'sg_task':self.taskObj,'sg_file_name':heroName,'sg_path':self.path_version_file,'description':description,'image':thumbPath,'sg_version_file_name':self.version_file_name,'entity':self.shotObj}
                else:
                    data = {'code':self.version_file_name,'project':self.proj,'user':self.currentUser,'sg_task':self.taskObj,'sg_file_name':heroName,'sg_path':self.path_version_file,'description':description,'image':thumbPath,'sg_version_file_name':self.version_file_name,'entity':self.seqObj}
               
                result = sgTools.sgCreateObj('Version',data)
                print "created " + self.version_file_name + " in shotGun"
            
            except:
                print "no camera seq or shotname in file name to establish shot.. adding to sequence"

        self.check = self.checkLocalVersion(self.filePath,self.pathDict)
        self.versionUp(self.filePath,self.check,False)
        cmds.setAttr("dsMetaData.Version",str(self.version_file_name),type="string")
        
        dsVerWindow.close()
        #self.close()
        

    def versionUp(self,filePath,version,val):
        if not re.search("/version/",filePath):
            filePathList = filePath.split("/")
            versionPath = filePath.replace(filePathList[-1],"version")
            versionPath = versionPath + "/" + filePathList[-1]
            if not os.path.isdir(versionPath):
                os.makedirs(versionPath)
                
            self.version_file_name = filePathList[-1].replace(self.ext,"_" + version + "_" + self.duckInitials +  self.ext)
            cmds.setAttr("dsMetaData.Version",str(self.version_file_name),type="string")
            self.path_version_file = versionPath + "/" + self.version_file_name
            
            if val == True:
                shutil.copy(filePath,versionPath + "/" + self.version_file_name)
                print "versioned UP"
                self.filePermissions(versionPath + "/" + self.version_file_name)
    
    def filePermissions(self,myFile):
        fileAtt = os.stat(myFile)[0]
        if (not fileAtt & stat.S_IWRITE):
           # File is read-only, so make it writeable
           os.chmod(myFile, stat.S_IWRITE)
        else:
           # File is writeable, so make it read-only
           os.chmod(myFile, stat.S_IREAD)

    def connect2SG(self,sName):
        
        projName = cmds.getAttr("dsMetaData.Project")
        epiName = cmds.getAttr("dsMetaData.Episode")
        seqID = cmds.getAttr("dsMetaData.sgSeqID")
        sgTask = cmds.getAttr("dsMetaData.sgTask")
        TaskID = cmds.getAttr("dsMetaData.sgTaskID")

        self.proj = sgTools.sgGetProject(projName,[])
        self.epiObj = sgTools.sgGetEpisode(epiName,projName,[])

        if TaskID == "none":
            TaskID = cmds.getAttr("dsMetaData."+sName+"_shotTaskID")
            shotID = cmds.getAttr("dsMetaData."+sName+"_shotID")
            self.shotObj = sgTools.sgGetObjbyID("Shot",int(shotID),[])
            self.wf = "shot" 
        else:
            self.seqObj = sgTools.sgGetObjbyID("Sequence",int(seqID),[])
            self.wf = "seq"
        
        self.taskObj = sgTools.sgGetObjbyID("Task",int(TaskID),[])
        
    def checkLocalVersion(self,filePath,pathDict):
        tmpList = []
        if re.search(".ma",filePath):
            self.ext = ".ma"
            dirPath = filePath.replace(self.pathDict['fileName'] + '.ma',"")
            
            self.fn = self.pathDict['fileName'] + self.ext
        if re.search(".mb",filePath):
            self.ext = ".mb"
            dirPath = filePath.replace(self.pathDict['fileName'] + '.mb',"")
            self.fn = self.pathDict['fileName'] + self.ext
        local = os.listdir(dirPath)
        
        if "version" in local:
            verPath = dirPath + "version/" + self.fn + "/"
            if os.path.isdir(verPath):
                verList = os.listdir(verPath)
                for ver in verList:
                    if re.search(pathDict['fileName'],ver):
                        tmpList.append(ver)
                nV = len(tmpList)  + 1
                ver = "v%03d" %nV
                return ver
            else:
                return "v001"
        else:
            return "v001"

    def load_config(self):
        '''
        Load config which is a dictionary and applying setting.
        '''
        if os.path.exists(self.config_path):
            print 'Loading config file from:', self.config_path
            config_file = open( '%s' % self.config_path, 'r')
            list = config_file.readlines()
            config_file.close()

            config = {}
            for option in list:
                key, value = option.split('=')
                config[key] = value.strip()

            try:
                index = [i for i in range(self.User_CB.count()) if self.User_CB.itemText(i) == config.get('USER')][0]
                self.User_CB.setCurrentIndex(index)
            except:
                os.remove(self.config_path)

    def save_config(self):
        '''
        Save setting to the config file as a dictionary.
        '''
        user = self.User_CB.currentText()
        
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
            
        config = open( '%s' % self.config_path, 'w')
        config.write('USER=%s\n' % (user))
        config.close()

        self.load_config()
        return self.config_path


def dsVersionUp():
    global dsVerWindow
    try:
        dsVerWindow.close()
    except:
        pass
    dsVerWindow = Window()
    dsVerWindow.show()