"""
Recipe Recommendations Page
- Smart Recommendations (Pantry + Expiry Priority)
- All Recipes (Browse + Filter)
- Favorites
- AI Suggestion (Groq)
"""

import streamlit as st
import requests
import json


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(page_title="Recipes", page_icon="🍳", layout="wide")

if 'token' not in st.session_state:
    st.warning("⚠️ Please login first!")
    st.stop()

API_URL = "http://localhost:8001"
headers = {"Authorization": f"Bearer {st.session_state.token}"}


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def toggle_favorite(recipe_id: int):
    try:
        response = requests.post(
            f"{API_URL}/api/recipes/{recipe_id}/favorite",
            headers=headers, timeout=5
        )
        if response.status_code == 200:
            result = response.json()
            st.toast(f"{'⭐ Added to' if result['is_favorite'] else '💔 Removed from'} favorites!")
            st.rerun()
        else:
            st.error("❌ Failed to update favorites")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def get_diet_badge(diet_type: str) -> str:
    return {
        "vegetarian": "🥗 Vegetarian",
        "vegan": "🌱 Vegan",
        "non_vegetarian": "🍖 Non-Veg"
    }.get(diet_type, "")


def get_difficulty_badge(difficulty: str) -> str:
    return {
        "easy": "✅ Easy",
        "medium": "⚠️ Medium",
        "hard": "🔥 Hard"
    }.get(difficulty, difficulty or "")


# ==========================================
# RECIPE DETAIL DIALOG (popup)
# ==========================================

@st.dialog("🍳 Recipe Details", width="large")
def show_recipe_dialog(recipe_id: int):
    """Opens as a true modal dialog popup"""
    try:
        resp = requests.get(
            f"{API_URL}/api/recipes/{recipe_id}",
            headers=headers, timeout=10
        )
        if resp.status_code != 200:
            st.error("❌ Could not load recipe details.")
            return

        r = resp.json()

        # Title
        st.title(f"🍳 {r['name']}")

        if r.get('description'):
            st.caption(f"_{r['description']}_")

        st.markdown("---")

        # Badges row
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            diet = get_diet_badge(r.get('diet_type', ''))
            if diet:
                st.info(diet)
        with b2:
            cuisine = r.get('cuisine', '').replace('_', ' ').title()
            if cuisine:
                st.info(f"🌍 {cuisine}")
        with b3:
            st.info(get_difficulty_badge(r.get('difficulty', '')))
        with b4:
            tags_raw = r.get('tags')
            if tags_raw:
                try:
                    tags = json.loads(tags_raw)
                    if tags:
                        st.info(f"🏷️ {', '.join(tags[:3])}")
                except Exception:
                    pass

        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("⏱️ Prep", f"{r.get('prep_time', 0)} min")
        m2.metric("🍳 Cook", f"{r.get('cook_time', 0)} min")
        m3.metric("👥 Serves", r.get('servings', 'N/A'))
        m4.metric("🔥 Calories", f"{r.get('calories', 'N/A')} kcal")

        # Nutrition
        if r.get('protein') or r.get('carbs') or r.get('fat'):
            st.markdown("**📊 Nutrition per Serving:**")
            n1, n2, n3 = st.columns(3)
            n1.success(f"💪 Protein: **{r.get('protein', 0)}g**")
            n2.warning(f"🍞 Carbs: **{r.get('carbs', 0)}g**")
            n3.info(f"🥑 Fat: **{r.get('fat', 0)}g**")

        st.markdown("---")

        # Ingredients + Instructions
        col_ing, col_ins = st.columns([1, 2])

        with col_ing:
            st.markdown("### 📋 Ingredients")
            try:
                ingredients = json.loads(r['ingredients'])
                for ing in ingredients:
                    if isinstance(ing, dict):
                        qty  = ing.get('quantity', '')
                        unit = ing.get('unit', '')
                        name = ing.get('name', '')
                        st.markdown(f"- **{qty} {unit}** {name}")
                    else:
                        st.markdown(f"- {ing}")
            except Exception:
                st.write(r.get('ingredients', 'N/A'))

        with col_ins:
            st.markdown("### 👨‍🍳 Instructions")
            try:
                instructions = json.loads(r['instructions'])
                for idx, step in enumerate(instructions, 1):
                    st.markdown(
                        f"""<div style='background:#1e1e2e;padding:10px 14px;
                        border-radius:8px;margin:6px 0;
                        border-left:4px solid #ff4b4b;line-height:1.6;'>
                        <strong>Step {idx}:</strong> {step}</div>""",
                        unsafe_allow_html=True
                    )
            except Exception:
                st.write(r.get('instructions', 'N/A'))

        st.markdown("---")

        # Favorite button inside dialog
        fav_text = "💔 Remove from Favorites" if r.get('is_favorite') else "⭐ Add to Favorites"
        fav_type = "secondary" if r.get('is_favorite') else "primary"
        if st.button(fav_text, type=fav_type,
                     key=f"fav_dialog_{recipe_id}",
                     use_container_width=True):
            toggle_favorite(recipe_id)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# ==========================================
