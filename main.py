import os
from dotenv import load_dotenv
from flask import Flask
from flask_bootstrap import Bootstrap5
from routes import routes

def create_app():
    app = Flask(__name__)

    load_dotenv()
    SECRET_KEY = os.getenv("SECRET_KEY")
    app.config["SECRET_KEY"] = SECRET_KEY

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    Bootstrap5(app)
    app.register_blueprint(routes)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()