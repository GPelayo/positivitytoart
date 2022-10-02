import hashlib
from typing import List

from positivity_models.models import (ArtStyle,
                                      ArticleAnalysis,
                                      Hashtag,
                                      RedditArticlePost,
                                      SuggestedHashtag,
                                      SocialsDraft,
                                      ScheduledSocialsPost)
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import exists, false, true

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

    def set_posts_as_read(self, article_posts: List[RedditArticlePost]):
        for ap in article_posts:
            ap.is_read = True
        self.session.commit()

    def get_all_reddit_analysis(self) -> List[ArticleAnalysis]:
        return self.session.query(ArticleAnalysis).all()

    def get_article_analysis(self, article_id: str) -> ArticleAnalysis:
        return self.session.query(ArticleAnalysis).filter(ArticleAnalysis.article_id == article_id).first()

    def get_all_art_styles(self) -> List[ArticleAnalysis]:
        return self.session.query(ArtStyle).all()

    def get_unused_analysis(self) -> List[ArticleAnalysis]:
        social_condition = ~exists().where(SocialsDraft.image_post_id == ArticleAnalysis.article_id)
        hashtag_condition = exists().where(SuggestedHashtag.article_id == ArticleAnalysis.article_id)
        order = ArticleAnalysis.date_analyzed.desc()
        return self.session.query(ArticleAnalysis).filter(social_condition).filter(hashtag_condition).order_by(order)

    def get_article_hashtags(self, article_id: str) -> List[Hashtag]:
        return self.session.query(Hashtag).filter(Hashtag.article_id == article_id).all()

    def get_tags_from_many_art_styles(self, art_style_ids: List[str]) -> List[Hashtag]:
        return self.session.query(Hashtag).filter(Hashtag.artstyle_id.in_(art_style_ids)).all()

    def has_hashtags(self, article_id: str) -> bool:
        obj = self.session.query(SuggestedHashtag).filter_by(article_id=article_id).first()
        return obj is not None

    def get_unread_reddit_news_posts(self, is_read: bool = None, limit: int = 1) -> List[RedditArticlePost]:
        read_expression = true() if is_read else false()
        condition = RedditArticlePost.is_read == read_expression if is_read is not None else true() == true()
        return self.session.query(RedditArticlePost).filter(condition).limit(limit=limit).all()

    # def write_scheduled_post(self, image_key, caption, scheduled_date) -> List[RedditArticlePost]:

    def write_art_style(self, art_style, hashtags):
        self.session.add(art_style)
        self.session.commit()
        self.session.bulk_save_objects(hashtags)
        self.session.commit()

    def write_suggested_hashtags(self, article_id, hashtags):
        hashtags_db_objects = []
        for hashtag in hashtags:
            hashtag_id = hashlib.md5(f'{hashtag}{article_id}'.encode('utf-8')).hexdigest()
            if not self.session.query(Hashtag.hashtag_id).filter_by(hashtag_id=hashtag_id).first():
                db_hashtag = Hashtag(hashtag_id, hashtag)
                db_hashtag.article_id = article_id
                hashtags_db_objects.append(db_hashtag)
            if not self.session.query(SuggestedHashtag.article_id).filter_by(article_id=article_id).first():
                hashtags_db_objects.append(SuggestedHashtag(hashtag_id, article_id))

        self.session.bulk_save_objects(hashtags_db_objects)
        self.session.commit()

    def write_scheduled_post(self, post_id, caption, scheduled_date, image_location):
        socials = 'Instagram'
        draft = SocialsDraft()
        draft.image_location_type = 'url'
        draft.image_location = image_location
        draft.caption = caption

        post = ScheduledSocialsPost()
        post.post_action_id = f'{post_id}-{socials.lower()}'
        post.image_post_id = draft.image_post_id = post_id
        post.scheduled_date = scheduled_date
        post.socials_platform = socials
        post.is_posted = False
        post.posting_notes = ''

        self.session.add(draft)
        self.session.add(post)
        self.session.commit()
