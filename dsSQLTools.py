import sqlite3 as lite
import os,sys

def getSG():
    sys.path.append('//vfx-data-server/dsGlobal/globalResources/Shotgun')
    from shotgun_api3 import Shotgun
    server = "https://duckling.shotgunstudio.com"
    scriptName = "assetOpenToShotgun"
    scriptId = "e932e9c2864c9bcdc3f3ddf8b801cc3d565bf51f"
    sg = Shotgun(server, scriptName, scriptId)
    return sg

def createDB(dbName):
    con = lite.connect(dbName + '.db')
    c= con.cursor()
    con.commit()
    con.close()

def createUserTable(dbName,tableName):
    con = lite.connect(dbName + '.db')
    cur= con.cursor()
    cur.execute("DROP TABLE IF EXISTS %s"%(tableName))
    cur.execute("CREATE TABLE %s(Id INT, Name TEXT, Initials TEXT,Status TEXT)" % tableName)
    con.commit()
    con.close()

def createFilmTable(dbName,tableName):
    con = lite.connect(dbName + '.db')
    cur= con.cursor()
    cur.execute("DROP TABLE IF EXISTS %s"%(tableName))
    cur.execute("CREATE TABLE %s(Id INT, Name TEXT,Status TEXT)" % tableName)
    con.commit()
    con.close()

def createNoteTable(dbName,tableName):
    con = lite.connect(dbName + '.db')
    cur= con.cursor()
    cur.execute("DROP TABLE IF EXISTS %s"%(tableName))
    cur.execute("CREATE TABLE %s(Id INT,TYPE TEXT,Status TEXT,Content TEXT, Attach TEXT, User TEXT)" % tableName)
    con.commit()
    con.close()

def addUser(dbName,tableName,id,name,initals,status):
    con = lite.connect(dbName + '.db')
    cur= con.cursor()
    cur.execute("INSERT INTO %s VALUES(%s,'%s','%s','%s')" % (tableName,id,name,initals,status))
    con.commit()
    con.close()
    
def addFilm(dbName,tableName,id,name,status):
    con = lite.connect(dbName + '.db')
    cur= con.cursor()
    cur.execute("INSERT INTO %s VALUES(%s,'%s','%s')" % (tableName,id,name,status))
    con.commit()
    con.close()

def getValueDB(dbName,tableName,colSearch,valSearch=None): 

    con = lite.connect(dbName + '.db')
    cur = con.cursor()
    if valSearch != None:
        cur.execute('SELECT * FROM %s WHERE %s="%s"' % (tableName,colSearch,valSearch))
    else:
        cur.execute('SELECT * FROM %s' % (tableName))
    rows = cur.fetchall()
    con.commit()
    con.close()
    return rows
    
def deleteTable(dbName,tableName):
    con = lite.connect(dbName + '.db')
    cur= con.cursor()
    cur.execute("DROP TABLE IF EXISTS %s"%(tableName))
    con.commit()
    con.close()
    
def modifyDB(dbName,tableName,colChange,valChange,colSearch,valSearch):
    con = lite.connect(dbName + '.db')
    cur = con.cursor()
    cur.execute('UPDATE %s set %s="%s" WHERE %s="%s"'%(tableName,colChange,valChange,colSearch,valSearch))
    con.commit()
    con.close()
        
def buildPeopleDB(dbName,tableName):
    print "Removing "+dbName+".db"
    if os.path.isfile(dbName+".db"):
        os.remove(dbName+".db")
    deleteTable(dbName,tableName)
    createDB(dbName)
    createUserTable(dbName,tableName)
    
    sg = getSG()
    peopleDict = sg.find("HumanUser", [["groups.Group.code","is","ducklings"]], ["name","projects","sg_initials","sg_status_list"])
    for peeps in peopleDict:
        id = peeps['id']
        Name = peeps['name']
        initials = peeps['sg_initials']
        status = peeps['sg_status_list']
        addUser(dbName,tableName,id,Name,initials,status)
    print "Created "+dbName+".db"
    
def buildProjectDB(dbName,tableName):
    print "Removing "+dbName+".db"
    if os.path.isfile(dbName+".db"):
        os.remove(dbName+".db")
    deleteTable(dbName,tableName)
    createDB(dbName)
    createFilmTable(dbName,tableName)
    
    sg = getSG()
    projDict = sg.find("Project", [], ['name','sg_status','id'])
    for proj in projDict:
        Name = proj['name']
        status = proj['sg_status']
        id = proj['id']
        addFilm(dbName,tableName,id,Name,status)
    print "Created "+dbName+".db"
    
