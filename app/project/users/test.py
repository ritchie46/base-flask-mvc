import unittest
from itsdangerous import URLSafeTimedSerializer
from project.test import InitTest
from project import app


class UsersTest(InitTest):

    def test_user_registration_form_displays(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Email", response.data)

    def test_valid_user_registration(self):
        response = self.register()
        self.assertIn(b'Thanks for registering!', response.data)

    def test_duplicate_email_user_registration(self):
        self.register()
        response = self.register()
        self.assertIn(b'is already registered.', response.data)

    def test_missing_field_user_registration(self):
        response = self.register(confirm_pw='')
        self.assertIn(b'This field is required.', response.data)

    def test_login_form_displays(self):
        response = self.app.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('log in', response.data.decode('utf-8').lower())

    def test_valid_login(self):
        self.register()
        response = self.login()
        self.assertIn(b"Please confirm your email first", response.data)

    def test_login_without_registering(self):
        response = self.login()
        self.assertIn(b'Error, incorrect login credentials.', response.data)

    def test_login_after_logout(self):
        # should display the login page when following /logout (when logged in as well as logged out)
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Log in', response.data)

    def test_confirmation_token(self):
        response = self.register_with_email()
        self.assertIn(b'Thank you for confirming your email address!', response.data)

    def test_user_profile_page(self):
        self.register_with_email()
        self.login()
        response = self.app.get('/user_profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Statistics', response.data)

    def test_user_profile_without_logging_in(self):
        response = self.app.get('/user_profile')
        self.assertEqual(response.status_code, 302)

    def test_change_email_page(self):
        self.register_with_email()
        self.login()
        response = self.app.get('/email_change')
        self.assertIn(b'Please enter your new email address:', response.data)

    def test_change_email_address(self):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps([self.email, 'new_email'], salt='email-confirmation')

        self.register_with_email()
        self.login()
        self.app.get(f'/confirm/{token}')
        response = self.app.get('/user_profile')
        self.assertIn(b'new_email', response.data)

    def test_change_email_with_existing_email_address(self):
        self.register_with_email()
        self.login()
        response = self.app.post('/email_change', data=dict(email=self.email))
        self.assertIn(b'Sorry, that email is already registered.', response.data)

    def test_change_password_not_logged_in_redirect(self):
        response = self.app.get('/password_change', follow_redirects=True)
        self.assertIn(b'Log in', response.data)

    def test_change_password(self):
        self.register_with_email()
        self.login()
        response = self.app.post('/password_change', data=dict(old_password=self.password,
                                                               password='new_password',
                                                               confirm='new_password'))
        self.assertIn(b'Password had been updated!', response.data)
        self.password = 'new_password'
        response = self.login()
        self.assertIn(self.email.encode(), response.data)

    def test_admin_view_users_valid_access(self):
        self.create_admin()
        self.login()
        response = self.app.get('/admin_view_users')
        self.assertIn(b'Administrative page', response.data)

    def test_admin_view_users_invalid_access(self):
        self.login()
        response = self.app.get('/admin_view_users', follow_redirects=True)
        self.assertIn(b'Log in', response.data)


if __name__ == "__main__":
    unittest.main()