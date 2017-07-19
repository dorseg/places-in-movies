import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider

from crawler.items import MovieItem

IMDB_URL = "http://imdb.com"

class IMDBSpider(CrawlSpider):
    name = 'imdb'
    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=("//div[@class='nav']/div/a[@class='lister-page-next next-page']",)),
                  callback="parse_page", follow= True),)

    def __init__(self, start=None, end=None, total=None, *args, **kwargs):
        super(IMDBSpider, self).__init__(*args, **kwargs)
        self.passed_pages = 0 # count the number of pages already followed
        self.total_pages = int(total) if total else 5
        self.start_year = int(start) if start else 1874
        self.end_year = int(end) if end else 2017

    # generate start_urls dynamically
    def start_requests(self):
        print "=====================start_requests================================"
        for year in range(self.start_year, self.end_year+1):
            # movies are sorted by number of votes
            yield scrapy.Request('http://www.imdb.com/search/title?year={year},{year}&title_type=feature&sort=num_votes,desc'.format(year=year))

    def parse_page(self, response):
        if self.passed_pages == self.total_pages:
            raise CloseSpider("Reached page limit {}".format(self.total_pages))

        print "=====================parse_page================================"
        content = response.xpath("//div[@class='lister-item-content']")
        paths = content.xpath("h3[@class='lister-item-header']/a/@href").extract() # list of paths of movies in the current page

        # all movies
        self.passed_pages += 1
        for path in paths:
            item = MovieItem()
            item['MainPageUrl'] = IMDB_URL + path
            request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
            request.meta['item'] = item
            yield request

        # # single movie
        # self.passed_pages += 1
        # path = paths[0]
        # item = MovieItem()
        # item['MainPageUrl'] = IMDB_URL + path
        # request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
        # request.meta['item'] = item
        # yield request

    parse_start_url = parse_page

    def parse_movie_details(self, response):
        print "=====================parse_movie_details================================"
        item = response.meta['item']
        print item
        synopsis_url = response.xpath("//a[text()='Plot Synopsis']/@href").extract()
        url = item['MainPageUrl']
        title = response.xpath("//div[@class='titleBar']/div[@class='title_wrapper']/h1/text()").extract()[0][:-1]
        if synopsis_url: # there is synopsis
            item['ID'] = url[url.find('/tt')+3:url.find('/?')] # +3 to ignore '/tt',
            item['Title'] = title
            item['Year'] = response.xpath("//div[@class='titleBar']/div[@class='title_wrapper']/h1/span/a/text()").extract()[0]
            item['Director'] = response.xpath("//div/span[@itemprop='director']/a/span/text()").extract()
            item['Genres'] = response.xpath("//div[@itemprop='genre']/a/text()").extract()
            item['Rating'] = response.xpath("//div[@class='ratings_wrapper']/div/div/strong/span/text()").extract()[0]

            # extract synopsis
            synopsis_url = IMDB_URL + response.xpath("//a[text()='Plot Synopsis']/@href").extract()[0]
            request = scrapy.Request(synopsis_url, callback=self.parse_synopsis)
            request.meta['item'] = item
            yield request

        else:
            print colors.FAIL + ">>>>>>>>>>>>>>>>>>>> Synopsis of \"{}\" NOT FOUND!!!!".format(title) + colors.ENDC

    def parse_synopsis(self,response):
        print "=====================parse_synopsis================================"
        item = response.meta['item']
        synopsis = response.xpath("//div[@id='swiki.2.1']/text()").extract() # list of paragraphs
        item['Synopsis'] = synopsis
        print item

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



