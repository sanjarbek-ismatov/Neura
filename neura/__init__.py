import os
from flask import Flask, render_template, g
from uuid import uuid4
from .auth import login_required


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=f'{uuid4()}',
        DATABASE=os.path.join(app.instance_path, 'database.sqlite'),
    )


    @app.route('/')
    @login_required
    def home():

        return render_template('home.html')

    from . import db, auth
    db.init_app(app)

    app.register_blueprint(auth.auth)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app