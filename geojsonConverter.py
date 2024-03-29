import ner, json, geojson, os
from opencage.geocoder import OpenCageGeocode
from geojson import Point, Feature, FeatureCollection

# first, run:
# java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.all.3class.distsim.crf.ser.gz -port 9191
# in stanford ner tagger folder


class GeoLocation(object):
    """
    Store GeoLocation details
    """
    def __init__(self, location, lng, lat):
        self.location = location
        self.lng = lng
        self.lat = lat

    def __repr__(self):
        return "(location: {}, lng: {}, lat: {})".format(self.location,self.lng,self.lat)

    def get_cords(self):
        return self.lng, self.lat


tagger = ner.SocketNER(host='localhost', port=9191, output_format='slashTags')
key = '62b1d8e337ce45d1b49f37ef167e7911'
geocoder = OpenCageGeocode(key)
features = []
limit = 2500
default_pic = "default_pic.jpg"


def get_geolocation(loc):
    geo = None
    result = geocoder.geocode(loc)
    if result and len(result):
        loc = result[0]['formatted']
        lng = result[0]['geometry']['lng']
        lat = result[0]["geometry"]['lat']
        geo = GeoLocation(loc, lng, lat)
    return geo


def movie_to_geojson(data_folder):
    counter = 0
    files = sorted(os.listdir(data_folder))
    print "Start encoding files in {}".format(data_folder)
    for file in files:
        if counter == limit:
            break
        counter += 1
        with open("{}/{}".format(data_folder, file), 'r') as f:
            print "====Parsing file {}====".format(file)
            movie_details = json.loads(f.read())
            synopsis = movie_details['synopsis']
            tagged_synopsis = tagger.get_entities(synopsis)
            if 'LOCATION' not in tagged_synopsis:
                print "No locations, continue..."
                continue
            locations = list(set(tagged_synopsis['LOCATION']))  # remove duplicates
            try:
                geolocations = filter(lambda x: x is not None, map(get_geolocation, locations))
            except Exception as e:
                print e
                break
            if not geolocations:
                print "No Geolocations, continue..."
                continue
            ignore_keys = ["filming_locations", "synopsis"]
            movie_details = {key: movie_details[key] for key in movie_details if key not in ignore_keys}
            movie_details["num_of_locations"] = len(geolocations);
            movie_details["marker-color"] = "0044FF"
            movie_details["marker-symbol"] = "cinema"
            for geo in geolocations:
                #print geo
                props = movie_details.copy()
                props["location"] = geo.location
                point = Point(geo.get_cords())
                feature = Feature(geometry=point, properties=props)
                features.append(feature)


def directors_to_geojson(data_folder):
    counter = 0
    files = os.listdir(data_folder)
    print "Start encoding files in {}".format(data_folder)
    for file in files:
        if counter == limit:
            break
        counter += 1
        with open("{}/{}".format(data_folder, file), 'r') as f:
            print "====Parsing file {}====".format(file)
            director_details = json.loads(f.read())
            places_birth = director_details['places_birth']
            if not places_birth:
                print "No place birth, continue..."
                continue
            try:
                geolocation = get_geolocation(places_birth)
            except Exception as e:
                print e
                break
            if not geolocation:
                print "No Geolocation, continue..."
                continue
            if not director_details['photo']:
                director_details['photo'] = default_pic
            director_details['location'] = geolocation.location
            director_details["marker-color"] = "FF0000"
            director_details["marker-symbol"] = "marker"
            props = director_details.copy()
            point = Point(geolocation.get_cords())
            feature = Feature(geometry=point, properties=props)
            features.append(feature)


def write_to_file(filename):
    collection = FeatureCollection(features)
    with open(filename, 'w') as out:
        geojson.dump(collection, out)


def main():
    #data_folder = u"data/1985_1995"
    #movie_to_geojson(data_folder1)
    data_folder = "/home/elisim/Downloads/temp"
    movie_to_geojson(data_folder)
    print "Created {} features".format(len(features))
    write_to_file("1990s2.geojson")

    # 1990s1.geojson
    # directors.geojson
    #


if __name__ == '__main__':
    main()






