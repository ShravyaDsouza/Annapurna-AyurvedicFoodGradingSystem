from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client.annapurna
score_collection = db.score

# Simulated data
email = "test@example.com"
score_data = {
    'score_id': ObjectId(),  # Unique identifier for each score entry
    'dosha': "Pitta",
    'categories': ["Fruits", "Nuts"],
    'results': [
        {
            "category": "Fruits",
            "ingredient": "Apple",
            "suitability": "The ingredient 'Apple' is suitable for 'Pitta' dosha.",
            "preferred_form": "Sweet",
            "restricted_form": "Sour"
        }
    ],
    'grade': 5,
    'timestamp': datetime.now()
}

# First, ensure that the document exists with an empty 'scores' array
score_collection.update_one(
    {'email': email},
    {
        '$setOnInsert': {'email': email, 'scores': []}
    },
    upsert=True
)

# Now, push the score_data into the 'scores' array
try:
    result = score_collection.update_one(
        {'email': email},
        {'$push': {'scores': score_data}}
    )
    print(f"Update result: {result.modified_count} document(s) modified.")
except Exception as e:
    print(f"Error during database update: {e}")
