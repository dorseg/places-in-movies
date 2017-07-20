import os, sys

def main():
    start, end, pages = sys.argv[1], sys.argv[2], sys.argv[3]
    os.chdir("crawler")
    print ">>>>>> Running scrapy..."
    os.system("scrapy crawl imdb -a start={} -a end={} -a total={}".format(start, end, pages))
    os.chdir("..")
    print ">>>>>> Running fetchData..."
    os.system("python fetchData.py {} {}".format(start, end))
    print ">>>>>> Done. Check data"

if __name__ == '__main__':
    main()
