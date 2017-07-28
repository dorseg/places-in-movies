import ner, json, geojson, os
from opencage.geocoder import OpenCageGeocode
from geojson import MultiPoint, Feature, FeatureCollection

# first, run:
# java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.all.3class.distsim.crf.ser.gz -port 9191
# in stanford ner tagger folder

tagger = ner.SocketNER(host='localhost', port=9191, output_format='slashTags')
key = '42bae5691544417f8d1a7922f8bc9d48'
geocoder = OpenCageGeocode(key)

features = []

def get_geolocation(loc):
    cord = ()
    result = geocoder.geocode(loc)
    if result and len(result):
        lng = result[0]['geometry']['lng']
        lat = result[0]["geometry"]['lat']
        cord = (lng,lat)
    return cord


print "Start parsing..."
files = os.listdir(u"data_example")
for file in files:
    with open("data_example/{}".format(file), 'r') as f:
        print "====Parsing file {}====".format(file)
        movie_details = json.loads(f.read())
        synopsis = movie_details['synopsis']
        tagged_synopsis = tagger.get_entities(synopsis)
        if 'LOCATION' not in tagged_synopsis:
            print "No locations, continue..."
            continue
        locations = tagged_synopsis['LOCATION']
        locations = list(set(tagged_synopsis['LOCATION']))  # remove duplicates
        geo_locations = filter(lambda cord: len(cord) > 0, map(get_geolocation, locations))
        points = MultiPoint(geo_locations)
        movie_details["synopsis_locations"] = locations
        feature = Feature(geometry=points, properties=movie_details)
        features.append(feature)

collection = FeatureCollection(features)
with open("movies.geojson", 'w') as out:
    geojson.dump(collection, out)




