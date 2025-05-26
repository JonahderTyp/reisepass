import logging
import os
from pathlib import Path

from flask import Flask
from flask_socketio import SocketIO

from .database.seeds import seed_database, seed_demo

socketio = SocketIO()


def create_app():
    logging.basicConfig(level=logging.INFO)
    logging.info("Creating App")

    INSTANCE_PATH = os.path.abspath(os.path.join(
        os.path.abspath(__path__[0]), "../instance"))

    logging.info(f"Instance Path: {INSTANCE_PATH}")

    app = Flask(__name__)
    socketio.init_app(app)

    CONFIG_PATH = Path(INSTANCE_PATH) / "config.cfg"
    if CONFIG_PATH.is_file():
        app.config.from_pyfile(str(CONFIG_PATH))
        logging.info(f"Loaded Config from {CONFIG_PATH}")
        if app.config.get("DEBUG", False):
            logging.info(f"Config:{str(app.config)}")
    else:
        logging.warning(f"No Config File Found at {CONFIG_PATH}")

    from reisepass.database.db import db
    db.init_app(app)

    with app.app_context():
        db.create_all()

        NEW_DB = all(db.session.query(table).first()
                     is None for table in db.metadata.sorted_tables)

        if NEW_DB:
            logging.info("All tables are empty. Seeding database...")
            seed_database()
            seed_demo()

    from .site import site
    app.register_blueprint(site)
    from .api import api
    app.register_blueprint(api)

    return app
