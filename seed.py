"""Utility file to seed ratings database from MovieLens data in seed_data/"""

from model import User, Rating, Movie, connect_to_db, db
from server import app


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


def load_ratings():
    """Load ratings from u.data into database."""


if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_movies()
    load_ratings()
