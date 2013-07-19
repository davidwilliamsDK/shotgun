# -*- coding: utf-8 -*-
"""
For detailed information please see
http://shotgunsoftware.github.com/shotgunEvents/api.html
"""
import logging
import pprint
import sg_utils
import sys, re, os
import platform
reload(sg_utils) 

if sys.platform == "linux2":
	sys.path.append('/dsGlobal/dsCore/dsCommon')
else:
	sys.path.append('//vfx-data-server/dsGlobal/dsCore/maya/dsCommon')
	
import dsFolderStruct as dsFS
reload(dsFS)

### Setting up local shotgun hook
apiKey = 'f821858c0b4e921bb8cc587002829d56ff2e2c5b'
scriptName = "eventTrigger_makeProjectFolders"
url = "https://duckling.shotgunstudio.com"

def registerCallbacks(reg):
	"""Register all necessary or appropriate callbacks for this plugin."""
	print "do nothing"
	# Specify who should recieve email notifications when they are sent out.
	#
	#reg.setEmails('me@mydomain.com')

	# Use a preconfigured logging.Logger object to report info to log file or
	# email. By default error and critical messages will be reported via email
	# and logged to file, all other levels are logged to file.
	#
	#reg.logger.debug('Loading logArgs plugin.')

	# Register a callback into the event processing system.
	#
	# Arguments:
	# - Shotgun script name
	# - Shotgun script key
	# - Callable
	# - Argument to pass through to the callable
	# - A filter to match events to so the callable is only invoked when
	#   appropriate
	#

	#reg.registerCallback(scriptName, apiKey, callback_createProjectFolder, {'Shotgun_Project_Change': ['sg_status']}, None)
	#reg.registerCallback( scriptName, apiKey, callback_episodeCreation, {'Shotgun_Scene_New': ['*']}, None)
	#reg.registerCallback( scriptName, apiKey, callback_seqCreation, {'Shotgun_Sequence_New': ['*']}, None)
	#reg.registerCallback( scriptName, apiKey, callback_shotCreation, {'Shotgun_Shot_New': ['*']}, None)

	#reg.registerCallback( scriptName, apiKey, callback_episodeUpdate, {'Shotgun_Scene_Change': ['sg_update_folder_structure']}, None)
	#reg.registerCallback( scriptName, apiKey, callback_seqUpdate, {'Shotgun_Sequence_Change': ['sg_update_folder_structure']}, None)
	#reg.registerCallback( scriptName, apiKey, callback_shotUpdate, {'Shotgun_Shot_Change': ['sg_update_folder_structure']}, None)

	filter_createProjectFolder = {'Shotgun_Scene_Change': ['sg_status']}
	reg.registerCallback(scriptName, apiKey, callback_createProjectFolder, filter_createProjectFolder, None)

	# Set the logging level for this particular plugin. Let error and above
	# messages through but block info and lower. This is particularly usefull
	# for enabling and disabling debugging on a per plugin basis.
	#reg.logger.setLevel(logging.ERROR)
	#reg.logger.setLevel(logging.INFO)




#----------------------------------------------------------------------------------
# Creating Task on new Project, matching start and due date for Project overview
#----------------------------------------------------------------------------------

def resetUpdateField(sg,event,args):
	setData = { "sg_update_folder_structure": '-',}
	sg_utils.sgUpdateEntity(sg, event["entity"], setData)
	print "resetting update"
	
def getPipe():
	if platform.system() == "Linux":
		dsPipe = "/dsPipe/"
		return dsPipe
	else:
		dsPipe = "//vfx-data-server/dsPipe/"
		return dsPipe

def callback_createProjectFolder(sg, logger, event, args):
	try:
		try:
			if not event["meta"]["new_value"] == "Active":
				return 0
		except:
			return 0
		
		fields = ['name']
		sgProj = sg_utils.sgGetEntityData(sg, event["entity"], fields)
		logger.info("Project(" + `event["entity"]["id"]` + ") turned Active. Building folders...")
		logger.info(pprint.pformat(sgProj))

		if event["meta"]["new_value"] == "Active":
			traverseProjectStructure( sg, sgProj )
			projname = sgProj['name']
			dsPipe = getPipe()
			
			#dsFS.dsCreateFs("PROJECT",dsPipe,str(projname))
	except:
		### Handle errors here
		#logger.error("\nCaught Event:\n%s\n" % pprint.pformat(event))
		raise

def callback_episodeCreation(sg, logger, event, args):
	logger.info(pprint.pformat("sgVal"))
	setData = { "sg_update_folder_structure": 'Update',}
	sg_utils.sgUpdateEntity(sg, event["entity"], setData)
	createEpiFolderStruct(sg, event, args)
	resetUpdateField(sg,event,args)
	
def callback_episodeUpdate(sg,logger,event,args):
	fields = ['sg_update_folder_structure']
	sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
	if sgVal['sg_update_folder_structure'] == 'Update':
		createEpiFolderStruct(sg, event, args)
		resetUpdateField(sg,event,args)
def createEpiFolderStruct(sg, event, args):
	print "create/check folder struct"
	fields = ['code','project','sg_update_folder_structure']
	sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)

	epiName = sgVal['code']
	epiNSplit = epiName.split("_")
	if epiNSplit != []:
		if len(epiNSplit[-1]) == 6:
			print "Created episode folderstruct"
			dsPipe = getPipe()
			epiPath = dsPipe + str(sgVal['project']['name']) + "/film/"
			dsFS.dsCreateFs("EPISODE",epiPath,epiName)
		else:
			print "#############NOFARMERS NUBMER###########"
	
