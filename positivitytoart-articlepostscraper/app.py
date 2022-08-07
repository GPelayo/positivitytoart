from chalice import Chalice
from chalicelib.updater import RedditArticlePostSerializer, NewsReader

app = Chalice(app_name='positivitytoart-articlepostscraper')


@app.schedule('rate(1 day)')
def scrape_posts(event):
    RedditArticlePostSerializer().get_articles()


@app.schedule('rate(10 minutes)')
def read_articles(event):
    NewsReader().read_articles(limit=4)
