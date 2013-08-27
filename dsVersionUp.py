
import sys, sip, re, os, shutil, subprocess, stat
from PyQt4 import QtGui, QtCore, uic
import sgTools
import dsCommon.dsOsUtil as dsOsUtil
reload(dsOsUtil)

if dsOsUtil.mayaRunning() == True:
    import maya.cmds as cmds
    import maya.OpenMayaUI as mui
    
def getMayaWindow():
    'Get the maya main window as a QMainWindow instance'
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

import dsCheck
reload(dsCheck)
dsCheck.dsMDCheck()

if sys.platform == "linux2":
    uiFile = '/dsGlobal/dsCore/shotgun/sgVersionUp.ui'
else:
    uiFile = '//vfx-data-server/dsGlobal/dsCore/shotgun/sgVersionUp.ui'
  
form_class, base_class = uic.loadUiType(uiFile)
class Window(base_class, form_class):

    def __init__(self, parent=None):
        base_class.__init__(self, parent)
        self.setupUi(self)
        self.setUp()
        
    def setUp(self):
        
        self.filePath = cmds.file(q=True,sn=True)
        
        if sys.platform == "linux2":
            self.filePath = self.filePath.replace("P:","//vfx-data-server/dsPipe")
            self.home = os.getenv("HOME")
            self.config_dir = '%s/.versionUp' % (self.home)
            self.config_path = '%s/config.ini' % (self.config_dir)

        elif sys.platform == 'win32':
            self.home = 'C:%s' % os.getenv("HOMEPATH")
            self.config_dir = '%s/.versionUp' % (self.home)
            self.config_dir = self.config_dir.replace("/","\\")
            self.config_path = '%s/config.ini' % (self.config_dir)
            self.config_path = self.config_path.replace("/","\\")
        
        self.GetUser()
        self.load_config()
        
        sgTask = cmds.getAttr("dsMetaData.sgTask")
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
        
        """ actions """
        
        self.User_CB.currentIndexChanged.connect(self.save_config)
        self.description_LE.returnPressed.connect(self.doIT)
        #self.description_LE.returnPressed.connect(self.sgCreateShotVersion)

    def GetUser(self):
        ##Test and return if Episode exists
        self.User_CB.clear()
        self.userDict = {}
        self.group = {'type': 'Group', 'id': 5}
        self.myPeople = sgTools.sgGetPeople()
        for user in sorted(self.myPeople):
            if str(user['sg_status_list']) == "act":
                userName = str(user['name'])
                self.User_CB.addItem(userName)
                self.userDict['id'] = user['id']
                self.userDict['sg_initials'] = user['sg_initials']
        
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
                
            self.connect2SG(sName)
            
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

    def versionUp(self,filePath,version,val):
        if not re.search("/version/",filePath):
            filePathList = filePath.split("/")
            versionPath = filePath.replace(filePathList[-1],"version")
            versionPath = versionPath + "/" + filePathList[-1]
            if not os.path.isdir(versionPath):
                os.makedirs(versionPath)
            self.version_file_name = filePathList[-1].replace(".ma","_" + version + "_" + self.duckInitials +  ".ma")
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
            dirPath = filePath.replace(self.pathDict['fileName'] + '.ma',"")
            self.fn = self.pathDict['fileName'] + '.ma'
        if re.search(".mb",filePath):
            dirPath = filePath.replace(self.pathDict['fileName'] + '.mb',"")
            self.fn = self.pathDict['fileName'] + '.mb'
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
    global myWindow
    myWindow = Window()
    myWindow.show()
