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

logging.basicConfig(filename='flask_app.log',level=logging.INFO)
logger = logging.getLogger()

consoleHandler = logging.StreamHandler()
logger.addHandler(consoleHandler)

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello():
	data_dict = request.args
	print "request_data: %s" % data_dict
	return "Hello From Flask!" + " Current Time is %s " % str(datetime.datetime.now())

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

