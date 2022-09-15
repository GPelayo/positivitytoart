from chalice import Chalice, BadRequestError

from chalicelib.database import Database
from urllib.parse import urlparse
from datetime import datetime

app = Chalice(app_name='positivitytoart-artposterapi')


@app.route('/v1/about', methods=['GET'])
def about():
    return {
        'message': 'Positivity to Art is a project for delivering positive news with AI generated art pieces.'
                   ' This API contains collection of NLP and Image Generation tools for Positivity to Art.'
    }


@app.route('/v1/budibase/post_schedule', methods=['POST'])
def generate_hashtags_sched():
    with Database() as database:
        json_params = app.current_request.json_body
        article_id = json_params.get('article_id')
        art_styles = json_params.get('art_styles').split(',')
        post_hashtags = json_params.get('topic_tags').split(',')
        extra_tags = json_params.get('extra_tags')
        style_tags = [hashtag.hashtag_text for hashtag in database.get_tags_from_many_art_styles(art_styles)]
        post_hashtags += style_tags

        hashtag_count = extra_tags.count('#') + len(post_hashtags)
        max_hashtags = 30

        if max_hashtags < hashtag_count:
            raise BadRequestError(f'Too Many Hashtags. Limit is {max_hashtags} (Received {hashtag_count}).')

        tag_section = ' '.join([f'#{tag}'.replace('?', '') for tag in post_hashtags])
        article_analysis = database.get_article_analysis(article_id)

        uri = urlparse(article_analysis.url)
        caption = f'{article_analysis.headline}\n\nSource: {uri.netloc}\n\n{tag_section} {extra_tags}'
        scheduled_date_string = json_params.get('instagram_scheduled_date')
        scheduled_date = datetime.strptime(scheduled_date_string, '%Y-%m-%d %H:%M')
        image_key = json_params.get('image_key')
        aws_region = 'us-west-2'
        image_bucket = 'gpllc-dalle-images'
        image_url = f'https://{image_bucket}.s3.{aws_region}.amazonaws.com/{image_key}'
        database.write_scheduled_post(article_id, caption, scheduled_date, image_url)

        return {
            'message': f'Successfully scheduled post for article {article_id}',
            'data_received': json_params,
        }
