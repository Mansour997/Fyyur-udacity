#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from inspect import isasyncgenfunction, isfunction
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import flask_migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from sqlalchemy import exc
import sys
from models import db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.s
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
migrate = Migrate(app, db)
db.init_app(app)

# TODO: connect to a local postgresql database [DONE]


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





#  Helper functions
#  ----------------------------------------------------------------

def linearsearch(arr, x):
   for i in range(len(arr)):
      if arr[i] == x:
         return i
   return -1


def binarySearch(arr, x):
    print('inside binary')
    print(arr)
    print(x)
    print(len(arr))
    if len(arr) == 1:
      if arr[0] == x:
        print('first if first if')
        return 5 
      else:
        print('first if first else')
        return -1
    
    if (len(arr) == 2):
      if (arr[0] == x or arr[1] == x):
        print('second if first if')
        return 5 
      else:
        print('second if first else')
        return -1
        
    l = 0
    r = len(arr)
    while (l <= r):
        m = l + ((r - l) // 2)
        print(m)
        res = (x == arr[m])
        print(res)
        # Check if x is present at mid
        if (res == 0):
            return m - 1
 
        # If x greater, ignore left half
        if (res > 0):
            l = m + 1
 
        # If x is smaller, ignore right half
        else:
            r = m - 1
 
    return -1







#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
  # TODO: replace with real venues data. [DONE]
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  theVenues = db.session.query(Venue).all()
  data = []
  statesCovered = []
  statesCovered.append((theVenues[0].state + theVenues[0].city).lower())

  # can use: db.session.query(Venue).distinct(Venue.city, Venue.state).all()


  # in this loop we will insert uniquely the states and cities only
  z = 0 
  for z in range(len(theVenues)):

    result = 0
    if(z == 0):
      result = -1
    else:
      result = linearsearch(statesCovered, (theVenues[z].state + theVenues[z].city).lower())
      


    if (result == -1):

      if(z != 0):
        statesCovered.append((theVenues[z].state + theVenues[z].city).lower())

      # in this loop we will go through all the venues and add the
      # venues in which the current state and city names are matched with them
      x = 0
      for x in range(len(theVenues)):


        if (statesCovered[-1] == (theVenues[x].state + theVenues[x].city).lower()):
          data.append({
            "city": theVenues[x].city,
            "state": theVenues[x].state,
            "venues": []
          })

          # in this loop we will insert all the venues of the same city/state
          y = 0
          for y in range(len(theVenues)):

            if (statesCovered[-1] == (theVenues[y].state + theVenues[y].city).lower()):
              

              upcoming_shows_count = 0
              
              for show in theVenues[y].shows:

                if (show.start_time > datetime.today()):
                  upcoming_shows_count += 1

              data[-1]["venues"].append({
                "id": theVenues[y].id,
                "name": theVenues[y].name,
                "num_upcoming_shows": upcoming_shows_count,
              })
            
            y += 1
        x += 1


    z +=1


  return render_template('pages/venues.html', areas=data);








@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.[DONE]
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_value = request.form.get('search_term', '')
  resData = Venue.query.filter(Venue.name.like('%' + search_value + '%')).all()
  data = []


  for res in resData:
    
    upcoming_shows_count = 0
    x = 0

    for x in range(len(res.shows)):
      if res.shows[x].start_time > datetime.today():
        upcoming_shows_count += 1 
      x += 1

    data.append({
      "id": res.id,
      "name": res.name,
      "num_upcoming_shows": upcoming_shows_count
    })

  response={
    "count": len(resData),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))








@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id [DONE]

  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  all_shows =  db.session.query(Show).join(Show.venue).filter(Show.venue_id==venue_id).all()

  past_shows = []
  upcoming_shows = []

  for show in all_shows:
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(venue)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  
  return render_template('pages/show_venue.html', venue=data)






#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)







