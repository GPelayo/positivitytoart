from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Date, ForeignKey, Integer, String

Base = declarative_base()


class RedditArticlePost(Base):
    __tablename__ = 'reddit_article_post'

    article_id = Column(String, primary_key=True)
    url = Column(String)
    title = Column(String)
    date_posted = Column(Date)
    score = Column(Integer)

    def __init__(self, article_id, title, url):
        super(RedditArticlePost, self).__init__()
        self.article_id = article_id
        self.title = title
        self.url = url


class NewsArticle(Base):
    __tablename__ = 'news_article'

    article_id = Column(String, primary_key=True)
    url = Column(String)
    headline = Column(String)
    date_written = Column(Date)
    description = Column(String)
    main_text = Column(String)
    suggested_prompts = relationship('SuggestedPrompt')

    def __init__(self, article_id, title, url):
        super(NewsArticle, self).__init__()
        self.article_id = article_id
        self.title = title
        self.url = url


class SuggestedPrompt(Base):
    __tablename__ = 'suggested_prompt'

    prompt_id = Column(String, primary_key=True)
    prompt_text = Column(String)
    article_id = Column(String, ForeignKey('news_article.article_id'))

    def __init__(self, prompt_id, prompt_text, article_post_id):
        super(SuggestedPrompt, self).__init__()
        self.prompt_id = prompt_id
        self.prompt_text = prompt_text
        self.article_post_id = article_post_id


class InstagramImagePost(Base):
    __tablename__ = 'instagram_image_post'

    image_post_id = Column(String, primary_key=True)
    caption = Column(String)
    image_location = Column(String)
    image_location_type = Column(String)


