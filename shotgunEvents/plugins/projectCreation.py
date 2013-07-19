# -*- coding: utf-8 -*-
"""
For detailed information please see

http://shotgunsoftware.github.com/shotgunEvents/api.html
"""
import logging
import pprint



def registerCallbacks(reg):
	"""Register all necessary or appropriate callbacks for this plugin."""


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

	projectCreationFilter = {'Shotgun_Project_Change': ['sg_status_list']}
	reg.registerCallback('eventTrigger_projectCreation', '1d447d89131cdc8cbb3cc800ba673db322bfabf5', projectCreationHandler, projectCreationFilter, None)

	# Set the logging level for this particular plugin. Let error and above
	# messages through but block info and lower. This is particularly usefull
	# for enabling and disabling debugging on a per plugin basis.
	#reg.logger.setLevel(logging.ERROR)
	reg.logger.setLevel(logging.INFO)


	



def projectCreationHandler():
  pass


	
"""	
def versionStatusUpdate(sg, logger, event, args):
    #logger.info("\nVersion Status Change:\n%s\n" % pprint.pformat(event))
            
    # Get Versions task
    if event['entity']:
        vTask = sg_utils.sgGetTasksByVersion(sg, event["entity"], ["sg_status_list", "content"] )
        
        if vTask:
            versions = sg_utils.sgGetVersionsByTask(sg, vTask, ["sg_status_list"] )
        else:
            logger.info("vTask is Nonetype. Skipping")
            return 0
    else:
        logger.info("event['entity'] is Nonetype. skipping")
        return 0

    
    taskStatus = 'ip' # If version exists Task should always be In Progress
    finCount = 0
    noteCount = 0
    
    for ver in versions:
            if ver["sg_status_list"] == "fin":
                    finCount += 1
            elif ver["sg_status_list"] == "nts":
                    noteCount += 1

    # If all Versions are finished set Task status to finished, otherwise In Progress.			
    if finCount and noteCount + finCount == len(versions):
            taskStatus = 'fin'
    else:
            taskStatus = 'ip'
    
    
    ### Updating status    
    if not vTask["sg_status_list"] == taskStatus:
            trigger = "\nTrigger:\n%s" % pprint.pformat(event['meta'])
            action = "\nChanging status on Task:%s(%i) from %s to %s" % (vTask['content'], vTask['id'], vTask['sg_status_list'], taskStatus)
            logger.info(trigger + action)
            sg_utils.sgSetTaskStatus(sg, vTask, taskStatus)
            
            










	
def taskStatusUpdate(sg, logger, event, args):
	#logger.info("\nTask Status Change:\n%s\n" % pprint.pformat(event))

	shot = sg_utils.sgGetShotByTask(sg, event["entity"], ["sg_status_list"])
	
	if not shot: 
		logger.info("shot didn't catch anything. Quitting")
		return
	
	shotTasks = sg_utils.sgGetTasksByShot(sg, shot, ["sg_status_list"])
	
	if not shotTasks:
		logger.info("shotTasks didn't catch anything. Quitting")
		return
	
	shotStatus = 'wtg'
	finCount = 0
	
	# If any task is not 'Waiting to start' set shot to 'In progress'
	for task in shotTasks:
		if not task["sg_status_list"] == "wtg":
			shotStatus = 'ip'
		
			if task["sg_status_list"] == "fin":
				finCount += 1
				
	# If all tasks are finished, set shot status to finished.
	if finCount == len(shotTasks):
		shotStatus = 'fin'
	elif finCount:
		shotStatus = 'ip'

	if not shot["sg_status_list"] == shotStatus:
		sg_utils.sgSetShotStatus(sg, shot, shotStatus)
		
	shotStatusUpdate(sg, shot)


def shotStatusUpdate(sg, shot):
	episode = sg_utils.sgGetEpisodeByShot(sg, shot)
	pprint.pprint(episode)
"""	