import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db
from backend.models.recipe import Recipe
import json

def seed_recipes():
    """Seed database with sample recipes"""
    db = SessionLocal()
    
    # Check if recipes already exist
    existing = db.query(Recipe).first()
    if existing:
        print("✅ Recipes already seeded!")
        db.close()
        return
    
    recipes_data = [
        {
            "name": "Vegetable Stir Fry",
            "description": "Quick and healthy vegetable stir fry with soy sauce",
            "category": "lunch",
            "cuisine": "chinese",
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "easy",
            "ingredients": json.dumps([
                {"name": "mixed vegetables", "quantity": "2", "unit": "cups"},
                {"name": "soy sauce", "quantity": "2", "unit": "tbsp"},
                {"name": "garlic", "quantity": "3", "unit": "cloves"},
                {"name": "oil", "quantity": "2", "unit": "tbsp"}
            ]),
            "instructions": json.dumps([
                "Heat oil in a wok or large pan",
                "Add minced garlic and sauté for 30 seconds",
                "Add vegetables and stir fry for 5-7 minutes",
                "Add soy sauce and cook for 2 more minutes",
                "Serve hot with rice"
            ]),
            "calories": 150,
            "protein": 5,
            "carbs": 20,
            "fat": 7
        },
        {
            "name": "Banana Smoothie",
            "description": "Creamy and nutritious banana smoothie",
            "category": "breakfast",
            "cuisine": "american",
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "difficulty": "easy",
            "ingredients": json.dumps([
                {"name": "banana", "quantity": "2", "unit": "pieces"},
                {"name": "milk", "quantity": "1", "unit": "cup"},
                {"name": "honey", "quantity": "1", "unit": "tbsp"},
                {"name": "ice", "quantity": "4", "unit": "cubes"}
            ]),
            "instructions": json.dumps([
                "Peel and slice bananas",
                "Add all ingredients to blender",
                "Blend until smooth",
                "Pour into glass and serve immediately"
            ]),
            "calories": 250,
            "protein": 8,
            "carbs": 52,
            "fat": 3
        },
        {
            "name": "Tomato Pasta",
            "description": "Simple pasta with fresh tomato sauce",
            "category": "dinner",
            "cuisine": "italian",
            "prep_time": 10,
            "cook_time": 20,
            "servings": 3,
            "difficulty": "easy",
            "ingredients": json.dumps([
                {"name": "pasta", "quantity": "300", "unit": "grams"},
                {"name": "tomatoes", "quantity": "4", "unit": "pieces"},
                {"name": "garlic", "quantity": "4", "unit": "cloves"},
                {"name": "olive oil", "quantity": "3", "unit": "tbsp"},
                {"name": "basil", "quantity": "1", "unit": "handful"}
            ]),
            "instructions": json.dumps([
                "Boil pasta according to package instructions",
                "Dice tomatoes and mince garlic",
                "Heat olive oil in pan, add garlic",
                "Add tomatoes and cook for 10 minutes",
                "Mix pasta with sauce, add basil",
                "Serve hot with cheese"
            ]),
            "calories": 350,
            "protein": 12,
            "carbs": 65,
            "fat": 8
        },
        {
            "name": "Fruit Salad",
            "description": "Fresh mixed fruit salad with honey dressing",
            "category": "snack",
            "cuisine": "international",
            "prep_time": 15,
            "cook_time": 0,
            "servings": 4,
            "difficulty": "easy",
            "ingredients": json.dumps([
                {"name": "apple", "quantity": "2", "unit": "pieces"},
                {"name": "banana", "quantity": "2", "unit": "pieces"},
                {"name": "orange", "quantity": "2", "unit": "pieces"},
                {"name": "grapes", "quantity": "1", "unit": "cup"},
                {"name": "honey", "quantity": "2", "unit": "tbsp"}
            ]),
            "instructions": json.dumps([
                "Wash all fruits thoroughly",
                "Dice apples and oranges",
                "Slice bananas",
                "Mix all fruits in a bowl",
                "Drizzle honey on top",
                "Chill and serve"
            ]),
            "calories": 120,
            "protein": 2,
            "carbs": 30,
            "fat": 0
        },
        {
            "name": "Egg Fried Rice",
            "description": "Classic egg fried rice with vegetables",
            "category": "lunch",
            "cuisine": "chinese",
            "prep_time": 10,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "easy",
            "ingredients": json.dumps([
                {"name": "rice", "quantity": "2", "unit": "cups"},
                {"name": "eggs", "quantity": "2", "unit": "pieces"},
                {"name": "mixed vegetables", "quantity": "1", "unit": "cup"},
                {"name": "soy sauce", "quantity": "2", "unit": "tbsp"},
                {"name": "oil", "quantity": "2", "unit": "tbsp"}
            ]),
            "instructions": json.dumps([
                "Cook rice and let it cool",
                "Beat eggs and scramble in hot oil",
                "Add vegetables and stir fry",
                "Add rice and soy sauce",
                "Mix well and cook for 5 minutes",
                "Serve hot"
            ]),
            "calories": 380,
            "protein": 14,
            "carbs": 58,
            "fat": 10
        }
    ]
    
    for recipe_data in recipes_data:
        recipe = Recipe(**recipe_data)
        db.add(recipe)
    
    db.commit()
    print(f"✅ Successfully seeded {len(recipes_data)} recipes!")
    db.close()

if __name__ == "__main__":
    print("🔧 Initializing database...")
    init_db()
    print("✅ Database initialized!")
    
    print("🌱 Seeding recipes...")
    seed_recipes()
    print("✅ All done!")
