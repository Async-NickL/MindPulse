from Backend.model.User import mongo
from datetime import datetime, timedelta
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

admin = mongo.db.admin
user = mongo.db.users

def joinGroup(user_id, group_code):
    try:
        group = admin.find_one({"_id": group_code})
        if not group:
            return False
        user_doc = user.find_one({"_id": user_id}) 
        if not user_doc:
            return False
        admin.update_one({"_id": group_code}, {"$push": {"members": user_id}})
        user.update_one({"_id": user_id}, {"$push": {"groups": group_code}})
        return True
    except Exception:
        return False

def getUsersGroups(user_id):
    try:
        user_doc = user.find_one({"_id": user_id})
        if not user_doc or 'groups' not in user_doc:
            return False
        return user_doc['groups']
    except Exception:
        return False

def createGroup(group_name, admin_id):
    try:
        group_id = str(uuid.uuid4())
        admin.insert_one({"_id": group_id, "username": admin_id, "group_name": group_name, "members": [admin_id]})
        return group_id
    except Exception:
        return False

def createAdmin(username, password, group_name):
    try:
        group_id = str(uuid.uuid4())
        if admin.find_one({"username": username}):
            return False
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        admin_doc = {
            "_id": group_id,
            "username": username,
            "password": hashed_password,
            "group_name": group_name,
            "members": [username] 
        }
        admin.insert_one(admin_doc)
        return group_id
    except Exception:
        return False

def loginAdmin(username, password):
    try:
        admin_doc = admin.find_one({"username": username})
        if not admin_doc:
            return False
        return check_password_hash(admin_doc['password'], password)
    except Exception:
        return False

def getMembers(group_id):
    try:
        admin_doc = admin.find_one({"_id": group_id})
        if not admin_doc:
            return False
        return admin_doc['members']
    except Exception:
        return []

def usernameToId(username):
    try:
        admin_doc = admin.find_one({"username": username})
        if not admin_doc:
            return False
        return admin_doc['_id']
    except Exception:
        return False

def getName(group_id):
    try:
        admin_doc = admin.find_one({"_id": group_id})
        if not admin_doc:
            return False
        return admin_doc['group_name']
    except Exception:
        return False

def removeUserById(user_id):
    try:
        admin_doc = admin.find_one({"members": user_id})
        if admin_doc:
            members = admin_doc["members"]
            members.remove(user_id)
            admin.update_one({"_id": admin_doc["_id"]}, {"$set": {"members": members}})
        
        user_doc = user.find_one({"_id": user_id})
        if user_doc and "groups" in user_doc:
            groups = user_doc["groups"] 
            groups.remove(admin_doc["_id"])
            user.update_one({"_id": user_id}, {"$set": {"groups": groups}})
        return True
    except Exception:
        return False
