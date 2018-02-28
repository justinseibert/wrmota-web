from flask import current_app, request
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import TextField, PasswordField, HiddenField, BooleanField, SelectField
from wtforms.validators import InputRequired, ValidationError, Email, DataRequired, EqualTo
from werkzeug.utils import secure_filename

from wrmota.api import hashes as Hash
from wrmota.api import sanitize as Sanitize
from wrmota import database as Database

class LoginForm(FlaskForm):
    username = TextField(label="User", validators=[InputRequired()], id="loginUser")
    password = PasswordField(label="Pass", validators=[InputRequired()], id="loginPass")

    def validate(self):
        if not super(LoginForm,self).validate():
            return False

        users = current_app.config['USERS']
        user = self.username.data

        if user in users:
            return users[user] == Hash.protect(self.password.data, current_app.config['SECRET_KEY'])
        else:
            return False

class CreateUserForm(FlaskForm):
    first_name = TextField(label="First Name", id="createFirst")
    last_name = TextField(label="Last Name", id="createLast")
    username = TextField(label="User Name", validators=[InputRequired()], id="createUser")
    password = PasswordField(label="Password", validators=[InputRequired()], id="createPassword")
    confirm = PasswordField(label="Confirm Password", validators=[InputRequired(), EqualTo('password', message="Passwords do not match")], id="createConfirm")
    email = TextField('email', validators=[Email(),DataRequired()], id="createEmail")
    recaptcha = RecaptchaField('recaptcha')

class LoginUserForm(FlaskForm):
    username = TextField(label="User Name", validators=[InputRequired()], id="loginUser")
    password = PasswordField(label="Password", validators=[InputRequired()], id="loginPassword")

class EmailForm(FlaskForm):
    email = TextField('email', validators=[Email(),DataRequired()])
    recaptcha = RecaptchaField('recaptcha')

class EditArtistForm(FlaskForm):
    artist_id = HiddenField('artist_id',id="EditArtistId")
    artist_meta_id = HiddenField('artist_meta_id',id="EditArtistMetaId")
    artist = TextField(label="Artist", id="EditArtist")
    email = TextField(label="Email", validators=[Email()], id="EditEmail")
    website = TextField(label="Website", id="EditWebsite")
    curator = SelectField(label="Curator", id="EditCurator")
    location = TextField(label="Location", id="EditLocation")

    confirmed = BooleanField(id="EditConfirmed")
    assigned = BooleanField(id="EditAssigned")
    info_sent = BooleanField(id="EditInfoSent")
    touched_base = BooleanField(id="EditTouchedBase")
    art_received = BooleanField(id="EditArtReceived")
    visitor = BooleanField(id="EditVisitor")

def handle_upload(files,filetypes):
    uploads = []
    failed = []
    for f in files:
        name = secure_filename(files[f].filename)
        if allowed_file(name, filetypes):
            media = Sanitize.media_file(name)
            media['filetype'] = filetypes

            try:
                files[f].save(media['full_path'])
                uploads.append(media)
                print('UPLOAD: succesfully saved {} to {}'.format(name,media['full_path']))
            except:
                failed.append(name)
                print('UPLOAD: failed to save {}'.format(name))
        else:
            failed.append(name)
            print('UPLOAD: incorrect filetype, failed to save {}'.format(name))

    return {
        'uploads': uploads,
        'failed': failed
    }

def allowed_file(filename, extensions):
    allowed = current_app.config['ALLOWED_FILES'][extensions]
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def get_curators():
    curators = Database.get_curators_list()
    return [(c,c) for c in curators]

def handle_error(form):
    return {
        'errors': form.errors,
        'message': 'There was an error with your form.'
    }