# RECIPE CARD
# ==========================================

def display_recipe_card(recipe: dict, key_prefix: str,
                         show_match: bool = False,
                         match_score: float = 0,
                         badge: str = "",
                         uses_expiring: bool = False):
    """Clean recipe card — View button opens a dialog popup"""

    with st.container(border=True):

        # Expiry / status badge
        if uses_expiring and badge:
            st.markdown(
                f"<span style='background:#ff4b4b;color:white;"
                f"padding:3px 10px;border-radius:5px;"
                f"font-size:12px;font-weight:bold;'>{badge}</span><br>",
                unsafe_allow_html=True
            )
        elif badge and show_match:
            st.markdown(
                f"<span style='background:#262730;color:white;"
                f"padding:3px 10px;border-radius:5px;"
                f"font-size:12px;'>{badge}</span><br>",
                unsafe_allow_html=True
            )

        # Title + Favorite button
        col_name, col_fav = st.columns([5, 1])
        with col_name:
            st.markdown(f"#### {recipe['name']}")
        with col_fav:
            fav_icon = "⭐" if recipe.get('is_favorite') else "☆"
            if st.button(
                fav_icon,
                key=f"fav_card_{key_prefix}_{recipe['id']}",
                help="Toggle Favorite",
                use_container_width=True
            ):
                toggle_favorite(recipe['id'])

        # Meta info in one clean caption line
        total_time = (recipe.get('prep_time') or 0) + (recipe.get('cook_time') or 0)
        cuisine    = recipe.get('cuisine', '').replace('_', ' ').title()
        diet       = get_diet_badge(recipe.get('diet_type', ''))
        diff       = get_difficulty_badge(recipe.get('difficulty', ''))
        cal        = recipe.get('calories', 'N/A')

        st.caption(
            f"🌍 {cuisine}  ·  ⏱️ {total_time} min  ·  "
            f"{diff}  ·  {diet}  ·  🔥 {cal} cal"
        )

        # Match score
        if show_match and match_score > 0:
            if match_score >= 80:
                st.success(f"✅ {match_score}% Match")
            elif match_score >= 50:
                st.warning(f"🟡 {match_score}% Match")
            else:
                st.info(f"🔵 {match_score}% Match")

        # View Details button → opens dialog
        if st.button(
            "👁️ View Details",
            key=f"view_{key_prefix}_{recipe['id']}",
            use_container_width=True,
            type="primary"
        ):
            show_recipe_dialog(recipe['id'])


# ==========================================
# MAIN PAGE HEADER
# ==========================================

st.title("🍳 Recipe Recommendations")
st.caption("Discover recipes based on your pantry, preferences & health goals.")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Smart Recommendations",
    "📚 All Recipes",
    "⭐ Favorites",
    "🔍 Search"
])


# ==========================================
# TAB 1: SMART RECOMMENDATIONS
# ==========================================