def buildFullProjectDB(projName,dbName,tableName):
    print "Removing "+dbName+".db"
    if os.path.isfile(dbName+".db"):
        os.remove(dbName+".db")
    deleteTable(dbName,tableName)
    createDB(dbName)
    createFilmTable(dbName,tableName)
    
    tableList = ["EPISODE","SEQUENCE","SHOT"]
    for table in tableList:
        tableName = table
        createFilmTable(dbName,tableName)

    sg = getSG()
    projObj = sg.find_one("Project", [["name", "is", str(projName)]], ['sg_status','id'])
    epiObj = sg.find("Scene",[['project.Project.name','is', str(projName)]], ['code','sg_status_list','id'])
    
    for epi in epiObj:
        id = int(epi['id'])
        Name = epi['code']
        status = epi['sg_status_list']
        tableName = "EPISODE"
        addFilm(dbName,tableName,id,Name,status)     
        
        epiName = epi['code']
        seqObj = sg.find("Sequence",[['project.Project.name','is', str(projName)],['scene_sg_sequence_1_scenes.Scene.code','is', str(epiName)]],['code','sg_status_list','id'])
        for seq in seqObj:
            id = int(seq['id'])
            Name = "%s_%s " % (epiName,seq['code'])
            status = seq['sg_status_list']
            tableName = "SEQUENCE"
            addFilm(dbName,tableName,id,Name,status)            
            
            seqName = seq['code']
            shotObj = sg.find("Shot", [['project.Project.name','is', str(projName)],['sg_sequence.Sequence.code','is', str(seqName)],['sg_scene.Scene.code','is', str(epiName)]],['code','sg_status_list','id'])
            for shot in shotObj:
                id = int(shot['id'])
                Name = " %s_%s_%s" % (epiName,seqName,shot['code'])
                status = shot['sg_status_list']
                tableName = "SHOT"
                addFilm(dbName,tableName,id,Name,status)
    print "Created "+dbName+".db"

def buildAllProjects():
    projList = []
    tmpList = os.listdir("P:/")
    for tmp in tmpList:
        tmpPath = "P:/"+tmp+"/.local"
        if os.path.isdir("P:/"+tmp+"/.local"):
            projList.append(tmpPath)
    
    for proj in projList:
        projName = proj.split("/")[1]
        dbName = proj + "/"+projName

        tableName = projName
        buildFullProjectDB(projName,dbName,str(tableName))
        
def buildGlobalUsers():
    dbName = "//vfx-data-server/dsGlobal/globalusers"
    tableName = "Users"   
    buildPeopleDB(dbName,tableName)

def buildGlobalProjects():
    dbName = "//vfx-data-server/dsGlobal/globalProjects"
    tableName = "Projects"   
    buildProjectDB(dbName,tableName)

def getNote(projName):
    sg = getSG()
    noteObj = sg.find("Note", [['project.Project.name','is', str(projName)]], ['replies','subject','content','attachments','user','note_links','sg_status_list','id'])

    for note in noteObj:
        try:
            print note['subject']
            print note['id']
            print note['note_links'][0]['name']
            print note['sg_status_list']
            print note['content']
            print note['attachments']
            print note['user']['name']
            
            print "############REPLY###############"
            replyObj = note['replies']
            for reply in replyObj:
                #print reply
                print reply['id']
                print reply['type']
                print reply['name']
        except:
            pass
        
#getNote("Lego_Movie")

#modifyDB(dbName,"SHOT","Status","rdy","Id",2778)

#buildGlobalProjects()
#print getValueDB("U:/globalProjects","Projects","Status",'Active')

#dbName = "//vfx-data-server/dsPipe/Lego_Ninjago/.local/Lego_Ninjago"

#if getValueDB(dbName,"SHOT","Id",2923) == []:
#    buildFullProjectDB("Lego_Ninjago",dbName,"Lego_Ninjago")
#else:
#    modifyDB(dbName,"SHOT","Status","ip","Id","2923")

#tableList = ["EPISODE","SEQUENCE","SHOT"]
#for table in tableList:
    #tableName = table
    #list = getValueDB(dbName,tableName,"Status","ip")
    #for l in list:
        #print l
    #list = getValueDB(dbName,"SHOT","Status")
    #f#or l in list:
        #print l

