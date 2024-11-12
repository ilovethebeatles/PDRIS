from flask import Flask, render_template, redirect, url_for, request, make_response, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask import jsonify
import requests 
import uuid
from urllib.parse import urlparse

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@db:3306/web_application'
db = SQLAlchemy(app)


class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    cookie = db.Column(db.String(256), nullable=True)
    avatar_url = db.Column(db.String(256), nullable=True)


class SessionCookies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cookie = db.Column(db.String(256), nullable=True)
    username = db.Column(db.String(256), nullable=False)
    last_login = db.Column(db.TIMESTAMP, nullable=True)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, nullable=True)



@app.route('/')
def Home():
    return render_template('index.html')



@app.route('/login')
def GetLogin():
    return render_template('auth.html')


def CheckTime(session_cookie):
    return session_cookie.last_login + timedelta(hours = 2) >= datetime.now()


@app.route('/login', methods=['POST'])
def PostLogin():
    login = request.form['username']
    password = request.form['password']
    user = users.query.filter_by(username=login, password=password).first()
    if user:
        unique_cookie = str(uuid.uuid4())
        expiration_time = datetime.now() + timedelta(hours = 2)
        response = make_response(redirect('my_account'))
        response.set_cookie('session_cookie', unique_cookie, max_age=7200, expires=expiration_time.timestamp())
        user.cookie = unique_cookie
        SessionCookies.query.filter_by(username = login).delete()
        session_cookie = SessionCookies(cookie = unique_cookie, username = login, last_login = expiration_time)
        db.session.add(session_cookie);
        db.session.commit()

        return response
    else:
        return 'Invalid username or password'


@app.route('/register', methods=['POST'])
def PostRegister():
    login = request.form['username']
    password = request.form['password']
    
    new_user = users(username=login, password=password, role='user');

    db.session.add(new_user)

    db.session.commit()

    return redirect("/login")



@app.route('/my_account')
def MyAccount():
    user_cookie = request.cookies.get('session_cookie')

    user = users.query.filter_by(cookie=user_cookie).first()
    if user:
        session_cookie = SessionCookies.query.filter_by(cookie = user_cookie).first()
        if CheckTime(session_cookie):
            if(user.role == "admin"):
                return redirect('/admin')
            return render_template('my_account.html', user = user)
    
    return redirect('/login')


@app.route('/register')
def GetRegister():
    return render_template('register.html')



@app.route('/logout')
def LogOut():
    user_cookie = request.cookies.get('session_cookie')
    user = users.query.filter_by(cookie=user_cookie).first()
    if user:
        user.cookie = None
        cookie_to_delete = SessionCookies.query.filter_by(cookie=user_cookie).first()
        db.session.delete(cookie_to_delete)
        db.session.commit()
        response = make_response(redirect('/'))
        response.set_cookie('session_cookie', user_cookie, max_age=7200, expires=datetime.now() - timedelta(days=1))
        return response
    else:
        return redirect('/login')



@app.route('/my_posts')
def MyPosts():
    user_cookie = request.cookies.get('session_cookie')
    user = users.query.filter_by(cookie=user_cookie).first()
    if user:
        session_cookie = SessionCookies.query.filter_by(cookie=user_cookie).first()
        if not CheckTime(session_cookie):
            return redirect('/my_account')

        user_posts = Posts.query.filter_by(author=user.username).all()
        return render_template('my_posts.html', posts=user_posts)
    else:
        return redirect('/login')



@app.route('/add_post', methods=['POST'])
def AddPost():
    user_cookie = request.cookies.get('session_cookie')
    user = users.query.filter_by(cookie=user_cookie).first()
    if user:
        content = request.form['content']
        new_post = Posts(author=user.username, content=content)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/my_posts')
    else:
        return redirect('/login')


@app.route('/upload_avatar', methods=['POST'])
def UploadAvatar():
    user_cookie = request.cookies.get('session_cookie')
    user = users.query.filter_by(cookie=user_cookie).first()
    if user:
        session_cookie = SessionCookies.query.filter_by(cookie=user_cookie).first()
        if not CheckTime(session_cookie):
            return redirect('/my_account')

        avatar_url = request.form['avatar_url']
        answer_on_request = requests.get(avatar_url)

        
        user.avatar_url = avatar_url
        db.session.commit()
        return redirect('/my_account')
    return redirect('/login')



@app.route('/admin')
def GetAdmin():
    user_cookie = request.cookies.get('session_cookie')
    user = users.query.filter_by(cookie=user_cookie).first()
    if(user):
        session_cookie = SessionCookies.query.filter_by(cookie=user_cookie).first()
        if(not CheckTime(session_cookie) or user.role != 'admin'):
            return redirect('/my_account')

        return render_template('admin.html')

    return redirect('/my_account')


def IsDigit(value):
    try:
        value = int(value)
        return True
    except ValueError:
        return False

@app.route('/set_level')
def SetLevel():
    user_cookie = request.cookies.get('session_cookie')
    user = users.query.filter_by(cookie=user_cookie).first()
    if user:
        session_cookie = SessionCookies.query.filter_by(cookie = user_cookie).first()
        if CheckTime(session_cookie):
            new_level = request.args.get('level')
            response = make_response(redirect('my_account'))
            if(not IsDigit(new_level)):
                new_level = 1
            response.set_cookie('level', new_level)
            return response


    return redirect('my_account')

@app.route('/admin/reset_password')
def ResetPassword():
    user_cookie = request.cookies.get('session_cookie')
    user = users.query.filter_by(cookie=user_cookie).first()

    if(not user):
        return redirect('/my_account')
  
    if(user.role == 'admin' or request.remote_addr == '127.0.0.1' or request.remote_addr == '::1'):
        username = request.args.get('username')
        password = request.args.get('password')
        change_user = users.query.filter_by(username=username).first()
        change_user.password = password
        db.session.commit()
        return redirect('/')
    else:
        return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug = True)
