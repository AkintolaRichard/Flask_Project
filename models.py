from app import db

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean(), default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean(), default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show (db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.ForeignKey('Venue.id'))
    start_time = db.Column(db.String())
    artists = db.relationship('Artist', backref=db.backref('artist', lazy=True))
    venues = db.relationship('Venue', backref=db.backref('venue', lazy=True))
    
    