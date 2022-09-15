from chalicelib.database import Database
from urllib.parse import urlparse


class PostFormatter:
    def format(self, article, hashtags, extra_suffix):
        with Database() as db:
            article_analysis = db.get_article_analysis(article_id)
            uri = urlparse(article_analysis.url)
            #TODO add ignoretags arg in get_article_hashtags
            post_hashtags = [hashtag.hashtag_text for hashtag in db.get_article_hashtags(article_id)]
            post_hashtags += [hashtag.hashtag_text for hashtag in db.get_tags_from_many_art_styles(art_style_ids)]

            tag_section = ' '.join([f'#{tag}'.replace('?', '') for tag in post_hashtags])
            source = uri.netloc.replace('www.', '')
            caption = f'{article_analysis.headline}\n\nSource: {source}\n\n{tag_section} {extra_suffix}'


if __name__ == '__main__':
    article_id = 'wtkkbk'
    style_ids = ['ai-art', 'oil-painting']

    PostFormatter().format(article_id, style_ids, "")
