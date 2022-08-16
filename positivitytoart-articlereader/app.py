from chalice import Chalice
from chalicelib.analysis import NewsReader

app = Chalice(app_name='positivitytoart-articlereader')


@app.schedule('rate(1 hour)')
def read_articles(event):
    NewsReader().read_articles(limit=4)
