from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re
import hashlib
import string

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:cheeze@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'fjdasl4543j54jkl5243l'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    body = db.Column(db.String(3000))
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    pw_hash = db.Column(db.String(150))
    posts = db.relationship("Blog", backref="owner")

    def __init__(self, name, password):
        self.name = name
        self.pw_hash = hash_pass(password)

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_empty(variable):
    if variable == "":
        return True


def validate_userORpass(submission):
    if not re.match("...", submission):
        return "Must be at least 3 characters"
    elif re.match(".{21,}" , submission):
        return "Must be fewer than 20 characters"
    elif re.match(".*\s" , submission):
        return "Cannot contain spaces"
    else:
        return ""

def match_pass(pass1, pass2):
    if pass2 != pass1:
        return "Passwords must match"
    else: 
        return ""

def check_email(submission):
    if not re.match("...", submission):
        return "Must be at least 3 characters"
    elif re.match(".{21,}" , submission):
        return "Must be fewer than 20 characters"
    elif re.match(".*\s" , submission):
        return "Cannot contain spaces"
    else:
        return ""

@app.before_request
def require_login():
    allowed_routes = ["login", "signup"]
    if request.endpoint not in allowed_routes and "id" not in session:
        return redirect("/login")

@app.route("/logout")
def logout():
    del session["id"]
    return redirect("/")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    name = ""
    pass1= ""
    pass2 = ""
    email = ""
    valid_name = ""
    valid_pass = ""
    matching_pass = ""
    emailok = ""
    if request.method == "POST":
        name = request.form["name"]
        pass1 = request.form["pass1"]
        pass2 = request.form["pass2"]
        email = request.form["email"]
        existing_user = User.query.filter_by(name=name).first()
        if not existing_user:
            if name == "":
                valid_name = "Field required"
            else:
                valid_name = validate_userORpass(name)
            if pass1 == "":
                valid_pass = "Field required"
            else:
                valid_pass = validate_userORpass(pass1)
            if valid_pass == "":
                matching_pass = match_pass(pass1, pass2)
            if email != "":
                emailok = check_email(email)
            if valid_name == "" and valid_pass == "" and matching_pass == "" and emailok == "":
                new_user = User(name, pass1)
                db.session.add(new_user)
                db.session.commit()
                session["id"] = new_user.id
                return redirect("/validated?user={0}".format(name))   
        else:
            return redirect("/login")      
    
    return render_template("signup.html", name=name, name_error=valid_name, pass1="", pass1_error=valid_pass, pass2="", pass2_error=matching_pass, email=email, email_error=emailok)

@app.route("/validated", methods=["GET", "POST"])
def validated():
    
    return redirect("/new-entry")

@app.route("/login", methods=["GET", "POST"])
def login():
    name = ""
    pw = ""
    name_exists = ""
    pw_exists = ""
    if request.method == "POST":
        name = request.form["name"]
        pw = request.form["pass"]
        if name == "":
            name_exists = "Field required"
        else:
            name_exists = User.query.filter_by(name=name).first()
        
        if pw == "":
            pw_exists = "Field required"
        else:
            pw_exists = User.query.filter_by(pw_hash=hash_pass(pw)).first()
        
        if name == name_exists.name and pw == pw_exists.pw_hash:
            user = User.query.filter_by(name=name).first()
            session["id"] = user.id
            return redirect("/")         
    
    return render_template("login.html", name=name, name_error=name_exists, pw=pw, pass_error=pw_exists)

@app.route("/", methods=["GET", "POST"])
def index():
    user_list = User.query.all()
    return render_template("index.html", users=user_list)

@app.route("/new-entry", methods=["GET", "POST"])
def new_entry():
    if request.method == "POST":

        return render_template("new-post.html")
    
    return render_template("new-post.html")

@app.route("/user-posts", methods=["GET", "POST"])
def blog_entry():
    posts = []
    check = request.args.get("entry")
    user_check = request.args.get("user")
    if check:
        blog_post = Blog.query.filter_by(id=int(check)).first()
        stitle = blog_post.title
        sbody = blog_post.body
    elif user_check:
        stitle = ""
        sbody = ""
        posts = Blog.query.filter_by(owner_id=user_check).all()
    else:    
        stitle = ""
        sbody = ""
        posts = Blog.query.filter_by(owner_id=session["id"]).all()
        
    if request.method == "POST":
        title = request.form["blog-title"]
        body = request.form["blog-content"]
        owner = User.query.filter_by(id=session["id"]).first()
        post = Blog(title, body, owner)
        empty_title = check_empty(title)
        empty_body = check_empty(body)
        if empty_title and not empty_body:
            return render_template("new-post.html", body_value=body, etitle="Title was empty")
        if empty_body and not empty_title:
            return render_template("new-post.html", title_value=title, ebody="Body was empty")
        if empty_title and empty_body:
            return render_template("new-post.html", body_value=body, etitle="Title was empty", title_value=body, ebody="Body was empty")
        db.session.add(post)
        db.session.commit()
        blog_post = Blog.query.filter_by(title=title).first()
        red_id = blog_post.id
        url = "/user-posts?entry={entry}"
        return redirect(url.format(entry=red_id))
    
    return render_template("posts.html", list=posts, stitle=stitle, sbody=sbody)

if __name__ == "__main__":
    app.run()
    