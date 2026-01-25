import streamlit as st
import requests
from datetime import datetime
import json

# Page config
st.set_page_config(page_title="Recipes", page_icon="🍳", layout="wide")

# Check authentication
if 'token' not in st.session_state:
    st.warning("⚠️ Please login first!")
    st.stop()

API_URL = "http://localhost:8000"
headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("🍳 Recipe Recommendations")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Smart Recommendations", "📚 All Recipes", "⭐ Favorites", "🔍 Search"])

# TAB 1: Smart Recommendations
with tab1:
    st.subheader("🎯 Recipes You Can Make Now")
    st.info("Based on items in your pantry!")
    
    try:
        response = requests.get(f"{API_URL}/api/recipes/recommendations/smart", headers=headers)
        
        if response.status_code == 200:
            recommendations = response.json()
            
            if recommendations:
                for rec in recommendations:
                    recipe = rec['recipe']
                    match_score = rec['match_score']
                    available = rec['available_ingredients']
                    missing = rec['missing_ingredients']
                    
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"### {recipe['name']}")
                            st.markdown(f"*{recipe['description']}*")
                            
                            # Tags
                            tags = f"🍽️ {recipe['category']} | 🌍 {recipe['cuisine']} | ⏱️ {recipe['prep_time'] + recipe['cook_time']} min | 👥 {recipe['servings']} servings"
                            st.caption(tags)
                        
                        with col2:
                            # Match score with color
                            if match_score >= 80:
                                st.success(f"✅ {match_score}% Match")
                            elif match_score >= 50:
                                st.warning(f"⚠️ {match_score}% Match")
                            else:
                                st.info(f"ℹ️ {match_score}% Match")
                        
                        with col3:
                            # View button
                            if st.button("👁️ View Recipe", key=f"view_rec_{recipe['id']}"):
                                st.session_state.selected_recipe_id = recipe['id']
                                st.rerun()
                        
                        # Expandable details
                        with st.expander("📋 Ingredients Status"):
                            st.markdown("**✅ You Have:**")
                            for ing in available:
                                st.markdown(f"- {ing}")
                            
                            if missing:
                                st.markdown("**❌ You Need:**")
                                for ing in missing:
                                    st.markdown(f"- {ing}")
                        
                        st.divider()
            else:
                st.info("🔍 Add more items to your pantry to get recipe recommendations!")
        else:
            st.error("❌ Failed to load recommendations")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# TAB 2: All Recipes
with tab2:
    st.subheader("📚 Browse All Recipes")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All", "breakfast", "lunch", "dinner", "snack", "dessert"]
        )
    
    with col2:
        cuisine_filter = st.selectbox(
            "Cuisine",
            ["All", "indian", "chinese", "italian", "american", "mexican", "international"]
        )
    
    with col3:
        difficulty_filter = st.selectbox(
            "Difficulty",
            ["All", "easy", "medium", "hard"]
        )
    
    with col4:
        max_time = st.number_input("Max Time (min)", min_value=0, max_value=180, value=60, step=15)
    
    # Build query params
    params = {}
    if category_filter != "All":
        params['category'] = category_filter
    if cuisine_filter != "All":
        params['cuisine'] = cuisine_filter
    if difficulty_filter != "All":
        params['difficulty'] = difficulty_filter
    if max_time > 0:
        params['max_time'] = max_time
    
    try:
        response = requests.get(f"{API_URL}/api/recipes/", headers=headers, params=params)
        
        if response.status_code == 200:
            recipes = response.json()
            
            st.write(f"Found **{len(recipes)}** recipes")
            
            # Display recipes in grid
            cols = st.columns(3)
            for idx, recipe in enumerate(recipes):
                with cols[idx % 3]:
                    with st.container():
                        st.markdown(f"### {recipe['name']}")
                        
                        # Difficulty badge
                        if recipe['difficulty'] == 'easy':
                            st.success("✅ Easy")
                        elif recipe['difficulty'] == 'medium':
                            st.warning("⚠️ Medium")
                        else:
                            st.error("🔥 Hard")
                        
                        st.caption(f"⏱️ {recipe['prep_time'] + recipe['cook_time']} min | 👥 {recipe['servings']} servings")
                        st.caption(f"🔥 {recipe.get('calories', 'N/A')} cal")
                        
                        col_fav, col_view = st.columns(2)
                        
                        with col_fav:
                            fav_icon = "⭐" if recipe.get('is_favorite') else "☆"
                            if st.button(f"{fav_icon}", key=f"fav_{recipe['id']}"):
                                try:
                                    fav_response = requests.post(
                                        f"{API_URL}/api/recipes/{recipe['id']}/favorite",
                                        headers=headers
                                    )
                                    if fav_response.status_code == 200:
                                        st.rerun()
                                except:
                                    pass
                        
                        with col_view:
                            if st.button("👁️ View", key=f"view_{recipe['id']}"):
                                st.session_state.selected_recipe_id = recipe['id']
                                st.rerun()
                        
                        st.divider()
        else:
            st.error("❌ Failed to load recipes")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# TAB 3: Favorites
