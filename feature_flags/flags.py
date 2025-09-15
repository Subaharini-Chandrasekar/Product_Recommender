from flask import current_app, g, has_app_context
from functools import wraps

class FeatureFlags:
    def __init__(self, mongo_client, default_flags=None):
        self.mongo_client = mongo_client
        self.flags_collection = mongo_client.db.feature_flags
        
        # If inside Flask app context, load default flags from config
        if has_app_context():
            self.default_flags = current_app.config.get('FEATURE_FLAGS', {})
        else:
            self.default_flags = default_flags or {}
        
        self._load_flags()
    
    def _load_flags(self):
        """Load flags from database or initialize if not present"""
        self.flags = self.default_flags.copy()
        
        # Override with flags from database
        for flag in self.flags_collection.find():
            if flag['name'] in self.flags:
                self.flags[flag['name']] = flag['enabled']
    
    def is_enabled(self, flag_name, user=None):
        """Check if a feature flag is enabled"""
        if flag_name not in self.flags:
            return False
            
        is_enabled = self.flags.get(flag_name, False)
        
        if user and is_enabled:
            flag_doc = self.flags_collection.find_one({"name": flag_name})
            if flag_doc and "rules" in flag_doc:
                rules = flag_doc["rules"]
                
                if rules.get("admin_only") and user.get("role") == "admin":
                    return True
                if "users" in rules and user.get("username") in rules["users"]:
                    return True
                if "percentage" in rules:
                    user_hash = hash(user.get("username", "")) % 100
                    return user_hash < rules["percentage"]
                    
                return False  # Default deny if rules exist but not matched
        
        return is_enabled
    
    def update_flag(self, flag_name, enabled, rules=None):
        """Update a feature flag in the database"""
        self.flags_collection.update_one(
            {"name": flag_name},
            {"$set": {"enabled": enabled, "rules": rules or {}}},
            upsert=True
        )
        self._load_flags()

# Decorator for feature flag checks
def feature_required(flag_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            feature_flags = getattr(g, 'feature_flags', None)
            user = getattr(g, 'user', None)
            
            if feature_flags and feature_flags.is_enabled(flag_name, user):
                return f(*args, **kwargs)
            else:
                return {"error": "Feature not available"}, 404
        return decorated_function
    return decorator
