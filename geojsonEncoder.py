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
key = '42bae5691544417f8d1a7922f8bc9d48'
geocoder = OpenCageGeocode(key)
features = []
limit = 100


def get_geolocation(loc):
    geo = None
    result = geocoder.geocode(loc)
    if result and len(result):
        lng = result[0]['geometry']['lng']
        lat = result[0]["geometry"]['lat']
        geo = GeoLocation(loc, lng, lat)
    return geo


def encode_to_geojson(data_folder):
    counter = 0
    files = os.listdir(data_folder)
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
            ignore_keys = ["filming_locations", "synopsis", "id"]
            movie_details = {key: movie_details[key] for key in movie_details if key not in ignore_keys}
            movie_details["marker-color"] = "0044FF"
            movie_details["marker-symbol"] = "cinema"
            for geo in geolocations:
                #print geo
                props = movie_details.copy()
                props["location"] = geo.location
                point = Point(geo.get_cords())
                feature = Feature(geometry=point, properties=props)
                features.append(feature)


def write_to_file():
    collection = FeatureCollection(features)
    with open("movies.geojson", 'w') as out:
        geojson.dump(collection, out)


def main():
    data_folder1 = u"data/1985_1995"
    data_folder2 = u"data/2005_2015"
    encode_to_geojson(data_folder1)
    encode_to_geojson(data_folder2)
    print "Created {} featurs".format(len(features))
    write_to_file()


if __name__ == '__main__':
    main()






