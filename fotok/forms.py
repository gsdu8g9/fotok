"""
This file stores WTForms classes that incapsulate Login ans Signup forms
together with validation.
"""

from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp
import re
from .models import User

class LoginForm(Form):
    username = TextField('Username', [
        DataRequired(),
        Length(max=100, message='Username must be up to 100 characters long'),
        Regexp(r'^[\w\d]+$', message='Only unicode letters and digits are allowed in username')
    ])
    password = PasswordField('Password', [DataRequired()])

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.user = None

    def validate(self):
        valid = super(LoginForm, self).validate()
        if not valid:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            self.username.errors.append('Unknown user')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True

class SignupForm(Form):
    username = TextField('Username', [
        DataRequired(),
        Length(max=100, message='Username must be up to 100 characters long'),
        Regexp(r'^[\w\d]+$', message='Only unicode letters and digits are allowed in username')
    ])
    password = PasswordField('Password', [DataRequired()])

    def validate(self):
        valid = super(SignupForm, self).validate()
        if not valid:
            return False

        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors.append('This username is already registered')
            return False

        return True
