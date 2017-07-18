from imdb import IMDb
ia = IMDb()

movieObject = ia.get_movie('0111161')
ia.update(movieObject, ['synopsis', 'locations'])  # fetch the 'synopsis' and 'locations' data sets.
locations = [location[:location.find('::')] for location in movieObject.get('locations')]
synopsis = movieObject.get('synopsis')
title = movieObject.get('title')
year = movieObject.get('year')
genres = movieObject.get('genres') # list of unicode strings
directors = [director.get('name') for director in movieObject.get('director')]  # Person list
rating = movieObject.get('rating')

print locations
print movieObject.summary()


