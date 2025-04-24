
import mysql.connector
from pymongo import MongoClient

from Connection import MySQLConnection, MongoDBConnection;
from DataMigrator import DataMigrator;

if __name__ == "__main__":
    mysql = MySQLConnection(
        host="localhost",
        user="root",
        password="sd5",
        database="sd3",
        port=3307
    )
    mongo = MongoDBConnection("mongodb://localhost:31017/", "sd3")

    try:
        mysql_conn = mysql.connect()
        migrator = DataMigrator(mysql_conn, mongo)

        migrator.export_mysql_to_mongo()
        migrator.normalize_foreign_keys()

    finally:
        mysql.close()
        mongo.close()
        print("✅ Migration process completed.")