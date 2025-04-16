from enum import unique

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer,primary_key = True ,autoincrement= True)
    name = db.Column(db.String(100), nullable = False, unique=True)
    birth_date = db.Column(db.Date, nullable = True)
    date_of_death = db.Column(db.Date, nullable = True)

    def __repr__(self):
        return (f"Author(id={self.author_id}, name={self.name},"
               f"birth_date={self.birth_date},date_of_death={self.date_of_death})")

    def __str__(self):
        return f"{self.name} (Born: {self.birth_date}, Died: {self.date_of_death})"

class Book(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer,primary_key = True,autoincrement= True)
    isbn = db.Column(db.String(13),unique =True, nullable= False)
    title = db.Column(db.String(200),nullable= False)
    publication_year = db.Column(db.Integer,nullable= True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'),nullable= False)

    author = db.relationship('Author', backref='books')
    def __repr__(self):
        return (f"Book(id={self.book_id},isbn={self.isbn}, title={self.title},"
                f" publication_year={self.publication_year}, author_id={self.author_id})")

    def __str__(self):
        return f"{self.title} ({self.publication_year}) by Author ID {self.author_id}"







