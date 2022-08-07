from chalice import Chalice
from chalicelib.updater import RedditArticlePostSerializer

app = Chalice(app_name='positivitytoart-articlepostscraper')


@app.schedule('rate(1 day)')
def scrape_posts(event):
    RedditArticlePostSerializer().get_articles()
