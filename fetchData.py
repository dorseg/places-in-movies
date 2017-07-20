from imdb import IMDb
import pickle, json, sys

PREFIX_URL = "www.imdb.com/title/tt"

class MovieDetails(object):
    """
    Store movie details
    """
    def __init__(self, id, url, title, year, genres, directors, rating, filming_locations, synopsis):
        self.id = id
        self.url = url
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

    #ids = [id[:-1] for id in ids] # remove last character
    return ids


def save_in_json(details):
    with open("data/{}.txt".format(details.id), 'wb') as out:
        json.dump(details.__dict__, out)


def fix_loc(loc):
    delimiter = loc.find('::')
    if delimiter == -1:
        return loc
    else:
        return loc[:delimiter]


def main():
    filename = str(sys.argv[1]) + "_" + str(sys.argv[2]) + ".txt"
    movie_ids = extract_ids("crawler/ids/{}".format(filename))
    print "Number of ids: ", len(movie_ids)

    ia = IMDb()
    for id in movie_ids:
        movie = ia.get_movie(id)
        print "Parse movie {}".format(id)
        ia.update(movie, ['synopsis', 'locations'])  # fetch the 'synopsis' and 'locations' data sets.
        synopsis = movie.get('synopsis')
        directors = movie.get('director') # list of Persons objects
        genres = movie.get('genres')  # list of unicode strings
        rating = movie.get('rating')
        locs = movie.get('locations')

        if not synopsis or not directors or not genres or not locs or not rating:
            print "Bad movie! Continue..."
            continue

        url = PREFIX_URL + id
        title = movie.get('title')
        year = movie.get('year')
        directors = [director.get('name') for director in directors] # list of unicode strings
        filming_locs = map(fix_loc, locs)

        movie_details = MovieDetails(id, url, title, year, genres, directors, rating, filming_locs, synopsis)
        save_in_json(movie_details)

if __name__ == '__main__':
    main()





