import os

rdb_host = os.environ.get('RDB_HOST')
rdb_port = os.environ.get('RDB_PORT')
rdb_user = os.environ.get('RDB_USER')
rdb_password = os.environ.get('RDB_PASSWORD')
rdb_database_name = os.environ.get('RDB_DATABASE_NAME')
rapidapi_key = os.environ.get('RAPIDAPI_KEY')
max_articles = int(os.environ.get('MAX_ARTICLES', -1))
