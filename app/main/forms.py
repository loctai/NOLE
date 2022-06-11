from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField,SelectField,IntegerField,MultipleFileField,FloatField
from wtforms.validators import Required, Length ,Regexp,Email, DataRequired, EqualTo
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired 
from flask_babel import _, lazy_gettext as _l
from app.utils.recaptcha3 import Recaptcha3Field
class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me' ,validators=[Length(0, 100)])
    submit = SubmitField('Submit', id="btn")

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64),Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,'Usernames must have only letters, ''numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', choices=[('admin','Admin'),('user','User')])
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit' ,id="btn" )

class PostForm(FlaskForm):
    title =StringField('Post Title', validators=[Required()])
    summary =TextAreaField('Post Summary', validators=[Required()])
    image = FileField('Post Image')
    body =TextAreaField('Post Body', id="editor1", validators=[Required()])
    Submit1 = SubmitField('Post', id="btn")
    
class CommentForm(FlaskForm):
    body = StringField( validators=[Required()])
    submit = SubmitField('Submit' , id="btn")

class PropertyForm(FlaskForm):
    title =StringField('Property Title', validators=[Required()])
    category = SelectField('Category', choices=[('For Sale','For Sale'),('For Rent','For Rent')])
    address = StringField('Address', validators=[Length(0, 64)])
    price = FloatField('Price', validators=[])
    body = TextAreaField('Description' , id="editor1")
    images = MultipleFileField('Add Images')
    submit1= SubmitField('Submit' , id="btn")

class InvestForm(FlaskForm):
    # payment = StringField(_('Payment system'), validators=[Required()])
    ch_payment = [('TRX', 'Tron'),('BTC', 'Bitcoin'),('ETH', 'Ethereum'),('USDT', 'Tether (ERC20)')]
    payment = SelectField(_('Payment system'), choices=ch_payment,validators=[DataRequired()], default='TRX')
    amount = IntegerField(_('Amount Invest'), validators=[Required()])
    submit = SubmitField(_('Replenish') , id="btn")
class withdrawCommissionForm(FlaskForm):
    # payment = StringField(_('Payment system'), validators=[Required()])
    ch_payment = [('QTC', 'Nole')]
    payment_system = SelectField(_('Payment system'), choices=ch_payment,validators=[DataRequired()], default='QTC')
    amount_usd = FloatField(_('Amount'), validators=[Required()])
    code = StringField(_('Code'), validators=[Required()])
    otp = StringField(_('Code'), validators=[Required()])
    address =StringField('Address', validators=[Required()])
    submit = SubmitField('Send Request' , id="btn")

class withdrawTokenForm(FlaskForm):
    # payment = StringField(_('Payment system'), validators=[Required()])
    ch_payment = [('COIN', 'QTC Wallet'), ('COIN_REWARD', ' QTC Reward')]
    wallet = SelectField('Choose Wallet', choices=ch_payment,validators=[DataRequired()], default='COIN')
    code = StringField(_('Code'), validators=[Required()])
    otp = StringField(_('Code'), validators=[Required()])
    amount = FloatField(_('Amount'), validators=[Required()])
    address =StringField('Address', validators=[Required()])
    submit = SubmitField('Send Request' , id="btn")

class convertTokenForm(FlaskForm):
    # payment = StringField(_('Payment system'), validators=[Required()])
    ch_to_wallet = [('ETH', 'Ethereum'), ('TRX', 'Tron')]
    to_wallet = SelectField(_('To wallet'), choices=ch_to_wallet,validators=[DataRequired()], default='ETH')
    amount_from = FloatField(_('Amount'), validators=[Required()])
    submit = SubmitField('Send Request' , id="btn")

class ResetPasswordForm(FlaskForm):
    old_password = PasswordField(_l('Current Password'), validators=[Required()])
    password = PasswordField(_l('Password'), validators=[ Required(), Length(8, 15)])
    password2 = PasswordField(_l('Repeat Password'), validators=[Required(), EqualTo('password')])
    submit = SubmitField(_l('Save'), id='btn')
class walletAddressForm(FlaskForm):
    coin_address = StringField('QTC Address', validators=[])
    eth_address = StringField('ETH Address', validators=[])
    code = StringField(_('Code'), validators=[Required()])
    # usdt_address = StringField('USDT Address', validators=[])
    trx_address = StringField('TRX Address', validators=[])
    submit = SubmitField(_l('Save'), id='btn')


class Form2FA(FlaskForm):
    otp = IntegerField(_('Input code from application'), validators=[Required()])
    submit = SubmitField(_l('Submit'), id='btn')


class KycForm(FlaskForm):
    fullname =StringField('Full Name', validators=[Required()])
    gender = SelectField('Gender', choices=[('Male','Male'),('Female','Female')], validators=[Required()])
    country =SelectField('Country or Origin',choices=[('')], validators=[Required()])
    passport =StringField('Passport/ID', validators=[Required()])
    front = FileField('Front Side' , validators=[Required()])
    back = FileField('Back Side' , validators=[Required()])
    selfie = FileField('Selfie with photo' , validators=[Required()])
    submit = SubmitField('Submit', id="btn")

class FormAvatar(FlaskForm):
    avatar = FileField('Avatar' , validators=[Required()])
    submit = SubmitField('Submit', id="btn")

class ContactForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    email = StringField("Email: ", validators=[Required(), Length(1, 64),Email()])
    message = TextAreaField("Message", validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit")

class withdrawCryptoForm(FlaskForm):
    # payment = StringField(_('Payment system'), validators=[Required()])
    _currency = StringField("Currency: ", validators=[DataRequired()])
    code = StringField(_('Code'), validators=[Required()])
    otp = StringField(_('Code'), validators=[Required()])
    amount = FloatField(_('Amount'), validators=[Required()])
    address =StringField('Address', validators=[Required()])