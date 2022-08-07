from datetime import datetime

import praw

from chalicelib.settings import reddit_client_id, reddit_client_secret
from chalicelib.database import Database
from models import RedditArticlePost


class RedditArticlePostSerializer:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_client_secret,
            user_agent="Comment Extraction (by u/gpelayollc)",
        )

    def get_articles(self, limit: int = 1000, score_threshold: int = 1000):
        db = Database()
        db_posts = []
        for praw_post in self.reddit.subreddit('UpliftingNews').new():
            if len(db_posts) >= limit:
                break

            if db.has_article(praw_post.id) or praw_post.score < score_threshold:
                continue

            db_post = RedditArticlePost(praw_post.id, praw_post.title, praw_post.url)
            db_post.score = praw_post.score
            db_post.date_posted = datetime.fromtimestamp(praw_post.created_utc)
            db_posts.append(db_post)

        db.batch_write_articles(db_posts)
        db.session.close()
