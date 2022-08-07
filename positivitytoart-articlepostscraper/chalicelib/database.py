from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from chalicelib.settings import rdb_port, rdb_host, rdb_user, rdb_password, rdb_database_name
from models import RedditArticlePost


class Database:
    def __init__(self):
        engine = create_engine(f'postgresql://{rdb_user}:{rdb_password}@{rdb_host}:{rdb_port}/{rdb_database_name}')
        self.session_maker = sessionmaker(bind=engine)
        self.session = self.session_maker()
        engine.connect()

    def has_article(self, article_id: str):
        obj = self.session.query(RedditArticlePost.article_id).filter_by(article_id=article_id).first()
        return obj is not None

    def batch_write_articles(self, articles: List[RedditArticlePost]):
        self.session.bulk_save_objects(articles)
        self.session.commit()
