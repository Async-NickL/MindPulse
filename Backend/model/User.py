from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import uuid
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv('MONGODB_URI')
mongo = PyMongo(app)
users = mongo.db.users

def generate_unique_id():
    return str(uuid.uuid4())

def createUser(name, email, profession, age, gender, passwd, groups):
    if users.find_one({'email': email}):
        return False
    
    # Hash the password before storing
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(passwd, method='pbkdf2:sha256')
    
    user_data = {
        "_id": generate_unique_id(),
        "name": name,
        "email": email,
        "age": int(age),
        "gender": gender,
        "profession": profession,
        "passwd": hashed_password,  # Store hashed password instead of plain text
        "groups": groups if groups else []
    }
    
    try:
        users.insert_one(user_data)
        return True
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return False

def loginUser(email, passwd):
    try:
        # Find user by email
        user = users.find_one({'email': email})
        if not user:
            print(f"No user found with email: {email}")
            return False
            
        # Verify password using secure comparison
        from werkzeug.security import check_password_hash
        if check_password_hash(user['passwd'], passwd):
            return True
            
        print(f"Invalid password for user: {email}")
        return False
        
    except Exception as e:
        print(f"Error during login: {str(e)}")
        return False

def getId(email):
    try:
        user = users.find_one({'email': email})
        if user and '_id' in user:
            return user['_id']
        print(f"No user ID found for email: {email}")
        return None
    except Exception as e:
        print(f"Error getting user ID: {str(e)}")
        return None

def getUser(id):
    try:
        if not id:
            print("No ID provided to getUser")
            return None
        user = users.find_one({'_id': id})
        if not user:
            print(f"No user found with ID: {id}")
        return user
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        return None




