"""
Seed Script - 60 Recipes (Tamil + Indian + International)
Run from project root:
python -m backend.data.seed_recipes
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database import SessionLocal
from backend.models.recipe import Recipe


RECIPES_DATA = [

    # =========================================================
    # 🌅 BREAKFAST (10 recipes)
    # =========================================================

    {
        "name": "Idli",
        "description": "Soft, fluffy steamed rice cakes made from fermented rice and urad dal batter. A staple South Indian breakfast served with sambar and chutney.",
        "category": "breakfast",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 480,
        "cook_time": 15,
        "servings": 4,
        "calories": 120,
        "protein": 4.0,
        "carbs": 22.0,
        "fat": 1.5,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "idli rice", "quantity": "2", "unit": "cups"},
            {"name": "urad dal", "quantity": "1", "unit": "cup"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "water", "quantity": "as needed", "unit": ""}
        ],
        "instructions": [
            "Wash and soak idli rice and urad dal separately for 6-8 hours.",
            "Drain the water and grind urad dal first to a smooth, fluffy batter adding little water.",
            "Grind rice to a slightly coarse batter separately.",
            "Mix both batters together, add salt and mix well with hands to help fermentation.",
            "Cover the batter and ferment overnight (8-10 hours) at room temperature.",
            "Next morning, gently stir the fermented batter.",
            "Grease idli moulds with oil and pour batter into each mould.",
            "Steam in an idli cooker for 10-12 minutes on medium flame.",
            "Insert a toothpick — if it comes out clean, idlis are done.",
            "Wait 2 minutes before removing. Serve hot with sambar and coconut chutney."
        ],
        "tags": ["popular", "healthy", "south-indian", "steam-cooked"]
    },

    {
        "name": "Dosa",
        "description": "Crispy golden crepes made from fermented rice and lentil batter. One of the most loved South Indian breakfast dishes, served with sambar and chutney.",
        "category": "breakfast",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 480,
        "cook_time": 20,
        "servings": 4,
        "calories": 160,
        "protein": 5.0,
        "carbs": 28.0,
        "fat": 3.5,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "idli rice", "quantity": "2", "unit": "cups"},
            {"name": "urad dal", "quantity": "0.5", "unit": "cup"},
            {"name": "fenugreek seeds", "quantity": "0.5", "unit": "tsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "water", "quantity": "as needed", "unit": ""}
        ],
        "instructions": [
            "Soak rice, urad dal and fenugreek seeds together for 6-8 hours.",
            "Drain and grind to a smooth, flowing batter. Add salt and mix well.",
            "Ferment the batter overnight in a warm place.",
            "Heat a flat non-stick pan or cast iron tawa on medium-high flame.",
            "Pour a ladle of batter in the center and spread in circular motion to form a thin crepe.",
            "Drizzle oil or ghee around the edges of the dosa.",
            "Cook until the edges lift up and the bottom turns golden and crispy.",
            "Fold and serve hot with coconut chutney and sambar."
        ],
        "tags": ["popular", "south-indian", "crispy", "street food"]
    },

    {
        "name": "Ven Pongal",
        "description": "A creamy, comforting South Indian breakfast made with rice and moong dal, tempered with ghee, cumin, pepper and cashews.",
        "category": "breakfast",
        "cuisine": "south_indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 3,
        "calories": 280,
        "protein": 8.0,
        "carbs": 42.0,
        "fat": 9.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "raw rice", "quantity": "1", "unit": "cup"},
            {"name": "moong dal", "quantity": "0.5", "unit": "cup"},
            {"name": "ghee", "quantity": "3", "unit": "tbsp"},
            {"name": "cumin seeds", "quantity": "1", "unit": "tsp"},
            {"name": "black pepper", "quantity": "1", "unit": "tsp"},
            {"name": "ginger", "quantity": "1", "unit": "inch"},
            {"name": "cashews", "quantity": "10", "unit": "pieces"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Dry roast moong dal until light golden. Wash rice and dal together.",
            "Pressure cook rice and dal with 4 cups water and salt for 4-5 whistles until mushy.",
            "Heat ghee in a pan. Add cashews and fry until golden. Remove and set aside.",
            "In the same ghee, add cumin seeds and let them splutter.",
            "Add crushed black pepper, ginger and curry leaves. Saute for 30 seconds.",
            "Add the cooked rice-dal mixture and mix well.",
            "Adjust consistency with hot water if needed.",
            "Add fried cashews on top and drizzle extra ghee.",
            "Serve hot with coconut chutney and sambar."
        ],
        "tags": ["popular", "south-indian", "comfort food", "healthy"]
    },

    {
        "name": "Upma",
        "description": "A savory semolina porridge tempered with mustard seeds, onions, green chillies and vegetables. A quick and filling South Indian breakfast.",
        "category": "breakfast",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 15,
        "servings": 2,
        "calories": 200,
        "protein": 5.0,
        "carbs": 35.0,
        "fat": 6.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "rava (semolina)", "quantity": "1", "unit": "cup"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "mustard seeds", "quantity": "1", "unit": "tsp"},
            {"name": "chana dal", "quantity": "1", "unit": "tsp"},
            {"name": "urad dal", "quantity": "1", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "water", "quantity": "2.5", "unit": "cups"}
        ],
        "instructions": [
            "Dry roast rava in a pan on low flame until light golden and aromatic. Set aside.",
            "Heat oil in a pan. Add mustard seeds and let them splutter.",
            "Add chana dal and urad dal. Fry until golden.",
            "Add curry leaves, green chillies and ginger. Saute for 30 seconds.",
            "Add chopped onions and fry until translucent.",
            "Pour 2.5 cups of water and salt. Bring to a boil.",
            "Slowly add roasted rava while stirring continuously to avoid lumps.",
            "Mix well, cover and cook on low flame for 3-4 minutes.",
            "Garnish with coriander and serve hot with coconut chutney."
        ],
        "tags": ["quick", "south-indian", "healthy", "popular"]
    },

    {
        "name": "Medu Vada",
        "description": "Crispy on the outside, soft on the inside deep fried urad dal donuts. A popular South Indian breakfast and snack served with sambar and chutney.",
        "category": "breakfast",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 240,
        "cook_time": 20,
        "servings": 4,
        "calories": 180,
        "protein": 7.0,
        "carbs": 20.0,
        "fat": 8.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "urad dal", "quantity": "1", "unit": "cup"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"}
        ],
        "instructions": [
            "Soak urad dal in water for 3-4 hours. Drain completely.",
            "Grind urad dal to a thick, smooth and fluffy batter using very little water.",
            "Add salt, pepper, chopped green chilli, ginger and curry leaves. Mix well.",
            "Heat oil in a deep pan to 180°C.",
            "Wet your hands, take a portion of batter and shape into a round disc.",
            "Make a hole in the center with your thumb to form a donut shape.",
            "Gently slide into hot oil and fry on medium flame.",
            "Fry for 3-4 minutes on each side until golden and crispy.",
            "Drain on paper towel. Serve hot with coconut chutney and sambar."
        ],
        "tags": ["popular", "south-indian", "crispy", "street food"]
    },

    {
        "name": "Pancakes",
        "description": "Fluffy American-style pancakes made with simple pantry ingredients. Golden on the outside, soft and airy on the inside. Perfect with maple syrup.",
        "category": "breakfast",
        "cuisine": "american",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 2,
        "calories": 320,
        "protein": 8.0,
        "carbs": 48.0,
        "fat": 10.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "all purpose flour", "quantity": "1", "unit": "cup"},
            {"name": "egg", "quantity": "1", "unit": "piece"},
            {"name": "milk", "quantity": "0.75", "unit": "cup"},
            {"name": "butter", "quantity": "2", "unit": "tbsp"},
            {"name": "sugar", "quantity": "1", "unit": "tbsp"},
            {"name": "baking powder", "quantity": "1", "unit": "tsp"},
            {"name": "salt", "quantity": "0.25", "unit": "tsp"},
            {"name": "vanilla extract", "quantity": "0.5", "unit": "tsp"}
        ],
        "instructions": [
            "In a bowl, mix flour, sugar, baking powder and salt together.",
            "In another bowl, whisk egg, milk, melted butter and vanilla extract.",
            "Pour wet ingredients into dry ingredients and mix gently until just combined. Do not overmix — lumps are okay.",
            "Let the batter rest for 5 minutes.",
            "Heat a non-stick pan on medium heat and lightly grease with butter.",
            "Pour 1/4 cup batter per pancake. Cook until bubbles form on surface (about 2 min).",
            "Flip and cook for another 1-2 minutes until golden.",
            "Serve warm with maple syrup, butter or fresh fruits."
        ],
        "tags": ["popular", "quick", "comfort food"]
    },

    {
        "name": "French Toast",
        "description": "Classic French Toast made with thick bread slices dipped in an egg-milk mixture and pan-fried until golden. A quick and satisfying breakfast.",
        "category": "breakfast",
        "cuisine": "continental",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 10,
        "servings": 2,
        "calories": 270,
        "protein": 9.0,
        "carbs": 35.0,
        "fat": 10.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "bread", "quantity": "4", "unit": "slices"},
            {"name": "egg", "quantity": "2", "unit": "pieces"},
            {"name": "milk", "quantity": "0.25", "unit": "cup"},
            {"name": "sugar", "quantity": "1", "unit": "tbsp"},
            {"name": "cinnamon powder", "quantity": "0.25", "unit": "tsp"},
            {"name": "butter", "quantity": "1", "unit": "tbsp"},
            {"name": "vanilla extract", "quantity": "0.25", "unit": "tsp"}
        ],
        "instructions": [
            "In a shallow bowl, whisk eggs, milk, sugar, cinnamon and vanilla extract together.",
            "Dip each bread slice into the egg mixture, coating both sides evenly.",
            "Let it soak for 10-15 seconds on each side.",
            "Heat butter in a non-stick pan over medium heat.",
            "Place soaked bread slices on the pan.",
            "Cook for 2-3 minutes per side until golden brown.",
            "Serve warm dusted with powdered sugar and maple syrup or honey."
        ],
        "tags": ["quick", "comfort food"]
    },

    {
        "name": "Oatmeal",
        "description": "Warm and creamy oatmeal cooked with milk and topped with fruits, nuts and honey. A highly nutritious and filling breakfast for a healthy start.",
        "category": "breakfast",
        "cuisine": "continental",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 2,
        "cook_time": 10,
        "servings": 1,
        "calories": 220,
        "protein": 8.0,
        "carbs": 38.0,
        "fat": 5.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "rolled oats", "quantity": "0.5", "unit": "cup"},
            {"name": "milk", "quantity": "1", "unit": "cup"},
            {"name": "honey", "quantity": "1", "unit": "tbsp"},
            {"name": "banana", "quantity": "1", "unit": "piece"},
            {"name": "almonds", "quantity": "5", "unit": "pieces"},
            {"name": "cinnamon powder", "quantity": "0.25", "unit": "tsp"},
            {"name": "salt", "quantity": "1", "unit": "pinch"}
        ],
        "instructions": [
            "Pour milk into a saucepan and bring to a gentle simmer.",
            "Add rolled oats and a pinch of salt. Stir well.",
            "Cook on low-medium heat for 5-7 minutes, stirring occasionally until thickened.",
            "Add cinnamon powder and mix.",
            "Pour into a bowl and drizzle honey on top.",
            "Top with sliced banana and crushed almonds.",
            "Serve immediately while warm."
        ],
        "tags": ["quick", "healthy", "low-calorie", "high-protein"]
    },

    {
        "name": "Poha",
        "description": "Flattened rice cooked with onions, mustard seeds, turmeric and peanuts. A light, quick and popular North/South Indian breakfast.",
        "category": "breakfast",
        "cuisine": "indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 2,
        "calories": 190,
        "protein": 5.0,
        "carbs": 34.0,
        "fat": 5.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "flattened rice (poha)", "quantity": "1.5", "unit": "cups"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "mustard seeds", "quantity": "0.5", "unit": "tsp"},
            {"name": "turmeric powder", "quantity": "0.25", "unit": "tsp"},
            {"name": "peanuts", "quantity": "2", "unit": "tbsp"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "lemon juice", "quantity": "1", "unit": "tbsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Rinse poha in a colander under running water until softened. Drain and set aside.",
            "Heat oil in a pan. Add peanuts and fry until crunchy. Remove and set aside.",
            "In the same oil, add mustard seeds. Let them splutter.",
            "Add curry leaves and green chillies. Saute for 30 seconds.",
            "Add chopped onions and cook until soft.",
            "Add turmeric powder and mix well.",
            "Add the soaked poha and salt. Mix gently.",
            "Cook for 3-4 minutes on low flame, stirring occasionally.",
            "Add fried peanuts, lemon juice and coriander leaves. Toss and serve hot."
        ],
        "tags": ["quick", "popular", "healthy"]
    },

    {
        "name": "Aloo Paratha",
        "description": "Whole wheat flatbread stuffed with spiced mashed potato filling. A hearty and popular North Indian breakfast served with butter, yogurt and pickle.",
        "category": "breakfast",
        "cuisine": "north_indian",
        "diet_type": "vegetarian",
        "difficulty": "medium",
        "prep_time": 20,
        "cook_time": 20,
        "servings": 3,
        "calories": 310,
        "protein": 7.0,
        "carbs": 50.0,
        "fat": 9.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "whole wheat flour", "quantity": "2", "unit": "cups"},
            {"name": "potato", "quantity": "3", "unit": "medium"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "garam masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "cumin seeds", "quantity": "0.5", "unit": "tsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"},
            {"name": "butter", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "1", "unit": "tbsp"}
        ],
        "instructions": [
            "Knead wheat flour with water and little oil into a soft smooth dough. Rest for 20 min.",
            "Boil potatoes, peel and mash completely without lumps.",
            "Mix mashed potatoes with chopped onion, green chilli, coriander, cumin, garam masala and salt.",
            "Divide dough into balls. Roll one ball into a small circle.",
            "Place stuffing in center, gather edges and seal. Flatten gently.",
            "Roll out stuffed ball into a round paratha evenly.",
            "Heat a tawa on medium heat. Cook paratha for 2 minutes per side.",
            "Apply butter and cook until golden brown spots appear on both sides.",
            "Serve hot with yogurt, butter and pickle."
        ],
        "tags": ["popular", "north-indian", "comfort food"]
    },

    # =========================================================
    # 🍛 LUNCH (12 recipes)
    # =========================================================

    {
        "name": "Sambar Rice",
        "description": "A wholesome South Indian meal of steamed rice mixed with sambar — a tangy lentil and vegetable stew. Comfort food at its best.",
        "category": "lunch",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 15,
        "cook_time": 40,
        "servings": 4,
        "calories": 320,
        "protein": 10.0,
        "carbs": 58.0,
        "fat": 6.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "toor dal", "quantity": "0.5", "unit": "cup"},
            {"name": "rice", "quantity": "2", "unit": "cups"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "drumstick", "quantity": "2", "unit": "pieces"},
            {"name": "brinjal", "quantity": "1", "unit": "medium"},
            {"name": "sambar powder", "quantity": "2", "unit": "tbsp"},
            {"name": "tamarind", "quantity": "1", "unit": "small ball"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "mustard seeds", "quantity": "1", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "2", "unit": "sprigs"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"}
        ],
        "instructions": [
            "Pressure cook toor dal with turmeric and water until soft. Mash well.",
            "Soak tamarind in warm water for 10 min and extract juice.",
            "Cook rice separately and keep warm.",
            "In a pot, heat oil and add mustard seeds. Let them splutter.",
            "Add curry leaves, onion and tomatoes. Cook until soft.",
            "Add vegetables (drumstick, brinjal) and saute for 3 minutes.",
            "Add tamarind juice, sambar powder and salt. Bring to boil.",
            "Add mashed dal and mix. Simmer for 15 minutes until thick.",
            "Adjust consistency with water. Serve hot over rice with papad."
        ],
        "tags": ["popular", "south-indian", "healthy", "comfort food"]
    },

    {
        "name": "Lemon Rice",
        "description": "Tangy and aromatic South Indian rice dish tempered with mustard seeds, curry leaves, peanuts and fresh lemon juice. Quick to make with leftover rice.",
        "category": "lunch",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 15,
        "servings": 3,
        "calories": 280,
        "protein": 6.0,
        "carbs": 50.0,
        "fat": 7.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "cooked rice", "quantity": "3", "unit": "cups"},
            {"name": "lemon", "quantity": "2", "unit": "pieces"},
            {"name": "peanuts", "quantity": "3", "unit": "tbsp"},
            {"name": "mustard seeds", "quantity": "1", "unit": "tsp"},
            {"name": "chana dal", "quantity": "1", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "curry leaves", "quantity": "2", "unit": "sprigs"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Spread cooked rice on a plate and let it cool slightly.",
            "Heat oil in a pan. Fry peanuts until crunchy. Remove and set aside.",
            "In the same oil, add mustard seeds and let them splutter.",
            "Add chana dal and fry until golden.",
            "Add curry leaves, green chillies and turmeric. Stir for 30 seconds.",
            "Add rice and salt. Mix gently without breaking the grains.",
            "Turn off flame and squeeze fresh lemon juice over the rice.",
            "Add fried peanuts and toss well.",
            "Serve with papad, pickle or yogurt."
        ],
        "tags": ["quick", "south-indian", "popular"]
    },

    {
        "name": "Curd Rice",
        "description": "A cooling South Indian dish of soft cooked rice mixed with yogurt and tempered with mustard seeds, ginger and curry leaves. Perfect for hot summer days.",
        "category": "lunch",
        "cuisine": "south_indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 10,
        "servings": 2,
        "calories": 250,
        "protein": 7.0,
        "carbs": 42.0,
        "fat": 5.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "cooked rice", "quantity": "2", "unit": "cups"},
            {"name": "yogurt (curd)", "quantity": "1", "unit": "cup"},
            {"name": "milk", "quantity": "0.25", "unit": "cup"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "green chilli", "quantity": "1", "unit": "piece"},
            {"name": "mustard seeds", "quantity": "0.5", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "pomegranate", "quantity": "2", "unit": "tbsp"},
            {"name": "coriander leaves", "quantity": "1", "unit": "tbsp"},
            {"name": "oil", "quantity": "1", "unit": "tsp"},
            {"name": "salt", "quantity": "0.75", "unit": "tsp"}
        ],
        "instructions": [
            "Mash warm cooked rice lightly with a spoon.",
            "Mix in yogurt and milk while rice is still slightly warm.",
            "Add salt and mix until creamy. Adjust consistency with more yogurt.",
            "Heat oil in a small pan. Add mustard seeds and let them splutter.",
            "Add curry leaves, chopped ginger and green chilli. Saute 30 seconds.",
            "Pour tempering over the curd rice and mix.",
            "Garnish with pomegranate seeds and coriander leaves.",
            "Serve chilled or at room temperature with pickle and papad."
        ],
        "tags": ["popular", "south-indian", "comfort food", "healthy"]
    },

    {
        "name": "Tamil Nadu Chicken Biryani",
        "description": "Aromatic and spicy Tamil-style chicken biryani cooked with seeraga samba rice, whole spices and a generous amount of onions and tomatoes.",
        "category": "lunch",
        "cuisine": "south_indian",
        "diet_type": "non_vegetarian",
        "difficulty": "hard",
        "prep_time": 30,
        "cook_time": 60,
        "servings": 5,
        "calories": 520,
        "protein": 28.0,
        "carbs": 65.0,
        "fat": 16.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "seeraga samba rice", "quantity": "2", "unit": "cups"},
            {"name": "chicken", "quantity": "500", "unit": "grams"},
            {"name": "onion", "quantity": "3", "unit": "large"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "yogurt", "quantity": "0.5", "unit": "cup"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "biryani masala", "quantity": "2", "unit": "tbsp"},
            {"name": "bay leaf", "quantity": "2", "unit": "pieces"},
            {"name": "cardamom", "quantity": "3", "unit": "pieces"},
            {"name": "cloves", "quantity": "4", "unit": "pieces"},
            {"name": "cinnamon", "quantity": "1", "unit": "inch"},
            {"name": "mint leaves", "quantity": "0.5", "unit": "cup"},
            {"name": "coriander leaves", "quantity": "0.5", "unit": "cup"},
            {"name": "oil", "quantity": "4", "unit": "tbsp"},
            {"name": "salt", "quantity": "2", "unit": "tsp"}
        ],
        "instructions": [
            "Wash and soak seeraga samba rice for 30 minutes. Drain.",
            "Marinate chicken with yogurt, ginger garlic paste, biryani masala and salt for 30 minutes.",
            "Heat oil in a heavy bottom pot. Add whole spices (bay leaf, cardamom, cloves, cinnamon).",
            "Add sliced onions and fry until deep golden brown — this is key to Tamil biryani flavor.",
            "Add tomatoes and cook until mushy.",
            "Add marinated chicken and cook on high flame for 5 minutes.",
            "Add mint and coriander leaves. Mix well.",
            "Add soaked rice and 3 cups water. Season with salt.",
            "Bring to boil, then reduce flame, cover tightly and cook for 20-25 minutes.",
            "Gently fluff with fork. Serve hot with raita and brinjal curry."
        ],
        "tags": ["popular", "south-indian", "spicy", "festive"]
    },

    {
        "name": "Hyderabadi Chicken Biryani",
        "description": "The iconic layered Hyderabadi dum biryani with long grain basmati rice, slow-cooked chicken in rich spices, saffron and crispy fried onions.",
        "category": "lunch",
        "cuisine": "indian",
        "diet_type": "non_vegetarian",
        "difficulty": "hard",
        "prep_time": 45,
        "cook_time": 60,
        "servings": 6,
        "calories": 560,
        "protein": 30.0,
        "carbs": 68.0,
        "fat": 18.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "basmati rice", "quantity": "3", "unit": "cups"},
            {"name": "chicken", "quantity": "750", "unit": "grams"},
            {"name": "fried onions (birista)", "quantity": "1", "unit": "cup"},
            {"name": "yogurt", "quantity": "1", "unit": "cup"},
            {"name": "ginger garlic paste", "quantity": "3", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "2", "unit": "tsp"},
            {"name": "saffron", "quantity": "a pinch", "unit": ""},
            {"name": "warm milk", "quantity": "2", "unit": "tbsp"},
            {"name": "biryani masala", "quantity": "2", "unit": "tbsp"},
            {"name": "mint leaves", "quantity": "1", "unit": "cup"},
            {"name": "ghee", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "2", "unit": "tsp"}
        ],
        "instructions": [
            "Marinate chicken with yogurt, ginger garlic paste, red chilli, biryani masala, half fried onions and salt. Marinate for 2 hours.",
            "Soak saffron in warm milk for 15 minutes.",
            "Parboil basmati rice with whole spices until 70% cooked. Drain.",
            "In a heavy pot, spread marinated chicken at the bottom.",
            "Layer half the parboiled rice over the chicken.",
            "Sprinkle half fried onions, mint leaves and saffron milk.",
            "Add remaining rice and repeat the layering.",
            "Drizzle ghee on top. Seal the pot with tight lid or dough.",
            "Cook on dum — high flame for 5 minutes, then very low for 25-30 minutes.",
            "Gently mix from the sides without disturbing layers. Serve with raita."
        ],
        "tags": ["popular", "spicy", "festive", "high-protein"]
    },

    {
        "name": "Mutton Biryani",
        "description": "Rich and flavorful mutton biryani slow-cooked with tender mutton pieces, aromatic basmati rice and whole spices. A royal Indian festive dish.",
        "category": "lunch",
        "cuisine": "indian",
        "diet_type": "non_vegetarian",
        "difficulty": "hard",
        "prep_time": 45,
        "cook_time": 90,
        "servings": 5,
        "calories": 590,
        "protein": 32.0,
        "carbs": 62.0,
        "fat": 22.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "basmati rice", "quantity": "2.5", "unit": "cups"},
            {"name": "mutton", "quantity": "600", "unit": "grams"},
            {"name": "onion", "quantity": "3", "unit": "large"},
            {"name": "yogurt", "quantity": "1", "unit": "cup"},
            {"name": "ginger garlic paste", "quantity": "3", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "2", "unit": "tsp"},
            {"name": "garam masala", "quantity": "1", "unit": "tsp"},
            {"name": "saffron", "quantity": "a pinch", "unit": ""},
            {"name": "mint leaves", "quantity": "1", "unit": "cup"},
            {"name": "ghee", "quantity": "4", "unit": "tbsp"},
            {"name": "whole spices", "quantity": "1", "unit": "set"},
            {"name": "salt", "quantity": "2", "unit": "tsp"}
        ],
        "instructions": [
            "Marinate mutton with yogurt, ginger garlic paste, red chilli, garam masala and salt. Marinate minimum 2 hours or overnight.",
            "Fry sliced onions in ghee until deep golden brown. Drain and set aside.",
            "Cook marinated mutton in a pressure cooker for 4-5 whistles until tender.",
            "Parboil basmati rice with whole spices until 70% cooked. Drain.",
            "In a heavy pot, layer cooked mutton with gravy at the bottom.",
            "Add a layer of parboiled rice. Sprinkle fried onions and mint.",
            "Repeat layers. Drizzle saffron milk and ghee on top.",
            "Seal with tight lid and cook on dum for 25-30 minutes on very low flame.",
            "Rest for 10 minutes before opening. Serve with raita and salan."
        ],
        "tags": ["popular", "festive", "spicy", "high-protein"]
    },

    {
        "name": "Egg Biryani",
        "description": "Flavorful egg biryani with hard-boiled eggs cooked in spicy masala layered with fragrant basmati rice. A quick alternative to meat biryani.",
        "category": "lunch",
        "cuisine": "indian",
        "diet_type": "non_vegetarian",
        "difficulty": "medium",
        "prep_time": 20,
        "cook_time": 40,
        "servings": 3,
        "calories": 420,
        "protein": 18.0,
        "carbs": 62.0,
        "fat": 12.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "basmati rice", "quantity": "2", "unit": "cups"},
            {"name": "egg", "quantity": "6", "unit": "pieces"},
            {"name": "onion", "quantity": "2", "unit": "large"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "biryani masala", "quantity": "2", "unit": "tbsp"},
            {"name": "mint leaves", "quantity": "0.5", "unit": "cup"},
            {"name": "yogurt", "quantity": "0.5", "unit": "cup"},
            {"name": "oil", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"}
        ],
        "instructions": [
            "Hard boil eggs, peel and make shallow cuts on them. Set aside.",
            "Wash and soak basmati rice for 20 minutes. Parboil until 70% cooked.",
            "Heat oil. Fry onions until golden. Add ginger garlic paste and fry.",
            "Add tomatoes and cook until oil separates.",
            "Add biryani masala, yogurt and salt. Mix well.",
            "Shallow fry the boiled eggs in this masala until lightly coated.",
            "In a pot, layer rice and egg masala alternately.",
            "Sprinkle mint and cover tightly. Cook on low flame for 20 minutes on dum.",
            "Fluff gently and serve with raita."
        ],
        "tags": ["popular", "high-protein", "spicy"]
    },

    {
        "name": "Fish Curry Rice",
        "description": "Traditional South Indian fish curry made with coconut milk, tamarind and aromatic spices, served over steamed rice. A coastal Tamil Nadu specialty.",
        "category": "lunch",
        "cuisine": "south_indian",
        "diet_type": "non_vegetarian",
        "difficulty": "medium",
        "prep_time": 15,
        "cook_time": 30,
        "servings": 4,
        "calories": 380,
        "protein": 26.0,
        "carbs": 42.0,
        "fat": 12.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "fish (Seer/Tilapia)", "quantity": "500", "unit": "grams"},
            {"name": "coconut milk", "quantity": "1", "unit": "cup"},
            {"name": "tamarind", "quantity": "1", "unit": "lemon-size"},
            {"name": "onion", "quantity": "2", "unit": "medium"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "red chilli powder", "quantity": "2", "unit": "tsp"},
            {"name": "coriander powder", "quantity": "1", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "2", "unit": "sprigs"},
            {"name": "mustard seeds", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"},
            {"name": "cooked rice", "quantity": "4", "unit": "cups"}
        ],
        "instructions": [
            "Clean fish pieces and marinate with turmeric and salt for 15 minutes.",
            "Extract tamarind juice from soaked tamarind.",
            "Heat oil in a clay pot or pan. Add mustard seeds and curry leaves.",
            "Add onions and fry until golden.",
            "Add tomatoes and cook until mushy.",
            "Add red chilli powder, coriander powder and cook until oil separates.",
            "Pour tamarind juice and bring to boil. Cook for 5 minutes.",
            "Add fish pieces gently. Simmer on low flame for 10 minutes.",
            "Add coconut milk and simmer for 5 more minutes. Do not boil after adding coconut milk.",
            "Serve hot over steamed rice with papad."
        ],
        "tags": ["popular", "south-indian", "spicy", "high-protein"]
    },

    {
        "name": "Veg Fried Rice",
        "description": "Chinese-style fried rice loaded with colorful vegetables, soy sauce and sesame oil. A quick and popular one-pot meal.",
        "category": "lunch",
        "cuisine": "chinese",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 3,
        "calories": 310,
        "protein": 7.0,
        "carbs": 55.0,
        "fat": 7.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "cooked rice (day old)", "quantity": "3", "unit": "cups"},
            {"name": "carrot", "quantity": "1", "unit": "medium"},
            {"name": "capsicum", "quantity": "1", "unit": "medium"},
            {"name": "spring onion", "quantity": "3", "unit": "stalks"},
            {"name": "garlic", "quantity": "4", "unit": "cloves"},
            {"name": "soy sauce", "quantity": "2", "unit": "tbsp"},
            {"name": "sesame oil", "quantity": "1", "unit": "tsp"},
            {"name": "vinegar", "quantity": "1", "unit": "tsp"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "0.5", "unit": "tsp"}
        ],
        "instructions": [
            "Use day-old cooked rice for best results. Break any lumps.",
            "Chop all vegetables into small, uniform pieces.",
            "Heat oil in a wok on very high flame.",
            "Add minced garlic and stir-fry for 30 seconds.",
            "Add carrots and stir-fry for 2 minutes.",
            "Add capsicum and stir-fry for 1 minute.",
            "Add rice and spread evenly in the wok. Let it sit for 1 minute.",
            "Add soy sauce, vinegar and black pepper. Toss well on high flame.",
            "Drizzle sesame oil, garnish with spring onions and serve hot."
        ],
        "tags": ["quick", "popular", "street food"]
    },

    {
        "name": "Pasta Primavera",
        "description": "Italian pasta tossed with fresh seasonal vegetables in olive oil and garlic. A light, colorful and healthy Mediterranean dish.",
        "category": "lunch",
        "cuisine": "italian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 2,
        "calories": 340,
        "protein": 10.0,
        "carbs": 58.0,
        "fat": 9.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "pasta (penne or fusilli)", "quantity": "200", "unit": "grams"},
            {"name": "broccoli", "quantity": "1", "unit": "cup"},
            {"name": "cherry tomatoes", "quantity": "10", "unit": "pieces"},
            {"name": "zucchini", "quantity": "1", "unit": "medium"},
            {"name": "capsicum", "quantity": "1", "unit": "medium"},
            {"name": "garlic", "quantity": "4", "unit": "cloves"},
            {"name": "olive oil", "quantity": "3", "unit": "tbsp"},
            {"name": "italian herbs", "quantity": "1", "unit": "tsp"},
            {"name": "parmesan cheese", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"}
        ],
        "instructions": [
            "Boil pasta in salted water until al dente (firm to bite). Drain and reserve 1/4 cup pasta water.",
            "Cut all vegetables into bite-size pieces.",
            "Heat olive oil in a large pan. Add minced garlic and saute until fragrant.",
            "Add broccoli and zucchini. Cook for 3-4 minutes.",
            "Add capsicum and cherry tomatoes. Cook for 2 minutes.",
            "Add cooked pasta and toss well.",
            "Add Italian herbs, salt and pepper. Add pasta water if dry.",
            "Serve garnished with parmesan cheese and fresh basil."
        ],
        "tags": ["healthy", "low-calorie"]
    },

    {
        "name": "Palak Paneer",
        "description": "Creamy pureed spinach gravy with soft paneer cubes. A nutritious and popular North Indian dish rich in iron and protein.",
        "category": "lunch",
        "cuisine": "north_indian",
        "diet_type": "vegetarian",
        "difficulty": "medium",
        "prep_time": 15,
        "cook_time": 25,
        "servings": 3,
        "calories": 290,
        "protein": 14.0,
        "carbs": 18.0,
        "fat": 18.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "spinach (palak)", "quantity": "4", "unit": "cups"},
            {"name": "paneer", "quantity": "200", "unit": "grams"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "tomato", "quantity": "1", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "1", "unit": "tbsp"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "cream", "quantity": "2", "unit": "tbsp"},
            {"name": "garam masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "cumin seeds", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Blanch spinach in boiling water for 2 minutes. Transfer to ice water immediately.",
            "Blend blanched spinach and green chillies to a smooth puree. Set aside.",
            "Cut paneer into cubes. Lightly fry in oil until golden. Set aside.",
            "In same pan, add cumin seeds. Add onions and fry until golden.",
            "Add ginger garlic paste and cook for 2 minutes.",
            "Add tomatoes and cook until oil separates.",
            "Add spinach puree and mix well. Cook for 5 minutes.",
            "Add garam masala, salt and fried paneer cubes.",
            "Simmer for 5 minutes. Add cream and stir gently.",
            "Serve hot with roti or naan."
        ],
        "tags": ["popular", "north-indian", "healthy", "high-protein"]
    },

    # =========================================================
    # 🌙 DINNER (10 recipes)
    # =========================================================

    {
        "name": "Chapati with Dal",
        "description": "Soft whole wheat flatbreads served with comforting dal — a simple, nourishing everyday Indian dinner that never gets old.",
        "category": "dinner",
        "cuisine": "indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 3,
        "calories": 290,
        "protein": 10.0,
        "carbs": 50.0,
        "fat": 6.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "whole wheat flour", "quantity": "2", "unit": "cups"},
            {"name": "toor dal", "quantity": "0.5", "unit": "cup"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "tomato", "quantity": "1", "unit": "medium"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "mustard seeds", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "water", "quantity": "as needed", "unit": ""}
        ],
        "instructions": [
            "Knead wheat flour with water and a pinch of salt into soft dough. Cover and rest 20 min.",
            "Pressure cook dal with turmeric, water and salt until soft.",
            "Heat oil, add mustard seeds, onions and tomatoes. Cook until soft.",
            "Add cooked dal to the tempering. Simmer for 10 minutes.",
            "Divide dough into equal balls. Roll each into thin round chapati.",
            "Heat a dry tawa on medium-high flame.",
            "Cook chapati for 1 minute per side, pressing edges to puff up.",
            "Apply ghee if desired. Serve hot with dal and pickle."
        ],
        "tags": ["popular", "healthy", "comfort food", "quick"]
    },

    {
        "name": "Egg Curry",
        "description": "Hard boiled eggs simmered in a spicy, tangy onion-tomato masala curry. A quick, protein-rich dinner favorite across Tamil Nadu.",
        "category": "dinner",
        "cuisine": "south_indian",
        "diet_type": "non_vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 3,
        "calories": 280,
        "protein": 16.0,
        "carbs": 15.0,
        "fat": 16.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "egg", "quantity": "6", "unit": "pieces"},
            {"name": "onion", "quantity": "2", "unit": "large"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "1.5", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "1.5", "unit": "tsp"},
            {"name": "coriander powder", "quantity": "1", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "garam masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "oil", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"}
        ],
        "instructions": [
            "Hard boil eggs for 10 minutes, peel and make shallow cuts on each egg.",
            "Heat oil in a pan. Shallow fry eggs until lightly browned. Remove and set aside.",
            "In same oil, add curry leaves and chopped onions. Fry until golden.",
            "Add ginger garlic paste and fry for 2 minutes.",
            "Add tomatoes and cook until oil separates.",
            "Add red chilli, coriander powder, turmeric and garam masala. Mix well.",
            "Add 1 cup water and bring to boil.",
            "Add fried eggs gently and simmer on low flame for 10 minutes.",
            "Garnish with coriander leaves. Serve with rice or chapati."
        ],
        "tags": ["popular", "south-indian", "quick", "high-protein"]
    },

    {
        "name": "Chicken Curry",
        "description": "A classic South Indian chicken curry with coconut, spices and a rich onion-tomato base. Served with rice or parotta, this is a beloved Tamil family recipe.",
        "category": "dinner",
        "cuisine": "south_indian",
        "diet_type": "non_vegetarian",
        "difficulty": "medium",
        "prep_time": 20,
        "cook_time": 40,
        "servings": 4,
        "calories": 380,
        "protein": 28.0,
        "carbs": 14.0,
        "fat": 22.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "chicken", "quantity": "500", "unit": "grams"},
            {"name": "onion", "quantity": "2", "unit": "large"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "2", "unit": "tsp"},
            {"name": "coriander powder", "quantity": "2", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "garam masala", "quantity": "1", "unit": "tsp"},
            {"name": "coconut (grated)", "quantity": "0.5", "unit": "cup"},
            {"name": "curry leaves", "quantity": "2", "unit": "sprigs"},
            {"name": "oil", "quantity": "4", "unit": "tbsp"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"}
        ],
        "instructions": [
            "Clean and cut chicken into pieces. Marinate with turmeric and salt.",
            "Grind grated coconut to a fine paste with a little water. Set aside.",
            "Heat oil in a heavy pan. Add curry leaves and sliced onions.",
            "Fry onions until deep golden brown.",
            "Add ginger garlic paste and fry for 2-3 minutes until raw smell goes.",
            "Add tomatoes and cook until oil separates from masala.",
            "Add red chilli, coriander powder and mix. Cook for 2 minutes.",
            "Add chicken pieces and fry on high flame for 5 minutes.",
            "Add coconut paste and 1 cup water. Mix well.",
            "Cover and cook on medium flame for 20-25 minutes until chicken is tender.",
            "Add garam masala and simmer for 5 more minutes. Serve with rice or parotta."
        ],
        "tags": ["popular", "south-indian", "spicy", "high-protein"]
    },

    {
        "name": "Dal Makhani",
        "description": "A rich, creamy and slow-cooked North Indian dal made with black lentils and kidney beans simmered overnight with butter and cream.",
        "category": "dinner",
        "cuisine": "north_indian",
        "diet_type": "vegetarian",
        "difficulty": "medium",
        "prep_time": 480,
        "cook_time": 60,
        "servings": 4,
        "calories": 320,
        "protein": 14.0,
        "carbs": 38.0,
        "fat": 14.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "black urad dal (whole)", "quantity": "1", "unit": "cup"},
            {"name": "kidney beans (rajma)", "quantity": "0.25", "unit": "cup"},
            {"name": "butter", "quantity": "3", "unit": "tbsp"},
            {"name": "cream", "quantity": "3", "unit": "tbsp"},
            {"name": "onion", "quantity": "1", "unit": "large"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "1", "unit": "tsp"},
            {"name": "garam masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"}
        ],
        "instructions": [
            "Soak black dal and rajma overnight in water.",
            "Pressure cook dal and rajma with salt and water for 8-10 whistles until very soft.",
            "Heat butter in a pan. Add onions and fry until golden brown.",
            "Add ginger garlic paste and cook for 2 minutes.",
            "Add tomatoes and cook until butter separates.",
            "Add red chilli powder and garam masala. Mix well.",
            "Add cooked dal to the masala. Mix and mash slightly.",
            "Simmer on very low flame for 30-40 minutes, stirring occasionally.",
            "Add cream and mix gently. Adjust salt.",
            "Serve hot garnished with cream and butter with naan or roti."
        ],
        "tags": ["popular", "north-indian", "comfort food", "high-protein"]
    },

    {
        "name": "Grilled Chicken",
        "description": "Juicy and flavorful grilled chicken marinated in herbs, garlic and lemon. A protein-rich, healthy and low-carb dinner option.",
        "category": "dinner",
        "cuisine": "continental",
        "diet_type": "non_vegetarian",
        "difficulty": "easy",
        "prep_time": 30,
        "cook_time": 20,
        "servings": 2,
        "calories": 280,
        "protein": 38.0,
        "carbs": 2.0,
        "fat": 12.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "chicken breast", "quantity": "400", "unit": "grams"},
            {"name": "olive oil", "quantity": "2", "unit": "tbsp"},
            {"name": "garlic", "quantity": "4", "unit": "cloves"},
            {"name": "lemon", "quantity": "1", "unit": "piece"},
            {"name": "oregano", "quantity": "1", "unit": "tsp"},
            {"name": "paprika", "quantity": "1", "unit": "tsp"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "mixed herbs", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Pound chicken breasts to even thickness for uniform cooking.",
            "Mix olive oil, minced garlic, lemon juice, oregano, paprika, herbs, salt and pepper.",
            "Coat chicken well with marinade. Marinate for minimum 30 minutes (or overnight).",
            "Preheat grill or grill pan to high heat.",
            "Oil the grill grates lightly.",
            "Grill chicken for 6-7 minutes on each side without moving.",
            "Check internal temperature should reach 75°C.",
            "Rest chicken for 5 minutes before slicing.",
            "Serve with grilled vegetables or salad and lemon wedges."
        ],
        "tags": ["healthy", "high-protein", "low-calorie"]
    },

    {
        "name": "Veg Noodles",
        "description": "Stir-fried Indo-Chinese noodles with colorful vegetables and sauces. A quick, popular and filling dinner for all ages.",
        "category": "dinner",
        "cuisine": "chinese",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 2,
        "calories": 350,
        "protein": 9.0,
        "carbs": 60.0,
        "fat": 8.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "hakka noodles", "quantity": "200", "unit": "grams"},
            {"name": "carrot", "quantity": "1", "unit": "medium"},
            {"name": "capsicum", "quantity": "1", "unit": "medium"},
            {"name": "cabbage", "quantity": "1", "unit": "cup"},
            {"name": "spring onion", "quantity": "3", "unit": "stalks"},
            {"name": "soy sauce", "quantity": "2", "unit": "tbsp"},
            {"name": "chilli sauce", "quantity": "1", "unit": "tbsp"},
            {"name": "vinegar", "quantity": "1", "unit": "tsp"},
            {"name": "garlic", "quantity": "4", "unit": "cloves"},
            {"name": "sesame oil", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "0.5", "unit": "tsp"}
        ],
        "instructions": [
            "Boil noodles in salted water until just cooked (al dente). Drain and toss with little oil.",
            "Julienne all vegetables into thin strips.",
            "Heat oil in a wok on very high flame.",
            "Add minced garlic and stir-fry for 30 seconds.",
            "Add carrots and cabbage. Stir-fry for 2 minutes on high flame.",
            "Add capsicum. Stir-fry for 1 minute.",
            "Add noodles and toss everything together.",
            "Add soy sauce, chilli sauce, vinegar and salt. Toss on high flame for 2 minutes.",
            "Drizzle sesame oil. Garnish with spring onions and serve immediately."
        ],
        "tags": ["quick", "popular", "street food"]
    },

    {
        "name": "Tomato Soup",
        "description": "Smooth, velvety tomato soup made with fresh tomatoes, garlic and cream. A simple yet comforting continental dinner starter.",
        "category": "dinner",
        "cuisine": "continental",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 2,
        "calories": 140,
        "protein": 3.0,
        "carbs": 18.0,
        "fat": 6.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "tomato", "quantity": "6", "unit": "large"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "garlic", "quantity": "4", "unit": "cloves"},
            {"name": "butter", "quantity": "1", "unit": "tbsp"},
            {"name": "cream", "quantity": "2", "unit": "tbsp"},
            {"name": "sugar", "quantity": "1", "unit": "tsp"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "italian herbs", "quantity": "0.5", "unit": "tsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Roughly chop tomatoes, onion and garlic.",
            "Heat butter in a pot. Add garlic and onions. Saute for 3 minutes.",
            "Add tomatoes and cook on medium flame for 10-12 minutes until soft.",
            "Let it cool slightly, then blend to a smooth puree.",
            "Strain through a sieve back into the pot for a smooth soup.",
            "Add salt, pepper, sugar and herbs. Bring to gentle simmer.",
            "Adjust consistency with water if too thick.",
            "Serve hot with a swirl of cream and crusty bread."
        ],
        "tags": ["healthy", "low-calorie", "quick", "comfort food"]
    },

    {
        "name": "Prawn Masala",
        "description": "Juicy prawns cooked in a spicy South Indian masala with coconut and curry leaves. A coastal Tamil Nadu delicacy bursting with flavors.",
        "category": "dinner",
        "cuisine": "south_indian",
        "diet_type": "non_vegetarian",
        "difficulty": "medium",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 3,
        "calories": 260,
        "protein": 24.0,
        "carbs": 12.0,
        "fat": 14.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "prawns", "quantity": "400", "unit": "grams"},
            {"name": "onion", "quantity": "2", "unit": "medium"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "2", "unit": "tsp"},
            {"name": "coriander powder", "quantity": "1", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "garam masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "2", "unit": "sprigs"},
            {"name": "coconut (grated)", "quantity": "3", "unit": "tbsp"},
            {"name": "oil", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Clean and devein prawns. Marinate with turmeric and salt for 10 minutes.",
            "Heat oil in a pan. Add curry leaves and sliced onions. Fry until golden.",
            "Add ginger garlic paste and cook for 2 minutes.",
            "Add tomatoes and cook until mushy.",
            "Add red chilli, coriander powder and garam masala. Cook for 2 minutes.",
            "Add prawns and toss well on high flame for 3 minutes.",
            "Add grated coconut and mix.",
            "Cook on medium flame for 8-10 minutes until prawns are cooked and masala is thick.",
            "Garnish with coriander leaves. Serve hot with rice or parotta."
        ],
        "tags": ["popular", "south-indian", "spicy", "high-protein"]
    },

    {
        "name": "Khichdi",
        "description": "A comforting one-pot meal of rice and lentils cooked together with mild spices and ghee. The ultimate Indian comfort food for sick days and busy nights.",
        "category": "dinner",
        "cuisine": "indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 2,
        "calories": 270,
        "protein": 9.0,
        "carbs": 46.0,
        "fat": 6.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "rice", "quantity": "0.5", "unit": "cup"},
            {"name": "moong dal (split)", "quantity": "0.5", "unit": "cup"},
            {"name": "ghee", "quantity": "2", "unit": "tbsp"},
            {"name": "cumin seeds", "quantity": "1", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.5", "unit": "tsp"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "water", "quantity": "3", "unit": "cups"}
        ],
        "instructions": [
            "Wash rice and moong dal together until water runs clear.",
            "Heat ghee in pressure cooker. Add cumin seeds and let them splutter.",
            "Add grated ginger and turmeric. Saute for 30 seconds.",
            "Add washed rice and dal. Saute for 2 minutes.",
            "Add water, salt and black pepper. Mix well.",
            "Pressure cook for 3-4 whistles on medium flame.",
            "Let pressure release naturally. Open and mix well.",
            "Add more hot water if too thick. Adjust salt.",
            "Serve hot topped with extra ghee and papad on the side."
        ],
        "tags": ["healthy", "comfort food", "quick", "low-calorie"]
    },

    {
        "name": "Butter Chicken",
        "description": "The iconic North Indian curry with tender chicken pieces in a rich, creamy tomato-based sauce. Mildly spiced and loved by all ages worldwide.",
        "category": "dinner",
        "cuisine": "north_indian",
        "diet_type": "non_vegetarian",
        "difficulty": "medium",
        "prep_time": 30,
        "cook_time": 35,
        "servings": 4,
        "calories": 420,
        "protein": 28.0,
        "carbs": 16.0,
        "fat": 26.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "chicken", "quantity": "500", "unit": "grams"},
            {"name": "butter", "quantity": "4", "unit": "tbsp"},
            {"name": "cream", "quantity": "0.5", "unit": "cup"},
            {"name": "tomato", "quantity": "4", "unit": "medium"},
            {"name": "onion", "quantity": "1", "unit": "large"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "kashmiri red chilli powder", "quantity": "2", "unit": "tsp"},
            {"name": "garam masala", "quantity": "1", "unit": "tsp"},
            {"name": "kasuri methi (dried fenugreek)", "quantity": "1", "unit": "tsp"},
            {"name": "yogurt", "quantity": "0.25", "unit": "cup"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"}
        ],
        "instructions": [
            "Marinate chicken with yogurt, ginger garlic paste, kashmiri chilli and salt for 1 hour.",
            "Grill or pan-fry marinated chicken until cooked. Set aside.",
            "Heat butter in a pan. Add chopped onions and fry until golden.",
            "Add ginger garlic paste and cook for 2 minutes.",
            "Add tomatoes and cook until completely soft and mushy.",
            "Blend this mixture to a smooth sauce. Strain and return to pan.",
            "Add kashmiri chilli powder, garam masala and cook for 5 minutes.",
            "Add cooked chicken pieces and simmer for 10 minutes.",
            "Add cream and kasuri methi (crushed). Simmer for 5 minutes.",
            "Serve hot with butter naan or steamed rice."
        ],
        "tags": ["popular", "north-indian", "comfort food", "high-protein"]
    },

    # =========================================================
    # 🍟 SNACKS (10 recipes)
    # =========================================================

    {
        "name": "Samosa",
        "description": "Crispy golden triangular pastry filled with spiced potato and peas. The most popular Indian street snack enjoyed with mint chutney and tamarind sauce.",
        "category": "snack",
        "cuisine": "indian",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 30,
        "cook_time": 30,
        "servings": 4,
        "calories": 260,
        "protein": 5.0,
        "carbs": 36.0,
        "fat": 12.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "all purpose flour (maida)", "quantity": "2", "unit": "cups"},
            {"name": "potato", "quantity": "4", "unit": "medium"},
            {"name": "peas", "quantity": "0.5", "unit": "cup"},
            {"name": "ginger", "quantity": "1", "unit": "inch"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "cumin seeds", "quantity": "1", "unit": "tsp"},
            {"name": "garam masala", "quantity": "1", "unit": "tsp"},
            {"name": "amchur (dry mango powder)", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Mix maida, salt and oil into a firm dough. Cover and rest for 30 minutes.",
            "Boil and mash potatoes. Mix with peas, ginger, green chilli, cumin, garam masala, amchur and salt.",
            "Divide dough into equal portions. Roll each into an oval.",
            "Cut oval in half. Shape each half into a cone and seal the edge with water.",
            "Fill cone with potato stuffing. Seal the top edge firmly.",
            "Heat oil in a deep pan on medium heat (not very hot).",
            "Fry samosas on medium-low flame for 8-10 minutes until golden and crispy.",
            "Do not fry on high heat — this will keep them crispy inside too.",
            "Drain on paper towel. Serve hot with mint chutney and tamarind sauce."
        ],
        "tags": ["popular", "street food", "spicy"]
    },

    {
        "name": "Onion Pakoda",
        "description": "Crispy fried fritters made with thinly sliced onions dipped in spiced chickpea flour batter. The perfect monsoon and evening snack.",
        "category": "snack",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 3,
        "calories": 220,
        "protein": 6.0,
        "carbs": 28.0,
        "fat": 10.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "onion", "quantity": "3", "unit": "large"},
            {"name": "chickpea flour (besan)", "quantity": "1", "unit": "cup"},
            {"name": "green chilli", "quantity": "3", "unit": "pieces"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "red chilli powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "cumin seeds", "quantity": "0.5", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Thinly slice onions and add salt. Mix and let rest for 5 minutes until they release moisture.",
            "Add besan, red chilli powder, cumin, chopped green chilli, ginger and curry leaves.",
            "Mix well without adding water — the onion moisture is sufficient.",
            "If the batter is too dry, add 1-2 tbsp water only.",
            "Heat oil in a deep pan to 180°C.",
            "Drop small portions of batter into oil using fingers or spoon.",
            "Fry on medium flame for 4-5 minutes, turning occasionally until golden and crispy.",
            "Drain on paper towels. Serve hot with mint chutney or ketchup."
        ],
        "tags": ["popular", "south-indian", "street food", "quick"]
    },

    {
        "name": "Murukku",
        "description": "Traditional South Indian spiral-shaped crispy snack made from rice flour and urad dal flour. A festive favorite, especially during Diwali.",
        "category": "snack",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 15,
        "cook_time": 30,
        "servings": 6,
        "calories": 180,
        "protein": 4.0,
        "carbs": 28.0,
        "fat": 7.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "rice flour", "quantity": "2", "unit": "cups"},
            {"name": "urad dal flour", "quantity": "0.25", "unit": "cup"},
            {"name": "butter", "quantity": "1", "unit": "tbsp"},
            {"name": "sesame seeds", "quantity": "1", "unit": "tbsp"},
            {"name": "cumin seeds", "quantity": "1", "unit": "tsp"},
            {"name": "red chilli powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "asafoetida", "quantity": "a pinch", "unit": ""},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"}
        ],
        "instructions": [
            "Mix rice flour, urad dal flour, sesame seeds, cumin, red chilli, asafoetida and salt.",
            "Add soft butter and mix until crumbly.",
            "Add water gradually and knead into a soft, pliable dough.",
            "Fill murukku press with dough using star-shaped disc.",
            "Heat oil in a deep pan to 175°C.",
            "Press murukku directly into oil in circular motions or press on back of ladle first.",
            "Fry on medium flame for 3-4 minutes, turning once, until golden and crispy.",
            "Drain on paper towels. Cool completely before storing.",
            "Store in airtight container. Stays crispy for up to 2 weeks."
        ],
        "tags": ["popular", "south-indian", "festive", "street food"]
    },

    {
        "name": "Bread Pakoda",
        "description": "Bread slices stuffed with spiced potato filling, dipped in besan batter and deep fried until golden. A popular Indian street food and tea-time snack.",
        "category": "snack",
        "cuisine": "indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 15,
        "cook_time": 15,
        "servings": 3,
        "calories": 240,
        "protein": 6.0,
        "carbs": 32.0,
        "fat": 10.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "bread", "quantity": "8", "unit": "slices"},
            {"name": "potato", "quantity": "2", "unit": "medium"},
            {"name": "chickpea flour (besan)", "quantity": "1", "unit": "cup"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "cumin seeds", "quantity": "0.5", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.25", "unit": "tsp"},
            {"name": "red chilli powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Boil and mash potatoes. Mix with green chilli, cumin, coriander leaves and salt.",
            "Make a thick flowing batter with besan, turmeric, red chilli, salt and water.",
            "Spread potato filling on one bread slice and cover with another slice.",
            "Cut diagonally into triangles.",
            "Heat oil in a deep pan.",
            "Dip each stuffed bread triangle into besan batter, coating all sides.",
            "Fry in hot oil on medium flame for 3-4 minutes until golden and crispy.",
            "Drain on paper towel. Serve hot with mint chutney and ketchup."
        ],
        "tags": ["popular", "street food", "quick"]
    },

    {
        "name": "Aloo Tikki",
        "description": "Golden crispy potato patties seasoned with spices and shallow fried. A beloved North Indian street food, often served in chaat.",
        "category": "snack",
        "cuisine": "north_indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 15,
        "cook_time": 20,
        "servings": 3,
        "calories": 200,
        "protein": 4.0,
        "carbs": 32.0,
        "fat": 8.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "potato", "quantity": "4", "unit": "large"},
            {"name": "bread crumbs", "quantity": "3", "unit": "tbsp"},
            {"name": "corn flour", "quantity": "2", "unit": "tbsp"},
            {"name": "green chilli", "quantity": "2", "unit": "pieces"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "cumin powder", "quantity": "1", "unit": "tsp"},
            {"name": "garam masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"},
            {"name": "oil", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Boil potatoes, peel and mash completely. Let cool.",
            "Add bread crumbs, corn flour, green chilli, ginger, cumin, garam masala, coriander and salt.",
            "Mix well and form into a smooth dough-like mixture.",
            "Divide into equal portions and shape into flat round patties.",
            "Heat oil in a flat pan on medium heat.",
            "Place tikkis on pan and cook for 4-5 minutes until golden and crispy.",
            "Flip carefully and cook the other side for 3-4 minutes.",
            "Serve hot with mint chutney, tamarind chutney and yogurt."
        ],
        "tags": ["popular", "north-indian", "street food", "quick"]
    },

    {
        "name": "Sundal",
        "description": "A healthy and protein-rich South Indian boiled chickpea or lentil stir-fry with coconut, curry leaves and mustard seeds. A popular Navratri and temple offering.",
        "category": "snack",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 480,
        "cook_time": 15,
        "servings": 3,
        "calories": 180,
        "protein": 10.0,
        "carbs": 28.0,
        "fat": 4.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "chickpeas (white chana)", "quantity": "1", "unit": "cup"},
            {"name": "grated coconut", "quantity": "3", "unit": "tbsp"},
            {"name": "mustard seeds", "quantity": "1", "unit": "tsp"},
            {"name": "urad dal", "quantity": "1", "unit": "tsp"},
            {"name": "red chilli (dry)", "quantity": "2", "unit": "pieces"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "asafoetida", "quantity": "a pinch", "unit": ""},
            {"name": "oil", "quantity": "1", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"}
        ],
        "instructions": [
            "Soak chickpeas overnight in water.",
            "Pressure cook soaked chickpeas with salt and water for 5-6 whistles until tender.",
            "Drain excess water and set aside.",
            "Heat oil in a pan. Add mustard seeds and let them splutter.",
            "Add urad dal and fry until golden.",
            "Add dry red chilli and curry leaves. Saute for 30 seconds.",
            "Add a pinch of asafoetida.",
            "Add cooked chickpeas and mix well on medium flame for 3 minutes.",
            "Add grated coconut and toss gently.",
            "Serve warm as a snack or prasad."
        ],
        "tags": ["healthy", "south-indian", "high-protein", "festive", "low-calorie"]
    },

    {
        "name": "Sandwich",
        "description": "A classic vegetable sandwich with fresh cucumber, tomato, onion and cheese between toasted bread slices. A quick, easy and satisfying snack.",
        "category": "snack",
        "cuisine": "continental",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 5,
        "servings": 2,
        "calories": 250,
        "protein": 9.0,
        "carbs": 36.0,
        "fat": 8.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "bread", "quantity": "4", "unit": "slices"},
            {"name": "cucumber", "quantity": "1", "unit": "medium"},
            {"name": "tomato", "quantity": "1", "unit": "medium"},
            {"name": "onion", "quantity": "0.5", "unit": "medium"},
            {"name": "cheese slice", "quantity": "2", "unit": "pieces"},
            {"name": "butter", "quantity": "1", "unit": "tbsp"},
            {"name": "green chutney", "quantity": "2", "unit": "tbsp"},
            {"name": "black pepper", "quantity": "0.25", "unit": "tsp"},
            {"name": "salt", "quantity": "0.25", "unit": "tsp"}
        ],
        "instructions": [
            "Thinly slice cucumber, tomato and onion.",
            "Toast bread slices lightly in a toaster or on a dry tawa.",
            "Spread green chutney on one slice and butter on another.",
            "Layer cucumber, tomato and onion slices on one bread.",
            "Season with salt and pepper.",
            "Place cheese slice on top.",
            "Cover with the second bread slice.",
            "Cut diagonally and serve immediately with ketchup."
        ],
        "tags": ["quick", "popular", "low-calorie"]
    },

    {
        "name": "Spring Rolls",
        "description": "Crispy Chinese-style spring rolls stuffed with seasoned vegetables. Fried to golden perfection and served with sweet chilli sauce.",
        "category": "snack",
        "cuisine": "chinese",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 20,
        "cook_time": 20,
        "servings": 3,
        "calories": 230,
        "protein": 5.0,
        "carbs": 30.0,
        "fat": 10.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "spring roll sheets", "quantity": "10", "unit": "pieces"},
            {"name": "cabbage", "quantity": "2", "unit": "cups"},
            {"name": "carrot", "quantity": "1", "unit": "medium"},
            {"name": "capsicum", "quantity": "1", "unit": "medium"},
            {"name": "spring onion", "quantity": "3", "unit": "stalks"},
            {"name": "garlic", "quantity": "3", "unit": "cloves"},
            {"name": "soy sauce", "quantity": "2", "unit": "tbsp"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "cornflour", "quantity": "2", "unit": "tbsp"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"},
            {"name": "salt", "quantity": "0.5", "unit": "tsp"}
        ],
        "instructions": [
            "Shred cabbage and julienne carrot and capsicum.",
            "Heat 2 tbsp oil in a wok. Add garlic and stir-fry.",
            "Add all vegetables and stir-fry on high flame for 3-4 minutes.",
            "Add soy sauce, pepper and salt. Toss well. Let filling cool completely.",
            "Mix cornflour with 2 tbsp water to make a paste (for sealing).",
            "Place a spring roll sheet on flat surface. Add 2 tbsp filling in center.",
            "Roll tightly, folding in the sides. Seal the edge with cornflour paste.",
            "Heat oil in deep pan. Fry spring rolls on medium flame until golden crispy.",
            "Drain and serve hot with sweet chilli sauce."
        ],
        "tags": ["popular", "street food", "crispy"]
    },

    {
        "name": "French Fries",
        "description": "Golden crispy potato fries seasoned with salt. A universally loved snack that's perfect with any dipping sauce.",
        "category": "snack",
        "cuisine": "american",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 20,
        "cook_time": 15,
        "servings": 2,
        "calories": 300,
        "protein": 4.0,
        "carbs": 40.0,
        "fat": 15.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "potato", "quantity": "4", "unit": "large"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "black pepper", "quantity": "0.25", "unit": "tsp"},
            {"name": "paprika (optional)", "quantity": "0.25", "unit": "tsp"}
        ],
        "instructions": [
            "Peel and cut potatoes into uniform stick shapes.",
            "Soak in cold water for 30 minutes — this removes starch for crispiness.",
            "Drain and pat completely dry with paper towels.",
            "Heat oil to 160°C for first fry.",
            "Fry potatoes in batches for 5-6 minutes until pale and cooked but not browned. Drain.",
            "Increase oil temperature to 190°C.",
            "Fry the pre-cooked fries again for 2-3 minutes until golden and crispy.",
            "Drain immediately and season with salt, pepper and paprika.",
            "Serve hot with ketchup or mayo."
        ],
        "tags": ["popular", "quick", "street food"]
    },

    {
        "name": "Boiled Egg Chaat",
        "description": "Hard boiled eggs topped with spiced yogurt, tamarind chutney, chaat masala and coriander. A quick, protein-rich Indian snack.",
        "category": "snack",
        "cuisine": "indian",
        "diet_type": "non_vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 10,
        "servings": 2,
        "calories": 160,
        "protein": 12.0,
        "carbs": 10.0,
        "fat": 8.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "egg", "quantity": "4", "unit": "pieces"},
            {"name": "yogurt", "quantity": "3", "unit": "tbsp"},
            {"name": "tamarind chutney", "quantity": "2", "unit": "tbsp"},
            {"name": "mint chutney", "quantity": "2", "unit": "tbsp"},
            {"name": "chaat masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "red chilli powder", "quantity": "0.25", "unit": "tsp"},
            {"name": "coriander leaves", "quantity": "1", "unit": "tbsp"},
            {"name": "onion", "quantity": "0.5", "unit": "medium"}
        ],
        "instructions": [
            "Hard boil eggs for 10 minutes. Cool in ice water and peel.",
            "Cut eggs in half lengthwise.",
            "Place egg halves on a plate cut-side up.",
            "Whisk yogurt until smooth.",
            "Spoon yogurt over each egg half.",
            "Drizzle tamarind and mint chutney over yogurt.",
            "Sprinkle chaat masala and red chilli powder.",
            "Top with finely chopped onion and fresh coriander.",
            "Serve immediately."
        ],
        "tags": ["quick", "high-protein", "low-calorie"]
    },

    # =========================================================
    # 🧃 BEVERAGES (10 recipes)
    # =========================================================

    {
        "name": "Masala Chai",
        "description": "The beloved Indian spiced tea brewed with ginger, cardamom, cinnamon and cloves in milk. A comforting cup that energizes any time of day.",
        "category": "beverage",
        "cuisine": "indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 2,
        "cook_time": 10,
        "servings": 2,
        "calories": 90,
        "protein": 3.0,
        "carbs": 12.0,
        "fat": 3.5,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "milk", "quantity": "2", "unit": "cups"},
            {"name": "water", "quantity": "0.5", "unit": "cup"},
            {"name": "tea leaves", "quantity": "2", "unit": "tsp"},
            {"name": "sugar", "quantity": "2", "unit": "tsp"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "cardamom", "quantity": "3", "unit": "pods"},
            {"name": "cinnamon", "quantity": "0.5", "unit": "inch"},
            {"name": "cloves", "quantity": "2", "unit": "pieces"},
            {"name": "black pepper", "quantity": "2", "unit": "peppercorns"}
        ],
        "instructions": [
            "Crush ginger, cardamom, cinnamon, cloves and black pepper coarsely.",
            "Boil water in a saucepan. Add crushed spices.",
            "Simmer for 2 minutes to extract flavors.",
            "Add tea leaves and boil for 1 minute.",
            "Add milk and sugar. Stir well.",
            "Bring to a full boil, then simmer on low flame for 3-4 minutes.",
            "Strain into cups through a fine strainer.",
            "Serve hot with biscuits or snacks."
        ],
        "tags": ["popular", "quick", "comfort food", "low-calorie"]
    },

    {
        "name": "Filter Coffee",
        "description": "The iconic South Indian filter coffee made with freshly brewed decoction and frothy hot milk. A morning ritual across Tamil Nadu and Karnataka.",
        "category": "beverage",
        "cuisine": "south_indian",
        "diet_type": "vegetarian",
        "difficulty": "medium",
        "prep_time": 10,
        "cook_time": 10,
        "servings": 2,
        "calories": 80,
        "protein": 3.0,
        "carbs": 10.0,
        "fat": 3.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "coffee powder (filter grade)", "quantity": "3", "unit": "tsp"},
            {"name": "milk", "quantity": "2", "unit": "cups"},
            {"name": "sugar", "quantity": "2", "unit": "tsp"},
            {"name": "hot water", "quantity": "0.5", "unit": "cup"}
        ],
        "instructions": [
            "Place coffee powder in the upper compartment of a South Indian filter.",
            "Press lightly with the disc provided.",
            "Pour hot (not boiling) water over the coffee powder.",
            "Cover and let decoction drip into the lower compartment for 10-15 minutes.",
            "Heat milk and froth it by pouring between two tumblers from a height.",
            "Pour 2-3 tbsp of strong coffee decoction into a tumbler.",
            "Add hot frothed milk and sugar. Stir well.",
            "Pour between tumbler and davara (small bowl) 3-4 times to cool and froth.",
            "Serve in the traditional davara-tumbler set."
        ],
        "tags": ["popular", "south-indian", "quick", "low-calorie"]
    },

    {
        "name": "Mango Lassi",
        "description": "A thick, creamy and refreshing yogurt-based drink blended with fresh mango pulp and a hint of cardamom. The king of Indian summer beverages.",
        "category": "beverage",
        "cuisine": "indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 2,
        "calories": 180,
        "protein": 5.0,
        "carbs": 32.0,
        "fat": 4.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "mango", "quantity": "1", "unit": "large"},
            {"name": "yogurt", "quantity": "1", "unit": "cup"},
            {"name": "milk", "quantity": "0.5", "unit": "cup"},
            {"name": "sugar", "quantity": "2", "unit": "tbsp"},
            {"name": "cardamom powder", "quantity": "0.25", "unit": "tsp"},
            {"name": "ice cubes", "quantity": "5", "unit": "pieces"}
        ],
        "instructions": [
            "Peel mango and cut the pulp away from seed.",
            "Add mango pieces to a blender.",
            "Add yogurt, milk, sugar and cardamom powder.",
            "Blend until completely smooth and creamy.",
            "Taste and adjust sugar if needed.",
            "Add ice cubes and blend briefly.",
            "Pour into tall glasses.",
            "Garnish with a slice of mango or pinch of cardamom. Serve chilled."
        ],
        "tags": ["popular", "quick", "healthy", "no-cook"]
    },

    {
        "name": "Buttermilk (Mor)",
        "description": "A cooling and digestive South Indian spiced buttermilk made with yogurt, water, ginger, green chilli and curry leaves. Called Mor in Tamil.",
        "category": "beverage",
        "cuisine": "south_indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 2,
        "calories": 60,
        "protein": 3.0,
        "carbs": 6.0,
        "fat": 2.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "yogurt (curd)", "quantity": "1", "unit": "cup"},
            {"name": "water", "quantity": "2", "unit": "cups"},
            {"name": "ginger", "quantity": "0.25", "unit": "inch"},
            {"name": "green chilli", "quantity": "0.5", "unit": "piece"},
            {"name": "curry leaves", "quantity": "4", "unit": "leaves"},
            {"name": "coriander leaves", "quantity": "1", "unit": "tbsp"},
            {"name": "salt", "quantity": "0.5", "unit": "tsp"},
            {"name": "cumin powder", "quantity": "0.25", "unit": "tsp"}
        ],
        "instructions": [
            "Add yogurt to a blender or churner.",
            "Add water and blend until smooth and frothy.",
            "Finely chop or grind ginger, green chilli and coriander leaves.",
            "Add chopped ingredients, salt and cumin powder to the buttermilk.",
            "Mix well or blend for 10 seconds.",
            "Tear curry leaves and add to the buttermilk.",
            "Taste and adjust salt.",
            "Serve chilled or at room temperature. Best consumed fresh."
        ],
        "tags": ["popular", "south-indian", "healthy", "low-calorie", "quick", "no-cook"]
    },

    {
        "name": "Badam Milk",
        "description": "A rich and nourishing milk drink made with ground almonds, saffron, cardamom and sugar. A traditional South Indian bedtime drink full of nutrients.",
        "category": "beverage",
        "cuisine": "south_indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 10,
        "servings": 2,
        "calories": 200,
        "protein": 7.0,
        "carbs": 22.0,
        "fat": 9.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "almonds", "quantity": "15", "unit": "pieces"},
            {"name": "milk", "quantity": "2", "unit": "cups"},
            {"name": "sugar", "quantity": "2", "unit": "tbsp"},
            {"name": "saffron", "quantity": "a pinch", "unit": ""},
            {"name": "cardamom powder", "quantity": "0.25", "unit": "tsp"},
            {"name": "pistachio (for garnish)", "quantity": "5", "unit": "pieces"}
        ],
        "instructions": [
            "Soak almonds in hot water for 30 minutes. Peel the skin off.",
            "Blend peeled almonds with 4 tbsp milk to a fine, smooth paste.",
            "Soak saffron in 2 tbsp warm milk for 5 minutes.",
            "Heat remaining milk in a saucepan on medium flame.",
            "Add almond paste and stir continuously to avoid lumps.",
            "Add saffron milk, sugar and cardamom powder.",
            "Simmer on low flame for 5-7 minutes, stirring frequently.",
            "Serve hot or chilled, garnished with sliced pistachios."
        ],
        "tags": ["popular", "south-indian", "healthy", "high-protein"]
    },

    {
        "name": "Nimbu Pani",
        "description": "Fresh Indian lemonade made with lemon juice, sugar, salt and a pinch of cumin. A refreshing and energizing summer drink.",
        "category": "beverage",
        "cuisine": "indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 2,
        "calories": 50,
        "protein": 0.5,
        "carbs": 12.0,
        "fat": 0.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "lemon", "quantity": "3", "unit": "pieces"},
            {"name": "water", "quantity": "2", "unit": "cups"},
            {"name": "sugar", "quantity": "3", "unit": "tbsp"},
            {"name": "black salt", "quantity": "0.25", "unit": "tsp"},
            {"name": "cumin powder", "quantity": "0.25", "unit": "tsp"},
            {"name": "mint leaves", "quantity": "5", "unit": "leaves"},
            {"name": "ice cubes", "quantity": "8", "unit": "pieces"}
        ],
        "instructions": [
            "Squeeze juice from lemons into a jug.",
            "Add sugar and stir until completely dissolved.",
            "Add water, black salt and cumin powder. Mix well.",
            "Taste and adjust sweetness and saltiness.",
            "Add ice cubes and mint leaves.",
            "Stir well and pour into glasses.",
            "Garnish with lemon slices. Serve immediately."
        ],
        "tags": ["popular", "quick", "healthy", "low-calorie", "no-cook"]
    },

    {
        "name": "Banana Smoothie",
        "description": "A thick, creamy and nutritious smoothie made with ripe bananas, milk and honey. A quick and filling healthy breakfast or post-workout drink.",
        "category": "beverage",
        "cuisine": "continental",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 1,
        "calories": 220,
        "protein": 6.0,
        "carbs": 42.0,
        "fat": 3.5,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "banana", "quantity": "2", "unit": "pieces"},
            {"name": "milk", "quantity": "1", "unit": "cup"},
            {"name": "honey", "quantity": "1", "unit": "tbsp"},
            {"name": "vanilla extract", "quantity": "0.25", "unit": "tsp"},
            {"name": "ice cubes", "quantity": "4", "unit": "pieces"}
        ],
        "instructions": [
            "Peel and break bananas into chunks.",
            "Add banana, milk, honey and vanilla extract to blender.",
            "Blend on high speed for 60 seconds until completely smooth.",
            "Add ice cubes and blend for another 30 seconds.",
            "Taste and adjust sweetness with more honey if needed.",
            "Pour into a glass and serve immediately.",
            "Optional: sprinkle cinnamon powder on top."
        ],
        "tags": ["quick", "healthy", "popular", "no-cook"]
    },

    {
        "name": "Haldi Doodh",
        "description": "Golden milk or turmeric latte — warm milk with turmeric, black pepper, ginger and honey. A powerful anti-inflammatory Ayurvedic drink for immunity.",
        "category": "beverage",
        "cuisine": "indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 2,
        "cook_time": 8,
        "servings": 1,
        "calories": 130,
        "protein": 5.0,
        "carbs": 16.0,
        "fat": 5.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "milk", "quantity": "1.5", "unit": "cups"},
            {"name": "turmeric powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "ginger", "quantity": "0.25", "unit": "inch"},
            {"name": "black pepper", "quantity": "2", "unit": "peppercorns"},
            {"name": "honey", "quantity": "1", "unit": "tsp"},
            {"name": "cinnamon", "quantity": "0.25", "unit": "tsp"}
        ],
        "instructions": [
            "Heat milk in a small saucepan on low-medium flame.",
            "Grate ginger finely or crush along with black pepper.",
            "Add turmeric powder, grated ginger, black pepper and cinnamon to milk.",
            "Stir continuously and heat until milk just begins to simmer.",
            "Do not boil — just heat until steaming.",
            "Remove from heat and strain into a cup.",
            "Add honey and stir well. Do not add honey to very hot milk.",
            "Serve warm before bed for best benefits."
        ],
        "tags": ["healthy", "popular", "low-calorie", "quick"]
    },

    {
        "name": "Orange Juice",
        "description": "Freshly squeezed orange juice full of vitamin C, natural sweetness and refreshing citrus flavor. The healthiest way to start your morning.",
        "category": "beverage",
        "cuisine": "continental",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 2,
        "calories": 110,
        "protein": 1.5,
        "carbs": 25.0,
        "fat": 0.5,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "orange", "quantity": "6", "unit": "medium"},
            {"name": "sugar (optional)", "quantity": "1", "unit": "tsp"},
            {"name": "salt (optional)", "quantity": "1", "unit": "pinch"},
            {"name": "ice cubes", "quantity": "5", "unit": "pieces"}
        ],
        "instructions": [
            "Roll oranges on the counter with your palm to loosen the juice.",
            "Cut each orange in half.",
            "Squeeze using a juicer, citrus press or by hand.",
            "Strain juice through a sieve to remove seeds and pulp (optional — keep pulp for fiber).",
            "Add a pinch of salt to enhance the flavor.",
            "Add sugar only if oranges are very sour.",
            "Pour over ice cubes in glasses.",
            "Serve immediately for maximum vitamin content."
        ],
        "tags": ["healthy", "popular", "quick", "low-calorie", "no-cook"]
    },

    {
        "name": "Chocolate Milkshake",
        "description": "A thick, indulgent chocolate milkshake made with cocoa powder, ice cream and chilled milk. A treat loved by kids and adults alike.",
        "category": "beverage",
        "cuisine": "american",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 0,
        "servings": 2,
        "calories": 320,
        "protein": 7.0,
        "carbs": 48.0,
        "fat": 12.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "milk", "quantity": "1.5", "unit": "cups"},
            {"name": "chocolate ice cream", "quantity": "3", "unit": "scoops"},
            {"name": "cocoa powder", "quantity": "2", "unit": "tbsp"},
            {"name": "sugar", "quantity": "1", "unit": "tbsp"},
            {"name": "vanilla extract", "quantity": "0.25", "unit": "tsp"}
        ],
        "instructions": [
            "Chill milk in refrigerator for at least 30 minutes.",
            "Add cold milk, ice cream scoops, cocoa powder and sugar to blender.",
            "Add vanilla extract.",
            "Blend on high speed for 60 seconds until thick and frothy.",
            "Taste and adjust sweetness.",
            "Pour into tall chilled glasses.",
            "Serve immediately with a straw and whipped cream on top."
        ],
        "tags": ["popular", "quick", "comfort food", "no-cook"]
    },

    # =========================================================
    # 🥗 HEALTHY EXTRAS (8 recipes)
    # =========================================================

    {
        "name": "Quinoa Salad",
        "description": "A nutritious and colorful salad with quinoa, fresh vegetables and lemon-herb dressing. High in protein and perfect for a healthy meal.",
        "category": "lunch",
        "cuisine": "continental",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 2,
        "calories": 280,
        "protein": 12.0,
        "carbs": 40.0,
        "fat": 9.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "quinoa", "quantity": "0.5", "unit": "cup"},
            {"name": "cucumber", "quantity": "1", "unit": "medium"},
            {"name": "cherry tomatoes", "quantity": "10", "unit": "pieces"},
            {"name": "capsicum", "quantity": "0.5", "unit": "medium"},
            {"name": "onion", "quantity": "0.25", "unit": "medium"},
            {"name": "lemon", "quantity": "1", "unit": "piece"},
            {"name": "olive oil", "quantity": "2", "unit": "tbsp"},
            {"name": "coriander leaves", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "0.5", "unit": "tsp"},
            {"name": "black pepper", "quantity": "0.25", "unit": "tsp"}
        ],
        "instructions": [
            "Rinse quinoa well under cold water.",
            "Cook quinoa with 1 cup water and a pinch of salt. Bring to boil, simmer for 12 minutes, fluff.",
            "Cool cooked quinoa completely.",
            "Dice cucumber, tomatoes, capsicum and onion.",
            "Make dressing: whisk olive oil, lemon juice, salt and pepper.",
            "Combine cooled quinoa with all vegetables.",
            "Pour dressing over salad and toss gently.",
            "Garnish with fresh coriander leaves.",
            "Serve immediately or refrigerate for up to 2 hours."
        ],
        "tags": ["healthy", "high-protein", "low-calorie", "quick"]
    },

    {
        "name": "Grilled Fish",
        "description": "Lightly marinated fish fillet grilled with Indian spices, lemon and herbs. A high-protein, low-fat healthy dinner popular in coastal Tamil Nadu.",
        "category": "dinner",
        "cuisine": "south_indian",
        "diet_type": "non_vegetarian",
        "difficulty": "easy",
        "prep_time": 20,
        "cook_time": 15,
        "servings": 2,
        "calories": 220,
        "protein": 32.0,
        "carbs": 4.0,
        "fat": 8.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "fish fillet (seer/tilapia)", "quantity": "400", "unit": "grams"},
            {"name": "lemon", "quantity": "1", "unit": "piece"},
            {"name": "ginger garlic paste", "quantity": "1", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "1", "unit": "tsp"},
            {"name": "turmeric", "quantity": "0.25", "unit": "tsp"},
            {"name": "coriander powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "pepper powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "oil", "quantity": "1", "unit": "tbsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"}
        ],
        "instructions": [
            "Clean fish fillets and pat completely dry.",
            "Mix ginger garlic paste, red chilli, turmeric, coriander powder, pepper, lemon juice, oil and salt into a marinade.",
            "Score the fish with shallow cuts to allow marinade to penetrate.",
            "Coat fish well with marinade. Marinate for minimum 20 minutes.",
            "Preheat a grill pan or outdoor grill to medium-high heat.",
            "Brush grill with little oil to prevent sticking.",
            "Grill fish for 5-6 minutes on one side without moving.",
            "Flip gently and grill other side for 4-5 minutes.",
            "Fish is done when it flakes easily with a fork.",
            "Garnish with coriander leaves and lemon wedges. Serve with salad."
        ],
        "tags": ["healthy", "high-protein", "low-calorie", "south-indian"]
    },

    {
        "name": "Vegetable Soup",
        "description": "A light, nourishing clear vegetable soup packed with colorful vegetables and herbs. Low calorie, healthy and perfect for weight loss.",
        "category": "dinner",
        "cuisine": "continental",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 2,
        "calories": 100,
        "protein": 3.0,
        "carbs": 16.0,
        "fat": 2.5,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "carrot", "quantity": "1", "unit": "medium"},
            {"name": "beans", "quantity": "0.5", "unit": "cup"},
            {"name": "capsicum", "quantity": "0.5", "unit": "medium"},
            {"name": "onion", "quantity": "1", "unit": "small"},
            {"name": "garlic", "quantity": "3", "unit": "cloves"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "celery", "quantity": "1", "unit": "stalk"},
            {"name": "black pepper", "quantity": "0.5", "unit": "tsp"},
            {"name": "mixed herbs", "quantity": "0.5", "unit": "tsp"},
            {"name": "olive oil", "quantity": "1", "unit": "tsp"},
            {"name": "salt", "quantity": "1", "unit": "tsp"},
            {"name": "water", "quantity": "3", "unit": "cups"}
        ],
        "instructions": [
            "Dice all vegetables into small uniform pieces.",
            "Heat olive oil in a pot. Add minced garlic and ginger. Saute for 1 minute.",
            "Add onion and saute until translucent.",
            "Add carrots and beans. Cook for 3 minutes.",
            "Add capsicum and celery. Stir for 2 minutes.",
            "Pour water and bring to a boil.",
            "Add salt, pepper and mixed herbs.",
            "Simmer on low flame for 12-15 minutes until vegetables are tender.",
            "Taste and adjust seasoning. Serve hot with bread."
        ],
        "tags": ["healthy", "low-calorie", "quick", "comfort food"]
    },

    {
        "name": "Moong Dal Soup",
        "description": "A light and digestive yellow moong dal soup tempered with cumin and ginger. Rich in protein, easy to digest and perfect for a healthy dinner.",
        "category": "dinner",
        "cuisine": "indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 20,
        "servings": 2,
        "calories": 160,
        "protein": 10.0,
        "carbs": 24.0,
        "fat": 3.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "yellow moong dal", "quantity": "0.5", "unit": "cup"},
            {"name": "ginger", "quantity": "0.5", "unit": "inch"},
            {"name": "garlic", "quantity": "3", "unit": "cloves"},
            {"name": "turmeric", "quantity": "0.25", "unit": "tsp"},
            {"name": "cumin seeds", "quantity": "1", "unit": "tsp"},
            {"name": "lemon juice", "quantity": "1", "unit": "tbsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"},
            {"name": "oil", "quantity": "1", "unit": "tsp"},
            {"name": "salt", "quantity": "0.75", "unit": "tsp"},
            {"name": "water", "quantity": "3", "unit": "cups"}
        ],
        "instructions": [
            "Wash moong dal well. Soak for 15 minutes if time allows.",
            "Pressure cook dal with water, turmeric and salt for 3 whistles.",
            "Mash the cooked dal slightly to make a semi-thick soup.",
            "Heat oil in a small pan. Add cumin seeds and let them splutter.",
            "Add minced ginger and garlic. Fry for 1 minute.",
            "Pour this tempering into the dal soup. Mix well.",
            "Add more water if too thick. Bring to a gentle simmer.",
            "Add lemon juice and mix.",
            "Garnish with fresh coriander. Serve hot as a light dinner."
        ],
        "tags": ["healthy", "high-protein", "low-calorie", "comfort food"]
    },

    {
        "name": "Oats Upma",
        "description": "A healthy and quick savory oats upma with vegetables and Indian spices. A nutritious alternative to regular upma, high in fiber.",
        "category": "breakfast",
        "cuisine": "south_indian",
        "diet_type": "vegan",
        "difficulty": "easy",
        "prep_time": 5,
        "cook_time": 15,
        "servings": 2,
        "calories": 210,
        "protein": 8.0,
        "carbs": 32.0,
        "fat": 6.0,
        "is_popular": False,
        "image_url": None,
        "ingredients": [
            {"name": "rolled oats", "quantity": "1", "unit": "cup"},
            {"name": "onion", "quantity": "1", "unit": "small"},
            {"name": "carrot", "quantity": "0.5", "unit": "medium"},
            {"name": "green chilli", "quantity": "1", "unit": "piece"},
            {"name": "mustard seeds", "quantity": "0.5", "unit": "tsp"},
            {"name": "urad dal", "quantity": "0.5", "unit": "tsp"},
            {"name": "curry leaves", "quantity": "1", "unit": "sprig"},
            {"name": "turmeric", "quantity": "0.25", "unit": "tsp"},
            {"name": "lemon juice", "quantity": "1", "unit": "tsp"},
            {"name": "oil", "quantity": "1", "unit": "tbsp"},
            {"name": "salt", "quantity": "0.75", "unit": "tsp"},
            {"name": "water", "quantity": "1", "unit": "cup"}
        ],
        "instructions": [
            "Dry roast rolled oats in a pan for 2-3 minutes until lightly toasted. Set aside.",
            "Heat oil in a pan. Add mustard seeds and let them splutter.",
            "Add urad dal and fry until golden.",
            "Add curry leaves and green chilli. Saute briefly.",
            "Add onion and carrot. Cook for 3-4 minutes.",
            "Add turmeric and salt. Mix well.",
            "Add water and bring to a boil.",
            "Add roasted oats and stir continuously.",
            "Cook on low flame for 3-4 minutes until water is absorbed.",
            "Squeeze lemon juice on top and serve hot."
        ],
        "tags": ["healthy", "quick", "low-calorie", "high-protein", "south-indian"]
    },

    {
        "name": "Paneer Bhurji",
        "description": "Scrambled cottage cheese cooked with onions, tomatoes and spices. A quick, high-protein North Indian breakfast or dinner side dish.",
        "category": "dinner",
        "cuisine": "north_indian",
        "diet_type": "vegetarian",
        "difficulty": "easy",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 2,
        "calories": 280,
        "protein": 18.0,
        "carbs": 10.0,
        "fat": 18.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "paneer", "quantity": "200", "unit": "grams"},
            {"name": "onion", "quantity": "1", "unit": "medium"},
            {"name": "tomato", "quantity": "1", "unit": "medium"},
            {"name": "capsicum", "quantity": "0.5", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "1", "unit": "tsp"},
            {"name": "green chilli", "quantity": "1", "unit": "piece"},
            {"name": "turmeric", "quantity": "0.25", "unit": "tsp"},
            {"name": "red chilli powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "garam masala", "quantity": "0.25", "unit": "tsp"},
            {"name": "coriander leaves", "quantity": "2", "unit": "tbsp"},
            {"name": "oil", "quantity": "2", "unit": "tbsp"},
            {"name": "salt", "quantity": "0.75", "unit": "tsp"}
        ],
        "instructions": [
            "Crumble paneer with your hands into small pieces. Set aside.",
            "Heat oil in a pan. Add ginger garlic paste and green chilli. Fry for 1 minute.",
            "Add finely chopped onions and fry until golden.",
            "Add tomatoes and capsicum. Cook until soft and oil separates.",
            "Add turmeric, red chilli powder and garam masala. Mix well.",
            "Add crumbled paneer and toss gently.",
            "Cook on medium flame for 4-5 minutes, stirring occasionally.",
            "Adjust salt. Garnish with fresh coriander leaves.",
            "Serve hot with roti, paratha or as a toast topping."
        ],
        "tags": ["quick", "high-protein", "north-indian", "popular"]
    },

    {
        "name": "Rajma Chawal",
        "description": "Red kidney beans slow cooked in a spiced tomato-onion gravy served over steamed rice. A wholesome and comforting North Indian comfort food.",
        "category": "lunch",
        "cuisine": "north_indian",
        "diet_type": "vegan",
        "difficulty": "medium",
        "prep_time": 480,
        "cook_time": 45,
        "servings": 4,
        "calories": 380,
        "protein": 15.0,
        "carbs": 64.0,
        "fat": 7.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "kidney beans (rajma)", "quantity": "1", "unit": "cup"},
            {"name": "rice", "quantity": "2", "unit": "cups"},
            {"name": "onion", "quantity": "2", "unit": "medium"},
            {"name": "tomato", "quantity": "3", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "red chilli powder", "quantity": "1", "unit": "tsp"},
            {"name": "coriander powder", "quantity": "1", "unit": "tsp"},
            {"name": "cumin seeds", "quantity": "1", "unit": "tsp"},
            {"name": "garam masala", "quantity": "0.5", "unit": "tsp"},
            {"name": "oil", "quantity": "3", "unit": "tbsp"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"}
        ],
        "instructions": [
            "Soak rajma in water overnight or minimum 8 hours.",
            "Pressure cook soaked rajma with salt and water for 6-7 whistles until very soft.",
            "Cook rice separately. Keep warm.",
            "Heat oil in a pan. Add cumin seeds and let them splutter.",
            "Add finely chopped onions and fry until deep golden brown.",
            "Add ginger garlic paste and cook for 2 minutes.",
            "Add tomatoes and cook until oil separates completely.",
            "Add red chilli, coriander powder and garam masala. Mix well.",
            "Add cooked rajma with its water. Stir well.",
            "Simmer on low flame for 20 minutes until gravy thickens.",
            "Serve hot over steamed rice with onion rings and lemon."
        ],
        "tags": ["popular", "north-indian", "high-protein", "comfort food"]
    },

    {
        "name": "Chole Bhature",
        "description": "Spicy and tangy chickpea curry served with deep fried fluffy bhature bread. A rich and indulgent North Indian breakfast and lunch specialty.",
        "category": "lunch",
        "cuisine": "north_indian",
        "diet_type": "vegan",
        "difficulty": "hard",
        "prep_time": 480,
        "cook_time": 45,
        "servings": 4,
        "calories": 520,
        "protein": 14.0,
        "carbs": 72.0,
        "fat": 20.0,
        "is_popular": True,
        "image_url": None,
        "ingredients": [
            {"name": "white chickpeas (kabuli chana)", "quantity": "1.5", "unit": "cups"},
            {"name": "all purpose flour (maida)", "quantity": "2", "unit": "cups"},
            {"name": "onion", "quantity": "2", "unit": "large"},
            {"name": "tomato", "quantity": "2", "unit": "medium"},
            {"name": "ginger garlic paste", "quantity": "2", "unit": "tbsp"},
            {"name": "chole masala powder", "quantity": "2", "unit": "tbsp"},
            {"name": "tea bag", "quantity": "1", "unit": "piece"},
            {"name": "yogurt", "quantity": "0.25", "unit": "cup"},
            {"name": "baking powder", "quantity": "0.5", "unit": "tsp"},
            {"name": "oil", "quantity": "1", "unit": "cup (for frying)"},
            {"name": "salt", "quantity": "1.5", "unit": "tsp"}
        ],
        "instructions": [
            "Soak chickpeas overnight. Pressure cook with tea bag (for dark color), salt and water for 6-7 whistles.",
            "For bhature: Mix maida, yogurt, baking powder, salt and water. Knead to soft dough. Rest 1 hour.",
            "Heat oil in pan. Fry onions golden. Add ginger garlic paste, cook 2 minutes.",
            "Add tomatoes and cook until oil separates.",
            "Add chole masala and cook for 3 minutes.",
            "Add cooked chickpeas. Simmer 20 minutes until thick gravy forms.",
            "Mash a few chickpeas to thicken the gravy naturally.",
            "For bhature: Divide dough into balls, roll into oval shapes.",
            "Deep fry each bhature in hot oil until puffed and golden on both sides.",
            "Serve hot chole with puffed bhature, onion rings and green chutney."
        ],
        "tags": ["popular", "north-indian", "street food", "festive", "high-protein"]
    }
]


# =========================================================
# Seed Function
# =========================================================

def seed_recipes():
    db = SessionLocal()

    try:
        count = db.query(Recipe).count()
        if count > 0:
            print(f"⚠️  Recipes already seeded ({count} recipes found). Skipping.")
            return

        print("🌱 Starting recipe seeding...")

        success_count = 0
        error_count = 0

        for r in RECIPES_DATA:
            try:
                recipe_obj = Recipe(
                    name=r["name"],
                    description=r["description"],
                    category=r["category"],
                    cuisine=r["cuisine"],
                    diet_type=r["diet_type"],
                    prep_time=r["prep_time"],
                    cook_time=r["cook_time"],
                    servings=r["servings"],
                    difficulty=r["difficulty"],
                    calories=r["calories"],
                    protein=r["protein"],
                    carbs=r["carbs"],
                    fat=r["fat"],
                    is_popular=r["is_popular"],
                    image_url=r["image_url"],
                    ingredients=json.dumps(r["ingredients"]),
                    instructions=json.dumps(r["instructions"]),
                    tags=json.dumps(r["tags"])
                )
                db.add(recipe_obj)
                success_count += 1
                print(f"   ✅ Added: {r['name']}")

            except Exception as e:
                error_count += 1
                print(f"   ❌ Failed to add {r['name']}: {str(e)}")

        db.commit()

        print("")
        print("=" * 50)
        print(f"✅ Seeding Complete!")
        print(f"   Total Recipes Added : {success_count}")
        print(f"   Errors              : {error_count}")
        print("=" * 50)

        # Summary by category
        categories = {}
        for r in RECIPES_DATA:
            cat = r["category"]
            categories[cat] = categories.get(cat, 0) + 1

        print("\n📊 Recipes by Category:")
        for cat, count in categories.items():
            print(f"   {cat.capitalize():<12}: {count} recipes")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {str(e)}")

    finally:
        db.close()


# =========================================================
# Run Directly
# =========================================================

if __name__ == "__main__":
    seed_recipes()
