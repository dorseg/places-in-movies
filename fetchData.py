from imdb import IMDb
ia = IMDb()

movie_ids = []

with open("crawler/ids/2016_2016.txt", 'r') as f:
    movie_ids = f.read().splitlines()

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