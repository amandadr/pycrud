import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.discovery import build

# Set up the database
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

# Set up the Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

app.app_context().push()

books = None

# Define the Book db model
class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    author = db.Column(db.String(80), unique=False, nullable=False)
    published = db.Column(db.String(80), unique=False, nullable=False)
    pages = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return "<Title: {}>".format(self.title)
    
# Define local routes
@app.route("/", methods=["GET", "POST"])
def home():
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

@app.route("/update-ajax",methods=["POST","GET"])
def ajaxfile():
    if request.method == 'POST':
        title = request.form.get("title")
        book = Book.query.filter_by(title=title).first()
        print(title)
    return {'htmlresponse': render_template('response.html', book=book)}

@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    book = Book.query.filter_by(title=title).first()
    db.session.delete(book)
    db.session.commit()
    return redirect("/")

# define Google Books api search route
API_KEY = "AIzaSyAtQqQIqtd1tOTmmCCuVXGoP5O9fhk-CM0"

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        results = search_books(search_term)
        books = Book.query.all()
        return render_template('home.html', search_term=search_term, results=results, books=books)
    else:
        books = Book.query.all()
        return render_template('home.html', books=books)

# define Google Books api search function
def search_books(query):
    service = build('books', 'v1', developerKey=API_KEY)
    request = service.volumes().list(q=query)
    response = request.execute()
    return response.get('items', [])

# define add book route
@app.route('/add_book', methods=['POST'])
def add_book():
    if request.method == 'POST':
        book_data = request.get_json()
        new_book = Book(title=book_data['title'],
                        author=book_data['author'],
                        published=book_data['published'],
                        pages=book_data['pages'])
        try:
            db.session.add(new_book)
            db.session.commit()
            return 'Success', 200  # Return a success response 
        except Exception as e:
            print('Error adding book:', e)
            return 'Error', 500  # Return an error response
    

  
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)