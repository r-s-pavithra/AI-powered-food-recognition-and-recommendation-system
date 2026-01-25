"""
Seed database with recipes
- First seeds 5 sample recipes for testing
- Then imports Indian recipes from Kaggle CSV (if available)
"""

import sys
import os
import pandas as pd
import json

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db
from backend.models.recipe import Recipe


def clean_ingredients(ingredients_str):
    """Convert ingredients string to JSON array format"""
    if pd.isna(ingredients_str) or not ingredients_str:
        return json.dumps([])

    # Split by comma and create list
    ingredients_list = [ing.strip() for ing in str(ingredients_str).split(',')]

    # Convert to JSON format with name and quantity
    formatted_ingredients = [
        {"name": ing, "quantity": "", "unit": ""} 
        for ing in ingredients_list if ing
    ]

    return json.dumps(formatted_ingredients)


def clean_instructions(instructions_str):
    """Convert instructions string to JSON array format"""
    if pd.isna(instructions_str) or not instructions_str:
        return json.dumps(["No instructions available"])

    instructions = str(instructions_str)

    # Try to split by numbered format (1. 2. 3.)
    import re
    steps = re.split(r'\d+\.\s*', instructions)
    steps = [step.strip() for step in steps if step.strip()]

    # If no numbered format, split by sentences
    if len(steps) <= 1:
        steps = [s.strip() + '.' for s in instructions.split('.') if s.strip()]

    return json.dumps(steps)


def seed_sample_recipes(db: Session):
    """Seed database with 5 sample recipes for testing"""

    print("\n📝 Seeding sample recipes...")

    # Check if sample recipes already exist
    existing = db.query(Recipe).filter(Recipe.name == 'Vegetable Stir Fry').first()
    if existing:
        print("   ⚠️  Sample recipes already exist, skipping...")
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
        }
    ]

    for recipe_data in recipes_data:
        recipe = Recipe(**recipe_data)
        db.add(recipe)

    db.commit()
    print(f"   ✅ Added {len(recipes_data)} sample recipes")


def import_indian_recipes(db: Session):
    """Import Indian recipes from Kaggle CSV"""

    print("\n📥 Importing Indian recipes from CSV...")

    # Path to CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'indianrecipes.csv')

    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"   ⚠️  CSV file not found at: {csv_path}")
        print(f"   ℹ️  Place indianrecipes.csv in backend/data/ to import Indian recipes")
        return

    # Check if already imported
    existing_count = db.query(Recipe).filter(Recipe.cuisine == 'indian').count()
    if existing_count > 100:  # If more than 100 Indian recipes already exist
        print(f"   ⚠️  Indian recipes already imported ({existing_count} found)")
        return

    try:
        # Read CSV
        print(f"   📂 Reading CSV file...")
        df = pd.read_csv(csv_path, encoding='utf-8')
        print(f"   ✅ Loaded {len(df)} recipes from CSV")

        # Import recipes
        imported = 0
        errors = 0

        for index, row in df.iterrows():
            try:
                # Use TranslatedRecipeName (English) if available
                recipe_name = row.get('TranslatedRecipeName') or row.get('RecipeName', '')

                # Skip if no name
                if pd.isna(recipe_name) or not recipe_name:
                    continue

                # Get ingredients and instructions (prefer English translations)
                ingredients = row.get('TranslatedIngredients') or row.get('Ingredients', '')
                instructions = row.get('TranslatedInstructions') or row.get('Instructions', '')

                # Create recipe
                recipe = Recipe(
                    name=str(recipe_name)[:255],
                    description=f"{row.get('Course', 'Indian')} - {row.get('Diet', '')}",
                    category=str(row.get('Course', 'Main Course'))[:50],
                    cuisine='indian',  # Mark as Indian
                    prep_time=int(row.get('PrepTimeInMins', 0)) if pd.notna(row.get('PrepTimeInMins')) else 0,
                    cook_time=int(row.get('CookTimeInMins', 0)) if pd.notna(row.get('CookTimeInMins')) else 0,
                    servings=int(row.get('Servings', 4)) if pd.notna(row.get('Servings')) else 4,
                    difficulty='medium',
                    ingredients=clean_ingredients(ingredients),
                    instructions=clean_instructions(instructions),
                    calories=None,
                    protein=None,
                    carbs=None,
                    fat=None
                )

                db.add(recipe)
                imported += 1

                # Commit every 100 recipes
                if imported % 100 == 0:
                    db.commit()
                    print(f"   ✅ Imported {imported} recipes...")

            except Exception as e:
                errors += 1
                if errors <= 3:  # Show first 3 errors only
                    print(f"   ⚠️  Error on row {index}: {str(e)[:80]}")
                continue

        # Final commit
        db.commit()

        print(f"\n   ✅ Successfully imported {imported} Indian recipes!")
        if errors > 0:
            print(f"   ⚠️  Skipped {errors} recipes due to errors")

    except Exception as e:
        print(f"   ❌ Error importing CSV: {e}")


def seed_recipes():
    """Main function to seed all recipes"""

    print("=" * 80)
    print("SEEDING RECIPES DATABASE")
    print("=" * 80)

    # Initialize database
    print("\n🔧 Initializing database...")
    init_db()
    print("   ✅ Database initialized")

    # Create session
    db = SessionLocal()

    try:
        # 1. Seed sample recipes
        seed_sample_recipes(db)

        # 2. Import Indian recipes from CSV
        import_indian_recipes(db)

        # Show final count
        total_recipes = db.query(Recipe).count()
        indian_recipes = db.query(Recipe).filter(Recipe.cuisine == 'indian').count()

        print("\n" + "=" * 80)
        print("✅ SEEDING COMPLETE!")
        print("=" * 80)
        print(f"📊 Total recipes in database: {total_recipes}")
        print(f"🇮🇳 Indian recipes: {indian_recipes}")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    print("\nInitializing database...")
    init_db()
    print("Database initialized!")

    print("\nSeeding recipes...")
    seed_recipes()

    print("\nAll done!")
