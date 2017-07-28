import ner, json

# first, run:
# java -mx1000m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer -loadClassifier classifiers/english.all.3class.distsim.crf.ser.gz -port 9191
# in stanford ner tagger folder

tagger = ner.SocketNER(host='localhost', port=9191, output_format='slashTags')

id = "1985_1995/0088889"

with open("data/{}.txt".format(id), 'r') as f:
    movie_details = json.loads(f.read())
    synopsis = movie_details['synopsis']

tagged_synopsis = tagger.get_entities(synopsis)
locations = list(set(tagged_synopsis['LOCATION']))
print locations
