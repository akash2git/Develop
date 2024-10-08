import sqlite3
from instagrapi import Client
from scripts.wish_logger import get_logger

logger = get_logger()

# try:
#     cursor = None
#     # Connect to SQLite database (or create it if it doesn't exist)
#     conn = sqlite3.connect('wish.db', check_same_thread=False)
#
#     # Create a cursor object to execute SQL commands
#     cursor = conn.cursor()
#
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS users (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT NOT NULL,
#             insta_id TEXT NOT NULL
#         )
#     ''')
# except Exception as e:
#     logger.exception("Exception while connecting to db: {}".format(e))


try:
    # Initialize the client
    client = Client()

    # Login with your Instagram username and password
    username = 'akash_sree123'
    password = 'akash2610'

    client.login(username, password)
except Exception as e:
    print("Exception whle logged in to admin account: {}".format(e))