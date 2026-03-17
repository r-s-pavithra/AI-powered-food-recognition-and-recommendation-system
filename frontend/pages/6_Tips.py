import urllib.parse

import plotly.express as px
import requests
import streamlit as st


st.set_page_config(page_title="Professional Tips", page_icon="💡", layout="wide")

if "token" not in st.session_state or not st.session_state.token:
    st.warning("⚠️ Please login first from the home page!")
    st.stop()

API_URL = "http://localhost:8001"
headers = {"Authorization": f"Bearer {st.session_state.token}"}

if "favorite_tips" not in st.session_state:
    st.session_state.favorite_tips = set()
if "applied_tips" not in st.session_state:
    st.session_state.applied_tips = set()
if "viewed_tips" not in st.session_state:
    st.session_state.viewed_tips = set()


def _get_profile():
    try:
        response = requests.get(f"{API_URL}/api/profile/", headers=headers, timeout=6)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}


def _get_expiring_items():
    try:
        response = requests.get(
            f"{API_URL}/api/alerts/expiring",
            headers=headers,
            params={"days": 10},
            timeout=6,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []


def _tip_card(tip: dict, key_prefix: str = ""):
    tip_id = tip["id"]
    st.session_state.viewed_tips.add(tip_id)
    key_suffix = f"{key_prefix}_{tip_id}" if key_prefix else tip_id

    with st.container(border=True):
        st.markdown(f"### 📌 {tip['title']} - {tip['tag']}")
        st.write(tip["advice"])
        st.caption(f"Source: {tip['source']} | {tip['metric']}")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("⭐ Favorite", key=f"fav_{key_suffix}", width="stretch"):
                st.session_state.favorite_tips.add(tip_id)
                st.success("Added to favorites.")
        with c2:
            if st.button("✓ Tip applied", key=f"applied_{key_suffix}", width="stretch"):
                st.session_state.applied_tips.add(tip_id)
                st.success("Great. Tip marked as applied.")
        with c3:
            wa_text = urllib.parse.quote(f"Nutrition Tip: {tip['title']} - {tip['advice']}")
            st.link_button(
                "📱 Share",
                f"https://wa.me/?text={wa_text}",
                width="stretch",
            )
        with c4:
            if st.button("🤖 Ask chatbot", key=f"ask_{key_suffix}", width="stretch"):
                st.session_state.quick_q = (
                    f"Explain this nutrition tip in simple steps: {tip['title']}. {tip['advice']}"
                )
                st.switch_page("pages/5_Chatbot.py")


WEIGHT_LOSS_TIPS = [
    {"id": "wl1", "title": "ICMR 21-21-21 Rule", "tag": "ICMR/NIN 2024", "advice": "Walk 21 min after meals (3x/day), drink water before meals, and keep dinner early. This reduces post-meal sugar spikes and overeating in Indian meal patterns.", "source": "National Institute of Nutrition", "metric": "Belly fat risk reduced in regular walkers"},
    {"id": "wl2", "title": "Plate Rule (50-25-25)", "tag": "ICMR/NIN 2024", "advice": "Fill 1/2 plate with vegetables, 1/4 with dal/paneer/egg, and 1/4 with roti/rice. Avoid extra fried side dishes in the same meal.", "source": "NIN Hyderabad", "metric": "~300-500 kcal/day control"},
    {"id": "wl3", "title": "Protein-First Breakfast", "tag": "ICMR 2024", "advice": "Choose high-protein starts: moong chilla + curd, egg bhurji + millet roti, or paneer bhurji. It reduces mid-morning cravings.", "source": "ICMR Dietary Guidelines 2024", "metric": "Better satiety for 4-5 hours"},
    {"id": "wl4", "title": "Smart Carb Swap", "tag": "NIN 2024", "advice": "Replace part of white rice with millets, hand-pounded rice, or extra sabzi. Keep rice to one cupped portion per meal.", "source": "National Institute of Nutrition", "metric": "Lower glycemic load"},
    {"id": "wl5", "title": "No Liquid Calories Rule", "tag": "ICMR 2024", "advice": "Avoid sugar drinks, sweet tea/coffee, and packaged juices on most days. Use unsweetened buttermilk or lemon water.", "source": "ICMR", "metric": "Cuts hidden sugars significantly"},
    {"id": "wl6", "title": "Fiber Before Carb", "tag": "NIN 2024", "advice": "Eat a small salad/vegetable bowl before rice/roti. This helps appetite control and smoother glucose response.", "source": "NIN Hyderabad", "metric": "Improves meal control"},
    {"id": "wl7", "title": "Weekly Meal Prep", "tag": "ICMR Practical Tip", "advice": "Plan 3 simple home meals and pre-cut vegetables. Meal prep lowers reliance on high-calorie outside food.", "source": "ICMR practice advisory", "metric": "Higher home-meal adherence"},
    {"id": "wl8", "title": "Late-Night Cutoff", "tag": "NIN 2024", "advice": "Keep a 2.5-3 hour gap between dinner and sleep. Avoid fried snacks and sweets at night.", "source": "National Institute of Nutrition", "metric": "Supports weight and sleep quality"},
]

DIABETES_TIPS = [
    {"id": "db1", "title": "Carb Consistency", "tag": "ICMR Diabetes Guidance", "advice": "Distribute carbs evenly through meals. Avoid a heavy high-rice lunch followed by sugary evening snacks.", "source": "ICMR 2024", "metric": "Reduces glucose swings"},
    {"id": "db2", "title": "Post-Meal Walk", "tag": "NIN 2024", "advice": "Walk 10-20 minutes after main meals to improve insulin response and lower postprandial spikes.", "source": "NIN Hyderabad", "metric": "Improves post-meal control"},
    {"id": "db3", "title": "Dal + Veg Pairing", "tag": "ICMR/NIN", "advice": "Always pair grain with dal/legume and vegetables. Avoid carb-only meals like plain rice with pickle.", "source": "NIN", "metric": "Better glycemic response"},
    {"id": "db4", "title": "Low GI Grain Rotation", "tag": "ICMR 2024", "advice": "Rotate millets, oats, hand-pounded rice, and whole wheat instead of refined flour-heavy foods.", "source": "ICMR", "metric": "Lower average meal GI"},
    {"id": "db5", "title": "Sugar Audit", "tag": "NIN Label Rule", "advice": "Check labels for sugar/glucose syrup/maltodextrin in packaged foods and sauces before buying.", "source": "NIN food label guidance", "metric": "Avoids hidden sugar load"},
    {"id": "db6", "title": "Fruit Timing Control", "tag": "ICMR 2024", "advice": "Take whole fruit in controlled portion, preferably between meals; avoid fruit juice.", "source": "ICMR", "metric": "Slower glucose rise"},
    {"id": "db7", "title": "Dinner Light + Early", "tag": "NIN 2024", "advice": "Keep dinner lighter than lunch with more vegetables and protein, fewer refined carbs.", "source": "NIN", "metric": "Better fasting sugar trends"},
]

HEART_TIPS = [
    {"id": "ht1", "title": "Oil Quantity Discipline", "tag": "ICMR 2024", "advice": "Track monthly oil usage. Favor steamed, sauteed, and grilled cooking over deep frying.", "source": "ICMR", "metric": "Lower saturated fat intake"},
    {"id": "ht2", "title": "Salt Awareness", "tag": "NIN 2024", "advice": "Reduce papads, pickles, and packaged snacks high in sodium. Taste before adding table salt.", "source": "NIN Hyderabad", "metric": "Supports BP control"},
    {"id": "ht3", "title": "Pulse + Nut Routine", "tag": "ICMR/NIN", "advice": "Include pulses daily and small portions of unsalted nuts. Supports lipid and heart health.", "source": "ICMR 2024", "metric": "Better lipid profile support"},
    {"id": "ht4", "title": "Weekend Fried-Food Limit", "tag": "Practical Cardio Rule", "advice": "Limit fried foods to planned occasional portions, not routine tea-time snacks.", "source": "NIN practical guidance", "metric": "Cuts trans-fat exposure"},
    {"id": "ht5", "title": "Fiber + Activity Pair", "tag": "ICMR 2024", "advice": "Use whole grains + vegetables and keep daily movement consistent for cardiometabolic protection.", "source": "ICMR", "metric": "Heart risk trend improvement"},
]

KIDS_TIPS = [
    {"id": "kd1", "title": "Protein in Every Tiffin", "tag": "NIN Child Nutrition", "advice": "Add one protein item daily: egg, paneer, chana, sprouts, or dal chilla.", "source": "NIN Hyderabad", "metric": "Supports growth and satiety"},
    {"id": "kd2", "title": "Color Plate Challenge", "tag": "ICMR Family Tip", "advice": "Aim for 3 colors in kids' meals using carrot, beet, greens, and seasonal fruit.", "source": "ICMR", "metric": "Improves micronutrient diversity"},
    {"id": "kd3", "title": "Milk + Ragi/Oats Combo", "tag": "NIN 2024", "advice": "Pair calcium sources with complex carbs for steady energy and stronger bones.", "source": "NIN", "metric": "Supports calcium adequacy"},
    {"id": "kd4", "title": "No Screen-Snack Loop", "tag": "Behavioral Nutrition", "advice": "Serve snacks at table, not in front of screens. This reduces mindless overeating.", "source": "NIN family behavior guide", "metric": "Better appetite regulation"},
    {"id": "kd5", "title": "Hydration Habit", "tag": "ICMR 2024", "advice": "Encourage water breaks and reduce sugary drinks. Use flavored water with lemon/mint if needed.", "source": "ICMR", "metric": "Lower sugar beverage exposure"},
]


WEIGHT_GAIN_TIPS = [
    {"id": "wg1", "title": "Protein + Calorie Combo Breakfast", "tag": "ICMR/NIN 2024", "advice": "Choose calorie-dense balanced breakfast: paneer bhurji + roti, or idli with peanut chutney and milk.", "source": "National Institute of Nutrition", "metric": "Supports healthy weight gain"},
    {"id": "wg2", "title": "Smart Energy Add-ons", "tag": "NIN 2024", "advice": "Add nuts, seeds, banana, dates, or curd to regular meals instead of relying on junk foods.", "source": "NIN Hyderabad", "metric": "Improves daily energy intake"},
    {"id": "wg3", "title": "3 Meals + 2 Mini Meals", "tag": "ICMR Practical Tip", "advice": "Maintain regular eating intervals with two mini-meals so total intake does not stay low.", "source": "ICMR practical guidance", "metric": "Improves calorie consistency"},
    {"id": "wg4", "title": "Strength + Protein Pairing", "tag": "ICMR Fitness Guidance", "advice": "Pair resistance exercise with protein-rich meals for quality weight gain (lean mass focus).", "source": "ICMR", "metric": "Better muscle gain quality"},
    {"id": "wg5", "title": "Fortify Routine Meals", "tag": "NIN 2024", "advice": "Enrich dal/rice meals with paneer, egg, sprouts, and moderate healthy fats for nutrient density.", "source": "NIN", "metric": "Higher nutrient-calorie density"},
]


def _build_pantry_tip(expiring_items):
    if not expiring_items:
        return None
    names = " ".join(str(i.get("product_name", "")).lower() for i in expiring_items)

    if "milk" in names and "egg" in names:
        return "🥚 Your expiring milk + eggs: try a high-protein breakfast (egg whites + oats + warm milk) tomorrow morning."
    if "toor" in names or "dal" in names:
        return "📦 Your dal is expiring soon: cook methi dal/sambar batch and refrigerate portions for 2 days."
    if "spinach" in names or "palak" in names:
        return "🥬 Leafy greens expiring: make palak dal or palak omelette today to reduce nutrient loss."
    if "curd" in names or "yogurt" in names:
        return "🥣 Use curd soon: make buttermilk/raita with lunch to prevent wastage."
    return "❄️ Some items are nearing expiry. Cook high-risk perishables first and shift stable items to later meals."


profile = _get_profile()
expiring_items = _get_expiring_items()

bmi = profile.get("bmi")
health_goal = (profile.get("health_goal") or "").lower()
fitness_goal = (profile.get("fitness_goal") or "").lower()
dietary_preferences = (profile.get("dietary_preferences") or "").lower()
goal = health_goal or fitness_goal

is_weight_loss_goal = (
    "weight_loss" in goal
    or "loss" in goal
    or "lose" in goal
)
is_weight_gain_goal = (
    "muscle_gain" in goal
    or "weight_gain" in goal
    or "gain" in goal
)
is_diabetes_goal = "diab" in health_goal or "diab" in dietary_preferences
is_heart_goal = any(
    k in health_goal
    for k in ["heart", "cardio", "bp", "hypertension", "cholesterol"]
)
is_kids_goal = any(k in health_goal for k in ["kids", "child", "children"]) or any(
    k in dietary_preferences for k in ["kids", "child", "children"]
)

if is_weight_gain_goal:
    weight_label = "Weight Gain (5 tips)"
    weight_tips = WEIGHT_GAIN_TIPS
elif is_weight_loss_goal:
    weight_label = "Weight Loss (8 tips)"
    weight_tips = WEIGHT_LOSS_TIPS
else:
    weight_label = "Weight Loss (8 tips)"
    weight_tips = WEIGHT_LOSS_TIPS


def _build_personalized_tips():
    picks = []
    seen = set()

    def add_many(items, max_count=3):
        count = 0
        for item in items:
            if item["id"] in seen:
                continue
            picks.append(item)
            seen.add(item["id"])
            count += 1
            if count >= max_count:
                break

    if is_weight_gain_goal:
        add_many(WEIGHT_GAIN_TIPS, 3)
    elif is_weight_loss_goal:
        add_many(WEIGHT_LOSS_TIPS, 3)
    elif bmi is not None and bmi > 25:
        add_many(WEIGHT_LOSS_TIPS, 3)
    elif bmi is not None and bmi < 18.5:
        add_many(WEIGHT_GAIN_TIPS, 3)

    if is_diabetes_goal:
        add_many(DIABETES_TIPS, 2)
    if is_heart_goal:
        add_many(HEART_TIPS, 2)
    if is_kids_goal:
        add_many(KIDS_TIPS, 2)

    if not picks:
        add_many(WEIGHT_LOSS_TIPS, 3)
        add_many(DIABETES_TIPS, 2)

    return picks

st.title("💡 Professional Nutrition Tips - ICMR Guidelines")
st.info("Curated for Indian households | Weight loss, diabetes, heart health, kids")

st.markdown(
    """
    <style>
    .tips-hero {
        background: linear-gradient(135deg, #f6f9f4 0%, #e6f4ea 100%);
        border: 1px solid #d8eadc;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    </style>
    <div class="tips-hero">
      <strong>Clinical Content Focus:</strong> Practical, Indian-meal-friendly guidance based on ICMR/NIN framing.
    </div>
    """,
    unsafe_allow_html=True,
)

# ICMR Plate Visual
plate_df = {"Section": ["Cereals/Grains", "Vegetables", "Protein (Dal/Pulses/Paneer/Egg)"], "Share": [50, 25, 25]}
fig = px.pie(
    plate_df,
    values="Share",
    names="Section",
    title="ICMR Plate Diagram (50-25-25)",
    color_discrete_sequence=["#6aa84f", "#93c47d", "#38761d"],
)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, width="stretch")


