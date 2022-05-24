from xmlrpc.client import Boolean
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

bcrypt = Bcrypt()

class User(db.Model):
    """User of Mangashelf"""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    username = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
    )

    password = db.Column(db.Text, nullable=False)
    bookmarks=db.relationship("Bookmark",backref="user")
    reviews = db.relationship("Review",backref="user")
    favorites = db.relationship("Favorite",backref="user")

    @classmethod
    def register(cls, username, password):
        """Register user w/hashed password & adds it to the db session and then returns the user"""

        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        user = cls(
            username=username,
            password=hashed_utf8,
        )
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Returns user if valid; else return False.
        """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

class Manga(db.Model):

    __tablename__ = "manga"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    native_title = db.Column(
        db.String,
    )
    english_title = db.Column(
        db.String,
    )
    large_image = db.Column(
        db.String,
        nullable=False
    )
    medium_image = db.Column(
        db.String,
        nullable=False
    )
    bookmarks=db.relationship("Bookmark",backref="manga")
    reviews=db.relationship("Review",backref="manga")
    favorites=db.relationship("Favorite", backref="manga")
    genres=db.relationship("Genre",
                            secondary='genretags',
                            backref="manga")

class Bookmark(db.Model):
    """keeps track of the user's last read chapter in a manga"""

    __tablename__ = 'bookmarks' 

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key=True
    )

    manga_id = db.Column(
        db.Integer,
        db.ForeignKey('manga.id', ondelete='cascade'),
        primary_key=True
    )
    chapter = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(db.Text, nullable=False)


class Review(db.Model):
    """a review of a manga by a user"""

    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    rating = db.Column(db.Integer, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    manga_id = db.Column(
        db.Integer,
        db.ForeignKey('manga.id', ondelete='cascade')
    )

class Favorite(db.Model):
    """keeps track of the user's last read chapter in a manga"""

    __tablename__ = 'favorites' 

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        primary_key=True
    )

    manga_id = db.Column(
        db.Integer,
        db.ForeignKey('manga.id', ondelete='cascade'),
        primary_key=True
    )

class Genre(db.Model):
    """Manga Genre"""

    __tablename__ = 'genres' 
    
    genre = db.Column(
        db.String,
        nullable=False,
        unique=True,
        primary_key=True,
    )

class GenreTag(db.Model):
    """Manga Genre tagged on to a manga"""

    __tablename__ = 'genretags' 
    
    genre_name = db.Column(
        db.String,
        db.ForeignKey('genres.genre', ondelete='cascade'),
        nullable=False,
        primary_key=True,
    )

    manga_id = db.Column(
        db.Integer,
        db.ForeignKey('manga.id', ondelete='cascade'),
        primary_key=True
    )
    



def connect_db(app):
    db.app = app
    db.init_app(app)


