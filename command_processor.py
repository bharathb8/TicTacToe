'''
Command Processor

Created On: Dec 16, 2017
'''

import os
import sys

from ttt_game import TTTGame

class CommandProcessor(object):

	def parseCommand(self, command_string):
	    command_parts = []
	    try:
		command_parts = command_string.split(" ")
	    except:
		logger.error("Exception while parsing command string.")
	    finally:
		return command_parts


	def processCommand(self, command_string="", request_data={}):
             response_msg = "Empty msg."
	     try:
		command_parts = self.parseCommand(command_string) 
		
		if not command_parts:
		    return
		print "command parts %s " % command_parts
		if command_parts[0].lower() == 'status':
		    channel_id = request_data['channel_id']
		    game_details = TTTGame.getGameDetailsByChannelId(channel_id)
		    if game_details:
			status = game_details['status']
			if status == 1:
			   response_msg = "Game in progress"
		    else:
			response_msg = "No games in the channel's history."
	    
	     except:
		pass
	     finally:
		return response_msg

