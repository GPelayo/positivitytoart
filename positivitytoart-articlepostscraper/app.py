from chalice import Chalice
from chalicelib.extraction import RedditArticleExtractor

app = Chalice(app_name='positivitytoart-articlepostscraper')


@app.schedule('rate(12 hours)')
def scrape_posts(event):
    RedditArticleExtractor().get_hot_articles()