tab_defs = [("Personalized For You", _build_personalized_tips()), (weight_label, weight_tips)]
if is_diabetes_goal:
    tab_defs.append(("Diabetes Control (7 tips)", DIABETES_TIPS))
if is_heart_goal:
    tab_defs.append(("Heart Health (5 tips)", HEART_TIPS))
if is_kids_goal:
    tab_defs.append(("Kids Nutrition (5 tips)", KIDS_TIPS))

tabs = st.tabs([t[0] for t in tab_defs])
for idx, (label, tips) in enumerate(tab_defs):
    with tabs[idx]:
        if label == "Personalized For You":
            st.info("These tips are prioritized using your profile, goals, and health preferences.")
        for tip in tips:
            _tip_card(tip, key_prefix=f"tab{idx}")

more_categories = []
if not is_diabetes_goal:
    more_categories.append(("Diabetes Control (7 tips)", DIABETES_TIPS))
if not is_heart_goal:
    more_categories.append(("Heart Health (5 tips)", HEART_TIPS))
if not is_kids_goal:
    more_categories.append(("Kids Nutrition (5 tips)", KIDS_TIPS))

if more_categories:
    st.markdown("---")
    st.subheader("More Categories")
    with st.expander("Show all categories"):
        for label, tips in more_categories:
            st.markdown(f"#### {label}")
            for tip in tips:
                _tip_card(tip, key_prefix=f"more_{label}")

