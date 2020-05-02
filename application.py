import os
import requests
from flask import Flask, session,  render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config['SECRET_KEY'] = 'super secret key'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
Session(app)


@app.route("/")
def index():
    return render_template("registration.html")


@app.route("/reg_success", methods=["Post"])
def reg_success():
	email = request.form.get("email")
	password = request.form.get("password")
	db = scoped_session(sessionmaker(bind=engine))
	cursor = db.execute("SELECT email FROM users").fetchall()
	for items in cursor:
		new = (email,)
		if new == items:
			return render_template('loginPage.html')
	if email == "" or password == "":
		return render_template("registration.html")
		# return render_template("loginPage.html")
	elif email != "" or password != "":
		db.execute("INSERT INTO users(email, password) VALUES (:email, :password)",{"email": email, "password": password})

	db.commit()
	
	return render_template("reg_success.html", email=email)


@app.route("/loginPage")
def loginPage():
	return render_template("loginPage.html")


@app.route("/recovery")
def recov_info():
	return render_template("recover.html")


@app.route("/recovered", methods=["Post"])
def recover():
	email = request.form.get("email")
	db = scoped_session(sessionmaker(bind=engine))
	password = db.execute("SELECT password FROM users WHERE email= :email", {"email": email}).fetchone()
	if password is None:
		found = False
		password=0
	else:
		password=password[0]
		found = True
	return render_template("recovered.html", password=password, found=found)


@app.route("/SearchBooks", methods=["Post"])
def SearchBooks():
	email = request.form.get("email")
	password = request.form.get("password")
	db = scoped_session(sessionmaker(bind=engine))
	checker = (email, password)
	cursor = db.execute("SELECT email,password FROM users").fetchall()
	for items in cursor:
		if checker == items:
			session['key']= email
			return render_template("SearchBooks.html", name=email)
	db.commit()
	return render_template('loginPage.html')


@app.route("/SearchBooks/again")
def Searchagain():
	return render_template("SearchBooks.html",name=session.get('key'))


@app.route("/ListBooks", methods=["Post"])
def listBooks():
	attribute = request.form.get("attribute")
	option = request.form.get("select")
	session_var_value = session.get('key')
	db = scoped_session(sessionmaker(bind=engine))
	if option == "isbn":
		cursor = db.execute("SELECT * FROM books WHERE isbn LIKE :attribute",{'attribute':'%' + attribute + '%'}).fetchall()
	elif option == "title":
		cursor = db.execute("SELECT * FROM books WHERE title LIKE :attribute",{'attribute':'%' + attribute + '%'}).fetchall()
	elif option == "author":
		cursor = db.execute("SELECT * FROM books WHERE author LIKE :attribute",{'attribute':'%' + attribute + '%'}).fetchall()
	else :
		return render_template("SearchBooks.html", name=session_var_value)
	
	if len(cursor) == 0:
		return render_template("errorSearching.html", name=session_var_value)
	else:
		New_cursor=[]
		for item in cursor:
			item = list(item)
			link = "See Details For " + str(item[2])
			item.append(link)
			New_cursor.append(item)
	session['bookstuple'] = New_cursor
	db.commit()
	return render_template('ListBooks.html', items=New_cursor, name=session_var_value)


@app.route("/Reviews/<title>")
def reviews(title):
	current_user = session['key']
	db = scoped_session(sessionmaker(bind=engine))
	book = db.execute("SELECT * FROM books WHERE title = :title", {"title": title}).fetchone()
	if book is None:
		return render_template("SearchBooks.html")
	session['title']=book
	# Get all reviews
	reviewAll = db.execute("SELECT email,rating,review FROM reviews WHERE title=:title",
						{"title": title}).fetchall()
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "bvpoh7UrKNALHQWarWfPQ", "isbns": book[1]})
	good_rating_count = ("Not available on goodreads", "Not available on goodreads")
	if res is not None:
		gooddata = res.json()
		good_rating_count = (gooddata["books"][0]["ratings_count"], gooddata["books"][0]["average_rating"])
	if len(reviewAll) == 0:
		found=False
	else:
		found=True
	db.commit()
	return render_template("BookPage.html", name=book[2], item=book, reviewAll=reviewAll, found=found,
							goodreads=good_rating_count)


@app.route("/reviewadded", methods=["Post"])
def addreview():
	current_user = session['key']
	title = session['title'][2]
	found = False
	db = scoped_session(sessionmaker(bind=engine))
	reviewAll = db.execute("SELECT email,rating,review FROM reviews WHERE title=:title",
						{"title": title}).fetchall()
	for data in reviewAll:
		user = data[0]
		if current_user == user:
			found = True
		else:
			found = False
	new_review = request.form.get("attribute")
	new_rating = request.form.get("select")
	if found:
		db.execute("UPDATE reviews SET review = :new_review, rating = :new_rating WHERE email=current_user and title=:title",
				{"new_review": new_review, "new_rating": new_rating, "title":title,"current_user":current_user})

	else:
		db.execute("INSERT INTO reviews(email, title, rating, review) VALUES (:email, :title, :new_rating, :new_review)",
				{"email":current_user, "new_review":new_review, "new_rating":new_rating, "title":title})
	db.commit()
	return render_template("reviewadded.html", name=title)


@app.route("/api/<isbn>")
def getbooks(isbn):
	db = scoped_session(sessionmaker(bind=engine))
	book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
	if book is None:
		return jsonify({"error": "BOOK NOT FOUND"}), 404
	# Get all passengers.
	reviewAll = db.execute("SELECT email,rating,review FROM reviews WHERE title=:title",
						{"title": book[2]}).fetchall()
	num_rating=0
	Total_rating=0
	for data in reviewAll:
		if len(reviewAll)==0:
			break
		num_rating +=1
		Total_rating = data[1]+Total_rating
	try:
		Average_rating = Total_rating/num_rating
	except (ZeroDivisionError,EOFError):
		Average_rating = "No reviews till now"
	return jsonify({
		"title": book[2],
		"author": book[3],
		"year": book[4],
		"isbn": book[1],
		"review_count": num_rating,
		"average_score": Average_rating
	})







