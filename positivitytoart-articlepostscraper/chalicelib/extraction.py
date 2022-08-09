from datetime import datetime

from praw.reddit import Reddit
from praw.models import ListingGenerator

from chalicelib.settings import reddit_client_id, reddit_client_secret
from chalicelib.database import Database
from models import RedditArticlePost


class RedditArticleExtractor:
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

