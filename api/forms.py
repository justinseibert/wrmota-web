from flask import current_app
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, ValidationError, Email, DataRequired

from wrmota.api import hashes as Hash

class LoginForm(FlaskForm):
    username = TextField(label='User', validators=[InputRequired()], id='loginUser')
    password = PasswordField(label='Pass', validators=[InputRequired()], id='loginPass')

    def validate(self):
        if not super(LoginForm,self).validate():
            return False

        users = current_app.config['USERS']
        user = self.username.data

        if user in users:
            return users[user] == Hash.protect(self.password.data, current_app.config['SECRET_KEY'])
        else:
            return False

class EmailForm(FlaskForm):
    email = TextField('email', validators=[Email(),DataRequired()])
    recaptcha = RecaptchaField('recaptcha')
