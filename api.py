import os  # Required for environment variables
from flask import Flask, request, jsonify
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import MongoClient

app = Flask(__name__)

# Env variable name: MONGO_URI (set on render)
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)

db = client['user_database']
users_collection = db['users']

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "message": "API is running",
        "success": True,
        "timestamp": datetime.now().isoformat()
    }), 200

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = list(users_collection.find())
        for user in users:
            user['_id'] = str(user['_id'])
        return jsonify({
            "message": "Users retrieved",
            "success": True,
            "users": users
        }), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "success": False}), 500

# Add new user
@app.route('/add', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'firstName' not in data:
            return jsonify({"message": "Missing required fields", "success": False}), 400
        
        new_user = {"email": data['email'], "firstName": data['firstName']}
        result = users_collection.insert_one(new_user)
        return jsonify({"message": "User added", "success": True, "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "success": False}), 500

# Get user by ID
@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({"message": "User not found", "success": False}), 404
        user['_id'] = str(user['_id'])
        return jsonify({"success": True, "user": user}), 200
    except Exception as e:
        return jsonify({"message": "Invalid ID format", "success": False}), 400

# Update user
@app.route('/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        update_data = {k: v for k, v in data.items() if k in ['email', 'firstName']}
        result = users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        if result.matched_count == 0:
            return jsonify({"message": "User not found", "success": False}), 404
        return jsonify({"message": "User updated", "success": True}), 200
    except Exception as e:
        return jsonify({"message": "Error updating user", "success": False}), 500

# Delete user
@app.route('/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"message": "User not found", "success": False}), 404
            
        return jsonify({"success": True, "message": "User deleted"}), 200
    except Exception as e:
        return jsonify({"message": "Internal error", "success": False}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host='0.0.0.0', port=port)