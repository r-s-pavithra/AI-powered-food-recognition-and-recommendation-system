import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date


st.set_page_config(page_title="Pantry", page_icon="📦", layout="wide")


API_URL = st.secrets.get("API_URL", "http://localhost:8001")
token = st.session_state.get("token")


if not token:
    st.warning("Please login first")
    st.stop()


st.title("📦 My Pantry")


# Fetch pantry items
try:
    response = requests.get(
        f"{API_URL}/api/pantry/items",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        items = response.json()
        
        if not items:
            st.info("Your pantry is empty. Add items to start tracking!")
        else:
            st.write(f"**Total Items:** {len(items)}")
            
            # Convert to DataFrame
            df = pd.DataFrame(items)
            df['expiry_date'] = pd.to_datetime(df['expiry_date']).dt.date
            df['days_until_expiry'] = df['expiry_date'].apply(
                lambda x: (x - date.today()).days
            )
            
            # Display items
            for idx, item in df.iterrows():
                days_left = item['days_until_expiry']
                
                if days_left < 0:
                    status = "🔴 Expired"
                    color = "red"
                elif days_left <= 2:
                    status = "🟠 Urgent"
                    color = "orange"
                elif days_left <= 7:
                    status = "🟡 Warning"
                    color = "yellow"
                else:
                    status = "🟢 Safe"
                    color = "green"
                
                with st.expander(f"{item['product_name']} - {status}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Category:** {item['category']}")
                        st.write(f"**Quantity:** {item['quantity']} {item['unit']}")
                    
                    with col2:
                        st.write(f"**Expiry Date:** {item['expiry_date']}")
                        st.write(f"**Days Left:** {days_left} days")
                    
                    with col3:
                        st.write(f"**Storage:** {item.get('storage_location', 'N/A')}")
                        st.write(f"**Source:** {item['source']}")
                    
                    st.write("---")
                    
                    # Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    
                    with btn_col1:
                        if st.button("✅ Mark as Used", key=f"used_{item['id']}", help="Item was consumed/used successfully"):
                            st.session_state[f"used_modal_{item['id']}"] = True
                    
                    with btn_col2:
                        if days_left <= 3:  # Show waste button for expired/near-expiry items
                            if st.button("🚮 Mark as Wasted", key=f"waste_{item['id']}", help="Item expired or spoiled"):
                                st.session_state[f"waste_modal_{item['id']}"] = True
                    
                    with btn_col3:
                        if st.button("🗑️ Delete", key=f"delete_{item['id']}", help="Remove without tracking"):
                            delete_response = requests.delete(
                                f"{API_URL}/api/pantry/items/{item['id']}",
                                headers={"Authorization": f"Bearer {token}"}
                            )
                            if delete_response.status_code == 200:
                                st.success("✅ Item deleted!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete item")
                    
                    # MODAL: Mark as Used/Consumed
                    if st.session_state.get(f"used_modal_{item['id']}", False):
                        st.write("---")
                        st.write("### ✅ Mark as Used/Consumed")
                        
                        with st.form(key=f"used_form_{item['id']}"):
                            quantity_used = st.number_input(
                                "Quantity Used",
                                min_value=0,
                                max_value=int(item['quantity']),
                                value=int(item['quantity']),
                                key=f"qty_used_{item['id']}"
                            )
                            
                            estimated_value = st.number_input(
                                "Estimated Value Saved (₹)",
                                min_value=0.0,
                                value=0.0,
                                step=10.0,
                                key=f"value_{item['id']}"
                            )
                            
                            col_submit, col_cancel = st.columns(2)
                            
                            with col_submit:
                                submit = st.form_submit_button("✅ Confirm")
                            
                            with col_cancel:
                                cancel = st.form_submit_button("❌ Cancel")
                            
                            if submit:
                                # Log as saved item (you'll need to create this endpoint)
                                save_data = {
                                    "pantry_item_id": item['id'],
                                    "product_name": item['product_name'],
                                    "category": item['category'],
                                    "quantity": quantity_used,
                                    "unit": item['unit'],
                                    "estimated_cost": estimated_value,
                                    "expiry_date": str(item['expiry_date']),
                                    "used_date": str(date.today()),
                                    "days_before_expiry": max(0, days_left)
                                }
                                
                                # API call to log saved item
                                response = requests.post(
                                    f"{API_URL}/api/waste/log-saved",
                                    headers={"Authorization": f"Bearer {token}"},
                                    json=save_data
                                )
                                
                                if response.status_code in [200, 201]:
                                    # Delete from pantry
                                    delete_response = requests.delete(
                                        f"{API_URL}/api/pantry/items/{item['id']}",
                                        headers={"Authorization": f"Bearer {token}"}
                                    )
                                    st.success("✅ Item marked as used! 🎉")
                                    del st.session_state[f"used_modal_{item['id']}"]
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to log item")
                            
                            if cancel:
                                del st.session_state[f"used_modal_{item['id']}"]
                                st.rerun()
                    
                    # MODAL: Mark as Wasted
                    if st.session_state.get(f"waste_modal_{item['id']}", False):
                        st.write("---")
                        st.write("### 🚮 Mark as Wasted")
                        
                        with st.form(key=f"waste_form_{item['id']}"):
                            reason = st.selectbox(
                                "Reason",
                                ["expired", "spoiled", "excess", "damaged", "other"],
                                key=f"reason_{item['id']}"
                            )
                            
                            estimated_cost = st.number_input(
                                "Estimated Cost Lost (₹)",
                                min_value=0.0,
                                value=0.0,
                                step=10.0,
                                key=f"cost_{item['id']}"
                            )
                            
                            col_submit, col_cancel = st.columns(2)
                            
                            with col_submit:
                                submit = st.form_submit_button("✅ Confirm")
                            
                            with col_cancel:
                                cancel = st.form_submit_button("❌ Cancel")
                            
                            if submit:
                                # Mark as wasted
                                response = requests.post(
                                    f"{API_URL}/api/waste/mark-from-pantry/{item['id']}",
                                    headers={"Authorization": f"Bearer {token}"},
                                    params={
                                        "reason": reason,
                                        "estimated_cost": estimated_cost
                                    }
                                )
                                
                                if response.status_code == 200:
                                    st.success("✅ Item marked as wasted")
                                    del st.session_state[f"waste_modal_{item['id']}"]
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to mark as wasted")
                            
                            if cancel:
                                del st.session_state[f"waste_modal_{item['id']}"]
                                st.rerun()
    else:
        st.error("Failed to fetch pantry items")
except Exception as e:
    st.error(f"Error: {str(e)}")
