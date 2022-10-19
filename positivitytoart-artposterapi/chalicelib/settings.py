import os

aws_region = os.environ.get('AWS_REGION')
aws_user = os.environ.get('AWS_USER')
rdb_host = os.environ.get('RDB_HOST')
rdb_port = os.environ.get('RDB_PORT')
rdb_user = os.environ.get('RDB_USER')
rdb_password = os.environ.get('RDB_PASSWORD')
rdb_database_name = os.environ.get('RDB_DATABASE_NAME')
hashtag_queue = os.environ.get('HASHTAG_QUEUE')
hashtag_api = os.environ.get('HASHTAG_API')
image_bucket_name = os.environ.get('IMAGE_CONTENT_BUCKET')
queue_url = f'https://sqs.{aws_region}.amazonaws.com/{aws_user}/{hashtag_queue}'
