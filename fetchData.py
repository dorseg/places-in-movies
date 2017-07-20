from imdb import IMDb
import pickle, json, sys

class MovieDetails(object):
    """
    Store movie details
    """
    def __init__(self, title, year, genres, directors, rating, filming_locations, synopsis):
        self.title = title
        self.year = year
        self.genres = genres
        self.directors = directors
        self.rating = rating
        self.filming_locations = filming_locations
        self.synopsis = synopsis


def extract_ids(filename):
    """
    :param filename: file containing movie ids
    :return: list of movie ids
    """
    ids = []
    with open(filename, 'rb') as f:
        while 1:
            try:
                ids.extend(pickle.load(f))
            except EOFError:
                break

    ids = [id[:-1] for id in ids] # remove last character
    return ids


def main():
    filename = str(sys.argv[1]) + "_" + str(sys.argv[2]) + ".txt"
    movie_ids = extract_ids("crawler/ids/{}".format(filename))
    print len(movie_ids) # <<<<<<<<<< remove

    ia = IMDb()
    for id in movie_ids:
        movie = ia.get_movie(id)
        print "Parsing movie {}".format(id)
        ia.update(movie, ['synopsis', 'locations'])  # fetch the 'synopsis' and 'locations' data sets.
        title = movie.get('title')
        #print "Movie name: {}".format(title)
        year = movie.get('year')
        genres = movie.get('genres')  # list of unicode strings
        directors = [director.get('name') for director in movie.get('director')]  # list of names
        rating = movie.get('rating')
        locs = movie.get('locations')
        filming_locs = [loc[:loc.find('::')] for loc in locs] if locs else None
        synopsis = movie.get('synopsis')
        movie_details = MovieDetails(title, year, genres, directors, rating, filming_locs, synopsis)
        with open("data/{}.txt".format(id), 'wb') as out:
            json.dump(movie_details.__dict__, out)

if __name__ == '__main__':
    main()





