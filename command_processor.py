'''
Command Processor

Created On: Dec 16, 2017
'''
import json
import logging
import os
import sys

from flask import jsonify
from ttt_game import TTTGame
from game_move import GameMove

logging.basicConfig(filename='command_processor.log',level=logging.INFO)
logger = logging.getLogger()

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

class CommandProcessor(object):

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
		'''
		Format user name for mentions 
		'''
		formatted_username = "<@%s>" % username
		return formatted_username
	def _getHelpMessage(self):
		help_message = '''
```Slack Tic-Tac-Toe:
1. /slack_ttt help - To display this message at any time.
2. /slack_ttt status - To show current status of game in the channel.
3. /slack_ttt challenge @player_name - To start a game against @player_name.
4. /slack_ttt mark <1-9> - To mark a spot number between 1-9 during the game.
5. /slack_ttt abandon - To abandon current game. Only participants can abandon.```
'''
		return help_message

	def createGame(self, player_1, player_2, request_data):
		'''
		Create a new game between Player1 and Player2
		'''
		game_id = None
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
		Given the current board, evaluate if we have a winner
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

	def _getPrettyPrintBoard(self, game_board):
		'''
		get pretty print version of the given board
		'''
		pp_row1 = '| ' + ' | '.join(game_board[0:3]) + ' |'
		pp_row2 = '| ' + ' | '.join(game_board[3:6]) + ' |'
		pp_row3 = '| ' + ' | '.join(game_board[6:])  + ' |'
		boundary_row = '|---+---+---|'

		pp_board = '```%s\n%s\n%s\n%s\n%s```' % (pp_row1, boundary_row, pp_row2, boundary_row, pp_row3)
		return pp_board

	def parseCommand(self, command_string):
		'''
		given the command text string, extract the individual words
		'''
		command_parts = []
		try:
			command_parts = command_string.split(" ")
		except:
			logger.error("Exception while parsing command string.")
		finally:
			return command_parts

	def processCommand(self, command_string="", request_data={}):
		'''
		This is the command processor function.
		Process 'status', 'challenge', 'mark' and 'help' commands. For any other 
		commands this will respond with help message.
		'''
		response_msg = ""
		response_type = "ephemeral"
		try:
			command_parts = self.parseCommand(command_string) 
		
			if not command_parts:
				response_msg = self._getHelpMessage()
				response_dict = {'text': response_msg, 'response_type': response_type}
				return

			logger.info("command parts %s " % command_parts)

			if command_parts[0].lower() == 'status':
				channel_id = request_data['channel_id']
				game_details = TTTGame.getGameDetailsByChannelId(channel_id)
				if game_details:
					status = game_details['status']
					if status == TTTGame.GAME_STATUS_IN_PROGRESS:
						response_msg = "Game in progress. %s 's turn to play" % self._getFormattedUserNameMention(game_details['current_player'])
						game_id = game_details['id']
						game_state = GameMove.getLatestGameState(game_id)
						if game_state:
							game_board = json.loads(game_state['game_board'])
						else:
							game_board = self._getNewGameBoard()
						board_string = self._getPrettyPrintBoard(game_board)
						response_msg = "%s\n\n%s" % (board_string, response_msg)
					elif status in [TTTGame.GAME_STATUS_COMPLETED, TTTGame.GAME_STATUS_ABANDONED]:
						response_msg = "No active games currently. All games have been completed.\n Would you like to start one?"
				else:
					response_msg = "No games in the channel's history."

				response_dict = {'text': response_msg, 'response_type': response_type}

			elif command_parts[0].lower() == 'challenge':
				# check if current channel has no on-going games
				channel_id = request_data['channel_id']
				game_details = TTTGame.getGameDetailsByChannelId(channel_id)
				if game_details:
					status = game_details['status']
					if status == TTTGame.GAME_STATUS_IN_PROGRESS:
						response_msg = "Sorry, a game is already in progress. %s 's turn to play" % self._getFormattedUserNameMention(game_details['current_player'])
						game_id = game_details['id']
						game_state = GameMove.getLatestGameState(game_id)
						game_board = json.loads(game_state['game_board'])
						board_string = self._getPrettyPrintBoard(game_board)
						response_msg = "%s\n\n%s" % (board_string, response_msg)
						response_dict = {'text': response_msg, 'response_type': response_type}
						return

				player_1 = request_data['user_id']
				player_2 = self._extractUserID(command_parts[1])
				# check if the player did not specify his own name to start a new game
				if (player_2 and player_1 == player_2) or (player_2 == 'USLACKBOT'):
					response_msg = "Please choose another player(except yourself and Slack Bot) to challenge a new game."
					response_dict = {'text': response_msg, 'response_type': response_type}
				else:
					# now we are good to start a new game between two players.
					game_id = self.createGame(player_1, player_2, request_data)
					if game_id:
						board_string = self._getPrettyPrintBoard(self._getNewGameBoard())
						response_msg = "%s\nGame started! \n %s v/s %s. \n %s's turn to play!" % (board_string, self._getFormattedUserNameMention(player_1),
																									self._getFormattedUserNameMention(player_2),
																									self._getFormattedUserNameMention(player_1))

					response_dict = {'text': response_msg, 'response_type': 'in_channel'}


			elif command_parts[0].lower() == 'mark':
				response_dict = self.makeMove(command_parts, request_data)

			elif command_parts[0].lower() == 'abandon':
				# check if current channel has no on-going games
				response_msg = self._getHelpMessage()
				channel_id = request_data['channel_id']
				game_details = TTTGame.getGameDetailsByChannelId(channel_id)
				if game_details:
					if game_details['status'] != TTTGame.GAME_STATUS_IN_PROGRESS:
						response_msg = "No active games currently. No game to abandon.\n Would you like to start a new one?"
					else:
						current_user = request_data['user_id']
						if current_user != game_details['player1_id'] and current_user != game_details['player2_id']:
							response_msg = "Sorry, you are not a player of the current game. You cannot abandon this game."
						else:
							game_id = game_details['id']
							TTTGame.updateGameAsCompleted(game_id, TTTGame.GAME_STATUS_ABANDONED)
							game_state = GameMove.getLatestGameState(game_id)
							if game_state:
								game_board = json.loads(game_state['game_board'])
							else:
								game_board = self._getNewGameBoard()
							board_string = self._getPrettyPrintBoard(game_board)
							response_msg = "%s\n\n%s" % (board_string, "Game abandoned by %s ." % self._getFormattedUserNameMention(current_user))
							response_type = "in_channel"

				response_dict = {'text': response_msg, 'response_type': response_type}
			else:
				response_msg = self._getHelpMessage()
				response_dict = {'text': response_msg, 'response_type': response_type}
		except:
			logger.error("Exception processing command. %s" % e)
		finally:
			return jsonify(response_dict)



	def makeMove(self, command_parts, request_data):
		'''
		Process Mark command by the player. 
		Evaluate if it is the player's valid turn. 
		If so, then mark the specified space.
		Evaluate the board if we have winner and update the game state.
		'''
		response_msg = ""
		response_type = "in_channel"
		game_id = None
		game_state = None
		try:
			channel_id = request_data['channel_id']

			# get the active game for the channel 
			latest_game_details = TTTGame.getGameDetailsByChannelId(channel_id)
			game_id = latest_game_details['id']
			game_state = GameMove.getLatestGameState(game_id)

			if len(command_parts) < 2:
				response_msg = "Please specify a number between 1 and 9 to mark. /slack_ttt mark <1-9>"
				response_type = "ephemeral"
				if game_state:
					game_board = json.loads(game_state['game_board'])
					board_string = self._getPrettyPrintBoard(game_board)
					response_msg = "%s\n\n%s" % (board_string, response_msg)
				return

			space_num = command_parts[1]
			if len(space_num) > 1:
				response_msg = "Please specify a number between 1 and 9 to mark. /slack_ttt mark <1-9>"
				response_type = "ephemeral"
				if game_state:
					game_board = json.loads(game_state['game_board'])
					board_string = self._getPrettyPrintBoard(game_board)
					response_msg = "%s\n\n%s" % (board_string, response_msg)
				return

			try:
				space_number = int(command_parts[1])
			except:
				response_msg = "Please specify a number between 1 and 9 to mark. /slack_ttt mark <1-9>"
				response_type = "ephemeral"
				if game_state:
					game_board = json.loads(game_state['game_board'])
					board_string = self._getPrettyPrintBoard(game_board)
					response_msg = "%s\n\n%s" % (board_string, response_msg)
				return

			# get the active game for the channel 
			latest_game_details = TTTGame.getGameDetailsByChannelId(channel_id)
			if not latest_game_details or latest_game_details['status'] == TTTGame.GAME_STATUS_COMPLETED:
				response_msg = "No active games in current channel. Start a new game?"
				response_type = "ephemeral"

			if latest_game_details['status'] == TTTGame.GAME_STATUS_IN_PROGRESS:

				request_user_id = request_data['user_id']
				current_player = latest_game_details['current_player']
				player_1 = latest_game_details['player1_id']
				player_2 = latest_game_details['player2_id']

				game_id = latest_game_details['id']
				game_state = GameMove.getLatestGameState(game_id)

				# If invalid space number is provided, display appropriate message 
				if space_number < 1 or space_number > 9:
					response_msg = "Not a valid spot number. Please specify a number between 1 and 9."
					response_type = "ephemeral"
					if game_state:
						game_board = json.loads(game_state['game_board'])
						board_string = self._getPrettyPrintBoard(game_board)
						response_msg = "%s\n\n%s" % (board_string, response_msg)
					return

				if request_user_id == current_player:
					
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

					# if an already marked spot is specified, then display a warning
					if game_board[space_number - 1] != '-':
						msg = "That spot is already marked. Please specify a valid spot."
						response_type = "ephemeral"
						board_string = self._getPrettyPrintBoard(game_board)
						response_msg = '%s\n\n%s' % (board_string, msg)
						return

					game_board[space_number - 1] = mark_character
					GameMove.addMove(game_id, current_player, move_num, game_board)
					board_string = self._getPrettyPrintBoard(game_board)
					# Check if the current move finishes the game.
					if self._evaluateGameBoard(game_board):
						# update the game state to complete
						TTTGame.updateGameAsCompletedWithWinner(game_id, current_player)
						msg = "Game over! %s wins the game!" % self._getFormattedUserNameMention(current_player)
						response_msg = "%s\n\n%s" % (board_string, msg)
					elif move_num == 9:
						# if we reached move number 9 without a winner then its a draw.
						TTTGame.updateGameAsCompleted(game_id, TTTGame.GAME_STATUS_COMPLETED)
						msg = "Game drawn!"
						response_msg = "%s\n\n%s" % (board_string, msg)
					else:
						# update who is the next player for the game.
						next_player = player_1 if current_player == player_2 else player_2
						TTTGame.updateGameDetails(game_id, next_player)
						msg = "%s's turn to play." % self._getFormattedUserNameMention(next_player)
						response_msg = '%s\n\n%s' % (board_string, msg)
				else:
					response_msg = "%s 's turn to play. Please wait your turn." % self._getFormattedUserNameMention(current_player)
					response_type = "ephemeral"
					if game_state:
						game_board = json.loads(game_state['game_board'])
						board_string = self._getPrettyPrintBoard(game_board)
						response_msg = "%s\n\n%s" % (board_string, response_msg)

		except Exception as e:
			logger.error("Exception in make move method. %s" % e)
		finally:
			response_dict = {'text': response_msg, 'response_type': response_type}
			return response_dict

