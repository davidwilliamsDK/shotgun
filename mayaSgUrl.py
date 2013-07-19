print 'v1.0.3'
### Still TO DO:
### versionUP
### restore
### Generate and update maya thumbnail and status update
### sort bye status... Future
import sys,sip,re,os,shutil,subprocess,pprint

if sys.platform == "linux2":
    uiFile = '/mounts/vfxstorage/dsDev/dsCore/shotgun/sgTasks.ui'
    sys.path.append('/mounts/vfxstorage/dsDev/dsCore/maya/dsCommon/')
    sys.path.append('/mounts/vfxstorage/dsDev/globalResources/Shotgun')
else:
    uiFile = '//vfx-data-server/dsDev/dsCore/shotgun/sgTasks.ui'
    sys.path.append('//vfx-data-server/dsDev/dsCore/maya/dsCommon/')
    sys.path.append('//vfx-data-server/dsGlobal/globalResources/Shotgun')

from shotgun_api3 import Shotgun
from PyQt4 import QtGui, QtCore, uic
import dsSgUtil;reload(dsSgUtil)
import dsProjectUtil;reload(dsProjectUtil)
import sgTools;reload(sgTools)

try:
    import maya.cmds as cmds
    import maya.OpenMaya as api
    import maya.OpenMayaUI as apiUI
except:
    pass

def getMayaWindow():
    'Get the maya main window as a QMainWindow instance'
    ptr = apiUI.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

