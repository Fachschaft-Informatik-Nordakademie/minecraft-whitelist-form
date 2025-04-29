import os

from flask import Flask, current_app
from flask_mail import Mail

mailsender = Mail()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'db.sqlite3'),
        ALLOWED_MAIL_SUFFIXES=["@nordakademie.de", "@nordakademie.org"],
        BASE_URL="http://localhost:5000",
        ADMIN_SECRET="buffalo",
        EXAROTON_API_TOKEN="",
        EXAROTON_SERVER_ID="",
        MAIL_SERVER="localhost",
        MAIL_PORT="1025",
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=False,
        MAIL_USERNAME="",
        MAIL_PASSWORD="",
        MAIL_DEFAULT_SENDER="noreply@nak-inf.de"
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    app.config.from_prefixed_env("MCWLF")
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    mailsender.init_app(app)

    from mc_whitelist_form import db, main
    db.init_app(app)
    app.register_blueprint(main.bp)

    return app
