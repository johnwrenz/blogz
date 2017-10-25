from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://blogz:blogz@localhost:8889/blogz"
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)
app.secret_key = 'blogme123'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_title = db.Column(db.String(120))
    blog_text = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #user = db.relationship('User')

    def __init__(self, blog_title, blog_text, owner):
        self.blog_title = blog_title
        self.blog_text = blog_text
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(15))
    blogs = db.relationship("Blog", backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
      

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        login_error = ""
        if user and user.password == password:
            session['username'] = username
           # flash("Logged in")
            return redirect("/newpost")
        else: 
            login_error = "User password is incorrect or user doesn't exit"
            #flash('password is not correct')
            return render_template('login.html', login_error=login_error)
    return render_template('login.html')


@app.route("/")
def index():
    blogs = Blog.query.order_by(Blog.id.desc()).all()
    return render_template("index.html", title="Blog Posts by Author", blogs=blogs)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    password_error =""
    verify_error =""
    username_error =""
    existing_user_error =""


    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if len(password)<3 or len(password)>20:
            #flash('password must be at least 3 characters and no more than 20 characters')    
            password_error = 'Password must be between 3 and 20 characters'
            #return render_template('signup.html', username = username)
        if ' ' in password:
            password_error = 'Password cannot contain spaces'    
        if password != verify:
            verify_error = "Password and verify password don't match"
            #return render_template('signup.html', username = username)
        if len(username)<3 or len(username)>20:
                #flash('password must be at least 3 characters and no more than 20 characters')    
            username_error = 'Username must be between 3 and 20 characters'
        if ' ' in username:
            username_error = "Username cannot contain spaces"    
        
        #if len(username)<1: 
         #   return render_template('signup.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            
            return redirect('/newpost')
        
        else:
            existing_user_error = "Username already exists"
            return render_template('signup.html', existing_user_error=existing_user_error)

    return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error) 

               

@app.route('/logout')
def logout(): 
    del session ['username']
    return redirect ('/blog')

        
@app.route('/blog')
def display_blogs():
    owner_id=request.args.get('user')
    if(owner_id):
        blogs = Blog.query.filter_by(owner_id=owner_id)
        return render_template('singleUser.html', title="Submitted By", blogs=blogs)
   
    blog_id = request.args.get("id") 

    if(blog_id):
        blog = Blog.query.get(blog_id)
        return render_template("blogentry.html", page_title='Blog Entry',blog=blog)
    sort_type=request.args.get('sort')
    if sort_type == "newest":
        blogs = Blog.query.order_by(Blog.created.desc()).all()
        
    else: 
        blogs = Blog.query.all()
            
    return render_template("blog.html", blogs=blogs)

@app.route("/newpost", methods=["GET", "POST"]) 
def newpost():
    if request.method == "GET":
        return render_template("newpost.html")

    if request.method == "POST":
        blog_title = request.form["blog_title"]
        blog_text = request.form["blog_text"]
       
        blog_title_error = ""
        blog_text_error = ""

        if len(blog_title) < 1:
            blog_title_error = "Invalid Title Entry, Please Enter a Title for your blog"
        if len(blog_text) < 1:
            blog_text_error = "Invalid Blog Entry, Please Enter a blog, we really want your input"
           
        if not blog_title_error and not blog_text_error: 
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(blog_title, blog_text, owner)
            
            db.session.add(new_blog)
            db.session.commit()
            query_param_url = "/blog?id=" + str(new_blog.id)
            return redirect (query_param_url)

        else:
            return render_template("newpost.html", title="Add Blog Entry")

if __name__ == '__main__':
    app.run()

