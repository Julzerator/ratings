"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""


    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Displaying a list of all users"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/user_profile/<int:user_id>')
def user_details(user_id):
    """Displays the details of a user profile"""

    user = User.query.filter_by(user_id = user_id).one()

    #Must have our joined query before we can filter things out of our query.
    user_movies = db.session.query(Movie.title, Rating.score, Movie.movie_id).join(Rating)
    user_movies = user_movies.filter(Rating.user_id == user.user_id)

    
    return render_template("user_details.html", user=user, user_movies=user_movies)


@app.route('/movies')
def movie_list():
    """Displaying a list of all movies"""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)


@app.route('/movie_details/<int:movie_id>')
def movie_details(movie_id):
    """Displays the details of a movie"""

    movie = Movie.query.filter_by(movie_id = movie_id).one()

    movie_ratings = db.session.query(Rating.score, User.user_id, User.email).join(User)
    movie_ratings = movie_ratings.filter(Rating.movie_id == movie.movie_id)

    print "These are our ratings ", movie_ratings
    
    return render_template("movie_details.html", movie=movie, movie_ratings=movie_ratings)



@app.route('/rate_movie/<int:movie_id>', methods=['POST'])
def rate_movie(movie_id):
    """Insert or Update user input if user is logged in, otherwise show login alert."""

    score = request.form["score_input"]
    #we have score, movie_id from router and user_id from session

    print "This is where we check out session ", session
    user_id = session['user_id']
    print "This is our user_id ", user_id


    # WE HAVE A PROBLEM HERE!!!! WE'LL DEAL WITH THIS TOMORROW. 
    rating = Rating.query.filter_by(movie_id, user_id).first() 

    new_rating = Rating(movie_id = movie_id,
                        user_id = user_id,
                        score = score)

    if session:
        if rating == None:
            # insert innto moview score in rating

            db.session.add(new_rating)   

            db.session.commit()

            flash("Thank you for rating this movie!")
        else:
            # update movie score in ratings into db 
            updated_rating = update(Rating).where(user_id=user_id).value(score= score)

            db.session.add(updated_rating)

            db.session.commit()


    else:
        flash ("""Hey there, looks like you aren't logged in at the moment. 
            To rate a movie, please log in""") 
        return redirect("/to_login")


@app.route('/to_login')
def to_login():
    """Takes the user to the login page"""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    """Logs a user into the website"""

    email = request.form["email_input"]
    password = request.form["password_input"]

    
    user = User.query.filter_by(email=email, password=password).first()
    
    # If email/password combo is not found?

    if user == None:
        flash( """Hey there! That email and/or password is not in our database. 
            Try again? Or signup!""")
        return redirect('/to_login')

    if 'user_id' in session:
        session['user_id'] = user.user_id
        flash("You are already logged in!") 
    else:
        session['user_id'] = user.user_id
        flash("You have successfully logged in!")

    print "*"*30
    print "This is our current session", session
    return redirect("/")

@app.route('/logout')
def logout():
    """Logs a user out of the site."""
    print "This is before logout", session
    del session['user_id']
    print "This is after", session
    flash("You have successfully logged out.")
    return redirect("/")

@app.route('/to_signup')
def to_signup():
    return render_template("subscribe.html")

@app.route('/signup', methods=['POST'])
def signup():
    """Adds a new user to the Users table"""

    email = request.form["email_input"]
    password = request.form["password_input"]
    age = request.form["age_input"]
    zipcode = request.form["zipcode_input"]

    # If there is already a user with that email?

    if User(email=email):
        flash("Woah there buddy. That email is taken. Sorry :( ")
        flash("Did you mean to log in instead?")

    else:
        new_user = User(email = email,
                    password = password,
                    age = age,
                    zipcode = zipcode)

        db.session.add(new_user)   

        db.session.commit()

        flash("Thank you for signing up for Judgemental Eye!")

    return render_template("login.html", email= email, password=password)



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()


# ******* NOTES *******

# We removed from our database movie_id = 267
