import os

rdb_host = os.environ.get('RDB_HOST')
rdb_port = os.environ.get('RDB_PORT')
rdb_user = os.environ.get('RDB_USER')
rdb_password = os.environ.get('RDB_PASSWORD')
rdb_database_name = os.environ.get('RDB_DATABASE_NAME')
openai_client = os.environ.get('OPENAI_ORG')
openai_password = os.environ.get('OPENAI_APIKEY')
openai_config_bucket_name = os.environ.get('OPENAI_CONFIG_S3_BUCKET_NAME')
