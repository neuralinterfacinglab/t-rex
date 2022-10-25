conda activate trex

$env:FLASK_ENV='development'
$env:FLASK_APP='flaskr'

start http://127.0.0.1:5000

flask run