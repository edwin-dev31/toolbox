import os
import json
from datetime import datetime
from bson import ObjectId


class DataMigrator:
    def __init__(self, mysql_conn, mongo_conn, export_folder="export_json"):
        self.mysql_conn = mysql_conn
        self.mongo_conn = mongo_conn
        self.export_folder = export_folder
        os.makedirs(self.export_folder, exist_ok=True)
        self.irregular_plurals = {
            "category": "categories",
        }

    @staticmethod
    def convert_objectid(obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def export_mysql_to_mongo(self):
        cursor = self.mysql_conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            print(f"Migrando tabla: {table}")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            docs = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
            mongo_collection = self.mongo_conn.db[table]

            if docs:
                mongo_collection.insert_many(docs)
                print(f"Inserted {len(docs)} documents in '{table}'")

                json_path = os.path.join(self.export_folder, f"{table}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(docs, f, ensure_ascii=False, indent=4, default=self.convert_objectid)
                    print(f"Tabla '{table}' exportada como JSON a '{json_path}'.")

        cursor.close()

    def normalize_foreign_keys(self):
        collections = self.mongo_conn.db.list_collection_names()
        id_maps = {}

        # Mapeo de id → _id
        for collection_name in collections:
            id_maps[collection_name] = {}
            for doc in self.mongo_conn.db[collection_name].find({}, {"_id": 1, "id": 1}):
                if "id" in doc:
                    id_maps[collection_name][doc["id"]] = doc["_id"]

        # Reemplazo de foreign keys y eliminación del campo "id"
        for collection_name in collections:
            collection = self.mongo_conn.db[collection_name]
            for doc in collection.find():
                updates = {}
                unset_fields = {"id": ""} if "id" in doc else {}

                for key, value in doc.items():
                    if key.endswith("_id") and not isinstance(value, ObjectId):
                        ref = key.replace("_id", "")
                        if ref in self.irregular_plurals:
                            ref = self.irregular_plurals[ref]
                        elif ref + "s" in id_maps:
                            ref += "s"
                        elif ref + "es" in id_maps:
                            ref += "es"

                        ref_map = id_maps.get(ref)
                        if ref_map and value in ref_map:
                            updates[key] = ref_map[value]

                update_query = {}
                if updates:
                    update_query["$set"] = updates
                if unset_fields:
                    update_query["$unset"] = unset_fields

                if update_query:
                    collection.update_one({"_id": doc["_id"]}, update_query)

        print("✅ Foreign keys updated and 'id' field removed.")



