import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from elispider.items import MovieItem

class IMDBSpider(CrawlSpider):
    name = 'imdb'
    rules = (
        # extract links at the bottom of the page. note that there are 'Prev' and 'Next'
        # links, so a bit of additional filtering is needed
        Rule(LinkExtractor(restrict_xpaths=('//*[@id="right"]/span/a')),
            process_links=lambda links: filter(lambda l: 'Next' in l.text, links),
            callback='parse_page',
            follow=True),
    )

    def __init__(self, start=None, end=None, *args, **kwargs):
      super(IMDBSpider, self).__init__(*args, **kwargs)
      self.start_year = int(start) if start else 1874
      self.end_year = int(end) if end else 2016

    # generate start_urls dynamically
    def start_requests(self):
        for year in range(self.start_year, self.end_year+1):
            yield scrapy.Request('http://www.imdb.com/search/title?year={year},{year}&title_type=feature&sort=moviemeter,asc'.format(year=year), callback=self.parse_page)

    def parse_page(self, response):
        print "=====================2parse_page================================"
        print "!!!", response.xpath("//div[@class='lister-item-content']")
        for sel in response.xpath("//div[@class='lister-item-content']"):
            item = MovieItem()
            item['Title'] = sel.xpath('a/text()').extract()[0]
            item['MainPageUrl']= "http://imdb.com"+sel.xpath('a/@href').extract()[0]
            request = scrapy.Request(item['MainPageUrl'], callback=self.parse_movie_details)
            request.meta['item'] = item
            yield request
    # make sure that the dynamically generated start_urls are parsed as well
    parse_start_url = parse_page

    # do your magic
    def parse_movie_details(self, response):
        print "=====================parse_movie_details================================"
        item = response.meta['item']
        item['Director'] = response.xpath("//div/span[@itemprop='director']/a/span/text()").extract()
        item['Writers'] = response.xpath("//div/span[@itemprop='creator']/a/span/text()").extract()  # this can deffinatly be multiple people.
        item['Sinopsis'] = response.xpath("//div[@itemprop='description']/text()").extract()[0]  # this one is going to need to be cleaned up
        item['Genres'] = response.xpath("//div[@itemprop='genre']/a/text()").extract()
        item['MpaaRating'] = response.xpath("//span[@itemprop='contentRating']/text()").extract()[0]

        print item