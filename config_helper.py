'''
Database config helper

'''
import MySQLdb as db 

def get_database_handle():
    db_handle = db.connect(user='slack_user', passwd='slack_password', host='127.0.0.1', port=3306, db='slack')
    return db_handle    
