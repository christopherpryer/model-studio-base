from flask import Flask, render_template
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext
from flask_login import LoginManager
import click
import os

from .utils import url_for, timestamp

db = SQLAlchemy()
from . import models

login_manager = LoginManager()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load instance config if it exists when not testing
        app.config.from_object('config.Config')
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    assets = Environment(app)
    Environment.auto_build = True
    Environment.debug = False
    less_bundle = Bundle('less/*.less',
                         filters='less,cssmin',
                         output='dist/css/styles.css',
                         extra={'rel': 'stylesheet/less'})
    js_bundle = Bundle('js/*.js',
                       filters='jsmin',
                       output='dist/js/main.js')
    assets.register('less_all', less_bundle)
    assets.register('js_all', js_bundle)

    db.init_app(app)

    @click.command('init-db')
    @with_appcontext
    def init_db_command():
        # clear existing data + create new tables
        db.drop_all()
        db.create_all()
        db.session.commit()

        # set up owner (to reset on go-live)
        user = models.User(
            email='owner@email.com',
            password='testing',
            role='Admin')
        db.session.add(user)
        db.session.commit()
        click.echo('Initialized the database.')

    app.cli.add_command(init_db_command)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import main
    app.register_blueprint(main.bp)

    from .dashboards import example_dashapp
    app = example_dashapp.init_app(app)

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.filter_by(id=user_id).first()

    return app
