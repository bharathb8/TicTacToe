'''
TicTacToe Game class definition

Created on: Dec 16, 2017
'''
import MySQLdb
from config_helper import get_database_handle

class TTTGame(object):

	GAME_STATUS_IN_PROGRESS = 1
	GAME_STATUS_COMPLETED = 2

	@staticmethod
	def getGameDetails(game_id=None):
		'''
		given a game_id retrieve its game details
		'''
		db_handle = None
		db_cursor = None
		row = None
		if not game_id:
			return None
		try:
			db_handle = get_database_handle()
			db_cursor = db_handle.cursor(MySQLdb.cursors.DictCursor) 
			status_query = '''
SELECT * FROM ttt_games
WHERE game_id = %(game_id)s
''' % {'game_id': game_id}
			db_cursor.execute(status_query)
			row = db_cursor.fetchone()
		finally:
			if db_cursor is not None:
				db_cursor.close()
			if db_handle is not None:
				db_handle.close()
			return row

	@staticmethod
	def getGameDetailsByChannelId(channel_id):
		'''
		get the latest game details for a channel_id
		'''
		db_handle = None
		db_cursor = None
		row = None
		if not channel_id:
			return None
		try:
			db_handle = get_database_handle()
			db_cursor = db_handle.cursor(MySQLdb.cursors.DictCursor)
			status_query = '''
SELECT * FROM ttt_games 
WHERE channel_id = '%(channel_id)s'
ORDER BY id desc
LIMIT 1
''' % {'channel_id': channel_id}
			db_cursor.execute(status_query)
			row = db_cursor.fetchone()
		except Exception as e:
			print e
		finally:
			if db_cursor is not None:
				db_cursor.close()
			if db_handle is not None:
				db_handle.close()
			return row

	@staticmethod
	def createGame(channel_id, player_1, player_2):
		'''
		Create a new game for Player1 and Player2 in the given Channel
		'''
		db_handle = None
		db_cursor = None
		created_game_id = None
		try:
			db_handle = get_database_handle()
			create_query = '''
INSERT INTO ttt_games
(channel_id, player1_id, player2_id, current_player, status, date_created)
VALUES
('%s', '%s', '%s', '%s', %s, %s)
			''' % (channel_id, player_1, player_2, player_1, TTTGame.GAME_STATUS_IN_PROGRESS, 'now()')
			db_cursor = db_handle.cursor(MySQLdb.cursors.DictCursor)
			db_cursor.execute(create_query)
			created_game_id = db_cursor.lastrowid
			db_handle.commit()
		except Exception as e:
			print "Exception: %s" % e
		finally:
			if db_cursor is not None:
					db_cursor.close()
			if db_handle is not None:
					db_handle.close()
			return created_game_id








