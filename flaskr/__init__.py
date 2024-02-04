import os

from flask import Flask

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
        # __name__ is the current Python module
        # inst_rel_config means the config files are rel to the instance folder
    # Def config settings for the app:
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # A route and simple page that says 'hello'
    @app.route('/hello')
    def hello():
        return 'Hello, world!'
    
    # Import the db file used to manage the database
    from . import db
    # Initialize the database
    db.init_app(app)

    # Import and register the auth blueprint
    from . import auth
    app.register_blueprint(auth.bp)
    
    
    return app