import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Waste Analytics", page_icon="📊", layout="wide")


API_URL = st.secrets.get("API_URL", "http://localhost:8000")
token = st.session_state.get("token")


if not token:
    st.warning("Please login first")
    st.stop()


headers = {"Authorization": f"Bearer {token}"}


st.title("📊 Waste & Savings Analytics")
st.write("Track your food waste and savings to reduce waste and save money!")


# Create tabs
tab1, tab2, tab3 = st.tabs(["🗑️ Waste Tracking", "✅ Items Saved", "📈 Statistics"])


# ============================================
# TAB 1: WASTE TRACKING
# ============================================
with tab1:
    st.header("🗑️ Waste Tracking")
    
    col1, col2 = st.columns([1, 2])
    
    # Log new waste item
    with col1:
        st.subheader("➕ Log Wasted Item")
        
        with st.form("log_waste_form"):
            product_name = st.text_input("Product Name*", placeholder="e.g., Milk")
            
            category = st.selectbox(
                "Category*",
                ["Dairy", "Vegetables", "Fruits", "Meat", "Grains", "Beverages", "Other"]
            )
            
            col_qty, col_unit = st.columns(2)
            with col_qty:
                quantity = st.number_input("Quantity*", min_value=1, value=1)
            with col_unit:
                unit = st.selectbox("Unit*", ["pieces", "kg", "liters", "grams", "ml"])
            
            reason = st.selectbox(
                "Reason*",
                ["expired", "spoiled", "excess", "damaged", "other"]
            )
            
            estimated_cost = st.number_input(
                "Estimated Cost (₹)",
                min_value=0.0,
                value=0.0,
                step=10.0
            )
            
            waste_date = st.date_input("Thrown Date", value=date.today())
            
            submitted = st.form_submit_button("🗑️ Log Waste", use_container_width=True, type="primary")
            
            if submitted:
                if product_name and category and quantity and unit and reason:
                    waste_data = {
                        "product_name": product_name,
                        "category": category,
                        "quantity": quantity,
                        "unit": unit,
                        "reason": reason,
                        "estimated_cost": estimated_cost,
                        "waste_date": waste_date.strftime("%Y-%m-%d")
                    }
                    
                    response = requests.post(
                        f"{API_URL}/api/waste/log",
                        headers=headers,
                        json=waste_data
                    )
                    
                    if response.status_code == 201:
                        st.success("✅ Waste logged successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to log waste")
                else:
                    st.error("Please fill in all required fields")
    
    # Display waste logs
    with col2:
        st.subheader("📋 Recent Waste Logs")
        
        try:
            response = requests.get(
                f"{API_URL}/api/waste/logs?limit=20",
                headers=headers
            )
            
            if response.status_code == 200:
                logs = response.json()
                
                if logs:
                    for log in logs:
                        with st.expander(f"🗑️ {log['product_name']} - {log['waste_date']}"):
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                st.write(f"**Category:** {log['category']}")
                                st.write(f"**Quantity:** {log['quantity']} {log['unit']}")
                                st.write(f"**Reason:** {log['reason']}")
                            
                            with col_b:
                                st.write(f"**Cost:** ₹{log['estimated_cost']}")
                                st.write(f"**Date:** {log['waste_date']}")
                            
                            if st.button(f"🗑️ Delete Log", key=f"del_waste_{log['id']}"):
                                delete_response = requests.delete(
                                    f"{API_URL}/api/waste/logs/{log['id']}",
                                    headers=headers
                                )
                                if delete_response.status_code == 200:
                                    st.success("✅ Log deleted!")
                                    st.rerun()
                else:
                    st.info("No waste logs yet. Start logging to track your waste!")
            else:
                st.error("Failed to fetch waste logs")
        except Exception as e:
            st.error(f"Error: {str(e)}")


