import os
import json
import uuid
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
 
class DataMigrator:
    def __init__(self, mysql_conn, mongo_conn, export_folder="export_json"):
        self.mysql_conn = mysql_conn
        self.mongo_conn = mongo_conn
        self.export_folder = export_folder
        os.makedirs(self.export_folder, exist_ok=True)
        self.irregular_plurals = {
            "category": "categories",
            "user": "users"
        }
        self.id_fields_map = {
            "user_id": "users",
            "category_id": "categories"
        }
 
    @staticmethod
    def is_valid_uuid(val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False
 
    @staticmethod
    def convert_to_objectid_if_uuid(val):
        """Convierte UUID strings a ObjectIds consistentes"""
        if isinstance(val, str) and DataMigrator.is_valid_uuid(val):
            # Genera un ObjectId determinístico basado en el UUID
            hex_str = val.replace("-", "")[:24]
            return ObjectId(hex_str.ljust(24, '0'))
        return val
 
    def export_mysql_to_mongo(self):
        cursor = self.mysql_conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
 
        for table in tables:
            print(f"Migrando tabla: {table}")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
 
            docs = []
            for row in rows:
                doc = {}
                for i in range(len(columns)):
                    key = columns[i]
                    value = row[i]
                   
                    # Convertir IDs UUID a ObjectId
                    if key == "id" or key.endswith("_id"):
                        value = self.convert_to_objectid_if_uuid(value)
                   
                    doc[key] = value
                docs.append(doc)
 
            mongo_collection = self.mongo_conn.db[table]
 
            if docs:
                try:
                    mongo_collection.insert_many(docs)
                    print(f"Inserted {len(docs)} documents in '{table}'")
 
                    json_path = os.path.join(self.export_folder, f"{table}.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(docs, f, ensure_ascii=False, indent=4, default=str)
                    print(f"Tabla '{table}' exportada como JSON a '{json_path}'.")
                except Exception as e:
                    print(f"Error insertando en {table}: {str(e)}")
 
        cursor.close()
 
    def normalize_foreign_keys(self):
        collections = self.mongo_conn.db.list_collection_names()
        id_maps = {}
 
        # Primera pasada: Mapear todos los IDs
        for collection_name in collections:
            id_maps[collection_name] = {}
            for doc in self.mongo_conn.db[collection_name].find():
                if "_id" in doc:
                    # Guardar mapeo para referencias
                    if "id" in doc:
                        id_maps[collection_name][doc["id"]] = doc["_id"]
 
        # Segunda pasada: Actualizar referencias
        for collection_name in collections:
            collection = self.mongo_conn.db[collection_name]
            for doc in collection.find():
                updates = {}
                unset_fields = {"id": ""} if "id" in doc else {}
 
                for key, value in doc.items():
                    # Procesar campos de referencia
                    if key.endswith("_id") and not isinstance(value, ObjectId):
                        ref_collection = self.id_fields_map.get(key, None)
                        if not ref_collection:
                            # Intenta deducir la colección referencia
                            ref = key.replace("_id", "")
                            ref_collection = self.irregular_plurals.get(ref, ref + "s")
                       
                        if ref_collection in id_maps and str(value) in id_maps[ref_collection]:
                            updates[key] = id_maps[ref_collection][str(value)]
                        else:
                            # Convertir UUIDs a ObjectId si no existe en el mapeo
                            new_id = self.convert_to_objectid_if_uuid(value)
                            if new_id != value:
                                updates[key] = new_id
 
                update_query = {}
                if updates:
                    update_query["$set"] = updates
                if unset_fields:
                    update_query["$unset"] = unset_fields
 
                if update_query:
                    try:
                        collection.update_one({"_id": doc["_id"]}, update_query)
                    except Exception as e:
                        print(f"Error updating {collection_name}.{doc['_id']}: {str(e)}")
 
        print("✅ Foreign keys normalized and 'id' field removed.")
 
    def migrate_all_ids_to_objectid(self):
        """Convierte todos los _id string a ObjectId"""
        collections = self.mongo_conn.db.list_collection_names()
       
        for collection_name in collections:
            collection = self.mongo_conn.db[collection_name]
            print(f"\nProcessing collection: {collection_name}")
           
            # Primero procesamos documentos con _id string
            string_id_docs = list(collection.find({"_id": {"$type": "string"}}))
           
            for doc in string_id_docs:
                old_id = doc["_id"]
               
                if self.is_valid_uuid(old_id):
                    new_id = self.convert_to_objectid_if_uuid(old_id)
                else:
                    # Para otros strings, generamos un nuevo ObjectId
                    new_id = ObjectId()
               
                try:
                    # Insertar nuevo documento con ObjectId
                    doc["_id"] = new_id
                    collection.insert_one(doc)
                   
                    # Eliminar el documento viejo
                    collection.delete_one({"_id": old_id})
                   
                    print(f"Migrated _id: {old_id} → {new_id}")
                   
                    # Actualizar referencias en otras colecciones
                    self.update_references(collection_name, old_id, new_id)
                   
                except Exception as e:
                    print(f"Error migrating {old_id}: {str(e)}")
 
        print("✅ All string _id fields migrated to ObjectId.")
 
    def update_references(self, source_collection, old_id, new_id):
        """Actualiza referencias a este ID en todas las colecciones"""
        for coll_name in self.mongo_conn.db.list_collection_names():
            if coll_name != source_collection:
                collection = self.mongo_conn.db[coll_name]
               
                # Buscar campos que terminen con _id y coincidan con el old_id
                update_result = collection.update_many(
                    {
                        "$or": [
                            {f"{source_collection[:-1]}_id": old_id},
                            {f"{source_collection}_id": old_id}
                        ]
                    },
                    {"$set": {
                        f"{source_collection[:-1]}_id": new_id,
                        f"{source_collection}_id": new_id
                    }}
                )
               
                if update_result.modified_count > 0:
                    print(f"Updated {update_result.modified_count} references in {coll_name}")
 
 