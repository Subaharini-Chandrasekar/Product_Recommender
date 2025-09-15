import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, password, role='user'):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role  # 'admin' or 'user'
        self.created_at = datetime.datetime.utcnow()
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username,
            'role': self.role,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        user = User(
            username=data['username'],
            password='',  # No need to set password as we already have the hash
            role=data.get('role', 'user')
        )
        user.password_hash = data['password_hash']
        user.created_at = data.get('created_at', datetime.datetime.utcnow())
        return user
