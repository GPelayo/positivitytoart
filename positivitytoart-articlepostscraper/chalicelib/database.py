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
        self.session = self.session_maker()
        engine.connect()

    def has_article(self, article_id: str) -> bool:
        obj = self.session.query(RedditArticlePost.article_id).filter_by(article_id=article_id).first()
        return obj is not None

    def batch_write_posts(self, articles: List[RedditArticlePost]):
        self.session.bulk_save_objects(articles)
        self.session.commit()