with tab3:
    st.subheader("⭐ Your Favorite Recipes")
    
    try:
        response = requests.get(f"{API_URL}/api/recipes/favorites/list", headers=headers)
        
        if response.status_code == 200:
            favorites = response.json()
            
            if favorites:
                for recipe in favorites:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.markdown(f"### {recipe['name']}")
                        st.caption(f"{recipe['category']} | {recipe['cuisine']}")
                    
                    with col2:
                        st.caption(f"⏱️ {recipe['prep_time'] + recipe['cook_time']} min")
                    
                    with col3:
                        if st.button("👁️ View", key=f"fav_view_{recipe['id']}"):
                            st.session_state.selected_recipe_id = recipe['id']
                            st.rerun()
                    
                    st.divider()
            else:
                st.info("⭐ No favorite recipes yet. Start exploring and add some!")
        else:
            st.error("❌ Failed to load favorites")
    
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# TAB 4: Search
with tab4:
    st.subheader("🔍 Search Recipes")
    
    search_query = st.text_input("Search by name", placeholder="e.g., pasta, smoothie, salad")
    
    if search_query:
        try:
            response = requests.get(
                f"{API_URL}/api/recipes/",
                headers=headers,
                params={"search": search_query}
            )
            
            if response.status_code == 200:
                results = response.json()
                
                if results:
                    st.success(f"Found {len(results)} recipes")
                    
                    for recipe in results:
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"### {recipe['name']}")
                            st.markdown(f"*{recipe['description']}*")
                            st.caption(f"{recipe['category']} | {recipe['cuisine']} | {recipe['difficulty']}")
                        
                        with col2:
                            if st.button("👁️ View", key=f"search_{recipe['id']}"):
                                st.session_state.selected_recipe_id = recipe['id']
                                st.rerun()
                        
                        st.divider()
                else:
                    st.info("No recipes found. Try a different search term.")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Recipe Detail Modal (if recipe selected)
if 'selected_recipe_id' in st.session_state:
    st.markdown("---")
    
    try:
        response = requests.get(
            f"{API_URL}/api/recipes/{st.session_state.selected_recipe_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            recipe = response.json()
            
            # Header with back button
            col1, col2 = st.columns([4, 1])
            with col1:
                st.title(f"🍳 {recipe['name']}")
            with col2:
                if st.button("⬅️ Back"):
                    del st.session_state.selected_recipe_id
                    st.rerun()
            
            st.markdown(f"*{recipe['description']}*")
            
            # Recipe info
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Prep Time", f"{recipe['prep_time']} min")
            with col2:
                st.metric("Cook Time", f"{recipe['cook_time']} min")
            with col3:
                st.metric("Servings", recipe['servings'])
            with col4:
                st.metric("Calories", recipe.get('calories', 'N/A'))
            
            # Nutrition info
            if recipe.get('protein'):
                st.markdown("### 📊 Nutrition (per serving)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.info(f"💪 Protein: {recipe['protein']}g")
                with col2:
                    st.info(f"🍞 Carbs: {recipe['carbs']}g")
                with col3:
                    st.info(f"🥑 Fat: {recipe['fat']}g")
            
            # Ingredients
            st.markdown("### 📋 Ingredients")
            try:
                ingredients = json.loads(recipe['ingredients'])
                for ing in ingredients:
                    st.markdown(f"- **{ing['quantity']} {ing['unit']}** {ing['name']}")
            except:
                st.write(recipe['ingredients'])
            
            # Instructions
            st.markdown("### 👨‍🍳 Instructions")
            try:
                instructions = json.loads(recipe['instructions'])
                for idx, step in enumerate(instructions, 1):
                    st.markdown(f"**Step {idx}:** {step}")
            except:
                st.write(recipe['instructions'])
            
            # Favorite button
            fav_text = "Remove from Favorites ⭐" if recipe.get('is_favorite') else "Add to Favorites ☆"
            if st.button(fav_text, type="primary"):
                try:
                    fav_response = requests.post(
                        f"{API_URL}/api/recipes/{recipe['id']}/favorite",
                        headers=headers
                    )
                    if fav_response.status_code == 200:
                        st.success("✅ Favorites updated!")
                        st.rerun()
                except:
                    st.error("❌ Failed to update favorites")
    
    except Exception as e:
        st.error(f"❌ Error loading recipe: {str(e)}")
