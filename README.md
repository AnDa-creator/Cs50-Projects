# Project 1

Web Programming with Python and JavaScript

Hello here is the info on my WEBSITE Titled 'BookTrivia'

THE REGISTRATION
============================================
Here you get to register your(or random) email address with your password. 
Already registered users are automatically redirected to the login page.

THE LOGIN PAGE
============================================
If you have already registered you would be taken to the 'searchbooks' page with correct password.
Otherwise you won't be able to login. You can also recover password from the database using the recover 
password link. If your email is not found in database you would not get any response from the page and
should register.

The Searchbooks page
===========================================
Here the user search for the books with three parameters as asked and gets back a table of books.
the books also contain relevent links to their own pages to submit review and get review from goodreads.

these are done in respective the "Searchbooks", "Listbooks" and "BooksPage". Relevent errors are also handled properly.

The API
==========================================
The API is also created with data from the database only(not rating from goodreads). However due to less reviews for such 
enormous quantity of books the table would be mostly empty.

LOGOUT
========================================
A logout button is also given to redirect to the login page. On login again, the session data gets overwritten to work for 
the new user. 

Import.py
=======================================
the import.py file is also included in the files