call activate trex

set FLASK_ENV=development
set FLASK_APP=flaskr

start /max http://127.0.0.1:5000

flask run
