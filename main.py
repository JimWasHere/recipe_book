from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_gravatar import Gravatar
from forms import CreateRecipeForm, RegisterForm, LoginForm, CommentForm
from functools import wraps

import os
# future_db = os.environ.get("DATABASE_URL", "sqlite:///blog.db")
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(25)
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///cookbook.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    posts = relationship("RecipePost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


class RecipePost(db.Model):
    __tablename__ = "recipe_posts"
    id = db.Column(db.Integer, primary_key=True)

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    # author = db.Column(db.String(250), nullable=False)

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    category = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    process = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    comments = relationship("Comment", back_populates="parent_post")


class Cookbook(db.Model):
    __tablename__ = "user_cookbooks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipe_posts.id"))
    category = db.Column(db.String(250), nullable=False)


class Cupboard(db.Model):
    __tablename__ = "user_cupboard"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    category = db.Column(db.String(250), nullable=False)
    item = db.Column(db.String(250), nullable=False)
    size = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(100))

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = relationship("User", back_populates="comments")

    post_id = db.Column(db.Integer, db.ForeignKey("recipe_posts.id"))
    parent_post = relationship("RecipePost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


db.create_all()
login_manager = LoginManager()
login_manager.init_app(app)


gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def get_all_recipes():
    recipes = RecipePost.query.all()
    print(recipes)
    recipes = None
    return render_template("index.html", all_recipes=recipes)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("You've already signed up, try logging in instead. :)")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("get_all_recipes"))
    return render_template("register.html", form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email or does not exist in the system.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Incorrect Password")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('get_all_recipes'))
        return render_template("login.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
