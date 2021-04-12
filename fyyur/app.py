#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from datetime import datetime
from flask import (
  Flask, 
  render_template, 
  request, Response, 
  flash, 
  redirect, 
  url_for, 
  jsonify
)
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from forms import *
from flask_migrate import Migrate
from models import db, Show, Artist, Venue
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app (app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




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
    upcoming_shows = []
    past_shows =[]
    for show in venue.shows:
      if show.startTime > datetime.now():
        upcoming_shows.append({
          "artist_id": show.artist.id, 
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.startTime)
          })
      else:
        past_shows.append({
          "artist_id": show.artist.id, 
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": str(show.startTime)
          })
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
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
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
  form = VenueForm(request.form)
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  form = VenueForm(request.form)
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
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
        flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
      
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
    upcoming_shows = []
    past_shows =[]
    for show in artist.shows:
      if show.startTime > datetime.now():
        upcoming_shows.append({
          "venue_id": show.venue.id, 
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.startTime
          })
      else:
        past_shows.append({
          "venue_id": show.venue.id, 
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.startTime)
          })
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
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
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
    artist = Artist.query.first_or_404(artist_id)
    form = ArtistForm(obj=artist)
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('Could not populate fields')
 

  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm(request.form)
  try:
    artist = Artist.query.filter_by(id=artist_id).all()[0]
    artist.name = form.name.data 
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website.data
    #artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
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
        flash('An error occurred. Artist ' + artist.name + ' could not be edited.')
 

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  error = False
  try:
    venue = Venue.query.first_or_404(venue_id)
    form = VenueForm(obj=venue)
  except:
    error=True
    print(sys.exc_info())
  finally:
    if error:
        flash('Could not populate fields')
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  form = VenueForm(request.form)
  try:
    venue = Venue.query.filter_by(id=venue_id).all()[0]
    venue.name = form.name.data 
    venue.city = form.city.data 
    venue.state = form.state.data 
    venue.address = form.address.data 
    venue.phone = form.phone.data 
    venue.facebook_link = form.facebook_link.data 
    venue.image_link = form.image_link.data
    venue.website = form.website.data
    #venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
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
        flash('An error occurred. Venue ' + venue.name + ' could not be edited.')
  
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
  form = ArtistForm(request.form)
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
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
        flash('An error occurred. Venue ' + artist.name + ' could not be listed.')
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
  form = ShowForm(request.form)
  try:
    show = Show()
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        flash('An error occurred show could not be listed.')
    else:
        flash('Show was successfully listed!')
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
    app.run(port=5000, debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
