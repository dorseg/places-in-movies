from imdb import IMDb
import pickle

movie_ids = []
filename = "crawler/ids/2010_2017.txt"
with open(filename, 'rb') as f:
    while 1:
        try:
            movie_ids.extend(pickle.load(f))
        except EOFError:
            break

print len(movie_ids)

ia = IMDb()
for id in movie_ids:
    movie = ia.get_movie(id)
    ia.update(movie, ['synopsis', 'locations'])  # fetch the 'synopsis' and 'locations' data sets.
    synopsis = movie.get('synopsis')
    title = movie.get('title')
    year = movie.get('year')
    genres = movie.get('genres')  # list of unicode strings
    rating = movie.get('rating')
    locations = [location[:location.find('::')] for location in movie.get('locations')] # list of names
    directors = [director.get('name') for director in movie.get('director')]  # list of names
