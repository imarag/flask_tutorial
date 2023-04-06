import sqlite3

import click
from flask import current_app, g

def get_db():
    # g is a special object unique for each request
    if 'db' not in g:
        g.db = sqlite3.connect( # establishes a connection to the file pointed by the DATABASE configuration key
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # tells the connection to return rows that behave like dict (access columns by name)

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# here we add the Python functions that will run the SQL commands in the schema.sql

def init_db():
    db = get_db()

    # open_resource opens a file relative to the flaskr package or the root_path (absolute path to the package filesystem)
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# it defines a command line command called init-db that calls the init_db function
@click.command('init-db') # run it with: flask --app flaskr init-db
def init_db_command():
    init_db()
    click.echo('Initialized the database')

# the functions init_db_command and close_db need to be registered with the application instance or they won't be used
# by the application.

def init_app(app):
    app.teardown_appcontext(close_db) #  call that function when cleaning up after returning the response.
    # The teardown_appcontext registers a function to be called when the application context is popped that is after
    # the request context

    app.cli.add_command(init_db_command) # adds a new command that can be called with the flask command