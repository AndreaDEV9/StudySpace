from flask import Flask
from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from routes.inicio import inicio_bp
    from routes.auth import auth_bp

    app.register_blueprint(inicio_bp)
    app.register_blueprint(auth_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)