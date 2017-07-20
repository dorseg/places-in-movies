from imdb import IMDb
import pickle
import MovieDetails
import json

ia = IMDb()
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
    title = movie.get('title')
    year = movie.get('year')
    genres = movie.get('genres')  # list of unicode strings
    directors = [director.get('name') for director in movie.get('director')]  # list of names
    rating = movie.get('rating')
    filming_locations = [location[:location.find('::')] for location in movie.get('locations')] # list of names
    synopsis = movie.get('synopsis')
    movie_details = MovieDetails(title, year, genres, directors, rating, filming_locations, synopsis)
    with open("data/{}.txt".format(id), 'w') as out:
        json.dump(movie_details, out)
