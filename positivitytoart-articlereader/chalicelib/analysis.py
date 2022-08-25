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

    def read_articles(self, limit: int = 1):
        db_articles = []
        with Database(db_connection_url=self.db_connection_url) as database:
            db_posts = database.get_unread_reddit_news_posts(limit=limit)

            for db_post in db_posts:
                querystring = {"url": db_post.url}
                news_log.log(logging.INFO, f'Reading article: {db_post.title}')
                response = requests.request("GET", self.api_url, headers=self.headers, params=querystring).json()
                api_article = response.get('article')
                db_article = ArticleAnalysis(db_post.article_id, db_post.title, db_post.url)
                if response.get('status') == 'error':
                    db_article.analysis_status = 'ERROR'
                    db_article.analysis_comments = api_article
                else:
                    db_article.headline = api_article.get('title')
                    db_article.date_written = api_article.get('published')
                    db_article.description = api_article.get('meta_description')
                    db_article.main_text = api_article.get('text')
                    db_article.analysis_status = 'OK'
                db_articles.append(db_article)

            database.set_posts_as_read(db_posts)
            database.batch_write_articles(db_articles)
