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
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    blog_title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    user = db.relationship('User')

    def __init__(self, blog_title, body, owner):
        self.blog_title = blog_title
        self.body = body
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
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

       # existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')   

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form ['username']
        password = request.form ['password']
        username = Username.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return rendirect('userblog')
        else: 
            flash('password is not correct')
    return render_template('login.html', title = 'User Login')

    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']
  
    
    #storage for error messages

    password_error =""
    verify_error =""
    username_error =""
        

    if password =="" or " " in password or len(password)<3 or len(password)>20:
        password_error = "invalid password"    

    if verify =="" or verify != password:
        password_error = "invalid verification"

    if username_error == "" and username_error =="" and verify_error =="" and password_error =="":
        return render_template("welcome.html", username = username)
    else:
        return render_template("index.html",username_error = username_error
                                           ,password_error = password_error
                                           ,verify_error = verify_error
                                           ,username = username)
                                        

@app.route('/logout')
def logout(): 
    del session ['username']
    return redirect ('/blog')

        
@app.route('/blog')
def blog():
    #return 'blogz'
    if request.args: 
        blog_id = request.args.get("id") 
        blog = Blog.query.get(blog_id)
        return render_template("blogentry.html", page_title='Blog Entry',blog=blog)
        
    else: 
        blogs = Blog.query.all()
            
        return render_template("blog.html", blogs=blogs)

@app.route("/newpost", methods=["GET", "POST"]) 
def newpost():
    blog_title = request.form['blog_title']
    blog = reuest.form['blog']

    if blog_title == "":
        flash("Blog title required")
        return render_template('newpost.html', title ="Blogs") 

    if blog_text == "":
        flash("No Blog text was added")
        return render_template('newpost.html', title = "Blog")

    if request.method == "GET":
        return render_template("newpost.html")

    if request.method == "POST":
        blog_title = request.form["title"]
        blog_body = request.form["body"]
        title_error = ""
        body_error = ""

        if len(blog_title) < 1:
            title_error = "Invalid Title Entry"
        if len(blog_body) < 1:
            body_error = "Invalid Blog Body Entry"
           
        if not title_error and not body_error: 
            new_blog = Blog(blog_title, blog_body)

            db.session.add(new_blog)
            db.session.commit()
            query_param_url = "/blog?id=" + str(new_blog.id)
            return redirect (query_param_url)

        else:
            return render_template("newpost.html", title="Add Blog Entry")
if __name__ == '__main__':
    app.run()

