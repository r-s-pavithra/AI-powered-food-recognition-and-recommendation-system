"""
Test Recipe Recommendations
"""
from backend.database import SessionLocal
from backend.models.user import User
from backend.models.recipe import Recipe
from backend.models.pantry_item import PantryItem
import json
import sys
sys.path.append('.')

db = SessionLocal()

# Get first user
user = db.query(User).first()
if not user:
    print("❌ No users found! Create a user first.")
    exit()

print(f"👤 Testing for user: {user.email}")

# Check pantry items
pantry = db.query(PantryItem).filter(PantryItem.user_id == user.id).all()
print(f"\n📦 Pantry Items ({len(pantry)}):")
for item in pantry:
    print(f"   - {item.product_name}")

# Check recipes
recipes = db.query(Recipe).limit(5).all()
print(f"\n🍳 Sample Recipes ({db.query(Recipe).count()} total):")
for recipe in recipes:
    print(f"\n   Recipe: {recipe.name}")
    try:
        ingredients = json.loads(recipe.ingredients)
        print(f"   Ingredients: {[ing['name'] for ing in ingredients[:5]]}")
    except:
        print(f"   Ingredients: [Error parsing]")

# Simulate matching
if pantry and recipes:
    available = [item.product_name.lower() for item in pantry]
    print(f"\n🔍 Matching Test:")
    print(f"   Available: {available}")
    
    for recipe in recipes[:3]:
        try:
            ingredients = json.loads(recipe.ingredients)
            ing_names = [ing['name'].lower() for ing in ingredients]
            
            matches = [ing for ing in ing_names 
                      if any(prod in ing or ing in prod for prod in available)]
            
            score = len(matches) / len(ing_names) if ing_names else 0
            print(f"\n   {recipe.name}: {score*100:.1f}% match")
            print(f"      Matched: {matches[:3]}")
        except:
            pass

db.close()
