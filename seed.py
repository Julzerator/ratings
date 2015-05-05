"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app
from datetime import datetime


def load_users():
    """Load users from u.user into database."""
    filepath = "./seed_data/u.user"
    users = open(filepath)


    for user in users:
        user = user.rstrip().split('|')
        db_user = User(user_id=user[0], age=user[1], zipcode=user[4])
        db.session.add(db_user)

    db.session.commit()

def load_movies():
    """Load movies from u.item into database."""
    filepath = "./seed_data/u.item"
    movies = open(filepath)

    for movie in movies:
        movie = movie.rstrip().split('|')
        title = movie[1][:-7]
        title = title.decode("latin-1")
        if movie[2]:
            date = datetime.strptime(movie[2], '%d-%b-%Y')
        else:
            date = None
        db_movie = Movie(
            movie_id = movie[0], title = title, 
            released_at = date, imdb_url = movie[4])
        db.session.add(db_movie)

    db.session.commit()


def load_ratings():
    """Load ratings from u.data into database."""
    filepath = "./seed_data/u.data"
    ratings = open(filepath)

    for rating in ratings:
        rating = rating.rstrip().split()

        db_rating = Rating(movie_id=rating[1], user_id=rating[0],
            score=rating[2])
        db.session.add(db_rating)

    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    load_ratings()
