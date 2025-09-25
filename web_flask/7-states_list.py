#!/usr/bin/python3
"""Flask app to display a HTML page
containing a list of all State objects
present in DBStorage sorted by name
"""
from flask import Flask, render_template
from models import storage
from models.state import State

app = Flask(__name__)


@app.teardown_appcontext
def teardown_appcontext(exception):
    """Remove the current SQLAlchemy session"""
    storage.close()


@app.route('/states_list', strict_slashes=False)
def states_list_route():
    """Display a HTML page with a list of all State objects
    present in DBStorage sorted by name
    """
    return render_template("7-states_list.html", states=storage.all(State))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
