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


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        return render_template("form.html")
    
    return render_template("form.html")

@app.route("/blog-entry", methods=["POST"])
def blog_entry():
    title = request.form["blog-title"]
    body = request.form["blog-content"]
    return title+"<br>"+body



if __name__ == "__main__":
    app.run()