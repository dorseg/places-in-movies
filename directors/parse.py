import sys, os
import pickle, json
import dbpedia

"""
Run this file with
> python parse.py <movies data directory>
"""

def parse_directors(data_dir):
    """
    :param data_dir: directory name contains the data to parse
    :return: python list of the directors names.
    """
    names = []
    for filename in os.listdir(data_dir):
        print "Parsing the file {}...".format(filename)
        name = get_director_name(data_dir + '/' + filename)
        names.extend(name)
    return names


def get_director_name(filename):
    """
    :param filename: movie's file name
    :return: list of director names
    """
    with open(filename, 'rb') as json_file:
        data = json.load(json_file)
    return data["directors"]


def save_in_file(filename, directors):
    """
    Save the directors list 'directors' in file named 'filename'
    """
    with open(filename, 'ab') as f:
        pickle.dump(directors, f)


def main():
    data_dir = sys.argv[1]
    print "Start parsing data from the directory:", data_dir
    directors = parse_directors(data_dir)
    save_in_file("directors_names.txt", directors)
    print "DONE"

    dbpedia.directors_data()

if __name__ == "__main__":
    main()


