from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os 

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Ensure upload directory exists
    with app.app_context():
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        app.logger.info(f"Upload directory ensured at: {upload_folder}")


    from app import routes
    app.register_blueprint(routes.bp)

    return app
