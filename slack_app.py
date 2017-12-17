'''
Slack Slash Command request handler

Created on: Dec 16, 2017
'''

import datetime
import logging
import os
import sys

from flask import Flask
from flask import request
from optparse import OptionParser

from command_processor import CommandProcessor

logging.basicConfig(filename='flask_app.log',level=logging.INFO)
logger = logging.getLogger()

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def processRequest():
	try:
		form_data_dict = request.form
		logger.info("request user_id : %s" % form_data_dict)
		logger.info("request team_id : %s" % form_data_dict['team_id'])
		cmdProcessor = CommandProcessor()
		response = cmdProcessor.processCommand(form_data_dict['text'], form_data_dict)
		return response
		#return "Hello From Flask!" + " request data: %s " % form_data_dict 
	except:
		return "Oops, could not process request."


@app.route("/time")
def getTime():
	return "Current Time is %s " % str(datetime.datetime.now())

@app.route("/hello", methods=['POST'])
def processHello():
	import pdb;pdb.set_trace()
	print "inside hello"
	return "Current Time is %s " % str(datetime.datetime.now())

if __name__ == "__main__":
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=False)

