from chalice import Chalice
from chalicelib.analysis import NewsReader
from chalicelib.extraction import RedditArticleExtractor

app = Chalice(app_name='positivitytoart-articlepostscraper')


@app.schedule('rate(1 day)')
def scrape_posts(event):
    RedditArticleExtractor().get_hot_articles()


@app.schedule('rate(1 hour)')
def read_articles(event):
    NewsReader().read_articles(limit=4)
