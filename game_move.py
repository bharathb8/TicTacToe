'''
Game Moves model definition

Created on: Dec 17, 2017
'''

import json
import MySQLdb
from config_helper import get_database_handle

class GameMove(object):

	@staticmethod
	def addMove(game_id, player_id, move_num, game_board):
		'''
		Add a game move to the given game_id made by the specified player_id
		'''
		db_handle = None
		db_cursor = None
		ret_status = False
		try:
			db_handle = get_database_handle()
			db_cursor = db_handle.cursor(MySQLdb.cursors.DictCursor)
			query = '''
INSERT INTO game_moves
(game_id, player_id, move_number, game_board)
VALUES
(%s, '%s', %s, '%s')''' % (game_id, player_id, move_num, json.dumps(game_board))

			db_cursor.execute(query)
			db_handle.commit()
			ret_status = True
		except Exception as e:
			print e
			ret_status = False
		finally:
			if db_cursor is not None:
				db_cursor.close()
			if db_handle is not None:
				db_handle.close()
			return ret_status

	@staticmethod
	def getLatestGameState(game_id):
		'''
		Add a game move to the given game_id made by the specified player_id
		'''
		db_handle = None
		db_cursor = None
		row = None
		try:
			db_handle = get_database_handle()
			db_cursor = db_handle.cursor(MySQLdb.cursors.DictCursor)
			query = '''
SELECT * FROM game_moves 
WHERE game_id = %s 
ORDER BY ID DESC
LIMIT 1 ''' % (game_id)
			db_cursor.execute(query)
			row = db_cursor.fetchone()

		except Exception as e:
			print e
		finally:
			if db_cursor is not None:
				db_cursor.close()
			if db_handle is not None:
				db_handle.close()
			return row
 


