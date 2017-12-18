'''
Command Processor

Created On: Dec 16, 2017
'''
import json
import os
import sys

from flask import jsonify
from ttt_game import TTTGame
from game_move import GameMove

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

	def _getFormattedUserNameMention(self, username):
		formatted_username = "<@%s>" % username
		return formatted_username

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
					elif status == TTTGame.GAME_STATUS_COMPLETED:
						response_msg = "No active games currently. All games have been completed.\n Would you like to start one?"
				else:
					response_msg = "No games in the channel's history."

			if command_parts[0].lower() == 'challenge':
				# check no games in progress in the channel
				player_1 = request_data['user_id']
				player_2 = self._extractUserID(command_parts[1])
				if player_2 and player_1 == player_2:
					response_msg = "Please choose another player(not your self) to challenge a new game."
					return
				game_id = self.createGame(player_1, player_2, request_data)
				if game_id:
					response_msg = "Game started! \n %s V/S %s. \n %s's turn to play!" % (self._getFormattedUserNameMention(player_1),
																						  self._getFormattedUserNameMention(player_2),
																						  self._getFormattedUserNameMention(player_1))

			if command_parts[0].lower() == 'mark':
				response_msg = self.makeMove(command_parts, request_data)

		except:
			pass
		finally:
			response_json = {'response_type': 'in_channel',
							 'text': response_msg}
			return jsonify(response_json)

	def createGame(self, player_1, player_2, request_data):
		'''
		Create a new game between Player1 and Player2
		'''
		try:
			game_id = TTTGame.createGame(request_data['channel_id'], player_1, player_2)
		except Exception as e:
			logger.error("Exception while creating game %s" % e)
		finally:
			return game_id

	def _getNewGameBoard(self):
		'''
		Generate an empty starting TTT game board
		'''
		return ['-' for _ in range(9)]

	def _evaluateGameBoard(self, board):
		'''
		Given the current board, evaluate if we have  winner
		'''
		# check for row matches
		if (board[0] != '-' and (board[0] == board[1] == board[2])) or \
			(board[3] != '-' and (board[3] == board[4] == board[5])) or \
			(board[6] != '-' and (board[6] == board[7] == board[8])):
			return True
		# check for column matches
		if (board[0] != '-' and (board[0] == board[3] == board[6])) or \
			(board[1] != '-' and (board[1] == board[4] == board[7])) or \
			(board[2] != '-' and (board[2] == board[5] == board[8])):
			return True

		# check left diagonal
		if board[0] != '-' and (board[0] == board[4] == board[8]):
			return True

		# check right diagonal
		if board[2] != '-' and (board[2] == board[4] == board[6]):
			return True

		return False


	def makeMove(self, command_parts, request_data):
		'''
		Process Move. 
		Evaluate if it is the player's valid turn. If so, then mark the specified space.
		Evaluate the board if we have winner and update the game state.
		'''
		response_msg = "Empty message from makeMove"
		try:
			channel_id = request_data['channel_id']
			space_number = int(command_parts[1])

			# get the active game for the channel 
			latest_game_details = TTTGame.getGameDetailsByChannelId(channel_id)
			if not latest_game_details or latest_game_details['status'] == TTTGame.GAME_STATUS_COMPLETED:
				response_msg = "No active games in current channel. Start a new game?"

			if latest_game_details['status'] == TTTGame.GAME_STATUS_IN_PROGRESS:
				if space_number < 1 or space_number > 9:
					response_msg = "Not a valid space number. Please specify a number between 1 and 9."

				request_user_id = request_data['user_id']
				current_player = latest_game_details['current_player']
				player_1 = latest_game_details['player1_id']
				player_2 = latest_game_details['player2_id']

				if request_user_id == current_player:
					game_id = latest_game_details['id']
					game_state = GameMove.getLatestGameState(game_id)
					if not game_state:
						# this means its a new game and no moves have been made yet.
						game_board = self._getNewGameBoard()
						move_num = 1
					else:
						game_board = json.loads(game_state['game_board'])
						move_num = game_state['move_number'] + 1

					if request_user_id == player_1:
						mark_character = 'X'
					elif request_user_id == player_2:
						mark_character = 'O'

					game_board[space_number - 1] = mark_character
					GameMove.addMove(game_id, current_player, move_num, game_board)
					# Check if the current move finishes the game.
					if self._evaluateGameBoard(game_board):
						# update the game state to complete
						TTTGame.updateGameAsCompleted(game_id, current_player)
						response_msg = "%s wins the game!" % self._getFormattedUserNameMention(current_player)

					else:
						# update who is the next player for the game.
						next_player = player_1 if current_player == player_2 else player_2
						TTTGame.updateGameDetails(game_id, next_player)
						response_msg = "Done. %s's turn to play." % self._getFormattedUserNameMention(next_player)

				else:
					response_msg = "%s 's turn to play. Please wait your turn." % self._getFormattedUserNameMention(current_player)

		except Exception as e:
			logger.error("Exception in make move method. %s" % e)
		finally:
			return response_msg

