import requests
from datetime import datetime, timedelta
import os


def fetch_product_info(barcode):
    """
    Fetch product information from multiple sources
    Tries: Open Food Facts → UPC Database → Manual fallback
    """
    
    # Try Open Food Facts first
    result = fetch_from_open_food_facts(barcode)
    if result.get('success'):
        return result
    
    # Try UPC Database as fallback
    result = fetch_from_upc_database(barcode)
    if result.get('success'):
        return result
    
    # Return barcode with manual entry option
    return {
        "success": False,
        "barcode": barcode,
        "error": "Product not found. Please enter details manually.",
        "manual_entry": True
    }


def fetch_from_open_food_facts(barcode):
    """
    Fetch from Open Food Facts API
    """
    try:
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 1:
                product = data.get('product', {})
                
                # Extract information
                product_name = product.get('product_name', 'Unknown Product')
                brands = product.get('brands', '')
                categories = product.get('categories', '')
                image_url = product.get('image_url', '')
                
                # Skip if no product name
                if not product_name or product_name == 'Unknown Product':
                    return {"success": False}
                
                # Determine category
                category = determine_category(categories)
                
                # Estimate expiry
                expiry_days = estimate_expiry_days(category, product_name)
                
                return {
                    "success": True,
                    "source": "Open Food Facts",
                    "product_name": f"{brands} {product_name}".strip(),
                    "category": category,
                    "barcode": barcode,
                    "image_url": image_url,
                    "expiry_days": expiry_days,
                    "raw_data": {
                        "brands": brands,
                        "categories": categories,
                        "ingredients": product.get('ingredients_text', ''),
                        "quantity": product.get('quantity', ''),
                    }
                }
        
        return {"success": False}
    
    except Exception as e:
        print(f"Open Food Facts error: {e}")
        return {"success": False}


def fetch_from_upc_database(barcode):
    """
    Fetch from UPCitemdb.com API (free tier)
    """
    try:
        url = f"https://api.upcitemdb.com/prod/trial/lookup"
        params = {"upc": barcode}
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('code') == 'OK' and data.get('items'):
                item = data['items'][0]
                
                product_name = item.get('title', 'Unknown Product')
                brand = item.get('brand', '')
                category = item.get('category', 'other')
                images = item.get('images', [])
                
                # Skip if no useful data
                if not product_name or product_name == 'Unknown Product':
                    return {"success": False}
                
                return {
                    "success": True,
                    "source": "UPC Database",
                    "product_name": f"{brand} {product_name}".strip(),
                    "category": determine_category(category),
                    "barcode": barcode,
                    "image_url": images[0] if images else "",
                    "expiry_days": estimate_expiry_days(determine_category(category), product_name),
                    "raw_data": {
                        "brand": brand,
                        "description": item.get('description', ''),
                    }
                }
        
        return {"success": False}
    
    except Exception as e:
        print(f"UPC Database error: {e}")
        return {"success": False}


def determine_category(categories_string):
    """Determine product category from category string"""
    if not categories_string:
        return 'other'
    
    categories_lower = str(categories_string).lower()
    
    if any(word in categories_lower for word in ['milk', 'dairy', 'cheese', 'yogurt', 'butter', 'cream', 'paneer']):
        return 'dairy'
    elif any(word in categories_lower for word in ['fruit', 'apple', 'banana', 'orange', 'mango', 'grape']):
        return 'fruits'
    elif any(word in categories_lower for word in ['vegetable', 'tomato', 'potato', 'carrot', 'onion', 'cabbage']):
        return 'vegetables'
    elif any(word in categories_lower for word in ['meat', 'chicken', 'beef', 'pork', 'fish', 'mutton', 'seafood']):
        return 'meat'
    elif any(word in categories_lower for word in ['bread', 'bakery', 'cake', 'biscuit', 'cookie', 'roti']):
        return 'bakery'
    elif any(word in categories_lower for word in ['beverage', 'drink', 'juice', 'soda', 'water', 'tea', 'coffee']):
        return 'beverages'
    elif any(word in categories_lower for word in ['snack', 'chips', 'candy', 'chocolate', 'namkeen']):
        return 'snacks'
    elif any(word in categories_lower for word in ['frozen', 'ice cream']):
        return 'frozen'
    elif any(word in categories_lower for word in ['canned', 'preserved', 'packaged', 'pickle']):
        return 'canned'
    elif any(word in categories_lower for word in ['grain', 'rice', 'wheat', 'flour', 'dal', 'atta']):
        return 'grains'
    else:
        return 'other'


def estimate_expiry_days(category, product_name):
    """Estimate expiry days based on category"""
    product_lower = product_name.lower()
    
    # Special cases
    if 'milk' in product_lower:
        return 3  # Fresh milk expires quickly
    elif 'bread' in product_lower or 'roti' in product_lower:
        return 2
    elif 'yogurt' in product_lower or 'curd' in product_lower:
        return 5
    
    # Category defaults
    expiry_map = {
        'dairy': 7,
        'fruits': 5,
        'vegetables': 7,
        'meat': 3,
        'bakery': 3,
        'beverages': 180,
        'snacks': 60,
        'frozen': 90,
        'canned': 365,
        'grains': 180,
        'other': 30
    }
    
    return expiry_map.get(category, 30)


def search_product_by_name(product_name):
    """
    Search for product by name (for manual entry support)
    """
    try:
        url = f"https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": product_name,
            "search_simple": 1,
            "json": 1,
            "page_size": 5
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])
            
            if products:
                suggestions = []
                for p in products[:5]:
                    suggestions.append({
                        "name": p.get('product_name', 'Unknown'),
                        "brand": p.get('brands', ''),
                        "category": determine_category(p.get('categories', '')),
                        "image": p.get('image_url', '')
                    })
                
                return {
                    "success": True,
                    "suggestions": suggestions
                }
        
        return {"success": False, "suggestions": []}
    
    except Exception as e:
        print(f"Search error: {e}")
        return {"success": False, "suggestions": []}
