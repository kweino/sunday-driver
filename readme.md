# Sunday Rider: A Motorcycle Road Recommendation Engine

Check out Sunday Rider:
https://kweino-sunday-rider-app-83lxpg.streamlitapp.com/

Sunday Rider provides recommendations for roads near a user's location that are highly rated by motorcyclists. Users can search for routes based on their location and other ride experience preferences, and if they find a route they like, the app can recommend similar routes to the liked route. 

## Data Ingestion

I deployed two Scrapy spiders to crawl each of the ~2100 routes on the www.motorcycleroads.com (MR.com) website. One spider grabbed basic route information for use in the recommendation engine. The other spider collected all of the user comments on each route for topic modeling.

## Under the Hood

The question driving this project is *what makes a great motorcycle route?*. Topic modeling of MR.com user comments revealed that users talk all the elements one would expect in a great ride: A *fun* ride with *beautiful scenery* and *fun curves*, hopefully with little to no *traffic*.

![](https://github.com/kweino/sunday-rider/blob/master/data/comments_top_unigrams.png?raw=true)

The recommendation engine running Sunday Rider employs a Nearest Neighbors algorithm in Scikit-Learn to generate recommendations for a given route using features in my dataset that quantify some of the themes above.