form_class, base_class = uic.loadUiType(uiFile)
class Window(base_class, form_class):  
    def __init__(self, parent=getMayaWindow()):
        super(base_class, self).__init__(parent)
        self.setupUi(self)
        self.setObjectName('ShotTaskViewer')
        self.setWindowTitle("Shot TaskViewer")
        
        '''A custom window with a demo set of ui widgets'''
        self.sg = sgTools.getSG()
        
        if sys.platform == "linux2":
            self.dsRelativePath = "/dsPipe/"
            self.presetMaya = "/globalMaya/Presets/defaultMaya/default.ma"
            self.home = os.getenv("HOME")
            self.config_dir = '%s/.mayaTV' % (self.home)
            self.config_path = '%s/mayaTV.ini' % (self.config_dir)
        else:
            self.dsRelativePath = "//vfx-data-server/dsPipe/"
            self.presetMaya = "//vfx-data-server/dsGlobal/globalMaya/Presets/defaultMaya/default.ma"
            self.home = 'C:%s' % os.getenv("HOMEPATH")
            self.config_dir = '%s/.mayaTV' % (self.home)
            self.config_dir = self.config_dir.replace("/","\\")
            self.config_path = '%s/mayaTV.ini' % (self.config_dir)
            self.config_path = self.config_path.replace("/","\\")
            
        
        self.mayaSteps = ["anim","effect","light"]
        self.nukeSteps = ["comp","roto"]
        self.publishSteps = ["publish2d","publish3d"]
        
        if not os.path.exists(self.config_path):
            self.sgGetUser()
            self.sgGetUserProjects()
        else:
            config = self.load_config()
            self.fillOut(config['USER'],config['PROJECT'])
            
        self.user_CB.currentIndexChanged.connect(self.sgGetUserProjects)
        #self.task_LW.itemClicked.connect(self.updateInfo)
        self.task_LW.itemActivated.connect(self.updateInfo)
        
        menu = QtGui.QMenu(self)
        self.actionOpen = menu.addAction("Open", self.launchMaya)
        self.actionVersionUp = menu.addAction("VersionUp", self.versionUp)
        self.actionRestore = menu.addAction("restore", self.restore)
        self.statusMenu = QtGui.QMenu("status")
        self.actionStatusRev = menu.addAction("rev",self.updateStatus)
        self.actionStatusIp = menu.addAction("ip",self.updateStatus)
        
        self.connect(self.task_LW,QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"), self.popUpTask)
        self.connect(self.version_LW,QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"), self.popUpVersion) 
        
        self.refresh_B.clicked.connect(self.UpdateContent)
        self.icon_PB.clicked.connect(self.createThumb)

    def popUpTask(self,pos):
        self.popMenu = QtGui.QMenu( self )
        self.popMenu.addAction( self.actionOpen )
        #self.popMenu.addAction( self.actionVersionUp )
        self.popMenu.addMenu(self.statusMenu)
        self.statusMenu.addAction(self.actionStatusIp)
        self.statusMenu.addAction(self.actionStatusRev)
        self.popMenu.exec_( self.task_LW.mapToGlobal(pos) )
    
    def popUpVersion(self,pos):
        self.popMenu = QtGui.QMenu( self )
        self.popMenu.addAction( self.actionOpen )
        self.popMenu.addAction( self.actionVersionUp )
        self.popMenu.addMenu(self.statusMenu)
        self.statusMenu.addAction(self.actionStatusIp)
        self.statusMenu.addAction(self.actionStatusRev)
        self.popMenu.addSeparator()
        self.popMenu.addAction( self.actionRestore )
        self.popMenu.exec_( self.version_LW.mapToGlobal(pos) )

    def versionUp(self):
        print "versionUp"
        path = self.taskWidgetToPath()
        scene = self.testScene()
        sgTools.actionVersionUp(path,scene)
        
    def restore(self):
        print "Restore"

    def createThumb(self):
        if self.testScene():
            print "createThumb"
            filePath = str(self.taskWidgetToPath())
            val = self.version_LW.count()
            verObj = self.version_LW.item(int(val)-1)
            version = verObj.text()
            thumbPath = sgTools.sgThumbnail(filePath,version,True)
            icon = QtGui.QIcon(thumbPath)
            self.icon_PB.setText("")
            self.icon_PB.setIcon(icon)
            verObj = self.verInfo[-1]
            sgTools.sgThumbUpdate("Version",verObj,thumbPath)
            return thumbPath

    def thumbNailUpdate(self):  
        filePath = str(self.taskWidgetToPath())
        val = self.version_LW.count()
        verObj = self.version_LW.item(int(val)-1)
        version = verObj.text()
        thumbPath = sgTools.sgThumbnail(filePath,version,False)
        return thumbPath

    def testScene(self):
        guiFilePath = str(self.taskWidgetToPath())
        filePath = cmds.file(q=True,sn=True)
        if str(guiFilePath) != str(filePath):
            #self.icon_PB.setEnabled(False)
            return False
        else:
            #self.icon_PB.setEnabled(True)
            return True
        
    def updateInfo(self):
        ##Fill out info side of UI
        self.testScene()
        self.version_LW.clear()
        self.version_LW.setEnabled(True)
        self.icon_PB.setEnabled(True)
        item = self.task_LW.currentItem()
        value = item.text(0)
        self.nameToTaskEntity(value)

        for obj in self.verInfo:
            verName = str(obj['code'])
            self.version_LW.addItem(str(verName))
            
        if self.task_LW.currentItem() != None:
            item = self.task_LW.currentItem()
            fileName = item.text(0)
            projName = item.text(1)
            epiName = item.text(3)
            taskName = item.text(4)
            status = item.text(7)
        
        if status == "rdy":
            self.statusText_TE.setText("Ready to Start")
        if status == "ip":
            self.statusText_TE.setText("In Progress")
        if status == "rev":
            self.statusText_TE.setText("Pending Review")
        if status == "fin":
            self.statusText_TE.setText("Final")
            
        thumbPath = self.thumbNailUpdate()
        if os.path.isfile(thumbPath):
            icon = QtGui.QIcon(thumbPath)
            self.icon_PB.setText("")
            self.icon_PB.setIcon(icon)
        else:
            self.icon_PB.setText("thumb")
        
    def updateStatus(self):
        obj = self.sender()
        statusName = obj.iconText()
        "push status update too sg.."
        if self.task_LW.currentItem() != None:
            item = self.task_LW.currentItem()
            fileName = item.text(0)
            projName = item.text(1)
            epiName = item.text(3)
            taskName = item.text(4)
        item = self.task_LW.currentItem()
        value = item.text(0)
        self.nameToTaskEntity(value)
        verID = self.verInfo[-1]['id']
        print statusName
        self.sg.update("Version",verID, {"sg_status_list":str(statusName)})

        bColor = self.getColor(statusName)
        self.UpdateContent()

    def UpdateContent(self):
        #self.fillOut(config['USER'],config['PROJECT'])
        dsUser = self.user_CB.currentText()
        project = self.project_CB.currentText()
        self.fillOut(dsUser,project)

    def fillOut(self,dsUser,project):
        self.save_config()
        self.task_LW.clear()
        self.epiList = []
        self.badList = ("clsd","hld","cmpt","omt")

        filter = [['task_assignees','is',self.myUser],['project.Project.name','is',str(project)],['project.Project.sg_status','is',str("Active")]]
        self.allTasks = self.sg.find("Task",filter,['entity.Shot.sg_scene.Scene','entity'])

        for task in self.allTasks:
            if not task['entity'] == None:
                if str(task['entity']['type']) == "Shot": 
                    self.epiName = task['entity.Shot.sg_scene.Scene']['name']
                    if self.epiName not in self.epiList:        
                        self.epiList.append(self.epiName)
        if self.epiList != []:
            self.addEpisodalContent()
        else:
            print "no shot tasks handed out to you..."
        
    def getColor(self, status):
        if str(status) == "rdy": return QtGui.QColor(0,150,200,255)
        if str(status) == "ip": return QtGui.QColor(0,100,0,255)
        if str(status) == "rev": return QtGui.QColor(50,100,200,255)
        if str(status) == "fin": return QtGui.QColor(50,50,50,255)

    def addEpisodalContent(self):
        ## add episode info from shotgun to task view
        for epi in self.epiList:
            filter = [['code','is',epi]]
            self.epiObj = self.sg.find_one("Scene",filter,['code','project','sg_status_list'])
            if str(self.epiObj['sg_status_list']) not in self.badList:
                temp = QtGui.QTreeWidgetItem()
                temp.setText(0,str(epi))
                self.task_LW.addTopLevelItem(temp)
                filter = [['task_assignees','is',self.myUser],['entity.Shot.sg_scene.Scene.code','is',str(epi)]]
                self.userTasks = self.sg.find("Task",filter,['content','entity','step','sg_status_list','id','sg_software'])
                for task in self.userTasks:
                    pipeStep = str(task['step']['name'])
                    if pipeStep in self.mayaSteps:
                        if str(task['content']) != "published3D":
                            shot = task['entity']
                            content = task['content']
                            filter = [['sg_task.Task.content','is',content],['entity','is',shot]]
                            dictFromSG = self.sg.find('Version',filter,['code','sg_path_to_frames','sg_status_list','sg_task','sg_file_name'] )
                            tmp = QtGui.QTreeWidgetItem()
                            if dictFromSG != []:
                                tmp.setText(0,str(dictFromSG[-1]['sg_file_name'])) 
                                tmp.setText(1,str(dictFromSG[-1]['code'])) 
                                tmp.setText(2,str(self.epiObj['project']['name']))
                                tmp.setText(3,str(self.epiObj['code']))
                                tmp.setText(4,str(task['content']))
                                tmp.setText(5,str(shot['name']))
                                tmp.setText(6,"epi")
                                tmp.setText(7,str(dictFromSG[-1]['sg_status_list']))
                                status = dictFromSG[-1]['sg_status_list']
				if status != None:
				  bColor = self.getColor(status)
				  tmp.setBackgroundColor(0,bColor)
                            else:
                                shotName = task['entity']['name']
                                shotID = task['entity']['id']
                                taskName = task['content']
                                pipeStep = task['step']['name']
                                filter = [['shots.Shot.id','is',shotID]]
                                seqObj = self.sg.find_one("Sequence",filter,['code','sg_sequence_type'])
                                seq = seqObj['code']
                                WF = seqObj['sg_sequence_type']
                                episode = self.epiObj['code']
                                epiShort = episode[:-7]
                                project = self.epiObj['project']['name']
                                user = self.myUser["sg_initials"]
                                if WF == "Sequence":
                                    file = seq + "_" + taskName + ".ma"
                                    pathToFile = project + "/film/" + episode + "/" + seq + "/" + "3D/" + pipeStep + "/"
                                if WF == "Shot":
                                    file = seq + "_" + shotName + "_" + taskName + ".ma"
                                    pathToFile = project + "/film/" + episode + "/" + seq +"/" + shotName + "/3D/" + pipeStep + "/"            
                                versionName = dsSgUtil.sgCreateEpisodeVersionOne(taskName,pipeStep,self.dsUser,shotName,seq,episode,project,WF,file,self.sg)
                                dsSgUtil.sgCreateMayaNukeVersion(versionName,file,pathToFile,self.sg)   
                                tmp.setText(0,str(file)) 
                                tmp.setText(1,str("v001")) 
                                temp.setText(2,str(project))
                                temp.setText(3,str(episode))
                                temp.setText(4,str(taskName))
                                temp.setText(5,str(shot['name']))
                                temp.setText(6,"epi")
                                temp.setText(7,"na")
				if status != None:
				  bColor = self.getColor(status)
				  tmp.setBackgroundColor(0,bColor)
                            temp.setExpanded(True)
                            temp.addChild(tmp)
                            self.task_LW.addTopLevelItem(temp)
        
    def createPath(self,fileName,dsProject,dsEpisode,dsTask,type):
        ## create path from what is selected in task view
        if type == "epi":
            epiName = dsSgUtil.sgTestEpi(dsProject,dsEpisode,self.sg)
            filter = [['sg_task.Task.content','is',str(dsTask)],['entity.Shot.sg_scene.Scene.code','is',str(epiName)]]
            self.userTasks = self.sg.find_one("Version",filter,['sg_path'])
            return str(self.dsRelativePath + self.userTasks['sg_path'])

    def nameToTaskEntity(self,value):
        ## find Task obj from name selected in task view
        item = self.task_LW.currentItem()
        fileName = item.text(0)
        projName = item.text(2)
        epiName = item.text(3)
        taskName = item.text(4)
        objName = item.text(5)
        type = item.text(6)
        if type == "epi":
            filter = [['task_assignees','is',self.myUser],['project.Project.name','is',str(projName)],['entity.Shot.code','is',str(objName)],['content','is',str(taskName)]]
            taskInfo = self.sg.find_one("Task",filter,['entity','sg_status_list','id'])
            self.verInfo = self.taskObjToVersion(taskInfo)

    def taskObjToVersion(self,taskObj):
        ##Get versions of what is selected from task view
        filter = [['sg_task.Task.id','is',taskObj['id']]]
        versionInfo = self.sg.find("Version",filter,['code','entity','sg_task','sg_file_name','description','sg_status_list','sg_path','id'])
        return(versionInfo)

    def taskWidgetToPath(self):
        if self.task_LW.currentItem() != None:
            item = self.task_LW.currentItem()
            fileName = item.text(0)
            projName = item.text(1)
            epiName = item.text(3)
            taskName = item.text(4)
            type = item.text(6)
        if re.search(".ma",fileName):
            path = self.createPath(fileName,projName,epiName,taskName,type)
            path = str(path) + str(fileName)
            return path
        else:
            return None
            
    def launchMaya(self):
        ## open file if not created create default maya scene
        path = str(self.taskWidgetToPath())
        if not os.path.isfile(path):
            shutil.copy(self.presetMaya,path)
        if cmds.file(q=True, anyModified=True) == True:
            self.saveConfirmDialog(path)
        else:
            cmds.file(path,o=True,f=True)
        self.updateInfo()

    def saveConfirmDialog(self, item):
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Want to to Save, before closing?", QtGui.QMessageBox.Yes |
            QtGui.QMessageBox.No| QtGui.QMessageBox.Cancel, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            cmds.file( save=True, type='mayaAscii' )
            cmds.file(item,o=True,f=True)
            self.statusbar.showMessage("File saved - File opened")
        elif reply == QtGui.QMessageBox.No:
            cmds.file(item, o=True, f=True)
            self.statusbar.showMessage("File opened")
        else:
            self.statusbar.showMessage("Open Scene Cancelled")
            
    def sgGetUser(self):
        ##Test and return if Episode exists
        self.user_CB.clear()
        self.userDict = {}
        self.userProject = {}
        self.group = {'type': 'Group', 'id': 5}
        self.myPeople = self.sg.find("HumanUser", [["groups","is",self.group],['sg_status_list','is','act']], ["name","projects"]) 
        for user in self.myPeople:
            userName = str(user['name'])
            self.user_CB.addItem(userName)
            self.userDict[userName] = user['id']
            self.userProject[userName] = user['projects']

    def sgGetUserProjects(self):
        ## Get users projects added from shotgun           
        self.project_CB.clear() 
        self.projList = []
        self.dsUser = self.user_CB.currentText()
        self.myUser = sgTools.sgGetUser(self.dsUser)
        filter = [['task_assignees','is',self.myUser],['project.Project.sg_status','is',"Active"]]
        projList = self.sg.find("Task",filter,['project'])
        for task in projList:
            if task['project']['name'] not in self.projList:
                self.projList.append(task['project']['name'])
        for proj in self.projList:
            self.project_CB.addItem(str(proj))
            
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
                option.replace("\n","")
                key,value = option.split("=")
                config[key] = value.strip()
                
            self.sgGetUser()
            try:
                index = [i for i in range(self.user_CB.count()) if self.user_CB.itemText(i) == config.get('USER')][0]
                self.user_CB.setCurrentIndex(index)
            except:
                self.user_CB.setCurrentIndex(1)
            self.sgGetUserProjects()
            try:
                index = [i for i in range(self.project_CB.count()) if self.project_CB.itemText(i) == config.get('PROJECT')][0]
                self.project_CB.setCurrentIndex(index)
            except:
                self.project_CB.setCurrentIndex(1)
            
            return config
            
    def save_config(self):
        '''
        Save setting to the config file as a dictionary.
        '''
        user = self.user_CB.currentText()
        project = self.project_CB.currentText()
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        config = open( '%s' % self.config_path, 'w')
        config.write('USER=%s\n' % (user))
        config.write('PROJECT=%s\n' % (project))
        config.close()
        return self.config_path    

def dsShotGun():
    global myWindow
    myWindow = Window()
    myWindow.show()