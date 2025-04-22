# 💾 MySQL to MongoDB Migration Tool

This script allows you to migrate data from a MySQL database to MongoDB, normalizing foreign keys and generating a backup in JSON format.

## 📦 Requirements

### 🔧 Dependencies

Make sure you have Python 3 and pip installed. Then install the following libraries:

```bash
pip install mysql-connector-python pymongo
```
---

#### 🗄️ MySQL Database Requirements
- You must provide valid credentials (host, user, password, database, port).
- Tables must contain data (they should not be completely empty).
- Tables must follow the following naming conventions:
	- Primary keys must be named id.
	- Foreign keys must end with _id, for example: user_id, category_id, idea_id, etc.
	- Irregular plural forms like category -> categories are supported via a custom dictionary within the script (irregular_plurals).

---

#### 🧬 MongoDB Behavior
The script will create a database (default is db3) and collections with the same name as the MySQL tables.

If collections already exist, documents will be appended (duplicates may occur if collections are not cleared beforehand).

#### 🗃️ JSON Export
All migrated data is also exported as .json files in the export_json directory (automatically created). You must have write permissions in the directory where the script is executed.

#### ✅ Execution
Run the script from main.py:

```bash
python main.py
```