with tab1:
    st.subheader("🎯 Smart Recommendations")

    col_info, col_refresh = st.columns([4, 1])
    with col_info:
        st.info("📦 Recipes ranked by your pantry — expiring items get priority!")
    with col_refresh:
        if st.button("🔄 Refresh", key="refresh_rec", use_container_width=True):
            st.rerun()

    try:
        with st.spinner("🔍 Finding best recipes for you..."):
            response = requests.get(
                f"{API_URL}/api/recipes/recommendations/smart",
                headers=headers, timeout=15
            )

        if response.status_code == 200:
            recommendations = response.json()

            if recommendations:
                expiring_recs = [r for r in recommendations if r.get('uses_expiring')]
                perfect_recs  = [r for r in recommendations if not r.get('uses_expiring') and r['match_score'] >= 80]
                partial_recs  = [r for r in recommendations if not r.get('uses_expiring') and 20 <= r['match_score'] < 80]
                popular_recs  = [r for r in recommendations if r['match_score'] == 0]

                st.success(f"✅ Found **{len(recommendations)}** recipes for you!")

                # ── Expiring items ──────────────────────
                if expiring_recs:
                    st.markdown("### 🔥 Use Before They Expire!")
                    st.warning("⏰ These recipes use ingredients expiring soon!")
                    cols = st.columns(2)
                    for idx, rec in enumerate(expiring_recs):
                        with cols[idx % 2]:
                            display_recipe_card(
                                rec['recipe'],
                                key_prefix=f"exp{idx}",
                                show_match=True,
                                match_score=rec['match_score'],
                                badge=rec.get('badge', ''),
                                uses_expiring=True
                            )

                # ── Perfect matches ─────────────────────
                if perfect_recs:
                    st.markdown("### ✅ Perfect Matches (80%+ available)")
                    cols = st.columns(2)
                    for idx, rec in enumerate(perfect_recs):
                        with cols[idx % 2]:
                            display_recipe_card(
                                rec['recipe'],
                                key_prefix=f"perf{idx}",
                                show_match=True,
                                match_score=rec['match_score'],
                                badge=rec.get('badge', '')
                            )

                # ── Partial matches ─────────────────────
                if partial_recs:
                    st.markdown("### 🟡 Partial Matches")
                    cols = st.columns(2)
                    for idx, rec in enumerate(partial_recs):
                        with cols[idx % 2]:
                            display_recipe_card(
                                rec['recipe'],
                                key_prefix=f"part{idx}",
                                show_match=True,
                                match_score=rec['match_score'],
                                badge=rec.get('badge', '')
                            )

                # ── Popular fallbacks ───────────────────
                if popular_recs:
                    st.markdown("### 🌟 Popular Picks")
                    cols = st.columns(2)
                    for idx, rec in enumerate(popular_recs):
                        with cols[idx % 2]:
                            display_recipe_card(
                                rec['recipe'],
                                key_prefix=f"pop{idx}",
                                badge="🌟 Popular"
                            )

            else:
                st.info("🔍 No recommendations yet!")
                with st.expander("💡 Tips to get recommendations"):
                    st.markdown("""
                    Add these common ingredients to your pantry:
                    - 🧅 Onions, Tomatoes, Potatoes
                    - 🍚 Rice, Wheat Flour
                    - 🥛 Milk, Yogurt, Butter
                    - 🧂 Salt, Oil, Spices
                    - 🥚 Eggs
                    """)

        else:
            st.error(f"❌ Failed to load (Status: {response.status_code})")
            if st.button("🔄 Retry", key="retry_rec"):
                st.rerun()

    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Please try again.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# ==========================================
# TAB 2: ALL RECIPES
# ==========================================

with tab2:
    st.subheader("📚 Browse All Recipes")

    # Filters
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        cat_f = st.selectbox("🍽️ Category",
            ["All", "breakfast", "lunch", "dinner", "snack", "beverage"],
            key="t2_cat")
    with c2:
        cui_f = st.selectbox("🌍 Cuisine",
            ["All", "south_indian", "north_indian", "chinese",
             "italian", "american", "continental"],
            key="t2_cui")
    with c3:
        dif_f = st.selectbox("⚖️ Difficulty",
            ["All", "easy", "medium", "hard"],
            key="t2_dif")
    with c4:
        diet_f = st.selectbox("🥗 Diet",
            ["All", "vegetarian", "vegan", "non_vegetarian"],
            key="t2_diet")
    with c5:
        maxt = st.number_input("⏱️ Max Time (min)",
            min_value=0, max_value=180,
            value=60, step=15, key="t2_time")

    search_q = st.text_input(
        "🔍 Search recipes",
        placeholder="e.g., idli, biryani, pasta...",
        key="t2_search"
    )

    # Build params
    params = {}
    if cat_f  != "All": params['category']   = cat_f
    if cui_f  != "All": params['cuisine']    = cui_f
    if dif_f  != "All": params['difficulty'] = dif_f
    if diet_f != "All": params['diet_type']  = diet_f
    if maxt   > 0:      params['max_time']   = maxt
    if search_q:        params['search']     = search_q

    try:
        resp = requests.get(
            f"{API_URL}/api/recipes/",
            headers=headers, params=params, timeout=10
        )

        if resp.status_code == 200:
            recipes = resp.json()
            st.write(f"**Found {len(recipes)} recipe(s)**")

            if recipes:
                cols = st.columns(2)
                for idx, recipe in enumerate(recipes):
                    with cols[idx % 2]:
                        display_recipe_card(recipe, key_prefix=f"t2_{idx}")
            else:
                st.info("No recipes found. Try adjusting your filters!")

        else:
            st.error("❌ Failed to load recipes")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# ==========================================
