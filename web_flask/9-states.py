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


@app.route('/states', strict_slashes=False)
def states_list_route():
    """Display a HTML page with a list of all State objects
    present in DBStorage sorted by name
    """
    return render_template("9-states.html", states=storage.all(State))


@app.route('/states/<id>', strict_slashes=False)
def states_id_route(id):
    """Display a HTML page with the State object
    with the id equal to the id argument
    or a 404 error if not found
    """
    state = None
    not_found = True
    for s in storage.all(State).values():
        if s.id == id:
            state = s
            not_found = False
            break
    return render_template("9-states.html", id=id, state=state,
                           not_found=not_found)


if __name__ == '__main__':
    """Run the Flask app"""
    app.run(host='0.0.0.0', port=5000)
