from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog"
app.config['SQLALCHEMY_ECHO'] = True 
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(800))

    def __init__(self, title, body):
        self.title = title
        self.body = body

    @app.route('/blog', methods=['POST', 'GET'])
    def index():
        if request.args: 
            blog_id = request.args.get("id") 
            blog = Blog.query.get(blog_id)
            return render_template("blogentry_html", blog=blog)
        
        else: 
            blogs = Blog.query.all()
            return render_template("Index.html",title="Build A Blog", blog=blogs)

    @app.route("/newpst", methods=["GET", "POST"]) 
    def add_blog():
        if request.method == "GET":
            return render_template("newpost.html", title="Add Blog Entry")

        if request.method == "POST":
            blog_title = request.form("title")
            blog_body = request.form("body")
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
                query_param_url = ".blog?id=" + str(new_blog.id)
                return redirect (query_param_url)

        else:
            return render_template("newpost.html", title="Add Blog Entry")
if __name__ == '__main__':
    app.run()


