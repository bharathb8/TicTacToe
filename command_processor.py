'''
Command Processor

Created On: Dec 16, 2017
'''

import os
import sys

from ttt_game import TTTGame
from config_helper import get_database_helper

class CommandProcessor(object):

	def processCommand(command_parts=[], request_data={}):
		try:

			if not command_parts:
				return

			if lower(command_parts[0]) == 'status':
				channel_id = request_data['channel_id']
				


		except:
			pass