from chalice import Chalice
from chalicelib.analysis import NewsReader
from chalicelib.settings import max_articles

app = Chalice(app_name='positivitytoart-articlereader')


@app.schedule('rate(1 hour)')
def read_articles(event):
    article_limit = max(max_articles, 1)
    NewsReader().read_articles(limit=article_limit)
