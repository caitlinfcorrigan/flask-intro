import sqlite3
import click

from flask import current_app, g

def get_db():
    # g stores data during a request including the connection?
    if 'db' not in g:
        # Establish the db connection
        g.db = sqlite3.connect(
            # current_app points to the Flask app handling the request
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # .Row treats the returns like dicts
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    # Opens file relative to flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command is a CLI command
@click.command('init-db')
def init_db_command():
    # Clear the existing data and create new tables
    init_db()
    click.echo('Initialized db.')

# Register the app
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)