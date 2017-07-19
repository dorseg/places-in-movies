# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class MovieItem(Item):
    MainPageUrl = Field()
    Title = Field()
    Rating = Field()
    Year = Field()
    ID = Field()
    Director = Field()
    Synopsis = Field()
    Genres = Field()


