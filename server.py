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


@app.route('/to_login')
def to_login():
    """Takes the user to the login page"""

    return render_template("login.html")


@app.route('/login', methods=['POST'])
def login():
    """Logs a user into the website"""

    email = request.form["email_input"]
    password = request.form["password_input"]

    user = User.query.filter_by(email=email, password=password).one()

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

    new_user = User(email = email,
                    password = password,
                    age = age,
                    zipcode = zipcode)

    db.session.add(new_user)   
    # db.session.flush()
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