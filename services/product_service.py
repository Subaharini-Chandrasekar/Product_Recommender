from models import Product

class ProductService:
    def __init__(self, mongo_client, feature_flags):
        self.mongo_client = mongo_client
        self.products_collection = mongo_client.db.products
        self.feature_flags = feature_flags
    
    def add_product(self, name, cost, image_url, category, description=''):
        product = Product(name, cost, image_url, category, description)
        self.products_collection.insert_one(product.to_dict())
        return product
    
    def get_products(self, filters=None):
        query = filters or {}
        products = self.products_collection.find(query)
        return [Product.from_dict(p) for p in products]
    
    def search_products(self, search_term):
        # Simple search by name
        query = {"name": {"$regex": search_term, "$options": "i"}}
        products = self.products_collection.find(query)
        return [Product.from_dict(p) for p in products]
    
    def get_recommendations(self, search_term, user=None):
        # Get products matching the search term
        matching_products = self.search_products(search_term)
        
        # If no products found, return empty list
        if not matching_products:
            return []
        
        # Basic recommendation: products from the same category
        categories = [p.category for p in matching_products]
        
        # Use advanced recommendations if feature flag is enabled
        if self.feature_flags.is_enabled('advanced_recommendations', user):
            return self._get_advanced_recommendations(categories, search_term, user)
        else:
            return self._get_basic_recommendations(categories)
    
    def _get_basic_recommendations(self, categories):
        # Get products from the same categories but exclude exact matches
        similar_products = self.products_collection.find({
            "category": {"$in": categories},
            "name": {"$not": {"$regex": "|".join(categories), "$options": "i"}}
        }).limit(5)
        return [Product.from_dict(p) for p in similar_products]
    
    def _get_advanced_recommendations(self, categories, search_term, user):
        # This would be a more sophisticated recommendation algorithm
        # Could consider user preferences, browsing history, etc.
        # For now, just add some additional filtering criteria
        
        # First get category-based recommendations
        base_recommendations = self._get_basic_recommendations(categories)
        
        # Then add some additional products that might be relevant
        # For example, products that are frequently bought together
        # This is just a placeholder - in a real system, you'd have actual data
        additional_query = {
            "$or": [
                {"description": {"$regex": search_term, "$options": "i"}},
                {"name": {"$regex": f".*{search_term[:3]}.*", "$options": "i"}}  # Partial match
            ]
        }
        additional_products = self.products_collection.find(additional_query).limit(3)
        additional_recommendations = [Product.from_dict(p) for p in additional_products]
        
        # Combine and return unique recommendations
        all_recommendations = base_recommendations + additional_recommendations
        # Remove duplicates based on product name
        seen_names = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec.name not in seen_names:
                seen_names.add(rec.name)
                unique_recommendations.append(rec)
                
        return unique_recommendations[:8]  # Limit to 8 recommendations