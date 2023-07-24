from flask import Flask, render_template, request, redirect, flash
from flask_login import login_required, current_user, LoginManager, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import re

from models import db, Post, MyUser
app = Flask(__name__, static_url_path='/static')
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'static/upload_pics'
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return MyUser.select().where(MyUser.id==int(user_id)).first()

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response


@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = MyUser.select().where(MyUser.email==email).first()
        if not user or not check_password_hash(user.password,password):
            flash('Please,check your login details and try again.')
            return redirect('/login/')
        else:
            login_user(user)
            return redirect('/')
    return render_template('login.html')



@app.route('/logout/')
def logout():
    logout_user()
    return render_template('login.html')




def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    return True


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        age = request.form['age']
        full_name = request.form['full_name']
        password = request.form['password']
        profile_picture = request.files['profile_picture']
        if profile_picture and allowed_file(profile_picture.filename):
            filename = secure_filename(profile_picture.filename)
            profile_picture.save(os.path.join(UPLOAD_FOLDER, filename))

        else:
            filename = 'test1.png'

        user = MyUser.select().where(MyUser.email == email).first()
        if user:
            flash('email address already exists')
            return redirect('/register/')
        if MyUser.select().where(MyUser.username == username).first():
            flash('username already exists')
            return redirect('/register/')
        else:
            if validate_password(password):
                MyUser.create(
                    email=email,
                    username=username,
                    age=age,
                    password=generate_password_hash(password),
                    full_name=full_name,
                    profile_picture=filename
                )
                return redirect('/login/')
            else:
                flash('wrong password')
                return redirect('/register/')
    return render_template('register.html')


@app.route('/create/',methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        Post.create(
            title = title,
            author = current_user,
            content = content
        )
        return redirect('/')
    return render_template('create.html')


@app.route('/<int:id>/')
def get_post(id):
    post = Post.select().where(Post.id==id).first()
    if post:
        return render_template('post_detail.html',post=post)
    return f'Post with id = {id} does not exist'



@app.route('/')
def index():
    all_posts = Post.select()
    return render_template('index.html',posts=all_posts)


@app.route('/<int:id>/update/',methods=('GET','POST'))
@login_required
def update(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if post:
            if current_user==post.author:
                title = request.form['title']
                content = request.form['content']
                obj = Post.update({
                    Post.title: title,
                    Post.content: content,
                }).where(Post.id==id)
                obj.execute()
                return redirect(f'/{id}')
            return f'You are not autor of this post!'
        return f'post with id = {id} does not exist'
    return render_template('update.html',post=post)



# @app.route('/changing/',methods=('GET','POST'))
# @login_required
# def prifile_update():
#     if request.method == 'POST':
#         title = request.form['Name']
#         content = request.form['User']
#         obj = MyUser.update({
#             MyUser.title: title,
#             MyUser.content: content,
#         }).where(MyUser.id==current_user.id)
#         obj.execute()
#         return redirect(f'/current_profile/')
#     return render_template('change.html', user=current_user)

sample_user = MyUser.get_by_id(1)
@app.route('/changing/', methods=['GET', 'POST'])
def change_information():
    if request.method == 'POST':
        new_username = request.form['new_username']
        new_email = request.form['new_email']
        new_age = request.form['new_age']
        new_fullname = request.form['new_fullname']
        sample_user.username = new_username
        sample_user.email = new_email
        sample_user.age = int(new_age)
        sample_user.full_name = new_fullname
        sample_user.save()
        return redirect('/current_profile/')

    return render_template('change.html', user=sample_user)



@app.route('/current_profile/')
@login_required
def profile():
    user = MyUser.select().where(MyUser.id == current_user.id).first()
    if user:
        posts = Post.select().where(Post.author == user)
        return render_template('profile.html', user=user, posts=posts)
    else:
        return f'User not found'




@app.route('/<int:id>/delete/', methods=('GET', 'POST'))
@login_required
def delete(id):
    post = Post.select().where(Post.id==id).first()
    if request.method == 'POST':
        if post:
            if current_user==post.author:
                post.delete_instance()
                return redirect('/')
            return f'you are not author of this post'
        return f'Post with id = {id} does not exists'
    return render_template('delete.html', post=post)


if __name__  == '__main__':
    app.run(debug=True)