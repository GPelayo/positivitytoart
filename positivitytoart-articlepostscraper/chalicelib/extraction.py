from datetime import datetime

from lxml.etree import LxmlError
from newsplease import NewsPlease
import praw

from chalicelib.settings import reddit_client_id, reddit_client_secret
from chalicelib.database import Database
from models import RedditArticlePost, AnalyzedNewsArticle


class RedditArticlePostSerializer:
    def __init__(self, reddit=None, db_connection_url=None):
        self.reddit = reddit or praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent="Comment Extraction (by u/gpelayollc)",
        )
        self.database = Database(db_connection_url)

    def get_articles(self, limit: int = 1000, score_threshold: int = 1000):
        db_posts = []
        for praw_post in self.reddit.subreddit('UpliftingNews').new():
            if len(db_posts) >= limit:
                break

            if self.database.has_article(praw_post.id) or praw_post.score < score_threshold:
                continue

            db_post = RedditArticlePost(praw_post.id, praw_post.title, praw_post.url)
            db_post.score = praw_post.score
            db_post.date_posted = datetime.fromtimestamp(praw_post.created_utc)
            db_post.is_read = False
            db_posts.append(db_post)

        self.database.batch_write_posts(db_posts)
        self.database.session.close()


class NewsReader:
    def __init__(self, db_connection_url=None):
        self.database = Database(db_connection_url)

    def read_articles(self, limit: int = 1):
        db_articles = []
        db_posts = self.database.get_unread_reddit_news_posts(limit=limit)
        for db_post in db_posts:
            try:
                scrapped_article = NewsPlease.from_url(db_post.url)
            except LxmlError as e:
                db_article = AnalyzedNewsArticle(db_post.article_id, db_post.title, db_post.url)
                db_article.analyze_status = 'ERROR'
                error_log = e.error_log if hasattr(e, "error_log") else ""
                db_article.analyze_comments = f'({type(e).__name__}){e} {error_log}'
            else:
                db_article = AnalyzedNewsArticle(db_post.article_id, scrapped_article.title, db_post.url)
                db_article.date_written = scrapped_article.date_publish
                db_article.description = scrapped_article.description
                db_article.main_text = scrapped_article.maintext
                db_article.analyze_status = 'OK'

            db_articles.append(db_article)

        self.database.set_posts_as_read(db_posts)
        self.database.batch_write_articles(db_articles)
