from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:cheese@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fjdasl4543j54jkl5243l'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    body = db.Column(db.String(3000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

def check_empty(variable):
    if variable == "":
        return True

@app.route("/new-entry", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        return render_template("form.html")
    
    return render_template("form.html")

@app.route("/", methods=["GET", "POST"])
def blog_entry():
    posts = []
    check = request.args.get("id")
    if check:
        blog_post = Blog.query.filter_by(id=int(check)).first()
        stitle = blog_post.title
        sbody = blog_post.body
    else:
        stitle = ""
        sbody = ""
        
    if request.method == "POST":
        title = request.form["blog-title"]
        body = request.form["blog-content"]
        post = Blog(title, body)
        empty_title = check_empty(title)
        empty_body = check_empty(body)
        if empty_title and not empty_body:
            return render_template("form.html", body_value=body, etitle="Title was empty")
        if empty_body and not empty_title:
            return render_template("form.html", title_value=title, ebody="Body was empty")
        if empty_title and empty_body:
            return render_template("form.html", body_value=body, etitle="Title was empty", title_value=body, ebody="Body was empty")
        db.session.add(post)
        db.session.commit()
        blog_post = Blog.query.filter_by(title=title).first()
        red_id = blog_post.id
        url = "/?id={id}"
        return redirect(url.format(id=red_id))
        #posts = Blog.query.all()
    
    if not check:
        posts = Blog.query.all()

    return render_template("posts.html", list=posts, stitle=stitle, sbody=sbody)



if __name__ == "__main__":
    app.run()


    