if is_weight_gain_goal:
    st.success("📈 Your profile goal is **weight gain / muscle gain**. Prioritizing gain-focused tips:")
    for tip in WEIGHT_GAIN_TIPS[:3]:
        st.markdown(f"- **{tip['title']}**: {tip['metric']}")
elif is_weight_loss_goal:
    st.success("🔥 Your profile goal is **weight loss**. Prioritizing loss-focused tips:")
    for tip in WEIGHT_LOSS_TIPS[:3]:
        st.markdown(f"- **{tip['title']}**: {tip['metric']}")
elif bmi is not None and bmi > 25:
    st.success(f"🔥 Based on your BMI **{bmi}** (overweight range), prioritize these:")
    for tip in WEIGHT_LOSS_TIPS[:3]:
        st.markdown(f"- **{tip['title']}**: {tip['metric']}")
elif bmi is not None and bmi < 18.5:
    st.success(f"📈 Based on your BMI **{bmi}** (underweight range), prioritize these:")
    for tip in WEIGHT_GAIN_TIPS[:3]:
        st.markdown(f"- **{tip['title']}**: {tip['metric']}")
elif bmi is not None:
    st.info(f"📊 Your BMI is **{bmi}**. Continue with balanced meal and activity tips.")
else:
    st.info("Add height and weight in Profile to unlock stronger goal-based personalization.")

if "diab" in health_goal or "diab" in dietary_preferences:
    st.warning("🍬 Diabetes-focused mode active: prioritizing glucose-control tips for your profile.")
    for tip in DIABETES_TIPS[:3]:
        st.markdown(f"- **{tip['title']}**: {tip['metric']}")


st.markdown("---")
st.subheader("📦 Pantry-Specific Smart Tip")
pantry_tip = _build_pantry_tip(expiring_items)
if pantry_tip:
    st.success(pantry_tip)
else:
    st.info("No near-expiry pantry items right now. Tips will auto-adjust once items are close to expiry.")


st.markdown("---")
st.subheader("📊 Quick Stats")

total_tips = 25
viewed_count = len(st.session_state.viewed_tips)
applied_count = len(st.session_state.applied_tips)
favorite_count = len(st.session_state.favorite_tips)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tips Viewed", f"{viewed_count}/{total_tips}")
c2.metric("Tips Applied", applied_count)
c3.metric("Favorite Tips", favorite_count)
c4.metric("Adoption Benchmark", "87%")





