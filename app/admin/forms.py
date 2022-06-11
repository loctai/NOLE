from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField,TextAreaField,SelectField,IntegerField,MultipleFileField, FloatField
from wtforms.validators import Required, Length ,Regexp,Email
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired 


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    # location = StringField('Location', validators=[Length(0, 64)])
    # about_me = TextAreaField('About me' ,validators=[Length(0, 100)])
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
    slug=StringField( validators=[Required()])
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
    price = IntegerField('Price', validators=[])
    body = TextAreaField('Description' , id="editor1")
    images = MultipleFileField('Add Images')
    submit1= SubmitField('Submit' , id="btn")

class ProfitForm(FlaskForm):
    level1 =FloatField('Level I', validators=[Required()])
    level2 =FloatField('Level II', validators=[Required()])
    level3 = FloatField('Level III', validators=[Required()])
    submit = SubmitField('Save', id="btn")    

