DIR="$( cd "$( dirname "$0" )" && pwd )"
export WEEKS_SECRET='something-really-secret'
export FLASK_APP="$DIR/autoapp.py"
export FLASK_DEBUG=1
flask run