import sys, sip, os, shutil
from PyQt4 import QtGui, QtCore, uic

def getMayaWindow():
    'Get the maya main window as a QMainWindow instance'
    ptr = mui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(ptr), QtCore.QObject)

import maya.cmds as cmds
import maya.OpenMaya as api
import maya.OpenMayaUI as mui
import sgTools


if sys.platform == "linux2":
    uiFile = '/dsGlobal/dsCore/shotgun/dsQuickLog.ui'
else:
    uiFile = '//vfx-data-server/dsGLobal/dsCore/shotgun/dsQuickLog.ui'

form_class, base_class = uic.loadUiType(uiFile)
class Window(base_class, form_class):
    def __init__(self, parent=getMayaWindow()):
        super(base_class, self).__init__(parent)
        self.setupUi(self)

        if sys.platform == "linux2":
            self.home = os.getenv("HOME")
            self.config_dir = '%s/.quickLog' % (self.home)
            self.config_path = '%s/config.ini' % (self.config_dir)

        elif sys.platform == 'win32':
            self.dailies = "//vfx-data-server/dsPipe/_DAILIES"
            self.home = 'C:%s' % os.getenv("HOMEPATH")
            self.config_dir = '%s/.quickLog' % (self.home)
            self.config_path = '%s/config.ini' % (self.config_dir)
        
        #self.task = {"Fall_2013_Thailand_Fixes":18089,"Fall_2013_Dailies":18560}
        self.task = {"Fall_2013_Thailand_Fixes":18089}
        self.init_user()
        self.load_config()
        self.init_task()

        self.screenGrab()
        
        self.user_CB.currentIndexChanged.connect(self.save_config)
        self.timeLog_LE.returnPressed.connect(self.doIT)
        self.screenShot_B.clicked.connect(self.screenGrab)


    def doIT(self):
        usrName = self.user_CB.currentText()
        task = self.task_CB.currentText()
        description = str(self.description_LE.text())
        timeLog = str(self.timeLog_LE.text())
        
        usr = sgTools.sgGetUserObj(usrName)
        
        projObj = sgTools.sgGetProject("TimeSheets")
        taskID = self.task[str(task)]
        taskObj = sgTools.sgGetTask(taskID)

        data = {'project':projObj,'user':usr,'entity':taskObj,'description':str(description),'duration':int(timeLog)}
        result = sgTools.sgCreateObj('TimeLog',data)

        timeLogID = result['id']
        newName = str(timeLogID) + "_" + usrName + ".jpg"
        
        shutil.copy(self.thumbPath,self.dailies + "/" + task + "/" + newName)

        self.close()

    def screenGrab(self):
        
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
        self.thumbPath = self.config_dir + "\\"+"sgrab.jpg"

        view = mui.M3dView.active3dView()
        image = api.MImage()
        view.readColorBuffer(image, True)
        
        image.writeToFile(self.thumbPath, 'jpg')
        self.updateThumb()
        
        
    def updateThumb(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(self.thumbPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.screenShot_B.setIcon(icon)

    def init_user(self):

        self.user_CB.clear()
        self.userDict = {}
        self.group = {'type': 'Group', 'id': 5}
        self.myPeople = sgTools.sgGetPeople()
        for user in sorted(self.myPeople):
            if str(user['sg_status_list']) == "act":
                userName = str(user['name'])
                self.user_CB.addItem(userName)
                self.userDict['id'] = user['id']
                self.userDict['sg_initials'] = user['sg_initials']
                
    def init_task(self):
        self.task_CB.clear()

        for task in self.task:
            print task
            self.task_CB.addItem(task)
        
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
                index = [i for i in range(self.user_CB.count()) if self.user_CB.itemText(i) == config.get('USER')][0]
                self.user_CB.setCurrentIndex(index)
            except:
                os.remove(self.config_path)

    def save_config(self):
        '''
        Save setting to the config file as a dictionary.
        '''
        user = self.user_CB.currentText()
        if not os.path.exists(self.config_dir):
            os.mkdir(self.config_dir)
            
        config = open( '%s' % self.config_path, 'w')
        config.write('USER=%s\n' % (user))
        config.close()

        return self.config_path
def dsQuickLog():
    global myWindow
    myWindow = Window()
    myWindow.show()