import pickle, json
from SPARQLWrapper import SPARQLWrapper, JSON


class Director(object):
    """
    Director representation.
    """
    def __init__(self, name):
        self.name = name
        self.url = None
        self.date_birth = None
        self.places_birth = []
        self.gender = None
        self.movies = []
        self.photo = None

    def __str__(self):
        name = "name: " + str(self.name)
        url = "url: " + str(self.url)
        date_birth = "date_birth: " + str(self.date_birth)
        places_birth = "places_birth: " + str(self.places_birth)
        gender = "gender: " + str(self.gender)
        movies = "movies: " + str(self.movies)
        photo = "photo: " + str(self.photo)
        return "\n".join([name, url, date_birth, places_birth, gender, movies, photo])


def extract_directors_names(filename):
    """
    :param filename: file contains the directors names
    :return: list of directors names
    """
    names = []
    with open(filename, 'rb') as f:
        while 1:
            try:
                names.extend(pickle.load(f))
            except EOFError:
                break
    return names


def save_in_json(director):
    filename = "_".join(director.name.split()) # firstName_lastName
    with open("data/{}.txt".format(filename), 'wb') as out:
        json.dump(director.__dict__, out)


def runquery(query):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results


def make_director_query(director_name):
    query =  """
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX yago: <http://dbpedia.org/class/yago/>

            SELECT DISTINCT ?url ?dateBirth ?placeBirth ?gender ?movie ?photo
                WHERE {{
                     ?url foaf:name "{}"@en .
                     ?url a yago:FilmMaker110088390.
                     OPTIONAL {{ ?url       dbo:birthDate  ?dateBirth     }}.
                     OPTIONAL {{ ?url       dbo:birthPlace ?placeBirth    }}.
                     OPTIONAL {{ ?url       dbo:deathPlace ?placeDeat     }}.
                     OPTIONAL {{ ?url       foaf:gender 	?gender	      }}.
                     OPTIONAL {{ ?movie_url dbo:director ?url	          }}.
                     OPTIONAL {{ ?movie_url foaf:name 	?movie	          }}.
                     OPTIONAL {{ ?url       dbo:thumbnail 	?photo        }}.
                }}
            """.format(director_name)
    return query


def make_director(name, res):
    vars = res["head"]["vars"]
    results = res["results"]["bindings"]
    if not results:
        return None
    ans = Director(name)
    for result in results:  # res: var -> ("value" -> val)
        for var in vars:
            var_res = result.get(var) # can be None if value not found
            if var_res:
                if var == "url":
                    ans.url = var_res["value"]
                elif var == "dateBirth":
                    ans.date_birth = var_res["value"]
                elif var == "placeBirth":
                    ans.places_birth.append(var_res["value"])
                elif var == "gender":
                    ans.gender = var_res["value"]
                elif var == "movie":
                    ans.movies.append(var_res["value"])
                elif var == "photo":
                    ans.photo = var_res["value"]

    ans.places_birth = fix_places(ans.places_birth)
    ans.movies = list(set(ans.movies))

    return ans


def fix_places(places):
    places = list(set(places)) # remove duplicates
    places = [place[place.rfind('/')+1:len(place)] for place in places] # only the name
    places = [place.replace('_', ' ') for place in places]
    places = ", ".join(places)
    return places


# debug
def print_results(results):
    vars = results["head"]["vars"]
    results = results["results"]["bindings"]
    if not results:
        print "No results"
        return
    for res in results:  # res: var -> ("value" -> val)
        for var in vars:
            var_res = res.get(var)  # can be None if value not found
            if var_res:
                print "{}: {}".format(var, var_res["value"])
            else:
                print "{}: None".format(var)


# debug
def test(name):
    q = make_director_query(name)
    res = runquery(q)
    director = make_director(name, res)
    print director


def directors_data():
    directors_names = extract_directors_names("directors_names.txt")
    directors_names = list(set(directors_names)) # remove duplicates
    count = 0 # counts the number of results found
    print "==== Start {} directors queries ====".format(len(directors_names))

    for idx, name in enumerate(directors_names):
        print "Running query with {} number {}...".format(name, idx)
        q = make_director_query(name)
        res = runquery(q)
        director = make_director(name, res)
        print director
        if director: # can be None if no results found
            save_in_json(director)
            count += 1
        print " =========== "
    print "DONE with {} directors".format(count)

    # test("Christopher Nolan")

if __name__ == "__main__":
    directors_data()