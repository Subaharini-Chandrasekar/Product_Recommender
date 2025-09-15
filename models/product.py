import datetime

class Product:
    def __init__(self, name, cost, image_url, category, description=''):
        self.name = name
        self.cost = cost
        self.image_url = image_url
        self.category = category
        self.description = description
        self.created_at = datetime.datetime.utcnow()
    
    def to_dict(self):
        return {
            'name': self.name,
            'cost': self.cost,
            'image_url': self.image_url,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data):
        return Product(
            name=data['name'],
            cost=data['cost'],
            image_url=data['image_url'],
            category=data['category'],
            description=data.get('description', '')
        )