@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead [DONE]
  # TODO: modify data to be the data object returned from db insertion [DONE]

  # extract data [DON E]
  # validate [DON E]
  # save it in an ORM object [DON E]
  # send it to the database [DON E]

  
  formV = VenueForm(request.form)

  name = formV.name.data
  city = formV.city.data
  state = formV.state.data
  address = formV.address.data
  phone = formV.phone.data
  image_link = formV.image_link.data
  genres = formV.genres.data
  facebook_link = formV.facebook_link.data
  website_link = formV.website_link.data
  seeking_talent = formV.seeking_talent.data
  seeking_description = formV.seeking_description.data


  print("this the content received from the formV:")
  print(name)
  print(phone)
  error = False

  venue = Venue(name = name,
                    city = city,
                    state = state,
                    address = address,
                    phone = phone,
                    image_link = image_link,
                    genres = ",".join(genres),
                    facebook_link = facebook_link,
                    website_link = website_link,
                    seeking_talent = seeking_talent,
                    seeking_description =seeking_description)
      
  try:
        db.session.add(venue)
        db.session.commit()
  except:
        print("problem occured")
        error = True
        db.session.rollback()
  finally:
        db.session.close()
  
  if not error:
    print("no error")
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + "f" + ' could not be listed.')


  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.[DONE]
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')






@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using[DONE]
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  venueId = request.form['venue_id']

  try:
    Venue.query.filter_by(id=venueId).delete()
    db.session.commit()
  except:
    print(sys.exc_info())
    db.session.rollback()
  finally:    
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  return None #jsonify({"success": True}) [complete]










#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database [DONE]

  artists = db.session.query(Artist).all()
  data = []

  for artist in artists:
    data.append({
    "id": artist.id,
    "name": artist.name,
    })

  return render_template('pages/artists.html', artists=data)







@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. [DONE]
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  
  search_value = request.form.get('search_term', '')
  resData = Artist.query.filter(Artist.name.like('%' + search_value + '%')).all()
  data = []


  for res in resData:
    
    upcoming_shows_count = 0
    x = 0

    for x in range(len(res.shows)):
      if res.shows[x].start_time > datetime.today():
        upcoming_shows_count += 1 
      x += 1

    data.append({
      "id": res.id,
      "name": res.name,
      "num_upcoming_shows": upcoming_shows_count
    })

  response={
    "count": len(resData),
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))







@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id [DONE]
  
  
  artist = db.session.query(Artist).filter_by(id=artist_id).first()
  all_shows =  db.session.query(Show).join(Show.artist).filter(Show.artist_id==artist_id).all()
  past_shows = []
  upcoming_shows = []


  for show in all_shows:
    temp_show = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    }
    if show.start_time <= datetime.now():
        past_shows.append(temp_show)
    else:
        upcoming_shows.append(temp_show)

  # object class to dict
  data = vars(artist)

  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)
  

  return render_template('pages/show_artist.html', artist=data)








#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artistData = db.session.query(Artist).filter_by(id=artist_id).first()

  artist={
    "id": artistData.id,
    "name": artistData.name,
    "genres": artistData.genres,
    "city": artistData.city,
    "state": artistData.state,
    "phone": artistData.phone,
    "website": artistData.website_link,
    "facebook_link": artistData.facebook_link,
    "seeking_venue": artistData.seeking_venue,
    "seeking_description": artistData.seeking_description,
    "image_link": artistData.image_link
  }

  form.name.data = artistData.name
  form.genres.data = artistData.genres.split(",")
  form.city.data = artistData.city
  form.state.data = artistData.state
  form.phone.data = artistData.phone
  form.website_link.data = artistData.website_link
  form.facebook_link.data = artistData.facebook_link
  form.seeking_venue.data = artistData.seeking_venue
  form.seeking_description.data = artistData.seeking_description
  form.image_link.data = artistData.image_link

  # TODO: populate form with fields from artist with ID <artist_id> [DONE]
  return render_template('forms/edit_artist.html', form=form, artist=artist)





@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing [DONE]
  # artist record with ID <artist_id> using the new attributes

  artist = db.session.query(Artist).filter_by(id=artist_id).first()
  
  formA = ArtistForm(request.form)


  artist.name = formA.name.data
  artist.genres = ','.join(formA.genres.data)
  artist.city = formA.city.data
  artist.state = formA.state.data
  artist.phone = formA.phone.data
  artist.facebook_link = formA.facebook_link.data
  artist.seeking_venue = True
  artist.seeking_description = formA.seeking_description.data
  artist.website_link = formA.website_link.data
  artist.image_link = formA.image_link.data

  try:
    db.session.commit()
  except:
    print("problem occured")
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))






