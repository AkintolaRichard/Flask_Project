#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
from sqlalchemy import select
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models import Artist, Venue, Show

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
  # TODO: replace with real venues data.
  data = []
  distinct_city = db.session.query(Venue.id, Venue.name, Venue.city, Venue.state).distinct(Venue.city)
  for id, name, city, state in distinct_city:
    each_city = {}
    each_city['city'] = city
    each_city['state'] = state
    thevenues = []
    each_venue_in_city = {}
    city_count = Venue.query.filter_by(city=city).count()
    for i in range(city_count):
      each_venue_in_city['id'] = id
      each_venue_in_city['name'] = name
      #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
      today = datetime.datetime.utcnow()
      count = 0
      shows_list = Show.query.filter_by(venue_id=id)
      if shows_list.count() != 0:
        if shows_list.count() >= 1:
          for show in shows_list:
            showtime = datetime.datetime.fromisoformat(show.start_time)
            if showtime >= today:
              count += 1
      else:
        count = 0
      each_venue_in_city['num_upcoming_shows'] = count
      thevenues.append(each_venue_in_city)
    each_city['venues'] = thevenues
    data.append(each_city)
  newlist  = sorted(data, key=lambda d: d['city'], reverse=True)
  
  return render_template('pages/venues.html', areas=newlist)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form["search_term"]
  response = {}
  each_result = []
  for v in Venue.query.all():
    if str(search).lower() in str(v.name).lower():
      each = {}
      each['id'] = v.id
      each['name'] = v.name
      today = datetime.datetime.utcnow()
      count = 0
      show_list = Show.query.filter_by(venue_id=v.id)
      if len(show_list) != 0:
        if len(show_list) != 1:
          for show in show_list:
            showtime = datetime.datetime.fromisoformat(show.start_time)
            if showtime >= today:
              count += 1
        else:
          showtime = datetime.datetime.fromisoformat(show.start_time)
          if showtime >= today:
            count += 1
      else:
        count = 0
      each['num_upcoming_shows'] = count
      each_result.append(each)
  response['count'] = len(each_result)
  response['data'] = each_result
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', search))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  current_venue = Venue.query.get(venue_id)
  thevenue = {}
  thevenue['id'] = current_venue.id
  thevenue['name'] = current_venue.name
  thevenue['genres'] = current_venue.genres.replace('{', '').replace('}', '').split(',')
  thevenue['address'] = current_venue.address
  thevenue['city'] = current_venue.city
  thevenue['state'] = current_venue.state
  thevenue['phone'] = current_venue.phone
  thevenue['website'] = current_venue.website
  thevenue['facebook_link'] = current_venue.facebook_link
  thevenue['seeking_talent'] = current_venue.seeking_talent
  thevenue['seeking_description'] = current_venue.seeking_description
  thevenue['image_link'] = current_venue.image_link
  today = datetime.datetime.utcnow()
  show_list = Show.query.filter_by(venue_id=current_venue.id)
  thepast_shows = []
  thecoming_shows = []
  if show_list.count() != 0:
    if show_list.count() >= 1:      
      for show in show_list:
        showtime = datetime.datetime.fromisoformat(show.start_time)
        if showtime < today:
          past_show_details = {}
          the_artist = Artist.query.get(show.artist_id)
          past_show_details['artist_id'] = the_artist.id
          past_show_details['artist_name'] = the_artist.name
          past_show_details['artist_image_link'] = the_artist.image_link
          past_show_details['start_time'] = show.start_time
          thepast_shows.append(past_show_details)
        elif showtime >= today:
          coming_show_details = {}
          the_artist = Artist.query.get(show.artist_id)
          coming_show_details['artist_id'] = the_artist.id
          coming_show_details['artist_name'] = the_artist.name
          coming_show_details['artist_image_link'] = the_artist.image_link
          coming_show_details['start_time'] = show.start_time
          thecoming_shows.append(coming_show_details)
  thevenue['past_shows'] = thepast_shows
  thevenue['upcoming_shows'] = thecoming_shows
  thevenue['past_shows_count'] = len(thepast_shows)
  thevenue['upcoming_shows_count'] = len(thecoming_shows)
  
  data = thevenue
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  venue = Venue()
  # TODO: modify data to be the data object returned from db insertion
  noerror = True
  for f in form:
    print(f.data)
  try:
    venue.name = form.name.data
    venue.genres = str(form.genres.data)
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    print(e)
    noerror = False
    db.session.rollback()
  finally:
    db.session.close()
  if noerror:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.') 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  noerror = True
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    noerror = False
    db.session.rollback()
  finally:
    db.session.close()
  if noerror:
    redirect(url_for('index'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return flash('An error occurred.') 

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist_list = []
  for a in Artist.query.all():
    each = {}
    each['id'] = a.id
    each['name'] = a.name
    artist_list.append(each)
  data = artist_list
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form["search_term"]
  search_result = {}
  each_result = []
  for a in Artist.query.all():
    if str(search).lower() in str(a.name).lower():
      each = {}
      each['id'] = a.id
      each['name'] = a.name
      today = datetime.datetime.utcnow()
      count = 0
      show_list = Show.query.filter_by(venue_id=a.id)
      if show_list.count() != 0:
        if show_list.count() != 1:
          for show in show_list:
            showtime = datetime.datetime.fromisoformat(show.start_time)
            if showtime >= today:
              count += 1
        else:
          showtime = datetime.datetime.fromisoformat(show.start_time)
          if showtime >= today:
            count += 1
      else:
        count = 0
      each['num_upcoming_shows'] = count
      each_result.append(each)
  search_result['count'] = len(each_result)
  search_result['data'] = each_result
  response = search_result
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', search))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  current_artist = Venue.query.get(artist_id)
  theartist = {}
  theartist['id'] = current_artist.id
  theartist['name'] = current_artist.name
  theartist['genres'] = current_artist.genres.replace('{', '').replace('}', '').split(',')
  theartist['address'] = current_artist.address
  theartist['city'] = current_artist.city
  theartist['state'] = current_artist.state
  theartist['phone'] = current_artist.phone
  theartist['website'] = current_artist.website
  theartist['facebook_link'] = current_artist.facebook_link
  theartist['seeking_talent'] = current_artist.seeking_talent
  theartist['seeking_description'] = current_artist.seeking_description
  theartist['image_link'] = current_artist.image_link
  today = datetime.datetime.utcnow()
  show_list = Show.query.filter_by(artist_id=current_artist.id)
  thepast_shows = []
  thecoming_shows = []
  if show_list.count() != 0:
    if show_list.count() >= 1:      
      for show in show_list:
        showtime = datetime.datetime.fromisoformat(show.start_time)
        if showtime < today:
          past_show_details = {}
          the_venue = Venue.query.get(show.venue_id)
          past_show_details['venue_id'] = the_venue.id
          past_show_details['venue_name'] = the_venue.name
          past_show_details['venue_image_link'] = the_venue.image_link
          past_show_details['start_time'] = show.start_time
          thepast_shows.append(past_show_details)
        elif showtime >= today:
          coming_show_details = {}
          the_venue = Venue.query.get(show.venue_id)
          coming_show_details['venue_id'] = the_venue.id
          coming_show_details['venue_name'] = the_venue.name
          coming_show_details['venue_image_link'] = the_venue.image_link
          coming_show_details['start_time'] = show.start_time
          thecoming_shows.append(coming_show_details)
  theartist['past_shows'] = thepast_shows
  theartist['upcoming_shows'] = thecoming_shows
  theartist['past_shows_count'] = len(thepast_shows)
  theartist['upcoming_shows_count'] = len(thecoming_shows)
  data = theartist
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  theartist = Artist.query.get(artist_id)
  artist  = {}
  artist['id'] = theartist.id
  artist['name'] = theartist.name
  artist['genres'] = theartist.genres.replace('{', '').replace('}', '').split(',')
  artist['city'] = theartist.city
  artist['state'] = theartist.state
  artist['phone'] = theartist.phone
  artist['website'] = theartist.website
  artist['facebook_link'] = theartist.facebook_link
  artist['seeking_venue'] = theartist.seeking_venue
  artist['seeking_description'] = theartist.seeking_description
  artist['image_link'] = theartist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist = Artist()
  noerror = True
  try:
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_talent = form.seeking_talent.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
  except:
    noerror = False
    db.session.rollback()
  finally:
    db.session.close()
  if noerror:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  thevenue = Venue.query.get(venue_id)
  venue  = {}
  venue['id'] = thevenue.id
  venue['name'] = thevenue.name
  venue['genres'] = thevenue.genres.replace('{', '').replace('}', '').split(',')
  venue['city'] = thevenue.city
  venue['state'] = thevenue.state
  venue['phone'] = thevenue.phone
  venue['website'] = thevenue.website
  venue['facebook_link'] = thevenue.facebook_link
  venue['seeking_talent'] = thevenue.seeking_talent
  venue['seeking_description'] = thevenue.seeking_description
  venue['image_link'] = thevenue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue()
  noerror = True
  try:
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
  except:
    noerror = False
    db.session.rollback()
  finally:
    db.session.close()
  if noerror:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  form = ArtistForm(request.form)
  artist = Artist()
  # TODO: modify data to be the data object returned from db insertion
  noerror = True
  try:
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
  except:
    noerror = False
    db.session.rollback()
  finally:
    db.session.close()
  if noerror:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.') 

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show_list = []
  result = db.session.execute(select(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Show.venues).join(Show.artists))
  for venueId, venueName, artistId, artistName, artistImageLink, showStartTime in result:
    each = {}
    each['venue_id'] = venueId
    each['venue_name'] = venueName
    each['artist_id'] = artistId
    each['artist_name'] = artistName
    each['artist_image_link'] = artistImageLink
    each['start_time'] = showStartTime
    show_list.append(each)
  data = show_list
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  show = Show()
  # TODO: modify data to be the data object returned from db insertion
  noerror = True
  try:
    show.artist_id = form.artist_id.data
    show.venue_id = form.venue_id.data
    show.start_time = form.start_time.data
    db.session.add(show)
    db.session.commit()
  except:
    noerror = False
    db.session.rollback()
  finally:
    db.session.close()
  if noerror:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred. Show could not be listed.')

  return render_template('pages/home.html')

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
