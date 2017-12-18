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

	def _extractUserID(self, unfurledUserName):
		'''
		Given unfurled username mentions from text message, extract the user ID from it.
		The format is: <@U876W903Z|user_name>
		'''
		user_id = None
		try:
			if not unfurledUserName.startswith('<') and not unfurledUserName.endswith('>'):
				return None

			combined_str = unfurledUserName.strip('<')
			combined_str = combined_str.strip('>')
			user_id, user_name = combined_str.split('|')
			user_id = user_id.strip('@')
		except Exception as e:
			logger.error("Exception while extracting user ID. %s" % e)
		finally:
			return user_id


	def processCommand(self, command_string="", request_data={}):
		response_msg = "Empty msg."
		try:
			command_parts = self.parseCommand(command_string) 
		
			if not command_parts:
				return
			print "command parts %s " % command_parts
			import pdb;pdb.set_trace()
			if command_parts[0].lower() == 'status':
				channel_id = request_data['channel_id']
				game_details = TTTGame.getGameDetailsByChannelId(channel_id)
				if game_details:
					status = game_details['status']
					if status == TTTGame.GAME_STATUS_IN_PROGRESS:
						response_msg = "Game in progress"
				else:
					response_msg = "No games in the channel's history."
			if command_parts[0].lower() == 'challenge':
				player_1 = request_data['user_id']
				player_2 = self._extractUserID(command_parts[1])
				if player_2 and player_1 == player_2:
					response_msg = "Please choose another player(not your self) to challenge a new game."
					return
				game_id = self.createGame(player_1, player_2, request_data)
				if game_id:
					response_msg = "Game started! \n %s V/S %s. \n %s's turn to play!" % (player_1, player_2, player_1)
				return
		except:
			pass
		finally:
			return response_msg

	def createGame(self, player_1, player_2, request_data):
		try:
			game_id = TTTGame.createGame(request_data['channel_id'], player_1, player_2)
		except Exception as e:
			logger.error("Exception while creating game %s" % e)
		finally:
			return game_id


