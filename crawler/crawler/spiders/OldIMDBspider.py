import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from crawler.items import MovieItem

IMDB_URL = "http://imdb.com"

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
        for year in range(self.start_year, self.end_year+1):
            # movies are sorted by number of votes
            yield scrapy.Request('http://www.imdb.com/search/title?year={year},{year}&title_type=feature&sort=num_votes,desc'.format(year=year))

    def parse_page(self, response):
        content = response.xpath("//div[@class='lister-item-content']")
        paths = content.xpath("h3[@class='lister-item-header']/a/@href").extract() # list of paths of movies in the current page

        # all movies
        for path in paths:
            item = MovieItem()
            item['MainPageUrl'] = IMDB_URL + path
            request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
            request.meta['item'] = item
            yield request

    # make sure that the start_urls are parsed as well
    parse_start_url = parse_page

    def parse_movie_details(self, response):
        pass # lots of parsing....

