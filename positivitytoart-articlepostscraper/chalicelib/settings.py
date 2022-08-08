import os

import dotenv

dotenv.load_dotenv()

reddit_client_id = os.environ.get('REDDIT_CLIENT_ID')
reddit_client_secret = os.environ.get('REDDIT_CLIENT_SECRET')
reddit_username = os.environ.get('REDDIT_USERNAME')
reddit_password = os.environ.get('REDDIT_PASSWORD')
rdb_host = os.environ.get('RDB_HOST')
rdb_port = os.environ.get('RDB_PORT')
rdb_user = os.environ.get('RDB_USER')
rdb_password = os.environ.get('RDB_PASSWORD')
rdb_database_name = os.environ.get('RDB_DATABASE_NAME')
