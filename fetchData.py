from imdb import IMDb
import MovieDetails
import json

ia = IMDb()

movie_ids = []

with open("crawler/ids/2016_2016.txt", 'r') as f:
    movie_ids = f.read().splitlines()

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
