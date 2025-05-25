from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Post Image', validators=[FileAllowed(['jpg', 'png'])])

class SlideForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    picture_desktop = FileField('Imagem Desktop', validators=[FileAllowed(['jpg', 'png'])])
    picture_mobile = FileField('Imagem Mobile', validators=[FileAllowed(['jpg', 'png'])])

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password (deixe vazio para não alterar)', validators=[Optional()])
    submit = SubmitField('Salvar')

