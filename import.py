import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


with open("books.csv", 'r') as books_file:
    reader = csv.reader(books_file)
    for isbn, title, author,publication in reader: # loop gives each column a name
        db.execute("INSERT INTO books(isbn, title, author, publication) VALUES (:isbn, :title, :author, :publication)",
                   {"isbn": isbn, "title": title, "author": author, "publication": publication}) 
        print(f"Added book titled {title} by {author} published on {publication} with ISBN {isbn}")
db.commit() # transactions are assumed, so close the transaction finished
