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

    movie = Movie.query.get(movie_id)

    user_id = session.get("user_id")

    # Determine if a user is logged in, and if they have rated this
    if user_id:
        user_rating = Rating.query.filter_by(
            movie_id=movie_id, user_id=user_id).first()

    else:
        user_rating = None

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    # Either use the prediction or their real rating

    if prediction:
        # User hasn't scored; use our prediction if we made one
        effective_rating = prediction

    elif user_rating:
        # User has already scored for real; use that
        effective_rating = user_rating.score

    else:
        # User hasn't scored, and we couldn't get a prediction
        effective_rating = None

    # Get the eye's rating, either by predicting or using real rating

    the_eye = User.query.get(952)
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        # We couldn't get an eye rating, so we'll skip difference
        difference = None

    # Depending on how different we are from the Eye, choose a message

    BERATEMENT_MESSAGES = [
        "I suppose you don't have such bad taste after all.",
        "I regret every decision that I've ever made that has brought me" +
            " to listen to your opinion.",
        "Words fail me, as your taste in movies has clearly failed you.",
        "That movie is great. For a clown to watch. Idiot.",
        "Words cannot express the awfulness of your taste."
    ]

    if difference is not None:
        beratement = BERATEMENT_MESSAGES[int(difference)]

    else:
        beratement = None

    # This is where we list the movie_ratings:
    movie_ratings = db.session.query(Rating.score, User.user_id, User.email).join(User)
    movie_ratings = movie_ratings.filter(Rating.movie_id == movie.movie_id)

    print "These are our ratings ", movie_ratings
    
    return render_template("movie_details.html",
        movie=movie, 
        movie_ratings=movie_ratings,
        user_rating=user_rating,
        average=avg_rating,
        prediction=prediction, 
        beratement=beratement,
        eye_rating=eye_rating
        )



@app.route('/rate_movie/<int:movie_id>', methods=['POST'])
def rate_movie(movie_id):
    """Insert or Update user input if user is logged in, otherwise show login alert."""

    score = request.form["score_input"]
    #we have score, movie_id from router and user_id from session

    print "*"*30, session

    if session != {}:
        user_id = session['user_id']

        rating = Rating.query.filter_by(movie_id=movie_id, user_id=user_id).first() 

        new_rating = Rating(movie_id = movie_id,
                            user_id = user_id,
                            score = score)
        if rating == None:

            db.session.add(new_rating)   
            db.session.commit()
            flash("Thank you for rating this movie!")
        else:

            rating.score = score

            db.session.commit()

        return redirect('/movie_details/%d' % movie_id)


    elif session == {}:
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
        print "This is before login", session
        del session['user_id']
        print "This is after del", session

        session['user_id'] = user.user_id
        print "This is after login", session
        flash("You are logged in!") 
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

    user = User.query.filter_by(email=email).first()
    # If there is already a user with that email?

    if user != None:
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
