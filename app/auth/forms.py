from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Email, Length , Regexp , EqualTo
from wtforms import ValidationError, validators
from app import mongo
from flask_babel import _, lazy_gettext as _l
from app.utils.recaptcha3 import Recaptcha3Field
validation_error_msgs = {
    'username_invalid' : 'username can be a combination of letters, dots, ' \
                         'numbers or underscores only',
    'username_used' : 'username already used',
    'email_used' : 'email is already registered',
    'email_invalid' : 'make sure you supplied your registered email address',
    'email_not_registered' : 'no user exists with this email address'
}
def username_validator(self, field):
        username = field.data
        if len(username) < 3:
            raise ValidationError(
                _('Username must be at least 3 characters long'))
        valid_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._'
        chars = list(username)
        for char in chars:
            if char not in valid_chars:
                raise ValidationError(
                    _("Username may only contain letters, numbers, '-', '.' and '_'"))

class LoginForm(FlaskForm):
    # email = StringField(_l('Email'), validators=[Required(),Length(1,64),Email()])
    username = StringField(_l('Username'), validators=[Required()])
    password =PasswordField(_l('Password') ,validators=[Required()])
    remember_me =BooleanField(_l('Keep me logged in'))
    # recaptcha = Recaptcha3Field(action="TestAction", execute_on_load=True)
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('Login'), id='btn')
 
class SignupForm(FlaskForm):
    email = StringField(_l('Email'), validators=[Required(), Length(1, 64),Email()])
    name = StringField(_l('Username'), validators=[
        validators.DataRequired(_('Username is required')),
        username_validator
    ])
    p_node = StringField(_l('Sponsor'), validators=[])
    password = PasswordField(_l('Password') , validators=[ Required(), Length(8, 15), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(_l('Confirm password'), validators=[Required()])
    # recaptcha = Recaptcha3Field(action="TestAction", execute_on_load=True)
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('SignUp'), id='btn')
    def validate_email(self, email):
        users = mongo.db.Users
        user = users.find({'email': email.data }).count()
        if int(user) >= 5:
            raise ValidationError(_l('Please use a different email address.'))
    def validate_name(self, name):
        users = mongo.db.Users
        user = users.find_one({'name': name.data.lower() })
        if user is not None:
            raise ValidationError(_l('This Username is already in use.'))

class SignupFormTree(FlaskForm):
    email = StringField(_l('Email'), validators=[Required(), Length(1, 64),Email()])
    name = StringField(_l('Username'), validators=[
        validators.DataRequired(_('Username is required')),
        username_validator
    ])
    p_node = StringField(_l('Sponsor'), validators=[Required()])
    p_binary = StringField('Binary', validators=[Required()])
    position = StringField('Position', validators=[])
    password = PasswordField(_l('Password') , validators=[ Required(), Length(8, 15), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField(_l('Confirm password'), validators=[Required()])
    # recaptcha = Recaptcha3Field(action="TestAction", execute_on_load=True)
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('SignUp'), id='btn')
    def validate_name(self, name):
        users = mongo.db.Users
        user = users.find_one({'name': name.data.lower() })
        if user is not None:
            raise ValidationError(_l('This Username is already in use.'))
    def validate_email(self, email):
        users = mongo.db.Users
        user = users.find({'email': email.data }).count()
        if int(user) >= 5:
            raise ValidationError(_l('Please use a different email address.'))
    def validate_p_node(self, p_node):
        users = mongo.db.Users
        user = users.find_one({'username': p_node.data.upper() })
        if user is None:
            raise ValidationError(_l('Sponsor not found'))
    def validate_p_binary(self, p_binary):
        users = mongo.db.Users
        user = users.find_one({'username': p_binary.data.upper() })
        if user is None:
            raise ValidationError(_l('Binary not found'))



class ResetPasswordRequestForm(FlaskForm):
    username = StringField(_l('Username'), validators=[Required()])
    # recaptcha = Recaptcha3Field(action="TestAction", execute_on_load=True)
    recaptcha = RecaptchaField()
    submit = SubmitField(_l('Request Password Reset'), id='btn')

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[Required()])
    password2 = PasswordField(_l('Repeat Password'), validators=[Required(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'), id='btn')

class FormAuthy(FlaskForm):
    code = StringField(_l('2FA Code'), validators=[Required()]) 
    # recaptcha = RecaptchaField()
    submit = SubmitField(_l('Login'), id='btn')