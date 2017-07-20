import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
import pickle

class IMDBSpider(CrawlSpider):
    name = 'imdb'
    rules = (
    Rule(LinkExtractor(allow=(), restrict_xpaths=("//div[@class='nav']/div/a[@class='lister-page-next next-page']",)),
         callback="parse_page", follow=True),)

    def __init__(self, start=None, end=None, total=None, *args, **kwargs):
        super(IMDBSpider, self).__init__(*args, **kwargs)
        self.passed_pages = 0  # count the number of pages already followed
        self.total_pages = int(total) if total else 5
        self.start_year = int(start) if start else 1874
        self.end_year = int(end) if end else 2017
        self.filename = str(self.start_year) + "_" + str(self.end_year)

    # generate start_urls dynamically
    def start_requests(self):
        print "=====================start_requests================================"
        for year in range(self.start_year, self.end_year + 1):
            # movies are sorted by number of votes
            yield scrapy.Request('http://www.imdb.com/search/title?year={year},{year}&title_type=feature&sort=num_votes,desc'.format(year=year))

    def parse_page(self, response):
        print "=====================parse_page================================"
        if self.passed_pages == self.total_pages:
            raise CloseSpider(colors.WARNING + "Reached page limit {}".format(self.total_pages) + colors.ENDC)

        content = response.xpath("//div[@class='lister-item-content']")
        paths = content.xpath("h3[@class='lister-item-header']/a/@href").extract()  # list of paths of movies in the current page
        ids = [path[path.find('tt')+2:path.find('/?')] for path in paths]
        self.passed_pages += 1
        print ids
        self.save_in_file(ids)

    def save_in_file(self, ids):
        with open(self.filename, 'ab') as f:
            pickle.dump(ids, f)

        #### reading it back to list
        # import pickle
        # ids = []
        # with open(filename, 'rb') as f:
        #    while 1:
        #        try:
        #            ids.append(pickle.load(f))
        #        except EOFError:
        #            break

    parse_start_url = parse_page # make sure that the start_urls are parsed as well



class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'





