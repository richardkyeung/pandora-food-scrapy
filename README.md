panfoopy
===================

Find good food with a simplistic scraping scrip.

This is just a fun little script that acts like a Pandora for food. Its
implementation is simplistic. You choose a set of restaurants on Yelp that you
like, and the script finds all reviewers that gave these restaurants 4-5 stars. You
trust these reviewers because they share your awesome taste in food. The script
then spits out all restaurants that these "trusted reviewers" also reviewed, and
their rating for each review.

You would need a few additional lines of code to turn the scrapy output into a
sorted list of restaurants. For example, the code below will sort restaurants by
number 5 star reviews from "trusted reviewers":

	import pandas
	reviews = pandas.read_csv('scrapy_output.csv')
	fiveStarReviews = reviews[reviews['rating']==5]
	fiveStarReviews.restaurant.value_counts()

There are countless ways you can improve on this. One obvious one is you would
want to normalize by total restaurant reviews. You would probably also want to
pull in restaurant category and location information.

Happy food hunting!

Note -- Scrapy is maturing quickly, and some of the methods used in this script
are already deprecated.


Usage
---

1. Install scrapy
2. Modify panfoopy.spiders.pandora_spider to have a list of your favorite resturants
    # yelp unique url endings for each restaurant
    RESTAURANTS = ['jims-original-hot-dog-chicago-2', \
                   'hoagy-house-chicago']
3. Run:
    scrapy crawl yelp -o output_filename.csv -t csv

