from flask import Flask, render_template
from flask_cors import CORS

from config import Config
from models import db
from routes.api import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    app.register_blueprint(api)

    @app.route("/")
    def index():
        return render_template("dashboard.html")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
