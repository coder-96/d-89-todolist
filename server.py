from flask import Flask, render_template, url_for, flash, redirect, request
from flask_bootstrap import Bootstrap
# from flask_ckeditor import CKEditor
# from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreateTodoForm, RegisterForm, LoginForm
# from flask_gravatar import Gravatar

# to create admin_only decorator
from functools import wraps
from flask import abort

import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"
# ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    todos = relationship("Todo", back_populates="user")

    def __repr__(self):
        return f'<User {self.name}>'


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="todos")


with app.app_context():
    db.create_all()

# # Create admin-only decorator
# def admin_only(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # If id is not 1 then return abort with 403 error
#         if current_user.id != 1:
#             return abort(403)
#         return f(*args, **kwargs)
#
#     return decorated_function


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for("login"))
        hashed_salted_password = generate_password_hash(method="pbkdf2:sha256", salt_length=8,
                                                        password=form.password.data)
        new_user = User(
            name=form.name.data,
            password=hashed_salted_password,
            email=form.email.data,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Find user by email entered.
        user = User.query.filter_by(email=email).first()
        # user = db.session.query(User).filter_by(email=email).first()
        if not user:
            flash("The email doesn't exist, please try again!")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again!")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/create", methods=["POST", "GET"])
@login_required
def create_todo():
    form = CreateTodoForm()
    if form.validate_on_submit():
        new_todo = Todo(
            name=form.title.data,
            completed=form.completed.data,
            user_id=current_user.id,
        )
        db.session.add(new_todo)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("todo_create.html", form=form)


@app.route('/home')
@login_required
def home():
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    # todos = db.session.query(Todo).filter_by(user_id=current_user.id).all()
    # todos = Todo.query.filter_by(user_id=current_user.id).first()
    # todos = Todo.query.all()
    return render_template("home.html", all_todos=todos, logged_in=current_user.is_authenticated)


@app.route("/update/<int:todo_id>", methods=["POST", "GET"])
@login_required
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    form = CreateTodoForm(
        title=todo.name,
        completed=todo.completed,
    )
    if form.validate_on_submit():
        todo.name = form.title.data
        todo.completed = form.completed.data
        # d = request.form["title"]/
        # d = request.form.get("title")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("update_todo.html", form=form)


@app.route("/delete/<int:todo_id>")
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/about')
@login_required
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


if __name__ == "__main__":
    app.run(debug=True)
