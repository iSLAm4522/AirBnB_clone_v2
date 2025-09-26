#!/usr/bin/python3
"""Flask app to display a HTML page
containing a list of all State objects
present in DBStorage sorted by name
"""
from flask import Flask, render_template
from models import storage
from models.state import State
from models.city import City


app = Flask(__name__)


@app.teardown_appcontext
def teardown_appcontext(exception):
    """Remove the current SQLAlchemy session"""
    storage.close()


@app.route('/cities_by_states', strict_slashes=False)
def cities_by_states_route():
    """Display a HTML page with a list of all State objects
    present in DBStorage sorted by name, and their
    corresponding City objects also sorted by name"""
    states = sorted(storage.all(State).values(), key=lambda x: x.name)
    for state in states:
        state.cities = sorted(state.cities, key=lambda x: x.name)
    return render_template("8-cities_by_states.html", states=states)


if __name__ == '__main__':
    """Run the Flask app"""
    app.run(host='0.0.0.0', port=5000)
