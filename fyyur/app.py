#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from datetime import datetime
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

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

    def __repr__(self):
      return f'<id: {self.id} name: {self.name}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  error = False
  try:
    city_state_list = Venue.query.distinct(Venue.city, Venue.state).all()
    data = []
    for city_state in city_state_list:
      venue_list = Venue.query.filter_by(city=city_state.city, state=city_state.state).all()
      venues_data = []
      for ven in venue_list:
        shows = Show.query.filter_by(venue_id=ven.id).all()
        num_shows = 0
        for show in shows:
          if show.startTime > datetime.now():
            num_shows = num_shows + 1
        venues_data.append({"id": ven.id,
        "name": ven.name,
        "num_upcoming_shows": num_shows
        })
      data.append({"city": city_state.city,
      "state": city_state.state,
      "venues": venues_data
      })
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('An error occurred.')

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  error = False
  try:
    search_term = request.form.get('search_term')
    venue_list = Venue.query.filter(Venue.name.like('%' + search_term + '%')).all()
    data = []
    for obj in venue_list:
      shows = Show.query.filter_by(venue_id=obj.id).all()
      num_shows = 0
      for show in shows:
        if show.startTime > datetime.now():
          num_shows = num_shows 
      data.append({"id": obj.id, "name": obj.name, "num_upcoming_shows": num_shows})

    response={
      "count": len(venue_list),
      "data": data
    }
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('An error occurred.')

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  error = False
  data={}
  try:
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    shows = Show.query.filter_by(venue_id=venue.id).all()
    num_shows = 0
    upcoming_shows = []
    past_shows =[]
    for show in shows:
      artist = Artist.query.filter_by(id=show.artist_id)
      if show.startTime > datetime.now():
        upcoming_shows.append({
          "artist_id": artist.id, 
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.startTime
          })
        num_shows = num_shows + 1
      else:
        past_shows.append({
          "artist_id": artist.id, 
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.startTime
          })
    past_shows_num = len(shows) - num_shows
    data={
      "id": venue.id,
      "name": venue.name,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_num,
      "upcoming_shows_count": num_shows
    }
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('An error occurred.')

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get("name") 
    city = request.form.get("city")
    state = request.form.get("state")
    address = request.form.get("address")
    phone = request.form.get("phone")
    facebook_link = request.form.get("facebook_link")
    new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link)
    db.session.add(new_venue)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + name + ' could not be listed.')
      
  return render_template('pages/home.html')
  
@app.route('/venues/<int:venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  error = False
  try:
    shows = Show.query.filter_by(venue_id=venue_id).all()
    for show in shows:
      try:
        db.session.delete(show)
        db.session.commit()
      except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        break
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    name = venue.name
    db.session.delete(venue)
    db.session.commit()
  except:
    db.sesison.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
      flash('Venue ' + name + ' was successfully deleted!')
    else:
      flash('An error occured. Venue ' + name + ' could not be deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  error = False
  try:
    artist_list = Artist.query.all()
    data = []
    for art in artist_list:
      data.append({
        "id": art.id,
        "name": art.name
      })
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('An error occurred.')
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  error = False
  try:
    search_term = request.form.get('search_term')
    artist_list = Artist.query.filter(Artist.name.like('%' + search_term + '%')).all()
    data = []
    for obj in artist_list:
      shows = Show.query.filter_by(venue_id=obj.id).all()
      num_shows = 0
      for show in shows:
        if show.startTime > datetime.now():
          num_shows = num_shows + 1
      data.append({"id": obj.id, "name": obj.name, "num_upcoming_shows": num_shows})

    response={
      "count": len(artist_list),
      "data": data
    }
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('An error occurred.')
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  error = False
  data={}
  try:
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    shows = Show.query.filter_by(artist_id=artist.id).all()
    num_shows = 0
    upcoming_shows = []
    past_shows =[]
    for show in shows:
      venue = Venue.query.filter_by(id=show.venue_id)
      if show.startTime > datetime.now():
        upcoming_shows.append({
          "venue_id": venue.id, 
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.startTime
          })
        num_shows = num_shows + 1
      else:
        past_shows.append({
          "venue_id": venue.id, 
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": show.startTime
          })
    past_shows_num = len(shows) - num_shows
    data={
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_num,
      "upcoming_shows_count": num_shows
    }
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('An error occurred.')

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  error = False
  try:
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    artist={
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": True,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('Could not populate fields')
 

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    artist.name = request.form.get("name") 
    artist.city = request.form.get("city")
    artist.state = request.form.get("state")
    artist.address = request.form.get("address")
    artist.phone = request.form.get("phone")
    artist.facebook_link = request.form.get("facebook_link")
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    else:
        flash('An error occurred. Artist ' + name + ' could not be edited.')
 

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  error = False
  try:
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    venue={
      "id": venue.id,
      "name": venue.name,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": True,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
    }
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('Could not populate fields')
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    venue.name = request.form.get("name") 
    venue.city = request.form.get("city")
    venue.state = request.form.get("state")
    venue.address = request.form.get("address")
    venue.phone = request.form.get("phone")
    venue.facebook_link = request.form.get("facebook_link")
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    else:
        flash('An error occurred. Venue ' + name + ' could not be edited.')
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    name = request.form.get("name") 
    city = request.form.get("city")
    state = request.form.get("state")
    phone = request.form.get("phone")
    facebook_link = request.form.get("facebook_link")
    new_artist = Artist(name=name, city=city, state=state, phone=phone, facebook_link=facebook_link)
    db.session.add(new_artist)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        flash('An error occurred. Venue ' + name + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  error = False
  try:
    show_list = Show.query.all()
    data = []
    for show in show_list:
      venue = Venue.query.filter(Venue.id==show.venue_id).all()
      artist = Artist.query.filter(Artist.id==show.artist_id).all()
      data.append({
      "venue_id": venue[0].id,
      "venue_name": venue[0].name,
      "artist_id": artist[0].id,
      "artist_name": artist[0].name,
      "artist_image_link": artist[0].image_link,
      "start_time": str(show.startTime)
      })
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('An error occurred.')
        
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    artist_id = request.form.get("artist_id") 
    venue_id = request.form.get("venue_id")
    startTime = request.form.get("startTime")
    show_venue = Venue.query.get(venue_id)
    show_artist = Artist.query.get(artist_id)
    show_venue.artists = [show_artist]
    show_artist.venues = [show_venue]
    new_show = Show(artist_id=artist_id, venue_id=venue_id, startTime=startTime)
    db.session.add(new_show)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        flash('Show was successfully listed!')
    else:
        flash('An error occurred show could not be listed.')
  return render_template('pages/home.html')


# Error handlers
# -------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
