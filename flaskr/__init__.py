# builtin
import os
import sys
import logging

# 3th party
from flask import Flask
from flask_cors import CORS
import libs.utils as utils

# constants
MAIN_DIR = utils.get_main_dir_from_config_file()
PASSWORD = utils.get_pass_from_config_file()


app = Flask(__name__)
CORS(app)

# define the format for the logs
format = logging.Formatter('%(asctime)s %(levelname)s file:(%(filename)s) func:%(funcName)s(%(lineno)d) msg:%(message)s',datefmt='%d/%m/%Y %H:%M:%S')

# get default logger (werkzeug) and make it log to a file too
web_logger = logging.getLogger('werkzeug')      # grabs underlying WSGI logger
web_logger.setLevel(logging.WARNING)
# TODO get the log file from the 'config.yaml'
web_file_handler = logging.FileHandler('web_record.log') # creates handler for the log file
web_file_handler.setFormatter(format)                # define the logging format for user defined messages
web_file_handler.setLevel(logging.DEBUG)
web_logger.addHandler(web_file_handler)


# create a new logger to log the server messages
server_logger = logging.getLogger('server')
server_logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('server_record.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(format)

stream = logging.StreamHandler(sys.stdout)
stream.setLevel(logging.DEBUG)
stream.setFormatter(format)

server_logger.addHandler(fh)
server_logger.addHandler(stream)

server_logger.info("=================== NEW EXECUTION =================== ")

# get the views and the routes 
from flaskr import views
from flaskr import routes



if __name__ == '__main__':
    server_logger.info('Starting server...')
    app.run(host="localhost", port=5000, debug=True)
