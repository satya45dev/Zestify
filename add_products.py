import os
import django
import urllib.request
from django.core.files.base import ContentFile

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from core.models import Product

def create_products():
    # List of products to add
    products_data = [
        {
            "name": "iPhone 17 Pro Max",
            "description": "The latest ultimate iPhone with titanium design, A19 Bionic chip, and 100x zoom.",
            "price": 1299.99,
            "image_url": "https://www.mobileana.com/wp-content/uploads/2025/06/Apple-iPhone-17-Pro-Max-Cosmic-Orange.webp" 
        },
        {
            "name": "Pro Football",
            "description": "Official size and weight professional match ball. High durability and grip.",
            "price": 29.99,
            "image_url": "https://m.media-amazon.com/images/I/61O1RqeDeQL._AC_UF894,1000_QL80_.jpg"
        },
        {
            "name": "Bose Noise Cancelling Headphones",
            "description": "World-class adjustable noise cancellation, high-fidelity audio, and comfortable fit.",
            "price": 349.00,
            "image_url": "https://m.media-amazon.com/images/I/51ZR4lyxBHL.jpg"
        },
        {
            "name": "Canon DSLR Camera",
            "description": "Capture stunning 4K video and 24MP photos with this versatile DSLR kit.",
            "price": 899.50,
            "image_url": "https://in.canon/media/image/2022/05/23/0ad3522b3e844ca19ac0a33a6b88cb28_EOS+R7+w+RF-S18-150mm+f3.5-6.3+IS+SSTM+Front+Slant.png"
        },
        {
            "name": "Smart Bluetooth Speakers",
            "description": "360-degree sound with deep bass and voice control assistant built-in.",
            "price": 199.99,
            "image_url": "https://avstore.in/cdn/shop/products/1.AVStore-Marshall-Acton-III-Top-Front-Hero-Black.jpg?v=1675690233&width=2048"
        }
    ]

    print("Starting to add products... Please wait while images download.")

    for item in products_data:
        # Check if product already exists to prevent duplicates
        if Product.objects.filter(name=item['name']).exists():
            print(f"Skipped: {item['name']} (Already exists)")
            continue

        # Download the image
        try:
            print(f"Downloading image for {item['name']}...")
            image_response = urllib.request.urlopen(item['image_url'])
            image_content = image_response.read()
            
            # Create the product object
            product = Product(
                name=item['name'],
                description=item['description'],
                price=item['price']
            )
            
            # Save the image file to the product
            file_name = f"{item['name'].lower().replace(' ', '_')}.jpg"
            product.image.save(file_name, ContentFile(image_content), save=True)
            
            print(f"Success: Added {item['name']}")
            
        except Exception as e:
            print(f"Error adding {item['name']}: {e}")

    print("\nAll Done! Run 'python manage.py runserver' and check your website.")

if __name__ == "__main__":
    create_products()