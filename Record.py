from pymongo import MongoClient
from datetime import datetime

# 🔌 Connection
client = MongoClient("mongodb+srv://Venkatesh:QH9xv5cxikhARPYr@cluster0.vsjmaj5.mongodb.net/")
db = client["my_db"]
collection = db["records"]

def insert_record(percent, amount):
    doc = {
        "timestamp": datetime.utcnow(),
        "percent": percent,
        "amount": amount
    }

    result = collection.insert_one(doc)
    print("Inserted:", result.inserted_id)


# Example
percent = input("Enter percent change: ")
amount = input("Enter amount: ")
insert_record(float(percent), float(amount))