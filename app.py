import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from data_models import db, Author, Book
from datetime import datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir,'data', 'library.sqlite')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    """Get the sort_by query parameter, default to 'title'
    """
    search_query = request.args.get('search','').strip()
    sort_by = request.args.get('sort_by', 'title')

    # Base query: join books with authors
    query = Book.query.join(Author).add_columns(Book.title, Author.name, Book.isbn)

    # Apply search filter
    if search_query:
        query = query.filter(
            (Book.title.ilike(f"%{search_query}%")) | (Author.name.ilike(f"%{search_query}%"))
        )
    # Apply sorting
    if sort_by == 'title':
        query = query.order_by(Book.title)
    elif sort_by == 'author':
        query = query.order_by(Author.name)

    books = query.all()

    # Check if results were found
    if not books:
        message = "No books found matching your search criteria."
    else:
        message = None

        # Fetch book details
    book_details = []
    for book, author_name, isbn in books:
        cover_image = get_cover_image(isbn)
        book_details.append({
            'title': book,
            'author': author_name,
            'cover_image': cover_image,
            'isbn': isbn
        })

    return render_template('home.html', books=book_details, sort_by=sort_by, message=message)

# Function to fetch book cover image
def get_cover_image(isbn):
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        return url
    return "https://via.placeholder.com/150"  # Placeholder if no image is found


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        date_of_death = request.form['date_of_death']
        # Convert strings to date objects (handle empty date_of_death properly)
        birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        date_of_death = datetime.strptime(date_of_death, "%Y-%m-%d").date() if date_of_death else None

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)

        db.session.add(new_author)
        db.session.commit()

        flash(f"Author {new_author.name} has been successfully added!", 'success')
        return redirect(url_for('add_author'))

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            isbn = request.form.get('isbn')
            title = request.form.get('title')
            publication_year = request.form.get('publication_year')
            author_id = int(request.form['author_id'])

            new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)

            db.session.add(new_book)
            db.session.commit()

            flash(f"Book '{new_book.title}' has been successfully added!", 'success')
            return redirect(url_for('add_book'))
        except KeyError as e:
            flash(f"Missing form field: {str(e)}", "danger")
            return redirect(url_for('add_book'))

        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('add_book'))

    authors = Author.query.all()
    return render_template('add_book.html', authors=authors)

@app.route('/book/<int:book_id>/delete', methods=['GET','POST'])
def delete_book(book_id):
    method = request.form.get('_method', 'POST')

    if method == 'DELETE':  # Simulate DELETE request
        book = Book.query.get_or_404(book_id)
        author_id = book.author_id

        db.session.delete(book)
        db.session.commit()

        # Delete author if they have no other books
        if not Book.query.filter_by(author_id=author_id).first():
            author = Author.query.get(author_id)
            if author:
                db.session.delete(author)
                db.session.commit()

        flash(f"Book '{book.title}' has been deleted successfully!", 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)