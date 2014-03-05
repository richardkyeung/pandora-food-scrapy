from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
import re

from panfoopy.items import Review

# url string components for reviewer pages
URL_BASE = 'http://www.yelp.com/user_details_reviews_self?userid='
FILTER_SETTINGS = '&review_filter=category&category_filter=restaurants'

# yelp unique url endings for each restaurant
RESTAURANTS = ['jims-original-hot-dog-chicago-2', \
               'hoagy-house-chicago']

def createRestaurantPageLinks(self, response):
   reviewsPerPage = 40
   hxs = HtmlXPathSelector(response)
   totalReviews = int(hxs.select('//div[@itemprop="aggregateRating"]//span[@itemprop="reviewCount"]/text()').extract()[0].strip().split(' ')[0])
   pages = [Request(url=response.url + '?start=' + str(reviewsPerPage*(n+1)), \
                    callback=self.parse) \
            for n in range(totalReviews/reviewsPerPage)]
   return pages

def createReviewerPageLinks(self, response):
   reviewsPerPage = 10
   hxs = HtmlXPathSelector(response)
   totalReviews = int(hxs.select('//div[@id="review_lister_header"]/em/text()').extract()[0].split(' ')[0])
   pages = [Request(url=response.url + '&rec_pagestart=' + str(reviewsPerPage*(n+1)), \
                    callback=self.parseReviewer) \
            for n in range(totalReviews/reviewsPerPage)]
   return pages

class RestaurantSpider(BaseSpider):
   name = 'yelp'
   allowed_domains = ['yelp.com']
   start_urls = [ 'http://www.yelp.com/biz/%s' % s for s in RESTAURANTS]

   # default parse used for the landing page for each start_url
   def parse(self, response):
      requests = []

      # extract all reviews from the page and return a list of requests for the 5 star reviewers' profiles
      hxs = HtmlXPathSelector(response)
      userIDs = [userUrl.split('?userid=')[1] for \
                 userUrl in hxs.select('//li[@class="user-name"]/a/@href').extract()]
      ratings = hxs.select('//div[@class="review-list"]//meta[@itemprop="ratingValue"]/@content').extract()

      for i in range(len(ratings)):
         if float(ratings[i]) >= 4:
             requests.append(Request(url=URL_BASE + userIDs[i] + FILTER_SETTINGS, \
                                     callback=self.parseReviewer))

      # request additional pages if we are on page 1 of the restaurant
      if response.url.find('?start=') == -1:
         requests += createRestaurantPageLinks(self, response)

      return requests

   # parse a given reviewer
   def parseReviewer(self, response):
      hxs = HtmlXPathSelector(response)
      restaurantUrls = hxs.select('//div[@class="review clearfix"]/ \
                                  div[@class="biz_info"]/h4/a/@href').extract()
      restaurants = [re.search(r'(?<=/biz/)[^#]*', rest).group() for rest in restaurantUrls]
      reviewerName = hxs.select('//title/text()').extract()[0].split('|')[0].replace('\'s Profile','').strip()
      reviewerUserID = re.search(r'(?<=userid=)[^&]*', response.url).group()
      ratingText = hxs.select('//div[@class="rating"]/i/@title').extract()
      ratings = [s.replace(' star rating','') for s in ratingText]

      reviews = []
      for i in range(len(restaurants)):
         review = Review()
         review['restaurant'] = restaurants[i]
         review['reviewerName'] = reviewerName
         review['reviewerUserID'] = reviewerUserID
         review['rating'] = float(ratings[i])
         reviews.append(review)

      # request additional pages if we are on page 1 of the reviewer
      additionalPages = []
      if response.url.find('&rec_pagestart=') == -1:
         additionalPages = createReviewerPageLinks(self, response)

      return reviews + additionalPages
