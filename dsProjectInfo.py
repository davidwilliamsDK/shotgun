import sys, os, re, shutil, imp

if sys.platform == "linux2":
    sys.path.append('/mounts/vfxstorage/dsDev/dsCore/shotgun/')
else:
    sys.path.append('//vfx-data-server/dsDev/dsCore/shotgun/')

import sgTools;reload(sgTools)

def sgGetData(project):
    print project
    sg = sgTools.getSG()  
    myProj = sgTools.sgGetProject(sg,project,['sg_budget','sg_balance','sg_cost'])
    sgGenerateBalance(sg,myProj)

def sgGenerateBalance(sg,myProj):
    print "freelancer cost = " + str(myProj['sg_cost'])
    print "budget = " + str(myProj['sg_budget'])
    print "balance = " + str(myProj['sg_balance'])
    val = sgGetTimeLogged(sg, project)
    print "time logged = " + "%.2f" %val[0]
    print "time logged as money = " + "%.2f" %val[1]
    newVal = "%.2f" %val[1]
    newBalance = myProj['sg_budget'] - myProj['sg_cost'] - float(newVal)
    sg.update("Project",myProj['id'], {"sg_balance":float(newBalance)})

def sgGetTimeLogged(sg, project):
    
    x = 0
    y = 0
    projTLogs = sg.find('TimeLog',[['project.Project.name','is',project]],['duration','user','content'])
    for log in projTLogs:
        userName = log['user']['name']
        tLogged = float(log['duration']) / 60
        userObj = sgTools.sgGetUserObj(userName,['sg_rate'])
        rateY = sgGetArtistHourly(userObj['sg_rate'],tLogged) 
        y = y + rateY
        x = x + tLogged
    dict=[x,y]
    return dict

def sgGetArtistHourly(rate,y):
    return rate * y

sg = sgTools.getSG()  
projList = sg.find('Project',[['sg_status','is','Active']],['name'])

for proj in projList:
    project = proj['name']
    sgGetData(project)    


