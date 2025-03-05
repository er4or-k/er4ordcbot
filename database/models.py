
from pymongo import MongoClient
import re
cluster = MongoClient("mongodb+srv://er4orbotofficial:sMFVidFlA8M4sRFr@er4orbot.nbcke.mongodb.net/database?retryWrites=true&w=majority&tlsAllowInvalidCertificates=true") # Replace with your MongoDB connection string
db = cluster["database"] # Your Database Name

#afk.pyclient = MongoClient("mongodb+srv://username:password@clustername.mongodb.net/database?retryWrites=true&w=majority")
afk_collection = db['afk_data']
#mute.py
mute_collection = db["mutes"]
#warn.py

warnings = db["warnings"]
warn_config = db["warn_config"]