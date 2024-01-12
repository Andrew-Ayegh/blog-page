import os
from functools import wraps
import secrets
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import Nullable
from forms import CreatePostForm, LoginForm, RegistrForm, CommentForm
import requests
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from libgravatar import Gravatar
from flask_migrate import Migrate, upgrade

app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_PKG_TYPE'] = 'full'
year = datetime.now().year
Bootstrap5(app)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', "sqlite:///posts.db")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
# app.secret_key = secrets.token_hex()
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager(app)


# migrate = Migrate(app, db)
gravatar = Gravatar("example@email.com")



# CONFIGURE TABLES
class BlogPost( db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    
    
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    
    # foreign key
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # author-post relationship
    author = relationship("User", back_populates="posts")
    # comment-post relationship
    comments = relationship('Comment', back_populates='parent_post')


# TODO: Create a User table for all your registered users. 
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id  = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    # post-author relationship
    posts = relationship("BlogPost", back_populates='author')
    # user-comment relationship
    comments = relationship('Comment', back_populates='comment_author')
    

# TODO: Create comment table for all users
class Comment(UserMixin, db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250))
    # comment author id
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # post id
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'))
    # post-comment relationship
    parent_post = relationship("BlogPost", back_populates="comments")
    # author-comment relationship
    comment_author = relationship("User", back_populates='comments')
    

with app.app_context():
    db.create_all()



@login_manager.user_loader
def loader_user(user_id):
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()

def admin_only(func):
    '''create admin previledges'''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)
    return decorated_function

@app.route("/")
def homepage():
    
    posts = db.session.execute(db.select(BlogPost)).scalars().all()
    form = CreatePostForm()
    return render_template("index.html", header="The Geek Gazette", header_text="A Blog By Your's Truly", year=year, image='home-bg.jpg', blog_posts=posts, form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    
    form = RegistrForm()
    if form.validate_on_submit():
        email = form.email.data
        password = generate_password_hash(password=form.password.data, method="pbkdf2:sha256", salt_length=8)
        name= form.name.data
        result = db.session.execute(db.select(User).where(User.email==email)).scalar()
        if result:
            flash(message="User already registered. Login", category='info')
            return redirect(url_for('login'))
        new_user = User(
            email=email,
            password=password,
            name=name
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('homepage'))
    return render_template('register.html', image="register-bg.jpg", form=form)

@app.route("/login", methods=["GET", "POST"]) 
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        result = db.session.execute(db.select(User).where(User.email==email)).scalar()
        if not result:
            flash("Incorrect Email. Try again")
            return redirect(url_for('login'))
        check_password = check_password_hash(pwhash=result.password, password=password)
        if not check_password:
            flash("Incorrect Password.Try Again")
            return redirect(url_for('login'))
        login_user(result)
        return redirect(url_for('homepage'))
    return render_template('login.html', image="login-bg.jpg", header="Welcome Back", form=form)

@app.route("/about")
def about():
    return render_template("about.html", header="About Geek Gazzet", header_text="", year = year, image='about-bg.jpg')


@app.route("/post", methods=["GET", "POST"])

def post():
    '''render all the blog post in the database'''
    comment_form = CommentForm()
    id = request.args.get('id')
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == id)).scalar()
    comments = db.session.execute(db.select(Comment).where(Comment.post_id == post.id)).scalars().all()
    
    if comment_form.validate_on_submit():
        comment = comment_form.comment.data
        user_comment = Comment(
            text=comment,
            parent_post=post,
            comment_author = current_user
        )
        db.session.add(user_comment)
        db.session.commit()
        
        comments = db.session.execute(db.select(Comment).where(Comment.post_id == post.id)).scalars().all()
        # for comment in all_comment:
        #     print(comment.comment_author.name)
        
        return render_template("post.html", header_text="", year=year, image='home-bg.jpg', blog_post=post,  form=comment_form, comments=comments, gravatar=gravatar)

    return render_template("post.html", header_text="",year=year, image='home-bg.jpg' ,blog_post=post,  form=comment_form, comments=comments, gravatar=gravatar)

@app.route("/new-post", methods=['GET', 'POST'])
@login_required
def add_new_post():
    form = CreatePostForm()
    if request.method == "POST":
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body= form.body.data,
            img_url=form.img_url.data,
            date=date.today().strftime("%B %d, %Y"),
            author = current_user
        )
        db.session.add(new_post)
        db.session.commit()

        
        return redirect(url_for("homepage"))
    return render_template("make-post.html", form=form, current_user=current_user, image='home-bg.jpg')


@app.route("/delete")
@admin_only
@login_required
def delete():
    id = request.args.get('id')
    post_to_delete = db.get_or_404(BlogPost, id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('homepage'))

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']
        return "<h1>Sucessfuly sent message</h1>"
    return render_template("contact.html", header="Contact Us", header_text="", year=year, image='contact-bg.jpg')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("homepage"))




if __name__ == "__main__":
    app.run(debug=True)