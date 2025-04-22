import os
import json
from datetime import datetime
from bson import ObjectId
import mysql.connector
from pymongo import MongoClient


class MySQLConnection:
    def __init__(self, host, user, password, database, port=3306):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "port": port
        }
        self.conn = None

    def connect(self):
        self.conn = mysql.connector.connect(**self.config)
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()


class MongoDBConnection:
    def __init__(self, uri, database_name):
        self.client = MongoClient(uri)
        self.db = self.client[database_name]

    def close(self):
        self.client.close()


