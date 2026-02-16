"""
Add recipes directly to database using SQLite
Run: python add_recipes.py
"""
import sqlite3
import json

# Connect to database
conn = sqlite3.connect("food_tracker.db")
cursor = conn.cursor()

# Sample recipes
recipes = [
    (
        "Paneer Butter Masala",
        "Rich and creamy paneer curry with butter and tomato gravy",
        "dinner",
        "indian",
        15, 25, 4,
        "medium",
        json.dumps([
            {"name": "paneer", "quantity": "250", "unit": "grams"},
            {"name": "butter", "quantity": "3", "unit": "tablespoons"},
            {"name": "tomato", "quantity": "4", "unit": "pieces"},
            {"name": "onion", "quantity": "2", "unit": "pieces"},
            {"name": "cream", "quantity": "1/2", "unit": "cup"},
        ]),
        json.dumps([
            "Heat butter in a pan and sauté onions until golden",
            "Add ginger garlic paste and tomatoes, cook until soft",
            "Blend the mixture into a smooth paste",
            "Add spices, cream and paneer cubes",
            "Simmer for 5-7 minutes"
        ]),
        None, 320, 12, 18, 22
    ),
    (
        "Egg Curry",
        "Boiled eggs in spicy tomato-onion gravy",
        "dinner",
        "indian",
        10, 20, 4,
        "easy",
        json.dumps([
            {"name": "eggs", "quantity": "6", "unit": "pieces"},
            {"name": "onion", "quantity": "2", "unit": "pieces"},
            {"name": "tomato", "quantity": "2", "unit": "pieces"},
            {"name": "oil", "quantity": "2", "unit": "tablespoons"},
        ]),
        json.dumps([
            "Boil and peel eggs",
            "Sauté onions until golden",
            "Add spices and tomatoes",
            "Add eggs and simmer"
        ]),
        None, 220, 14, 10, 14
    ),
    (
        "Maggi Noodles",
        "Quick instant noodles with vegetables",
        "snack",
        "international",
        2, 5, 1,
        "easy",
        json.dumps([
            {"name": "maggi", "quantity": "1", "unit": "packet"},
            {"name": "water", "quantity": "1.5", "unit": "cups"},
            {"name": "vegetables", "quantity": "1/2", "unit": "cup"},
        ]),
        json.dumps([
            "Boil water",
            "Add noodles and vegetables",
            "Cook for 2 minutes",
            "Add seasoning"
        ]),
        None, 310, 8, 46, 10
    ),
    (
        "Vegetable Paratha",
        "Stuffed whole wheat flatbread",
        "breakfast",
        "indian",
        15, 20, 4,
        "medium",
        json.dumps([
            {"name": "whole wheat flour", "quantity": "2", "unit": "cups"},
            {"name": "potato", "quantity": "2", "unit": "pieces"},
            {"name": "vegetables", "quantity": "1", "unit": "cup"},
            {"name": "butter", "quantity": "2", "unit": "tablespoons"},
        ]),
        json.dumps([
            "Knead dough with flour",
            "Prepare vegetable stuffing",
            "Roll and stuff",
            "Cook on griddle with butter"
        ]),
        None, 280, 8, 48, 7
    ),
    (
        "Dal Tadka",
        "Tempered yellow lentils",
        "lunch",
        "indian",
        10, 25, 4,
        "easy",
        json.dumps([
            {"name": "lentils", "quantity": "1", "unit": "cup"},
            {"name": "onion", "quantity": "1", "unit": "piece"},
            {"name": "tomato", "quantity": "1", "unit": "piece"},
            {"name": "oil", "quantity": "2", "unit": "tablespoons"},
        ]),
        json.dumps([
            "Cook lentils until soft",
            "Prepare tempering with spices",
            "Pour over dal",
            "Simmer for 5 minutes"
        ]),
        None, 180, 12, 28, 4
    ),
    (
        "Butter Toast",
        "Simple buttered toast",
        "breakfast",
        "international",
        2, 3, 1,
        "easy",
        json.dumps([
            {"name": "bread", "quantity": "2", "unit": "slices"},
            {"name": "butter", "quantity": "1", "unit": "tablespoon"},
        ]),
        json.dumps([
            "Toast bread slices",
            "Spread butter on hot toast",
            "Serve immediately"
        ]),
        None, 150, 4, 20, 6
    ),
    (
        "Milk Shake",
        "Creamy cold milk drink",
        "snack",
        "international",
        5, 0, 1,
        "easy",
        json.dumps([
            {"name": "milk", "quantity": "1", "unit": "cup"},
            {"name": "sugar", "quantity": "2", "unit": "tablespoons"},
            {"name": "ice cream", "quantity": "2", "unit": "scoops"},
        ]),
        json.dumps([
            "Add all ingredients to blender",
            "Blend until smooth",
            "Serve chilled"
        ]),
        None, 280, 8, 45, 8
    ),
    (
        "Omelet",
        "Simple egg omelet",
        "breakfast",
        "international",
        3, 5, 1,
        "easy",
        json.dumps([
            {"name": "eggs", "quantity": "2", "unit": "pieces"},
            {"name": "onion", "quantity": "1/4", "unit": "piece"},
            {"name": "butter", "quantity": "1", "unit": "tablespoon"},
        ]),
        json.dumps([
            "Beat eggs with salt",
            "Heat butter in pan",
            "Pour eggs and cook",
            "Flip and serve"
        ]),
        None, 200, 13, 2, 15
    ),
]

print("\n" + "="*60)
print("📥 ADDING RECIPES TO DATABASE")
print("="*60 + "\n")

added = 0
skipped = 0

for recipe in recipes:
    name = recipe[0]
    
    # Check if exists
    cursor.execute("SELECT id FROM recipes WHERE name = ?", (name,))
    if cursor.fetchone():
        print(f"⏭️  Skipping '{name}' (already exists)")
        skipped += 1
        continue
    
    # Insert recipe
    try:
        cursor.execute("""
            INSERT INTO recipes (
                name, description, category, cuisine,
                prep_time, cook_time, servings, difficulty,
                ingredients, instructions,
                image_url, calories, protein, carbs, fat
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, recipe)
        
        print(f"✅ Added: {name}")
        added += 1
    except Exception as e:
        print(f"❌ Error adding '{name}': {e}")

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM recipes")
total = cursor.fetchone()[0]

print(f"\n" + "="*60)
print(f"✅ Import Complete!")
print(f"   Added: {added}")
print(f"   Skipped: {skipped}")
print(f"   Total in DB: {total}")
print("="*60 + "\n")

conn.close()