# ============================================
# TAB 2: ITEMS SAVED
# ============================================
with tab2:
    st.header("✅ Items Saved (Used Before Expiry)")
    
    try:
        # Get saved items
        response = requests.get(
            f"{API_URL}/api/waste/saved-items?limit=50",
            headers=headers
        )
        
        if response.status_code == 200:
            saved_items = response.json()
            
            if saved_items:
                # Show stats
                total_saved = len(saved_items)
                total_value = sum(item['estimated_cost'] for item in saved_items)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Items Saved", total_saved)
                with col2:
                    st.metric("Total Value Saved", f"₹{total_value:.2f}")
                with col3:
                    avg_days = sum(item['days_before_expiry'] for item in saved_items) / len(saved_items)
                    st.metric("Avg Days Before Expiry", f"{avg_days:.1f}")
                
                st.divider()
                
                # Display saved items
                st.subheader("📋 Saved Items List")
                
                for item in saved_items:
                    with st.expander(f"✅ {item['product_name']} - Used on {item['used_date']}"):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.write(f"**Category:** {item['category']}")
                            st.write(f"**Quantity:** {item['quantity']} {item['unit']}")
                            st.write(f"**Value Saved:** ₹{item['estimated_cost']}")
                        
                        with col_b:
                            st.write(f"**Expiry Date:** {item['expiry_date']}")
                            st.write(f"**Used Date:** {item['used_date']}")
                            st.write(f"**Days Before Expiry:** {item['days_before_expiry']} days")
                        
                        # Success message
                        if item['days_before_expiry'] >= 3:
                            st.success(f"🎉 Great! Used {item['days_before_expiry']} days before expiry!")
                        elif item['days_before_expiry'] >= 0:
                            st.info(f"✅ Used just in time!")
                        else:
                            st.warning(f"⚠️ Used {abs(item['days_before_expiry'])} days after expiry")
            else:
                st.info("No saved items yet. Mark items as 'Used' from the Pantry page to track your savings!")
        else:
            st.error("Failed to fetch saved items")
    except Exception as e:
        st.error(f"Error: {str(e)}")


# ============================================
# TAB 3: STATISTICS
# ============================================
with tab3:
    st.header("📈 Statistics & Insights")
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col2:
        period = st.selectbox("Period", [7, 30, 90], format_func=lambda x: f"Last {x} days")
    
    try:
        # Get waste stats
        waste_response = requests.get(
            f"{API_URL}/api/waste/stats?days={period}",
            headers=headers
        )
        
        # Get savings stats
        savings_response = requests.get(
            f"{API_URL}/api/waste/savings-stats?days={period}",
            headers=headers
        )
        
        if waste_response.status_code == 200 and savings_response.status_code == 200:
            waste_stats = waste_response.json()
            savings_stats = savings_response.json()
            
            # Overall metrics
            st.subheader("📊 Overall Impact")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Items Wasted",
                    waste_stats['total_items_wasted'],
                    delta=f"-₹{waste_stats['total_cost']:.0f}",
                    delta_color="inverse"
                )
            
            with col2:
                st.metric(
                    "Items Saved",
                    savings_stats['total_items_saved'],
                    delta=f"+₹{savings_stats['total_value_saved']:.0f}",
                    delta_color="normal"
                )
            
            with col3:
                total_items = waste_stats['total_items_wasted'] + savings_stats['total_items_saved']
                if total_items > 0:
                    save_rate = (savings_stats['total_items_saved'] / total_items) * 100
                else:
                    save_rate = 0
                st.metric("Save Rate", f"{save_rate:.1f}%")
            
            with col4:
                net_impact = savings_stats['total_value_saved'] - waste_stats['total_cost']
                st.metric(
                    "Net Impact",
                    f"₹{abs(net_impact):.0f}",
                    delta="Profit" if net_impact > 0 else "Loss",
                    delta_color="normal" if net_impact > 0 else "inverse"
                )
            
            st.divider()
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🗑️ Waste by Category")
                if waste_stats['items_by_category']:
                    fig = px.pie(
                        names=list(waste_stats['items_by_category'].keys()),
                        values=list(waste_stats['items_by_category'].values()),
                        title="Wasted Items Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No waste data yet")
            
            with col2:
                st.subheader("✅ Saved by Category")
                if savings_stats['items_by_category']:
                    fig = px.pie(
                        names=list(savings_stats['items_by_category'].keys()),
                        values=list(savings_stats['items_by_category'].values()),
                        title="Saved Items Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No saved items data yet")
            
            # Waste reasons
            if waste_stats['items_by_reason']:
                st.subheader("🔍 Waste Reasons")
                fig = px.bar(
                    x=list(waste_stats['items_by_reason'].keys()),
                    y=list(waste_stats['items_by_reason'].values()),
                    labels={'x': 'Reason', 'y': 'Count'},
                    title="Why Food Gets Wasted"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Top wasted items
            if waste_stats['top_wasted_items']:
                st.subheader("⚠️ Most Wasted Items")
                df = pd.DataFrame(waste_stats['top_wasted_items'])
                st.dataframe(
                    df[['product', 'count', 'cost']],
                    column_config={
                        "product": "Product",
                        "count": "Times Wasted",
                        "cost": st.column_config.NumberColumn("Total Cost", format="₹%.2f")
                    },
                    hide_index=True,
                    use_container_width=True
                )
        else:
            st.error("Failed to load statistics")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")


# Tips section
st.divider()
st.subheader("💡 Tips to Reduce Waste")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("🥬 **Plan Meals**\n\nPlan your meals weekly to buy only what you need")

with col2:
    st.info("❄️ **Store Properly**\n\nStore food correctly to extend shelf life")

with col3:
    st.info("🔄 **First In, First Out**\n\nUse older items before newer ones")
