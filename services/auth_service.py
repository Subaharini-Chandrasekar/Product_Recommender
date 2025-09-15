from models import User

class AuthService:
    def __init__(self, mongo_client):
        self.mongo_client = mongo_client
        self.users_collection = mongo_client.db.users
    
    def register_user(self, username, password, role='user'):
        # Check if user already exists
        if self.users_collection.find_one({'username': username}):
            return False, "Username already exists"
        
        user = User(username, password, role)
        user_dict = user.to_dict()
        user_dict['password_hash'] = user.password_hash
        
        self.users_collection.insert_one(user_dict)
        return True, "User registered successfully"
    
    def authenticate_user(self, username, password):
        user_data = self.users_collection.find_one({'username': username})
        if not user_data:
            return None, "Invalid username or password"
        
        user = User.from_dict(user_data)
        if not user.check_password(password):
            return None, "Invalid username or password"
        
        return user, "Authentication successful"