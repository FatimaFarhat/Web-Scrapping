import pymongo
import json

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]

file_path = 'data//all_articles_original_20K.json'

# Load and insert JSON data
with open(file_path, 'rt', encoding='utf-8') as f:
    data = json.load(f)
    collection.insert_many(data)

print("Data inserted successfully!")