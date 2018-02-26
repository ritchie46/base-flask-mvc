from app.project import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.Binary(60), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)  # online or not
    confirmation_email_sent_date = db.Column(db.DateTime, nullable=True)
    email_confirmed = db.Column(db.Boolean, nullable=True)
    email_confirmation_date = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    registration_date = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String, default='user')

    def __init__(self, email, pw, cesd=None):
        self.email = email

        # calls the setter
        self.password_ = pw
        self.authenticated = False
        self.confirmation_email_sent_date = cesd
        self.email_confirmed = False
        self.email_confirmation_date = None
        self.last_logged_in = None
        self.current_logged_in = datetime.now()

    def __repr__(self):
        return '<User {}'.format(self.name)

    # password encryption
    @hybrid_property
    def password_(self):
        return self.password

    @password_.setter
    def password_(self, pw):
        self.password = bcrypt.generate_password_hash(pw)

    @hybrid_method
    def is_correct_password(self, pw):
        return bcrypt.check_password_hash(self.password_, pw)

    # methods required for user login (flask_login module)
    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_active(self):
        """
        All users are active.
        """
        return True

    @property
    def is_anonymous(self):
        """
        Don't support anonymous users
        """
        return False

    def get_id(self):
        return str(self.id)




