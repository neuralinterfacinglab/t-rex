# builtin
import sys
import logging
from datetime import datetime

# 3rd party
from pathlib import Path
from flask import Flask
from flask_cors import CORS
import libs.utils as utils

# constants
MAIN_DIR = utils.get_main_dir_from_config_file()
PASSWORD = utils.get_pass_from_config_file()

app = Flask(__name__)
CORS(app)

# define the format for the logs
format = logging.Formatter(
    '%(asctime)s %(levelname)s file:(%(filename)s (%(lineno)d)) %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

# define a file that will contain the default logs of flask and of our server
date = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")  # get the current date
# define the name of the log file
web_log_file_name = ''.join([date, '_web', '.log'])
# define the name of the log file
server_log_file_name = ''.join([date, '_server', '.log'])
log_file_path = Path(MAIN_DIR)/'resources'/'logs'  # define the path
log_file_path.mkdir(parents=True, exist_ok=True)  # create the log file

# set the file handler for the web logger used by flask (werkzeug), and only log Warning messages
web_logger = logging.getLogger('werkzeug')  # grabs underlying WSGI logger
# remove the StreamHandler that werkzeug contains (we don't want this logger to print to the console)
web_logger.handlers.clear()
web_logger.setLevel(logging.DEBUG)
web_file_handler = logging.FileHandler(
    log_file_path/web_log_file_name)  # creates handler for the log file
web_logger.addHandler(web_file_handler)

# create a new logger to log the server messages
server_logger = logging.getLogger('server')
server_logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(log_file_path/server_log_file_name)
fh.setFormatter(format)

stream = logging.StreamHandler(sys.stdout)
stream.setFormatter(format)

server_logger.addHandler(fh)
server_logger.addHandler(stream)

server_logger.info("=================== NEW EXECUTION ===================")

# load the views and routes
from flaskr import routes
from flaskr import views

if __name__ == '__main__':
    server_logger.info('Starting server...')
    app.run(host="localhost", port=5000, debug=True)
