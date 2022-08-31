import os

rdb_host = os.environ.get('RDB_HOST')
rdb_port = os.environ.get('RDB_PORT')
rdb_user = os.environ.get('RDB_USER')
rdb_password = os.environ.get('RDB_PASSWORD')
rdb_database_name = os.environ.get('RDB_DATABASE_NAME')
extractnews_api = os.environ.get('EXTRACTNEWS_APIKEY')
max_articles = int(os.environ.get('MAX_ARTICLES', -1))
