from flask import Flask, render_template,redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask import request
from datetime import datetime
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo.db'
app.config['SECRET_KEY'] = 'thisissecret'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)



class Register(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),nullable=False)
    email = db.Column(db.String(80),nullable=False)
    firstname = db.Column(db.String(80),nullable=False)
    lastname = db.Column(db.String(80),nullable=False)
    password = db.Column(db.String(80),nullable=False) 

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80),nullable=False)
    content = db.Column(db.Text(),nullable=False)  
    pub_date = db.Column(db.DateTime(),nullable=False,default=datetime.utcnow)
    author = db.Column(db.String(20),nullable=False,default='N/A')

@login_manager.user_loader
def load_user(user_id):
    return Register.query.get(int(user_id))

@app.route('/login',methods=['GET','POST']) 
def login():
    if request.method=='POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user=Register.query.filter_by(username=username).first()
        if user and password == user.password:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return('Error')              
    else:
        return render_template('login.html')


@app.route('/logout',methods=['GET','POST'])
@login_required 
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/')
def index():
    blog = Blog.query.all()
    return render_template('index.html',blog=blog)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        lst = []
        username = request.form.get('username') 
        email = request.form.get('email')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        password = request.form.get('password')
        usernames = Register.query.all()
        for un in usernames:
            lst.append(un.username)
        if (username=='' or email=='' or firstname=='' or lastname=='' or password==''):
            flash("Error: All fields are required","danger")   
            return redirect('/register')
        elif username in lst:
            flash("Error: username aleady exists!","danger")
            return redirect('/register')   
        else:    
            form = Register(username=username,email=email,firstname=firstname,lastname=lastname,password=password)
            db.session.add(form)
            db.session.commit()
            flash("User has been registered successfully","success")
            return redirect('/login')    
    return render_template('register.html')


@app.route('/blog_post',methods=['GET','POST'])
@login_required 
def blogpost():
    if request.method=='POST':
        title = request.form.get('title') 
        content = request.form.get('content')
        author = request.form.get('author')
        post = Blog(title=title,content=content,author=author)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))        
    return render_template('blog.html')


@app.route('/blog_detail/<int:id>',methods=['GET','POST'])
@login_required 
def blog_detail(id):
    blog = Blog.query.get(id)
    return render_template('blog_detail.html',blog=blog)


@app.route('/delete/<int:id>',methods=['GET','POST'])
@login_required 
def delete_blog(id):
    blog = Blog.query.get(id)
    db.session.delete(blog)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>',methods=['GET','POST'])
@login_required 
def edit_blog(id):
    blog = Blog.query.get(id)
    if request.method=='POST':
        blog.title = request.form.get('title')
        blog.content = request.form.get('content')
        blog.author = request.form.get('author')
        db.session.commit()
        return redirect(url_for('index'))    
    else:
        return render_template('edit.html',blog=blog)



if __name__ == '__main__':
    app.run(debug=True)    