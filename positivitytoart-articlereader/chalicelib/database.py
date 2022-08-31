from typing import List

from positivity_models.models import ArticleAnalysis, RedditArticlePost
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import false

from chalicelib.settings import rdb_database_name, rdb_host, rdb_password, rdb_port, rdb_user


class Database:
    def __init__(self, db_connection_url=None):
        url = db_connection_url or f'postgresql://{rdb_user}:{rdb_password}@{rdb_host}:{rdb_port}/{rdb_database_name}'
        engine = create_engine(url)
        self.session_maker = sessionmaker(bind=engine)
        self.session = None

    def __enter__(self):
        self.session = self.session_maker()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def set_post_as_read(self, article_posts: List[RedditArticlePost]):
        for ap in article_posts:
            ap.is_read = True
        self.session.commit()

    def batch_set_posts_as_read(self, article_posts: List[RedditArticlePost]):
        for ap in article_posts:
            ap.is_read = True
        self.session.commit()

    def get_reddit_news_post(self, article_id: str) -> RedditArticlePost:
        return self.session.query(RedditArticlePost).filter(RedditArticlePost.article_id == article_id).one()

    def get_unread_reddit_news_posts(self, limit: int = 1) -> List[RedditArticlePost]:
        condition = RedditArticlePost.is_read == false()
        return self.session.query(RedditArticlePost).filter(condition).limit(limit=limit).all()

    def write_articles(self, article: ArticleAnalysis):
        self.session.add(article)
        self.session.commit()

    def batch_write_articles(self, articles: List[ArticleAnalysis]):
        self.session.bulk_save_objects(articles)
        self.session.commit()

