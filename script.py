import os, sys, math

### Bad movies calculation
# bad movies will be relative to the number of movies. We decided
# to set:
#     bad_movies = 0.2 * num_of_movies
# Therefore:
#     pages = (num_of_movies + 0.2*num_of_movies)/MOVIES_IN_PAGE with upper bound

MOVIES_IN_PAGE = 50

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def main():
    start, end, num_of_movies = sys.argv[1], sys.argv[2], int(sys.argv[3])
    pages = int(math.ceil((1.2*num_of_movies)/MOVIES_IN_PAGE))
    print colors.FAIL + ">>>>>> Number of pages: {}".format(pages) + colors.ENDC
    os.chdir("crawler")
    print colors.FAIL + ">>>>>> Running scrapy..."+ colors.ENDC
    os.system("scrapy crawl imdb -a start={} -a end={} -a total={}".format(start, end, pages))
    os.chdir("..")
    print colors.FAIL + ">>>>>> Running fetchData..." + colors.ENDC
    os.system("python fetchData.py {} {} {}".format(start, end, num_of_movies))
    print colors.FAIL + ">>>>>> Done. Check data" + colors.ENDC

if __name__ == '__main__':
    main()

