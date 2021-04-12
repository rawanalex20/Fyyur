from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Show(db.Model):
    __tablename__ = 'show'    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    startTime = db.Column(db.DateTime, nullable=False)

    venue = db.relationship('Venue', backref=db.backref('venues'))
    artist = db.relationship('Artist', backref=db.backref('artists'))

    def __repr__(self):
      return f'<id: {self.id} venue_id: {self.venue_id} artist_id: {self.artist_id} startTime:{self.startTime}>'


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genres = db.Column(db.String)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False )
    address = db.Column(db.String(120), nullable=False )
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String)

    shows = db.relationship('Show', backref=db.backref('venues'), lazy="joined")

    def __repr__(self):
      return f'<id: {self.id} name: {self.name}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String)

    shows = db.relationship('Show', backref=db.backref('artists'), lazy="joined")

    def __repr__(self):
      return f'<id: {self.id} name: {self.name}>'