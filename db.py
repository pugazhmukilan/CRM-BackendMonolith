from pymongo import MongoClient
import os
from dotenv import load_dotenv  
load_dotenv() 
MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)
db = client["mini_crm"]
users_col = db["users"]
customers_col = db["customers"]
campaigns_col = db["campaigns"]
