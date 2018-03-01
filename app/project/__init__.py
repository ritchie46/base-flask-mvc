from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_pyfile("../instance/flask.cfg")

db = SQLAlchemy(app)

# password encryption
bcrypt = Bcrypt(app)

# https://flask-login.readthedocs.io/en/latest/
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'

from project.models import User


@login_manager.user_loader
def load_user(user_id):
    # sqlalchemy query
    return User.query.filter(User.id == int(user_id)).first()

# mail
mail = Mail(app)

from project.users.views import bp as users_bp
app.register_blueprint(users_bp)


