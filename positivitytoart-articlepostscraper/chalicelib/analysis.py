import logging
import sys

from lxml.etree import LxmlError
from newsplease import NewsPlease

from chalicelib.database import Database
from positivity_models.models import ArticleAnalysis

logging.basicConfig(level=logging.INFO,
                    handlers=[logging.StreamHandler(sys.stdout)])
news_log = logging.getLogger(__name__)
news_log.setLevel(logging.INFO)


class NewsReader:
    def __init__(self, db_connection_url=None):
        self.database = Database(db_connection_url)

    def read_articles(self, limit: int = 1):
        db_articles = []
        db_posts = self.database.get_unread_reddit_news_posts(limit=limit)
        for db_post in db_posts:
            try:
                news_log.log(logging.INFO, f'Reading article: {db_post.title}')
                scrapped_article = NewsPlease.from_url(db_post.url)
            except LxmlError as e:
                db_article = ArticleAnalysis(db_post.article_id, db_post.title, db_post.url)
                db_article.analysis_status = 'ERROR'
                error_log = e.error_log if hasattr(e, "error_log") else ""
                db_article.analysis_comments = f'({type(e).__name__}){e} {error_log}'
            else:
                db_article = ArticleAnalysis(db_post.article_id, scrapped_article.title, db_post.url)
                db_article.date_written = scrapped_article.date_publish
                db_article.description = scrapped_article.description
                db_article.main_text = scrapped_article.maintext
                db_article.analysis_status = 'OK'

            db_articles.append(db_article)

        self.database.set_posts_as_read(db_posts)
        self.database.batch_write_articles(db_articles)
