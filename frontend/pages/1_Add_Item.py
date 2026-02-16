import streamlit as st
import requests
from datetime import datetime, timedelta
from PIL import Image
import io

# Page config
st.set_page_config(page_title="Add Item", page_icon="➕", layout="wide")

# Check authentication
if 'token' not in st.session_state:
    st.warning("⚠️ Please login first!")
    st.stop()

API_URL = "http://localhost:8001"
headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.title("➕ Add Item to Pantry")

# Tabs for different input methods
tab1, tab2 = st.tabs(["📷 Scan Barcode", "✍️ Manual Entry"])

# TAB 1: Barcode Scanning
with tab1:
    st.subheader("📷 Scan Product Barcode")
    st.info("Take a photo of the product barcode to auto-fill details!")
    
    # Camera input
    camera_image = st.camera_input("Take a picture of the barcode")
    
    if camera_image:
        # Display the captured image
        st.image(camera_image, caption="Captured Image", width=300)
        
        if st.button("🔍 Scan Barcode", type="primary"):
            with st.spinner("Scanning barcode..."):
                try:
                    # Prepare file for upload
                    files = {
                        "file": ("barcode.jpg", camera_image.getvalue(), "image/jpeg")
                    }
                    
                    # Call barcode scanning API
                    response = requests.post(
                        f"{API_URL}/api/pantry/scan-barcode",
                        headers=headers,
                        files=files
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get('success'):
                            barcode = result.get('barcode')
                            product = result.get('product')
                            
                            st.success(f"✅ Barcode detected: {barcode}")
                            
                            if product and product.get('success'):
                                # Product found in database
                                st.success(f"🎉 Product found: {product['product_name']}")
                                
                                # Store in session state for form
                                st.session_state.scanned_product = {
                                    'product_name': product['product_name'],
                                    'category': product['category'],
                                    'barcode': barcode,
                                    'expiry_days': product['expiry_days'],
                                    'image_url': product.get('image_url', '')
                                }
                                
                                # Show product details
                                col1, col2 = st.columns([1, 2])
                                
                                with col1:
                                    if product.get('image_url'):
                                        st.image(product['image_url'], width=200)
                                
                                with col2:
                                    st.markdown(f"**Product:** {product['product_name']}")
                                    st.markdown(f"**Category:** {product['category']}")
                                    st.markdown(f"**Barcode:** {barcode}")
                                    st.markdown(f"**Estimated Expiry:** {product['expiry_days']} days")
                                
                                st.info("👇 Review details below and click 'Add to Pantry'")
                            else:
                                # Barcode found but no product info
                                st.warning(f"⚠️ Barcode {barcode} detected but product not found in database.")
                                st.info("Please enter product details manually below.")
                                
                                st.session_state.scanned_product = {
                                    'barcode': barcode,
                                    'product_name': '',
                                    'category': 'other'
                                }
                        else:
                            st.error(f"❌ {result.get('error', 'Failed to scan barcode')}")
                            st.info("💡 Tips: Ensure good lighting, hold phone steady, keep barcode in focus")
                    else:
                        st.error("❌ Failed to scan barcode. Please try again.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Form for scanned product
    if 'scanned_product' in st.session_state:
        st.markdown("---")
        st.subheader("📝 Confirm Product Details")
        
        scanned = st.session_state.scanned_product
        
        with st.form("scanned_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_name = st.text_input(
                    "Product Name *",
                    value=scanned.get('product_name', ''),
                    placeholder="e.g., Amul Milk"
                )
                
                category = st.selectbox(
                    "Category *",
                    options=["dairy", "fruits", "vegetables", "meat", "bakery", "beverages", "snacks", "frozen", "canned", "grains", "other"],
                    index=["dairy", "fruits", "vegetables", "meat", "bakery", "beverages", "snacks", "frozen", "canned", "grains", "other"].index(scanned.get('category', 'other'))
                )
                
                quantity = st.number_input("Quantity *", min_value=1, value=1)
                
                storage_location = st.selectbox(
                    "Storage Location",
                    ["fridge", "freezer", "pantry", "counter"]
                )
            
            with col2:
                # Calculate expiry date
                default_days = scanned.get('expiry_days', 7)
                default_expiry = datetime.now() + timedelta(days=default_days)
                
                expiry_date = st.date_input(
                    "Expiry Date *",
                    value=default_expiry,
                    min_value=datetime.now().date()
                )
                
                unit = st.selectbox(
                    "Unit",
                    ["pieces", "liters", "kg", "grams", "ml", "packets"]
                )
                
                purchase_date = st.date_input(
                    "Purchase Date",
                    value=datetime.now()
                )
            
            submit = st.form_submit_button("✅ Add to Pantry", type="primary", use_container_width=True)
            
            if submit:
                if not product_name:
                    st.error("❌ Product name is required!")
                else:
                    item_data = {
                        "product_name": product_name,
                        "category": category,
                        "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                        "quantity": quantity,
                        "unit": unit,
                        "storage_location": storage_location,
                        "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                        "barcode": scanned.get('barcode', ''),
                        "source": "barcode_scan"
                    }
                    
                    try:
                        response = requests.post(
                            f"{API_URL}/api/pantry/add",
                            json=item_data,
                            headers=headers
                        )
                        
                        if response.status_code == 201:
                            st.success("✅ Item added to pantry successfully!")
                            del st.session_state.scanned_product
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to add item: {response.text}")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# TAB 2: Manual Entry (existing code)
with tab2:
    st.subheader("✍️ Enter Details Manually")
    
    with st.form("manual_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name *", placeholder="e.g., Milk, Bread, Tomatoes")
            
            category = st.selectbox(
                "Category *",
                ["dairy", "fruits", "vegetables", "meat", "bakery", "beverages", "snacks", "frozen", "canned", "grains", "other"]
            )
            
            quantity = st.number_input("Quantity *", min_value=1, value=1)
            
            storage_location = st.selectbox(
                "Storage Location",
                ["fridge", "freezer", "pantry", "counter"]
            )
        
        with col2:
            expiry_date = st.date_input(
                "Expiry Date *",
                value=datetime.now() + timedelta(days=7),
                min_value=datetime.now().date()
            )
            
            unit = st.selectbox(
                "Unit",
                ["pieces", "liters", "kg", "grams", "ml", "packets"]
            )
            
            purchase_date = st.date_input(
                "Purchase Date",
                value=datetime.now()
            )
        
        submit_manual = st.form_submit_button("➕ Add Item", type="primary", use_container_width=True)
        
        if submit_manual:
            if not product_name:
                st.error("❌ Product name is required!")
            else:
                item_data = {
                    "product_name": product_name,
                    "category": category,
                    "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                    "quantity": quantity,
                    "unit": unit,
                    "storage_location": storage_location,
                    "purchase_date": purchase_date.strftime("%Y-%m-%d"),
                    "source": "manual"
                }
                
                try:
                    response = requests.post(
                        f"{API_URL}/api/pantry/add",
                        json=item_data,
                        headers=headers
                    )
                    
                    if response.status_code == 201:
                        st.success("✅ Item added successfully!")
                        st.balloons()
                    else:
                        st.error(f"❌ Failed to add item: {response.text}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
