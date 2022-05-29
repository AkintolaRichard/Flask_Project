from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean(), default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean(), default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show (db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.ForeignKey('artists.id'))
    venue_id = db.Column(db.ForeignKey('venues.id'))
    start_time = db.Column(db.String())
    artists = db.relationship('Artist', backref=db.backref('artist', lazy=True))
    venues = db.relationship('Venue', backref=db.backref('venue', lazy=True))
    
    