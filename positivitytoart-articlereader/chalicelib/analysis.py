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
    def __init__(self, db_connection_url=None, api_key=None):
        self.db_connection_url = db_connection_url
        self.host = 'extract-news.p.rapidapi.com'
        self.api_url = f'https://{self.host}/v0/article'
        self.headers = {
            "X-RapidAPI-Key": api_key or extractnews_api,
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

        return article

    def read_articles(self, limit: int = 1):
        with Database(db_connection_url=self.db_connection_url) as database:
            db_posts = database.get_unread_reddit_news_posts(limit=limit)
            db_article = [self._read_article(db_post, 'Scheduled write.') for db_post in db_posts]
            database.batch_set_posts_as_read(db_posts)
            database.batch_write_articles(db_article)

    def read_article(self, article_id: str):
        with Database(self.db_connection_url) as database:
            db_post = database.get_reddit_news_post(article_id)
            db_article = self._read_article(db_post, 'Manually written.')
            database.set_posts_as_read(db_post)
            database.write_articles(db_article)
