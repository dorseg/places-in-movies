import pickle


def extract_directors_names(filename):
    """
    :param filename: file directors names
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


def get_data_dbpedia(names):
    pass
