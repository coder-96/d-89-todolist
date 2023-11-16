from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


# forms

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    sign_up = SubmitField("Sign up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


# class AdminPasswordForm(FlaskForm):
#     password = PasswordField("Password", validators=[DataRequired()])
#     confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
#     submit = SubmitField("Change Password")


class CreateTodoForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    completed = BooleanField()
    submit = SubmitField("Save")
