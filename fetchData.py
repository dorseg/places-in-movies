from imdb import IMDb
import pickle, json, sys

PREFIX_URL = "www.imdb.com/title/tt"

PARSED_MOVIES = 0
TOTAL_MOVIES = 0

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
    global PARSED_MOVIES
    PARSED_MOVIES += 1
    with open("data/{}.txt".format(details.id), 'wb') as out:
        json.dump(details.__dict__, out)


def fix_loc(loc):
    delimiter = loc.find('::')
    if delimiter == -1:
        return loc
    else:
        return loc[:delimiter]


def main():
    global TOTAL_MOVIES
    filename = str(sys.argv[1]) + "_" + str(sys.argv[2]) + ".txt"
    TOTAL_MOVIES = int(sys.argv[3])
    movie_ids = extract_ids("crawler/ids/{}".format(filename))
    print "Number of ids: ", len(movie_ids)
    print "Start parsing {} movies...".format(TOTAL_MOVIES)
    ia = IMDb()
    for id in movie_ids:
        if PARSED_MOVIES == TOTAL_MOVIES:
            print "============== DONE =============="
            break

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





