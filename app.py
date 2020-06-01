#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    show = db.relationship('Show', backref='venue')
    def __repr__(self):
     return f'{self.id}{self.name}'

    
    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String())
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    show= db.relationship('Show',backref='artist')

    def __repr__(self):
     return f'<Artist {self.id} {self.name}>'

class Show(db.Model):
    
    __tablename__='Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'))
    venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'))
    start_time = db.Column(db.DateTime)
    def __repr__(self):
     return f'<Show {self.id} {self.start_time}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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

  data=[]
  
  alll = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  

  for each in alll:
    each_venues = Venue.query.filter_by(city=each.city).filter_by(state=each.state).all()
    venue_data = []
    for venue in each_venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
      })
    data.append({
      "city": each.city,
      "state": each.state, 
      "venues": venue_data
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
 
  the_indicated = request.form.get('Hop', 'Music','')
  all_result = db.session.query(Venue).filter(Venue.name.ilike(f'%{the_indicated}%')).all()
  data = []

  for result in all_result:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count": len(all_result),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue =Venue.query.get(venue_id)
  upcoming_shows = []
  past_shows = []
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
 
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()


  for show in past_shows_query:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")    
    })

  data = {
    "id": venue.id,"name": venue.name,
    "genres": venue.genres,"address": venue.address,
    "city": venue.city,"state": venue.state,
    "phone": venue.phone,"website": venue.website,
    "facebook_link": venue.facebook_link,"seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,"image_link": venue.image_link,
    "past_shows": past_shows,"upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),"upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  error=False
  try:
    name =  request.form['name']
    city =  request.form['city']
    state =  request.form['state']
    genres=  request.form.getlist('genres')
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_talent= True if 'seeking_talent' in request.form else False
    seeking_description=request.form['seeking_description']
    
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                  facebook_link=facebook_link, image_link=image_link, website=website,
                    seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
    error =True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  if not error:
   flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # on unsuccessful db insert, flash an error instead.
  if error :
   flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  try:
    venue = Venue.query.get('venue_id')
    db.session.delete(venue)
    db.session.commit()
  except:
    error =True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
 
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  #  replace with real data returned from querying the database
  data= db.session.query(Artist).all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
 
  the_indicated = request.form.get('A', 'band','')
  all_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{the_indicated}%')).all()
  data = []

  for result in all_result:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
    })
  
  response={
    "count": len(all_result),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
 
  artist =Artist.query.get(artist_id)
  upcoming_shows = []
  past_shows = []
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()


  for show in past_shows_query:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
 

  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_image_link": show.venue.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })


  data = {
    "id": artist.id,"name": artist.name,
    "genres": artist.genres,"city": artist.city,
    "state": artist.state,"phone": artist.phone,
    "website": artist.website,"facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,"seeking_description": artist.seeking_description,
    "image_link": artist.image_link,"past_shows": past_shows,
    "upcoming_shows": upcoming_shows,"past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website.data = artist.website
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  error=False
  artist =Artist.query.get(artist_id)
  try:
      artist.name =  request.form['name']
      artist.city =  request.form['city']
      artist.state =  request.form['state']
      artist.genres=  request.form.getlist('genres')
      artist.phone = request.form['phone']
      artist.image_link = request.form['image_link']
      fartist.acebook_link = request.form['facebook_link']
      artist.website = request.form['website']
      artist.seeking_venue= True if 'seeking_venue' in request.form else False
      artist.seeking_description=request.form['seeking_description']
      
      db.session.commit()
  except:
      error =True
      db.session.rollback()
      print(sys.exc_info())
  finally:
    db.session.close()
 
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website.data = venue.website
  form.seeking_venue.data = venue.seeking_venue
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  error=False
  venue=Venue.query.get(venue_id)
  try:
    venue.name =  request.form['name']
    venue.city =  request.form['city']
    venue.state =  request.form['state']
    venue.genres=  request.form.getlist('genres')
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link = request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    venue.website = request.form['website']
    venue.seeking_talent= True if 'seeking_talent' in request.form else False
    venue.seeking_description=request.form['seeking_description']
    

    db.session.commit()
  except:
    error =True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
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
  error=False
  try:
      artist = Artist()
      artist.name =  request.form['name']
      artist.city =  request.form['city']
      artist.state =  request.form['state']
      artist.genres=  request.form.getlist('genres')
      artist.phone = request.form['phone']
      artist.image_link = request.form['image_link']
      facebook_link = request.form['facebook_link']
      artist.website = request.form['website']
      artist.seeking_venue= True if 'seeking_venue' in request.form else False
      artist.seeking_description=request.form['seeking_description']
      
      
      db.session.add(artist)
      db.session.commit()
  except:
      error =True
      db.session.rollback()
      print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  if not error:
   flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # on unsuccessful db insert, flash an error instead.
  if error :
   flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data=[]
  alll=db.session.query(Show).join(Artist).join(Venue).all()
  
  for show in alll :
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
      
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
 
   error=False
   try:  
      show = Show(venue_id= request.form['venue_id'], artist_id=request.form['artist_id'], start_time=equest.form['start_time'])
      db.session.add(show)
      db.session.commit()
   except:
      error =True
      db.session.rollback()
      print(sys.exc_info())
   finally:
      db.session.close()

  # on successful db insert, flash success
   if not error:
     flash('Show was successfully listed!')
  # on unsuccessful db insert, flash an error instead.
   if error:
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
