import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('init-db')
@click.option('--force/--no-force', default=False, help='Overwrite current database?')
def init_db(force):
    if not force:
        try:
            current_app.open_instance_resource(current_app.config["DATABASE"], "rb").close()
            return
        except OSError:
            pass

    print("Initializing database...")
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)