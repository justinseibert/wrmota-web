import os
from flask import Flask, g, render_template, flash
from flask_assets import Environment, Bundle
from flask_wtf.csrf import CSRFProtect

from wrmota import config_public as ConfigPublic
from wrmota import config_private as ConfigPrivate

def create_app(config='PRODUCTION', app_name=None):
    app_name = ConfigPublic.DefaultConfig.PROJECT
    public = ConfigPublic.get_config(config)
    private = ConfigPrivate.get_config(config)
    blueprints = public.BLUEPRINTS
    extensions = public.EXTENSIONS

    app = Flask(app_name)
    assets = Environment(app)
    csrf = CSRFProtect(app)

    configure_app(app, public, private)
    configure_blueprints(app, blueprints)
    configure_extensions(assets, extensions)

    configure_hook(app)
    configure_logging(app)
    configure_error_handlers(app)

    csrf.exempt('wrmota.views.api.get_json_data')
    csrf.exempt('wrmota.views.api.accept_email_data')

    return app

def configure_app(app, public,private):
    app.config.from_object(private)
    app.config.from_object(public)
    app.url_map.default_subdomain = ''

def configure_blueprints(app, blueprints):
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

def configure_extensions(assets, extensions):
    for extension in extensions:
        try:
            depends = extension['depends']
        except:
            depends = ''

        assets.register(extension['name'], Bundle(
            *extension['bundle'],
            filters=extension['filters'],
            output=extension['output'],
            depends=depends
        ))


def configure_hook(app):
    @app.teardown_appcontext
    def close_db(error):
        if hasattr(g, 'sqlite_db'):
            g.sqlite_db.close()

def configure_logging(app):
    pass

def configure_error_handlers(app):
    @app.errorhandler(500)
    def server_error_page(error):
        type = 500
        message = 'uh oh, server thing happened'
        return render_template('site/error.html', message=message, type=type), 500

    @app.errorhandler(503)
    def server_error_page(error):
        type = 503
        message = 'maintaining stuff, come back later'
        return render_template('site/error.html', message=message, type=type), 503

    @app.errorhandler(404)
    def notfound_error_page(error):
        type = 404
        message = 'nope, nothing here'
        return render_template('site/error.html', message=message, type=type), 404

    @app.errorhandler(403)
    def forbidden_error_page(error):
        type = 403
        message = 'sorry, not allowed'
        return render_template('site/error.html', message=message, type=type), 403
