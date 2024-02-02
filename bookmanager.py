import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Set up the database
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

# Set up the Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

app.app_context().push()

# Define the Book db model
class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    author = db.Column(db.String(80), unique=False, nullable=False)
    published = db.Column(db.String(80), unique=False, nullable=False)
    pages = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return "<Title: {}>".format(self.title)
    
# Define the routes
@app.route("/", methods=["GET", "POST"])
def home():
    books = None
    if request.form:
        try:
            book = Book(title=request.form.get("title"), author=request.form.get("author"), published=request.form.get("published"), pages=request.form.get("pages"))
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            print("Failed to add book")
            print(e)
    books = Book.query.all()
    return render_template("home.html", books=books)

@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        book = Book.query.filter_by(title=oldtitle).first()
        book.title = newtitle
        db.session.commit()
    except Exception as e:
        print("Couldn't update book title")
        print(e)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/")
  
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)