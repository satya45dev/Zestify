import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import Category, Product

def init_categories():
    # 1. Create the requested categories
    category_names = ['Smartphone', 'Music', 'Sports', 'Electronics']
    categories = {}
    
    print("Creating categories...")
    for name in category_names:
        cat, created = Category.objects.get_or_create(name=name)
        categories[name] = cat
        print(f" - {name}")

    # 2. Assign existing products to categories (Auto-assign logic)
    print("\nUpdating products...")
    all_products = Product.objects.all()
    
    for p in all_products:
        name_lower = p.name.lower()
        
        if 'phone' in name_lower or 'iphone' in name_lower:
            p.category = categories['Smartphone']
        elif 'football' in name_lower or 'shoe' in name_lower:
            p.category = categories['Sports']
        elif 'headphone' in name_lower or 'speaker' in name_lower:
            p.category = categories['Music']
        elif 'camera' in name_lower or 'laptop' in name_lower:
            p.category = categories['Electronics']
        
        p.save()
        print(f" - Assigned '{p.name}' to {p.category}")

if __name__ == "__main__":
    init_categories()