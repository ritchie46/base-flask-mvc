import unittest
from app.project import app, db, mail
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from app.project.models import User


class InitTest(unittest.TestCase):
    # method names are hooks from unittest.TestCase

    email = 'myemail@email.com'
    password = 'mypwof6char'

    # called prior to test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        self.app = app.test_client()
        db.session.close_all()
        db.drop_all()
        db.create_all()

        mail.init_app(app)
        self.assertEqual(app.debug, False)

    # called after test is executed
    def tearDown(self):
        pass

    def register(self, confirm_pw='mypwof6char'):
        return self.app.post(
            '/register',
            data=dict(email=self.email, password=self.password, confirm=confirm_pw),
            follow_redirects=True
        )

    def register_with_email(self):
        """
        Register user via email confirmation token.
        """
        self.register(self.password)
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(self.email, salt='email-confirmation')
        return self.app.get(f"/confirm/{token}", follow_redirects=True)

    def login(self):
        return self.app.post(
            '/login',
            data=dict(email=self.email, password=self.password),
            follow_redirects=True
        )

    def create_admin(self):
        admin = User(self.email, self.password)
        admin.registration_date = datetime.now()
        admin.email_confirmed = True
        admin.role = 'admin'
        db.session.add(admin)
        db.session.commit()
        self.admin = admin