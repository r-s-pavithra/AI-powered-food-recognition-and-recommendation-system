"""
Import sample recipes into database
Run: python import_sample_recipes.py
"""
import sys
sys.path.append('.')

from database import SessionLocal
from models.recipe import Recipe
import json

db = SessionLocal()

# Sample Indian recipes
sample_recipes = [
    {
        "name": "Paneer Butter Masala",
        "description": "Rich and creamy paneer curry with butter and tomato gravy",
        "category": "dinner",
        "cuisine": "indian",
        "prep_time": 15,
        "cook_time": 25,
        "servings": 4,
        "difficulty": "medium",
        "ingredients": json.dumps([
            {"name": "paneer", "quantity": "250", "unit": "grams"},
            {"name": "butter", "quantity": "3", "unit": "tablespoons"},
            {"name": "tomato", "quantity": "4", "unit": "pieces"},
            {"name": "onion", "quantity": "2", "unit": "pieces"},
            {"name": "cream", "quantity": "1/2", "unit": "cup"},
            {"name": "ginger garlic paste", "quantity": "1", "unit": "tablespoon"},
            {"name": "red chili powder", "quantity": "1", "unit": "teaspoon"},
            {"name": "garam masala", "quantity": "1", "unit": "teaspoon"},
            {"name": "salt", "quantity": "to taste", "unit": ""},
        ]),
        "instructions": json.dumps([
            "Heat butter in a pan and sauté onions until golden",
            "Add ginger garlic paste and tomatoes, cook until soft",
            "Blend the mixture into a smooth paste",
            "Add spices, cream and paneer cubes",
            "Simmer for 5-7 minutes and garnish with cream"
        ]),
        "calories": 320,
        "protein": 12,
        "carbs": 18,
        "fat": 22
    },
    {
        "name": "Vegetable Biryani",
        "description": "Fragrant rice dish with mixed vegetables and aromatic spices",
        "category": "lunch",
        "cuisine": "indian",
        "prep_time": 20,
        "cook_time": 30,
        "servings": 4,
        "difficulty": "medium",
        "ingredients": json.dumps([
            {"name": "basmati rice", "quantity": "2", "unit": "cups"},
            {"name": "mixed vegetables", "quantity": "2", "unit": "cups"},
            {"name": "onion", "quantity": "2", "unit": "pieces"},
            {"name": "tomato", "quantity": "2", "unit": "pieces"},
            {"name": "yogurt", "quantity": "1/2", "unit": "cup"},
            {"name": "ginger garlic paste", "quantity": "1", "unit": "tablespoon"},
            {"name": "biryani masala", "quantity": "2", "unit": "tablespoons"},
            {"name": "mint leaves", "quantity": "1/4", "unit": "cup"},
            {"name": "oil", "quantity": "3", "unit": "tablespoons"},
        ]),
        "instructions": json.dumps([
            "Soak rice for 30 minutes, then cook until 70% done",
            "Sauté onions until golden, add ginger garlic paste",
            "Add vegetables and spices, cook for 5 minutes",
            "Layer rice and vegetable mixture",
            "Cover and cook on low heat for 15 minutes"
        ]),
        "calories": 380,
        "protein": 10,
        "carbs": 65,
        "fat": 8
    },
    {
        "name": "Masala Dosa",
        "description": "Crispy South Indian crepe filled with spiced potato mixture",
        "category": "breakfast",
        "cuisine": "indian",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "difficulty": "medium",
        "ingredients": json.dumps([
            {"name": "dosa batter", "quantity": "2", "unit": "cups"},
            {"name": "potato", "quantity": "4", "unit": "pieces"},
            {"name": "onion", "quantity": "1", "unit": "piece"},
            {"name": "green chili", "quantity": "2", "unit": "pieces"},
            {"name": "mustard seeds", "quantity": "1", "unit": "teaspoon"},
            {"name": "curry leaves", "quantity": "10", "unit": "leaves"},
            {"name": "turmeric powder", "quantity": "1/2", "unit": "teaspoon"},
            {"name": "oil", "quantity": "2", "unit": "tablespoons"},
        ]),
        "instructions": json.dumps([
            "Boil and mash potatoes",
            "Heat oil, add mustard seeds and curry leaves",
            "Add onions, chilies and spices",
            "Mix in mashed potatoes",
            "Spread dosa batter on hot griddle, fill with potato mixture"
        ]),
        "calories": 250,
        "protein": 6,
        "carbs": 45,
        "fat": 5
    },
    {
        "name": "Chicken Curry",
        "description": "Classic Indian chicken curry with rich gravy",
        "category": "dinner",
        "cuisine": "indian",
        "prep_time": 15,
        "cook_time": 35,
        "servings": 4,
        "difficulty": "easy",
        "ingredients": json.dumps([
            {"name": "chicken", "quantity": "500", "unit": "grams"},
            {"name": "onion", "quantity": "2", "unit": "pieces"},
            {"name": "tomato", "quantity": "3", "unit": "pieces"},
            {"name": "ginger garlic paste", "quantity": "1", "unit": "tablespoon"},
            {"name": "yogurt", "quantity": "1/2", "unit": "cup"},
            {"name": "curry powder", "quantity": "2", "unit": "tablespoons"},
            {"name": "oil", "quantity": "3", "unit": "tablespoons"},
            {"name": "salt", "quantity": "to taste", "unit": ""},
        ]),
        "instructions": json.dumps([
            "Marinate chicken with yogurt and spices",
            "Sauté onions until brown",
            "Add ginger garlic paste and tomatoes",
            "Add chicken and cook covered",
            "Simmer until chicken is tender"
        ]),
        "calories": 280,
        "protein": 30,
        "carbs": 12,
        "fat": 12
    },
    {
        "name": "Dal Tadka",
        "description": "Tempered yellow lentils with aromatic spices",
        "category": "lunch",
        "cuisine": "indian",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 4,
        "difficulty": "easy",
        "ingredients": json.dumps([
            {"name": "yellow lentils", "quantity": "1", "unit": "cup"},
            {"name": "onion", "quantity": "1", "unit": "piece"},
            {"name": "tomato", "quantity": "1", "unit": "piece"},
            {"name": "garlic", "quantity": "4", "unit": "cloves"},
            {"name": "cumin seeds", "quantity": "1", "unit": "teaspoon"},
            {"name": "turmeric powder", "quantity": "1/2", "unit": "teaspoon"},
            {"name": "ghee", "quantity": "2", "unit": "tablespoons"},
            {"name": "salt", "quantity": "to taste", "unit": ""},
        ]),
        "instructions": json.dumps([
            "Pressure cook lentils with turmeric until soft",
            "Heat ghee and add cumin seeds",
            "Add garlic, onions and tomatoes",
            "Pour tempering over cooked dal",
            "Simmer for 5 minutes"
        ]),
        "calories": 180,
        "protein": 12,
        "carbs": 28,
        "fat": 4
    },
    {
        "name": "Egg Curry",
        "description": "Boiled eggs in spicy tomato-onion gravy",
        "category": "dinner",
        "cuisine": "indian",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 4,
        "difficulty": "easy",
        "ingredients": json.dumps([
            {"name": "eggs", "quantity": "6", "unit": "pieces"},
            {"name": "onion", "quantity": "2", "unit": "pieces"},
            {"name": "tomato", "quantity": "2", "unit": "pieces"},
            {"name": "ginger garlic paste", "quantity": "1", "unit": "tablespoon"},
            {"name": "curry powder", "quantity": "1", "unit": "tablespoon"},
            {"name": "coconut milk", "quantity": "1/2", "unit": "cup"},
            {"name": "oil", "quantity": "2", "unit": "tablespoons"},
        ]),
        "instructions": json.dumps([
            "Boil and peel eggs",
            "Sauté onions until golden",
            "Add ginger garlic paste and spices",
            "Add tomatoes and cook until soft",
            "Add coconut milk and eggs, simmer"
        ]),
        "calories": 220,
        "protein": 14,
        "carbs": 10,
        "fat": 14
    },
    {
        "name": "Maggi Noodles",
        "description": "Quick and easy instant noodles with vegetables",
        "category": "snack",
        "cuisine": "international",
        "prep_time": 2,
        "cook_time": 5,
        "servings": 1,
        "difficulty": "easy",
        "ingredients": json.dumps([
            {"name": "maggi noodles", "quantity": "1", "unit": "packet"},
            {"name": "water", "quantity": "1.5", "unit": "cups"},
            {"name": "vegetables", "quantity": "1/2", "unit": "cup"},
            {"name": "onion", "quantity": "1/4", "unit": "piece"},
        ]),
        "instructions": json.dumps([
            "Boil water in a pan",
            "Add noodles and vegetables",
            "Cook for 2 minutes",
            "Add masala seasoning and mix well"
        ]),
        "calories": 310,
        "protein": 8,
        "carbs": 46,
        "fat": 10
    },
    {
        "name": "Vegetable Paratha",
        "description": "Stuffed whole wheat flatbread with spiced vegetables",
        "category": "breakfast",
        "cuisine": "indian",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 4,
        "difficulty": "medium",
        "ingredients": json.dumps([
            {"name": "whole wheat flour", "quantity": "2", "unit": "cups"},
            {"name": "potato", "quantity": "2", "unit": "pieces"},
            {"name": "cauliflower", "quantity": "1", "unit": "cup"},
            {"name": "peas", "quantity": "1/2", "unit": "cup"},
            {"name": "spices", "quantity": "1", "unit": "tablespoon"},
            {"name": "butter", "quantity": "2", "unit": "tablespoons"},
        ]),
        "instructions": json.dumps([
            "Knead dough with wheat flour",
            "Prepare vegetable stuffing with mashed potatoes and vegetables",
            "Roll out dough and place stuffing in center",
            "Seal and roll into flatbread",
            "Cook on griddle with butter"
        ]),
        "calories": 280,
        "protein": 8,
        "carbs": 48,
        "fat": 7
    }
]

print("\n" + "="*60)
print("📥 IMPORTING RECIPES")
print("="*60 + "\n")

try:
    for recipe_data in sample_recipes:
        # Check if recipe already exists
        existing = db.query(Recipe).filter(Recipe.name == recipe_data['name']).first()
        
        if existing:
            print(f"⏭️  Skipping '{recipe_data['name']}' (already exists)")
            continue
        
        # Create new recipe
        recipe = Recipe(**recipe_data)
        db.add(recipe)
        print(f"✅ Added: {recipe_data['name']}")
    
    db.commit()
    
    # Count total
    total = db.query(Recipe).count()
    print(f"\n🎉 Success! Total recipes in database: {total}")
    
except Exception as e:
    db.rollback()
    print(f"\n❌ Error: {e}")
finally:
    db.close()

print("\n" + "="*60)
print("✅ Import complete!")
print("="*60 + "\n")
