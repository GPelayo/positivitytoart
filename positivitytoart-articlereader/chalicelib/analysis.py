from datetime import datetime
import logging
import sys

import requests

from chalicelib.database import Database
from chalicelib.settings import extractnews_api
from positivity_models.models import ArticleAnalysis

logging.basicConfig(level=logging.INFO,
                    handlers=[logging.StreamHandler(sys.stdout)])
news_log = logging.getLogger(__name__)
news_log.setLevel(logging.INFO)


class NewsReader:
    def __init__(self, db_connection_url=None):
        self.db_connection_url = db_connection_url
        self.host = 'extract-news.p.rapidapi.com'
        self.api_url = f'https://{self.host}/v0/article'
        self.headers = {
            "X-RapidAPI-Key": extractnews_api,
            "X-RapidAPI-Host": self.host
        }

    def _read_article(self, database, post):
        querystring = {"url": post.url}
        news_log.log(logging.INFO, f'Reading article: {post.title}')
        response = requests.request("GET", self.api_url, headers=self.headers, params=querystring).json()
        api_article = response.get('article')
        article = ArticleAnalysis(post.article_id, post.title, post.url)
        if response.get('status') == 'error':
            article.analysis_status = 'ERROR'
            article.analysis_comments = api_article
        else:
            article.headline = api_article.get('title')
            article.date_written = api_article.get('published')
            article.description = api_article.get('meta_description')
            article.main_text = api_article.get('text')
            article.analysis_status = 'OK'
            article.date_analyzed = datetime.now()

            database.set_posts_as_read(db_posts)
            database.batch_write_articles(db_articles)
