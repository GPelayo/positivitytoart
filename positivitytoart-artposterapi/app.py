from datetime import datetime
from urllib.parse import urlparse

import boto3
from chalice import Chalice, BadRequestError, CORSConfig
import requests

from chalicelib.database import Database
from chalicelib.settings import hashtag_api, hashtag_queue, queue_url, aws_region, image_bucket_name

app = Chalice(app_name='positivitytoart-artposterapi')


@app.route('/v1/about', methods=['GET'])
def about():
    return {
        'message': 'Positivity to Art is a project for delivering positive news with AI generated art pieces.'
                   ' This API contains collection of NLP and Image Generation tools for Positivity to Art.'
    }


max_hashtag_attempts = 3


@app.on_sqs_message(queue=hashtag_queue)
def generate_hashtags(event):
    with Database() as database:
        for record in event:
            article_id = record.body
            article_analysis = database.get_article_analysis(article_id)
            complete_text = f"{article_analysis.main_text} {article_analysis.description}"
            request_json = {'text': complete_text}
            for _ in range(max_hashtag_attempts):
                hashtag_response = requests.post(hashtag_api, json=request_json)

                if hashtag_response.ok:
                    break
            hashtags = hashtag_response.json().get('hashtags')
            database.write_suggested_hashtags(article_analysis.article_id, hashtags)


@app.route('/v1/analysis', methods=['GET', 'OPTiONS'], cors=CORSConfig(allow_headers=['Content-Type']))
def list_article_analysis():
    with Database() as database:
        return {
            'analyses': [analysis.to_dict() for analysis in database.list_reddit_analysis()]
        }


@app.route('/v1/analysis/{article_id}', methods=['GET', 'OPTiONS'], cors=CORSConfig(allow_headers=['Content-Type']))
def get_article_analysis(article_id):
    with Database() as database:
        return {
            'analysis': database.get_article_analysis(article_id).to_dict(),
            'hashtags': [hashtag.to_dict() for hashtag in database.get_article_hashtags(article_id)],
            'art_styles': [style.to_dict() for style in database.get_all_art_styles()]
        }


@app.route('/v1/unused_analysis', methods=['GET', 'OPTiONS'], cors=CORSConfig(allow_headers=['Content-Type']))
def list_unused_analysis():
    with Database() as database:
        return {
            'analyses': [analysis.to_dict() for analysis in database.get_unused_analysis()]
        }


@app.route('/v1/art_style', methods=['GET'], cors=CORSConfig(allow_headers=['Content-Type']))
def list_art_styles():
    with Database() as database:
        return {
            'art_styles': [style.to_dict() for style in database.get_all_art_styles()]
        }


@app.route('/v1/analysis/hashtags', methods=['POST', 'OPTiONS'], cors=CORSConfig(allow_headers=['Content-Type']))
def list_art_styles():
    request = app.current_request.json_body
    article_id = request.get('article_id')
    sqs = boto3.client('sqs')
    sqs.send_message(QueueUrl=queue_url, MessageBody=article_id)
    print(f'Starting process to generate hashtags for article, {article_id}')


@app.route('/v1/budibase/hashtags/{article_id}', methods=['POST'])
def send_hashtag_request(article_id):
    sqs = boto3.client('sqs')
    sqs.send_message(QueueUrl=queue_url, MessageBody=article_id)
    return {'message': f'Starting process to generate hashtags for article, {article_id}'}


@app.route('/v1/budibase/post_schedule', methods=['POST'])
def set_post_schedule():
    json_params = app.current_request.json_body
    article_id = json_params.get('article_id')
    art_styles = json_params.get('art_styles').split(',')
    post_hashtags = json_params.get('topic_tags').split(',')
    extra_tags = json_params.get('extra_tags')
    schedule_date = json_params.get('instagram_scheduled_date')
    image_key = json_params.get('image_key')
    submit_draft(article_id, art_styles, post_hashtags, extra_tags, image_key)
    scheduled_date = datetime.strptime(schedule_date or datetime.now(), '%Y-%m-%d %H:%M')

    with Database() as database:
        database.write_scheduled_insta_post(article_id, scheduled_date)

    return {
        'message': f'Successfully scheduled post for article {article_id}',
        'data_received': json_params,
    }


@app.route('/v1/draft', methods=['GET'], cors=CORSConfig(allow_headers=['Content-Type']))
def list_draft():
    with Database() as database:
        return {
            'drafts': [{**a.to_dict(), **d.to_dict()} for d, a in database.list_drafts()]
        }


@app.route('/v1/draft', methods=['POST'], cors=CORSConfig(allow_headers=['Content-Type']))
def create_draft():
    json_params = app.current_request.json_body
    article_id = json_params.get('article_id')
    art_styles = json_params.get('art_style_ids')
    post_hashtags = json_params.get('auto_hashtag_ids')
    extra_tags = json_params.get('extra_tags')
    submit_draft(article_id, art_styles, post_hashtags, extra_tags, article_id)

    return {
        'message': f'Successfully scheduled post for article {article_id}',
        'data_received': json_params,
    }


@app.route('/v1/draft/{article_id}/image',
           methods=['POST'],
           cors=CORSConfig(allow_headers=['Content-Type', 'Range', 'Accept', 'Content-Language']),
           content_types=['image/png', 'image/jpg', 'image/jpeg'])
def upload_image(article_id):
    image_bytes = app.current_request.raw_body
    res = boto3.resource('s3')
    obj = res.Object(image_bucket_name, article_id)
    obj.put(Body=image_bytes)
    return {'message': f'Added Draft for article {article_id}.'}


def submit_draft(article_id, art_styles, post_hashtags, extra_tags, image_key):
    with Database() as database:
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
        image_url = f'https://{image_bucket_name}.s3.{aws_region}.amazonaws.com/{image_key}'
        database.submit_draft(article_id, caption, image_url)
