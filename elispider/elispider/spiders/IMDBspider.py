import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider

from elispider.items import MovieItem

IMDB_URL = "http://imdb.com"
TOTAL_PAGES = 5  # modify to control the number of pages to follow
PASSED_PAGES = 0 # count the number of pages already followed

class IMDBSpider(CrawlSpider):
    name = 'imdb'
    rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=("//div[@class='nav']/div/a[@class='lister-page-next next-page']",)),
                  callback="parse_page", follow= True),)

    def __init__(self, start=None, end=None, *args, **kwargs):
        super(IMDBSpider, self).__init__(*args, **kwargs)
        self.start_year = int(start) if start else 1874
        self.end_year = int(end) if end else 2017

    # generate start_urls dynamically
    def start_requests(self):
        print "=====================start_requests================================"
        for year in range(self.start_year, self.end_year+1):
            # sorted by number of votes
            yield scrapy.Request('http://www.imdb.com/search/title?year={year},{year}&title_type=feature&sort=num_votes,desc'.format(year=year))

    def parse_page(self, response):
        global TOTAL_PAGES, PASSED_PAGES
        if PASSED_PAGES == TOTAL_PAGES:
            raise CloseSpider("Reached page limit {}".format(TOTAL_PAGES))
        print "=====================parse_page================================"

        content = response.xpath("//div[@class='lister-item-content']")
        paths = content.xpath("h3[@class='lister-item-header']/a/@href").extract() # list of paths of movies in the current page

        # for path in paths:
        #     item = MovieItem()
        #     item['MainPageUrl'] = "http://imdb.com" + path
        #     request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
        #     request.meta['item'] = item
        #     yield request

        # single movie
        path = paths[0]
        item = MovieItem()
        item['MainPageUrl'] = IMDB_URL + path
        request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
        request.meta['item'] = item
        PASSED_PAGES += 1
        yield request

    parse_start_url = parse_page

    def parse_movie_details(self, response):
        print "=====================parse_movie_details================================"
        item = response.meta['item']
        synopsis_url = response.xpath("//a[text()='Plot Synopsis']/@href").extract()
        url = item['MainPageUrl']
        title = response.xpath("//div[@class='titleBar']/div[@class='title_wrapper']/h1/text()").extract()[0][:-1]
        if synopsis_url:
            item['ID'] = url[url.find('/tt')+3:url.find('/?')] # to ignore 'tt', change to +3
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
            print ">>>>>>>>>>>>>>>>>>>> Synopsis of \"{}\" NOT FOUND!!!!".format(title)

    def parse_synopsis(self,response):
        print "=====================parse_synopsis================================"
        item = response.meta['item']
        synopsis = response.xpath("//div[@id='swiki.2.1']/text()").extract()[0] # list of paragraphs
        item['Synopsis'] = synopsis
        print item



