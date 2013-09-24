# -*- coding: utf-8 -*-
"""
For detailed information please see

http://shotgunsoftware.github.com/shotgunEvents/api.html
"""
import logging
import pprint
import sg_utils;reload(sg_utils) 
import sys
sys.path.append('//vfx-data-server/dsDev/dsCore/Shotgun')
import sgTools;reload(sgTools)


### Setting up local shotgun hook
apiKey = '114101ed238549f285df856f65e89a089c50d7fa'
scriptName = "eventTrigger_connectingFields"
url = "https://duckling.shotgunstudio.com"




def registerCallbacks(reg):
	"""Register all necessary or appropriate callbacks for this plugin."""


	filter_projectBudgetChange = {'Shotgun_Project_Change': ['sg_budget', 'sg_cost']}
	reg.registerCallback( scriptName, apiKey, callback_projectBudgetChange, filter_projectBudgetChange, None)

	#filter_timeReport = {'Shotgun_TimeLog_New': ['entity', 'duration','project','time_logs_sum']}
	#reg.registerCallback( scriptName, apiKey, callback_projTimeDuration, filter_timeReport, None)

	#filter_timeReport = {'Shotgun_TimeLog_Change': ['entity', 'duration','project','time_logs_sum']}
	#reg.registerCallback( scriptName, apiKey, callback_projTimeDuration, filter_timeReport, None)

	reg.registerCallback( scriptName, apiKey, callback_projectReport, {'Shotgun_Project_Change': ['sg_create_report','name','sg_task_bid_summary','users']}, None)

	# Set the logging level for this particular plugin. Let error and above
	# messages through but block info and lower. This is particularly usefull
	# for enabling and disabling debugging on a per plugin basis.
	#reg.logger.setLevel(logging.ERROR)
	reg.logger.setLevel(logging.INFO)



def resetUpdateField(sg,event,args):
	setData = { "sg_create_report": '-',}
	sg_utils.sgUpdateEntity(sg, event["entity"], setData)
	print "resetting update"

#----------------------------------------------------------------------------------
# create project report document
#----------------------------------------------------------------------------------
def callback_projectReport(sg, logger, event, args):
    try:
        #logger.info("\nEvent:\n%s\n" % pprint.pformat(event))
		#fields = ['project','duration']
		#sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
		#pprint.pprint(sgVal)
		#print int(sgVal['duration']) / 60
        #fields = ['sg_time_logged']
        
		fields = ['sg_create_report','name','sg_task_bid_summary','users']
		sgVal = sg_utils.sgGetEntityData(sg, event["entity"], fields)
		
		if sgVal['sg_create_report'] == 'createReport':
			getUsersTimeInfo(sg,sgVal)
			resetUpdateField(sg,event,args)
    except:
        ### Handle errors here
        logger.error("\nCaught Event:\n%s\n" % pprint.pformat(event))
        raise
       
def getUsersTimeInfo(sg,sgVal):
	for user in sgVal['users']:
		userLogs = sg.find( 'TimeLog',[['project.Project.name','is',str(sgVal['name'])]],['entity','user', 'duration','project','time_logs_sum'])

		for log in userLogs:
			if user['name'] == log['user']['name']:
				print log['id']
#----------------------------------------------------------------------------------
# Synching Project balance as an equation of [sg_budget - sg_cost]
#----------------------------------------------------------------------------------
def callback_projectBudgetChange(sg, logger, event, args):
    try:
        #logger.info("\nEvent:\n%s\n" % pprint.pformat(event))
                
        fields = ['sg_budget', 'sg_cost']
        sgProj = sg_utils.sgGetEntityData(sg, event['entity'], fields = fields)
        
        if not validate_sgObj(sgProj, fields):
            logger.error("Return value doesn't contain fields: " + `fields`)
            
        
        for f in fields:
            if sgProj[f] == None:
                logger.info("Either of " + `fields`+ " weren't set. Skipping balance update")
                return 0
            
        balance = sgProj["sg_budget"] - sgProj["sg_cost"]
        sgData = {"sg_balance" : balance}
        
        
        ### Writing what I'm doing
        logger.info("Setting project(" + `sgProj['id']` + ") balance to: " + `balance`)
        
        # Setting session for browser response
        sg_utils.sgSetSessionUUID(sg, logger, event )
            
        # Performing update
        sg_utils.sgUpdateEntity( sg, sgProj, sgData )
        

    except:
        ### Handle errors here
        #logger.error("\nCaught Event:\n%s\n" % pprint.pformat(event))
        raise
        






def validate_sgObj(sgObj, fields):
    for f in fields:
        if not sgObj.has_key(f):
            return 0
    return 1


