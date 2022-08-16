from chalice import Chalice
from chalicelib.extraction import RedditArticleExtractor

app = Chalice(app_name='positivitytoart-articlepostscraper')


@app.schedule('rate(1 day)')
def scrape_posts(event):
    RedditArticleExtractor().get_hot_articles()