@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venueData = db.session.query(Venue).filter_by(id=venue_id).first()


  venue = {
    "id": venueData.id,
    "name": venueData.name,
    "genres": venueData.genres.split(','),
    "address": venueData.address,
    "city": venueData.city,
    "state": venueData.state,
    "phone": venueData.phone,
    "website": venueData.website_link,
    "facebook_link": venueData.facebook_link,
    "seeking_talent": venueData.seeking_talent,
    "seeking_description": venueData.seeking_description,
    "image_link": venueData.image_link
  }

  form.name.data = venueData.name
  form.genres.data = venueData.genres.split(",")
  form.city.data = venueData.city
  form.state.data = venueData.state
  form.phone.data = venueData.phone
  form.website_link.data = venueData.website_link
  form.facebook_link.data = venueData.facebook_link
  form.seeking_talent.data = venueData.seeking_talent
  form.seeking_description.data = venueData.seeking_description
  form.image_link.data = venueData.image_link


  # TODO: populate form with values from venue with ID <venue_id> [DONE]
  return render_template('forms/edit_venue.html', form=form, venue=venue)





@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing [DONE]
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)

  form = VenueForm(request.form)

  venue.name = form.name.data
  venue.genres = ','.join(form.genres.data)
  venue.address = form.address.data
  venue.city = form.city.data
  venue.state = form.state.data
  venue.phone = form.phone.data
  venue.website_link = form.website_link.data
  venue.facebook_link = form.facebook_link.data
  venue.seeking_talent = True
  venue.seeking_description = form.seeking_description.data
  venue.image_link = form.image_link.data

  try:
    db.session.commit()
  except:
    print("problem occured")
    print(sys.exc_info())
    db.session.rollback()
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
  # TODO: insert form data as a new Venue record in the db, instead [DONE]
  # TODO: modify data to be the data object returned from db insertion [DONE]

    
  formA = ArtistForm(request.form)

  name = formA.name.data
  city = formA.city.data
  state = formA.state.data
  phone = formA.phone.data
  genres = formA.genres.data
  image_link = formA.image_link.data
  facebook_link = formA.facebook_link.data
  website_link = formA.website_link.data
  seeking_venue = formA.seeking_venue.data
  seeking_description = formA.seeking_description.data

  error = False

  artist = Artist(name = name,
                    city = city,
                    state = state,
                    phone = phone,
                    image_link = image_link,
                    genres = ",".join(genres),
                    facebook_link = facebook_link,
                    website_link = website_link,
                    seeking_venue = seeking_venue,
                    seeking_description =seeking_description)
    

  try:
        db.session.add(artist)
        db.session.commit()
  except:
        print("problem occured")
        print(sys.exc_info())
        error = True
        db.session.rollback()
  finally:
        db.session.close()
  
  if not error:
        print("no error")
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
        flash('An error occurred. Artist ' + artist.name + ' could not be listed.')



  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead. [DONE]
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.[DONE]
  
  current_date = datetime.today()

  shows = db.session.query(Show).filter(Show.start_time > current_date).all()

  data=[]

  for show in shows:
    data.append({
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": show.artist.image_link,
    "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
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
  # TODO: insert form data as a new Show record in the db, instead [DONE]

  formS = ShowForm(request.form)

  artist_id = formS.artist_id.data
  venue_id = formS.venue_id.data
  start_time = formS.start_time.data
  
  #.date().strftime('%m/%d/%y %H:%M:%S')
  
  #datetime.strptime('2021/12/22 12:22:23', '%m/%d/%y %H:%M:%S')

  
  show = Show(artist_id = int(artist_id),
              venue_id = int(venue_id),
              start_time = start_time)

  error = False
  print('show:')
  print(show)
  print(show.start_time)
  try:
        db.session.add(show)
        db.session.commit()
  except:
        print("problem occured")
        print(sys.exc_info())
        error = True
        db.session.rollback()
  finally:
        db.session.close()
  
  if not error:
    print("no error")
    flash('Show was successfully listed!')
  else:
    flash('An error occurred. Show could not be listed.')


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.[DONE]
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