def callback_seqCreation(sg,logger,event,args):
	logger.info(pprint.pformat("sgVal"))
	setData = { "sg_update_folder_structure": 'Update',}
	sg_utils.sgUpdateEntity(sg, event["entity"], setData)
	createSeqFolderStruct(sg, event, args)
	resetUpdateField(sg,event,args)
	
def callback_seqUpdate(sg,logger,event,args):
	fields = ['sg_update_folder_structure']
	sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
	if sgVal['sg_update_folder_structure'] == 'Update':
		createSeqFolderStruct(sg, event, args)
		resetUpdateField(sg,event,args)

def createSeqFolderStruct(sg,event,args):
	fields = ['code','scene_sg_sequence_1_scenes','project','sg_status_list','sg_sequence_type']
	sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
	#logger.info(pprint.pformat(sgVal))
	print "Created sequence folderstruct"
	dsPipe = getPipe()
	seqName = sgVal['code']
	projName = sgVal['project']['name']
	epiName = sgVal['scene_sg_sequence_1_scenes'][0]['name']
	seqPath = str(dsPipe) + projName + "/film/" + epiName + "/"
	WFType = sgVal['sg_sequence_type']

	if not seqName[-6:] == "(Copy)":
		if WFType == "Shot":
			if not os.path.isdir( seqPath + seqName):
				os.mkdir(seqPath + seqName)
		if WFType == "Sequence":
			dsFS.dsCreateFs("SEQUENCE",seqPath ,seqName)
			
def callback_shotCreation(sg,logger,event,args):
	logger.info(pprint.pformat("sgVal"))
	setData = { "sg_update_folder_structure": 'Update',}
	sg_utils.sgUpdateEntity(sg, event["entity"], setData)
	createShotFolderStruct(sg, event, args)
	resetUpdateField(sg,event,args)

def callback_shotUpdate(sg,logger,event,args):
	fields = ['sg_update_folder_structure']
	sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
	if sgVal['sg_update_folder_structure'] == 'Update':
		createShotFolderStruct(sg, event, args)
		resetUpdateField(sg,event,args)

def createShotFolderStruct(sg, event, args):
	fields = ['code','sg_scene','project','sg_sequence','sg_status_list','id']
	sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
	print "Created shot folderstruct"
	dsPipe = getPipe()
	shotName = sgVal['code']
	seqName = sgVal['sg_sequence']['name']
	projName = sgVal['project']['name']
	epiName = sgVal['sg_scene']['name']
	shotID = sgVal['id']

	wfVal = sg.find_one( 'Sequence' ,[['shots.Shot.id','is', shotID]],['code','sg_sequence_type'])
	WFType = wfVal['sg_sequence_type']		
	shotPath = str(dsPipe) + projName + "/film/" + epiName + "/" + seqName + "/" 
	if not shotName[-6:] == "(Copy)":
		if WFType == "Shot":
			dsFS.dsCreateFs("SHOT",shotPath,shotName)
			dsFS.dsCreateFs("SEQUENCE",shotPath,shotName)
		if WFType == "Sequence":
			dsFS.dsCreateFs("SHOT",shotPath,shotName)

def traverseProjectStructure( sg, sgProject ):

	epFields = ['code']
	seqFields = ['code','sg_sequence_type']
	shFields = ['code','id']

	episodes = sg_utils.sgListProjectEntities( sg, sgProject, "Scene", fields = epFields )
	sequences = sg_utils.sgListProjectEntities( sg, sgProject, "Sequence", fields = seqFields )
	shots = sg_utils.sgListProjectEntities( sg, sgProject, "Shot", fields = shFields )

	print episodes
	print sequences

	print "\nProject: "
	dsPipe = getPipe()
	projPath = dsPipe + sgProject['name']
	sgProj = sgProject['name']
	
	if episodes != None:
		for epi in episodes:
			print "\nEpisodes"
			epiPath = projPath + "/film/"
			epiName = str(epi['code'])
			dsFS.dsCreateFs("EPISODE",epiPath,epiName)
			
			if sequences != None:
				for seq in sequences:
					print "\nSequences: "
					seqPath = dsPipe + sgProj + "/film/" + str(epi['code']) + "/"
					seqName = str(seq['code'])
					WFType = seq['sg_sequence_type']
					if not seqName[-6:] == "(Copy)":
						if WFType == "Shot":
							if not os.path.isdir( seqPath + seqName):
								os.mkdir(seqPath + seqName)
						if WFType == "Sequence":
							dsFS.dsCreateFs("SEQUENCE",seqPath ,seqName)
					if shots != None:
						for shot in shots:
							print "\nShots: "
							shotPath = dsPipe + sgProj + "/film/" + str(epi['code']) + "/" + str(seq['code']) + "/"
							shotName = str(shot['code'])
							shotID = shot['id']
							wfVal = sg.find_one( 'Sequence' ,[['shots.Shot.id','is', shotID]],['code','sg_sequence_type'])
							WFType = wfVal['sg_sequence_type']		
							if not shotName[-6:] == "(Copy)":
								if WFType == "Shot":
									dsFS.dsCreateFs("SHOT",shotPath,shotName)
									dsFS.dsCreateFs("SEQUENCE",shotPath,shotName)
								if WFType == "Sequence":
									dsFS.dsCreateFs("SHOT",shotPath,shotName)
