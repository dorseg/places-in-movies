import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from elispider.items import MovieItem

IMDB_URL = "http://imdb.com"
TOTAL_PAGES = 5  # modify to control the number of pages to follow
PASSED_PAGES = 0 # count the number of pages already followed

class IMDBSpider(scrapy.Spider):
    name = 'imdb'

    def __init__(self, start=None, end=None, *args, **kwargs):
        super(IMDBSpider, self).__init__(*args, **kwargs)
        self.start_year = int(start) if start else 1874
        self.end_year = int(end) if end else 2016

    # generate start_urls dynamically
    def start_requests(self):
        print "=====================start_requests================================"
        for year in range(self.start_year, self.end_year+1):
            # sorted by number of votes
            yield scrapy.Request('http://www.imdb.com/search/title?year={year},{year}&title_type=feature&sort=num_votes,desc'.format(year=year), callback=self.parse_page)

    def parse_page(self, response):
        print "=====================parse_page================================"
        next_page = response.xpath("//div[@class='nav']/div/a[@class='lister-page-next next-page']/@href").extract_first()
        next_url = IMDB_URL + '/search/title' + next_page if next else None # next page might not appear

        content = response.xpath("//div[@class='lister-item-content']")
        paths = content.xpath("h3[@class='lister-item-header']/a/@href").extract() # list of paths of movies in the current page
        # ids = [path[path.find('tt'):path.find('/?')] for path in paths] <<<<<<<<<<<<< REMOVE

        # for path in paths:
        #     item = MovieItem()
        #     item['MainPageUrl'] = "http://imdb.com" + path
        #     request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
        #     request.meta['item'] = item
        #     yield request

        path = paths[0]
        item = MovieItem()
        item['MainPageUrl'] = IMDB_URL + path
        item['NextPageUrl'] = next_url
        request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
        request.meta['item'] = item
        yield request

    def parse_movie_details(self, response):
        print "=====================parse_movie_details================================"
        item = response.meta['item']
        synopsis_url = response.xpath("//a[text()='Plot Synopsis']/@href").extract()
        url = item['MainPageUrl']
        if synopsis_url:
            item['ID'] = url[url.find('/tt')+1:url.find('/?')] # to ignore 'tt', change to +3
            item['Title'] = response.xpath("//div[@class='titleBar']/div[@class='title_wrapper']/h1/text()").extract()[0][:-1]
            item['Year'] = response.xpath("//div[@class='titleBar']/div[@class='title_wrapper']/h1/span/a/text()").extract()[0]
            item['Director'] = response.xpath("//div/span[@itemprop='director']/a/span/text()").extract()
            item['Genres'] = response.xpath("//div[@itemprop='genre']/a/text()").extract()
            item['Rating'] = response.xpath("//div[@class='ratings_wrapper']/div/div/strong/span/text()").extract()[0]

            # extract synopsis
            synopsis_url = IMDB_URL + response.xpath("//a[text()='Plot Synopsis']/@href").extract()[0]
            request = scrapy.Request(synopsis_url, callback=self.parse_synopsis)
            request.meta['item'] = item
            yield request

        # move to next page
        else:
            print "=====================move_to_next_page================================"
            global TOTAL_PAGES, PASSED_PAGES
            if PASSED_PAGES == TOTAL_PAGES:  # already followed enough pages
                PASSED_PAGES = 0  # reset
                return
            elif item['NextPageUrl']:
                PASSED_PAGES += 1
                request = scrapy.Request(item['NextPageUrl'], callback=self.parse_page)
                yield request

    def parse_synopsis(self,response):
        print "=====================parse_synopsis================================"
        item = response.meta['item']
        synopsis = response.xpath("//div[@id='swiki.2.1']/text()").extract()[0] # list of paragraphs
        item['Synopsis'] = synopsis
        print item

        # move to next page
        print "=====================move_to_next_page================================"
        global TOTAL_PAGES, PASSED_PAGES
        if PASSED_PAGES == TOTAL_PAGES:  # already followed enough pages
            PASSED_PAGES = 0  # reset
            return
        elif item['NextPageUrl']:
            PASSED_PAGES += 1
            request = scrapy.Request(item['NextPageUrl'], callback=self.parse_page)
            yield request

    def move_to_next_page(self, next_url):
        print "=====================move_to_next_page================================"
        global TOTAL_PAGES, PASSED_PAGES
        if PASSED_PAGES == TOTAL_PAGES: # already followed enough pages
            PASSED_PAGES = 0 # reset
            return
        elif next_url:
            PASSED_PAGES += 1
            request = scrapy.Request(next_url, callback=self.parse_page)
            yield request