# TAB 3: FAVORITES
# ==========================================

with tab3:
    st.subheader("⭐ Your Favorite Recipes")

    col_i, col_r = st.columns([4, 1])
    with col_i:
        st.info("❤️ Recipes you've saved as favorites")
    with col_r:
        if st.button("🔄 Refresh", key="t3_refresh", use_container_width=True):
            st.rerun()

    try:
        resp = requests.get(
            f"{API_URL}/api/recipes/favorites/list",
            headers=headers, timeout=10
        )

        if resp.status_code == 200:
            favorites = resp.json()

            if favorites:
                st.success(f"You have **{len(favorites)}** favorite recipe(s)!")
                cols = st.columns(2)
                for idx, recipe in enumerate(favorites):
                    with cols[idx % 2]:
                        display_recipe_card(recipe, key_prefix=f"t3_{idx}")
            else:
                st.info("⭐ No favorites yet!")
                st.markdown("""
                **How to add favorites:**
                - Browse **All Recipes** or **Smart Recommendations**
                - Click **☆** on any recipe card to save it
                - Or open a recipe and click **⭐ Add to Favorites**
                """)

        else:
            st.error("❌ Failed to load favorites")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


# ==========================================
# TAB 4: SEARCH
# ==========================================

with tab4:
    st.subheader("🔍 Search Recipes")
    st.info("Search any recipe by name, ingredient, or cuisine!")

    search_query = st.text_input(
        "Search",
        placeholder="e.g., idli, biryani, pasta, chicken curry...",
        key="t4_search"
    )

    if search_query:
        try:
            with st.spinner("🔍 Searching..."):
                resp = requests.get(
                    f"{API_URL}/api/recipes/",
                    headers=headers,
                    params={"search": search_query},
                    timeout=10
                )

            if resp.status_code == 200:
                results = resp.json()

                if results:
                    st.success(f"✅ Found **{len(results)}** recipe(s) for **'{search_query}'**")

                    cols = st.columns(2)
                    for idx, recipe in enumerate(results):
                        with cols[idx % 2]:
                            display_recipe_card(recipe, key_prefix=f"t4_{idx}")
                else:
                    st.info(f"No recipes found for **'{search_query}'**.")
                    st.markdown("""
                    **💡 Try searching for:**
                    - Idli, Dosa, Upma, Pongal
                    - Biryani, Fried Rice, Pasta
                    - Chicken, Egg, Paneer
                    - Smoothie, Lassi, Coffee
                    """)

            else:
                st.error(f"❌ Search failed (Status: {resp.status_code})")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    else:
        # Show placeholder when no search
        st.markdown("---")
        st.markdown("### 💡 Popular Searches")

        popular = ["Biryani", "Dosa", "Pasta", "Chicken Curry",
                   "Idli", "Fried Rice", "Smoothie", "Paneer"]

        cols = st.columns(4)
        for idx, term in enumerate(popular):
            with cols[idx % 4]:
                if st.button(f"🔍 {term}", key=f"pop_search_{idx}",
                             use_container_width=True):
                    st.session_state.t4_search_term = term
                    st.rerun()

        # If a popular term was clicked
        if 'T4_search_term' in st.session_state:
            del st.session_state.t4_search_term
