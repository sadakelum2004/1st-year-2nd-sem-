# pharmacy.py
import streamlit as st
from utils import *
import re
from datetime import datetime


def validate_email(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """Validate phone number contains exactly 10 digits"""
    return phone.isdigit() and len(phone) == 10


def validate_id_number(id_str, field_name):
    """Validate ID numbers to be exactly 10 characters (alphanumeric)"""
    if len(id_str) != 10:
        return f"{field_name} must be exactly 10 characters long"
    if not id_str.isalnum():
        return f"{field_name} must contain only letters and numbers"
    return None


def pharmacy_registration():
    """Pharmacy registration page"""
    display_header()
    st.subheader("💊 Pharmacy Registration")

    if st.button("< Back to Main", key="back_to_main_pharmacy_reg"):
        st.session_state.page = "main"
        st.rerun()

    with st.form("pharmacy_registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            pharmacy_name = st.text_input("Pharmacy Name*", key="pharmacy_name")
            br_number = st.text_input("BR Number*", key="pharmacy_br",
                                      max_chars=10,
                                      help="Must be exactly 10 characters")
            sl_pharmacy_id = st.text_input("SL Pharmacy Council Registration ID*",
                                           key="pharmacy_sl_id",
                                           max_chars=10,
                                           help="Must be exactly 10 characters")
            owner_name = st.text_input("Owner Name*", key="pharmacy_owner")

        with col2:
            phone = st.text_input("Contact Number*", key="pharmacy_phone",
                                  max_chars=10,
                                  help="Must be exactly 10 digits")
            email = st.text_input("Email*", key="pharmacy_email")

            all_cities = get_all_cities()
            city = st.selectbox("City*", ["Select"] + all_cities, key="pharmacy_city")

        address = st.text_area("Address*", key="pharmacy_address")
        password = st.text_input("Password*", type="password", key="pharmacy_password")
        confirm_password = st.text_input("Confirm Password*", type="password",
                                         key="pharmacy_confirm_password")

        submitted = st.form_submit_button("Register Pharmacy", use_container_width=True, type="primary")

        if submitted:
            validation_errors = []

            # Check required fields
            if not all([pharmacy_name, br_number, sl_pharmacy_id, owner_name, phone, email, address, password,
                        confirm_password, city]):
                validation_errors.append("Please fill in all required fields (*)")

            # Validate BR Number (10 characters)
            br_validation_error = validate_id_number(br_number, "BR Number")
            if br_validation_error:
                validation_errors.append(br_validation_error)

            # Validate SL Pharmacy Council Registration ID (10 characters)
            sl_id_validation_error = validate_id_number(sl_pharmacy_id, "SL Pharmacy Council Registration ID")
            if sl_id_validation_error:
                validation_errors.append(sl_id_validation_error)

            # Validate phone number (10 digits)
            if not validate_phone(phone):
                validation_errors.append("Phone number must contain exactly 10 digits")

            # Validate email format
            if email and not validate_email(email):
                validation_errors.append("Please enter a valid email address (e.g., example@domain.com)")

            # Password validation
            if password != confirm_password:
                validation_errors.append("Passwords do not match")

            if len(password) < 6:
                validation_errors.append("Password must be at least 6 characters long")

            # City validation
            if city == "Select":
                validation_errors.append("Please select city")

            # Check for duplicate phone number
            if phone and validate_phone(phone):
                if any(pharmacy.get("phone") == phone for pharmacy in st.session_state.app.data["pharmacies"]):
                    validation_errors.append("Phone number already registered. Please login.")

            # Check for duplicate email
            if email and validate_email(email):
                if any(pharmacy.get("email") == email for pharmacy in st.session_state.app.data["pharmacies"]):
                    validation_errors.append("Email already registered. Please login.")

            # Check for duplicate BR number
            if br_number and not br_validation_error:
                if any(pharmacy.get("br_number") == br_number for pharmacy in st.session_state.app.data["pharmacies"]):
                    validation_errors.append("BR Number already registered.")

            # Check for duplicate SL Pharmacy ID
            if sl_pharmacy_id and not sl_id_validation_error:
                if any(pharmacy.get("sl_pharmacy_id") == sl_pharmacy_id for pharmacy in
                       st.session_state.app.data["pharmacies"]):
                    validation_errors.append("SL Pharmacy Council Registration ID already registered.")

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                return

            # All validations passed - proceed with registration
            username = st.session_state.app.generate_username(pharmacy_name, phone)

            new_pharmacy = {
                "id": st.session_state.app.generate_id("pharm"),
                "name": pharmacy_name,
                "br_number": br_number,
                "sl_pharmacy_id": sl_pharmacy_id,
                "owner_name": owner_name,
                "phone": phone,
                "email": email,
                "city": city,
                "address": address,
                "username": username,
                "password": password,
                "verified": True,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "commission_records": []  # New field for tracking commissions
            }

            st.session_state.app.data['pharmacies'].append(new_pharmacy)
            st.session_state.app.save_data('pharmacies')

            st.success(f"✅ Pharmacy Registration Successful! Username: {username}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Go to Login", use_container_width=True, key="go_to_login_pharmacy", type="primary"):
                    st.session_state.page = "pharmacy_login"
                    st.rerun()
            with col2:
                if st.button("Back to Main", use_container_width=True, key="back_to_main_pharmacy"):
                    st.session_state.page = "main"
                    st.rerun()


def pharmacy_login():
    """Pharmacy login page"""
    display_header()
    st.subheader("💊 Pharmacy Login")

    if st.button("< Back to Main", key="back_to_main_pharmacy_login"):
        st.session_state.page = "main"
        st.rerun()

    if st.button("New Pharmacy? Register Here", key="new_pharmacy_register"):
        st.session_state.page = "pharmacy_register"
        st.rerun()

    with st.form("pharmacy_login_form"):
        login_id = st.text_input("Phone Number or BR Number", key="pharmacy_login_input")
        password = st.text_input("Password", type="password", key="pharmacy_login_password")

        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            if not login_id or not password:
                st.error("Please enter both login ID and password")
                return

            pharmacy = None
            for pharm in st.session_state.app.data['pharmacies']:
                if (pharm.get("phone") == login_id or pharm.get("br_number") == login_id) and pharm.get(
                        "password") == password:
                    pharmacy = pharm
                    break

            if pharmacy:
                st.session_state.current_user = pharmacy
                st.session_state.user_type = "pharmacy"
                st.session_state.page = "pharmacy_dashboard"
                st.success(f"Welcome back, {pharmacy['name']}! 💊")
                st.rerun()
            else:
                st.error("Invalid login credentials")


def pharmacy_dashboard():
    """Pharmacy dashboard"""
    display_header()

    st.sidebar.title(f"💊 {st.session_state.current_user['name']}")
    st.sidebar.subheader("Pharmacy Dashboard")

    nav_options = {
        "🏠 Home Page ": "overview",
        "📦 Inventory Management": "inventory",
        "📋 Prescription Requests": "prescriptions",
        "💊 Medicine Catalog": "catalog",
        "💬 Patient Messages": "chats",
        "🔔 Notifications": "notifications",
        "💰 Commission Reports": "commission_reports"  # New option
    }

    for option, page in nav_options.items():
        if st.sidebar.button(option, use_container_width=True, key=f"pharm_nav_{page}"):
            st.session_state.dashboard_page = page

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True, key="pharmacy_logout"):
        st.session_state.current_user = None
        st.session_state.user_type = None
        st.session_state.page = "main"
        st.rerun()

    if st.session_state.dashboard_page == "overview":
        pharmacy_dashboard_overview()
    elif st.session_state.dashboard_page == "inventory":
        manage_inventory()
    elif st.session_state.dashboard_page == "prescriptions":
        view_shared_prescriptions_pharmacy()
    elif st.session_state.dashboard_page == "catalog":
        manage_medicine_catalog()
    elif st.session_state.dashboard_page == "chats":
        view_pharmacy_chats()
    elif st.session_state.dashboard_page == "notifications":
        view_notifications()
    elif st.session_state.dashboard_page == "commission_reports":
        pharmacy_commission_reports()  # New function


def pharmacy_dashboard_overview():
    """Pharmacy dashboard overview"""
    st.subheader("🏠 Pharmacy Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        inventory_count = len([inv for inv in st.session_state.app.data['inventory']
                               if inv['pharmacy_id'] == st.session_state.current_user['id']])
        st.metric("Inventory Items", inventory_count)

    with col2:
        shared_prescriptions = len([pp for pp in st.session_state.app.data['prescription_pharmacy']
                                    if pp['pharmacy_id'] == st.session_state.current_user['id']])
        st.metric("Prescription Requests", shared_prescriptions)

    with col3:
        pending_prescriptions = len([pp for pp in st.session_state.app.data['prescription_pharmacy']
                                     if pp['pharmacy_id'] == st.session_state.current_user['id']
                                     and pp['status'] in ['shared', 'availability_checked']])
        st.metric("Pending Requests", pending_prescriptions)

    with col4:
        unread_chats = len([chat for chat in st.session_state.app.data['chats']
                            if chat['sender_type'] == 'patient'
                            and any(pp for pp in st.session_state.app.data['prescription_pharmacy']
                                    if pp['id'] == chat.get('prescription_pharmacy_id')
                                    and pp['pharmacy_id'] == st.session_state.current_user['id'])
                            and not chat.get('read', False)])
        st.metric("Unread Messages", unread_chats)

    # Low stock alert
    st.write("### 🔴 Low Stock Alert")
    low_stock_items = [inv for inv in st.session_state.app.data['inventory']
                       if inv['pharmacy_id'] == st.session_state.current_user['id']
                       and inv['quantity'] < 10]

    if low_stock_items:
        for item in low_stock_items:
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.warning(f"**{item['medicine_name']}** - {item['medicine_dose']}")
                with col2:
                    st.write(f"Current Stock: **{item['quantity']}**")
                with col3:
                    if st.button("Restock", key=f"restock_{item['id']}"):
                        st.session_state.selected_inventory_item = item
                        st.session_state.dashboard_page = "inventory"
                        st.rerun()
    else:
        st.success("✅ All items are sufficiently stocked")

    # Recent prescription requests
    st.write("### 📋 Recent Prescription Requests")
    shared_prescriptions = [pp for pp in st.session_state.app.data['prescription_pharmacy']
                            if pp['pharmacy_id'] == st.session_state.current_user['id']]

    if shared_prescriptions:
        recent_shared = sorted(shared_prescriptions, key=lambda x: x['shared_date'], reverse=True)[:5]
        for shared in recent_shared:
            prescription = next((p for p in st.session_state.app.data['prescriptions']
                                 if p['id'] == shared['prescription_id']), None)
            patient = next((p for p in st.session_state.app.data['patients']
                            if p['id'] == shared['patient_id']), None)

            if prescription and patient:
                status_color = {
                    'shared': '🔴',
                    'availability_checked': '🟡',
                    'quotation_sent': '🔵',
                    'completed': '🟢'
                }.get(shared['status'], '⚪')

                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"{status_color} **{patient['name']}**")
                        st.write(f"*{prescription['date']}*")
                    with col2:
                        status_text = shared['status'].replace('_', ' ').title()
                        st.write(f"**Status:** {status_text}")
                    with col3:
                        if st.button("View", key=f"view_{shared['id']}"):
                            st.session_state.selected_prescription = shared
                            st.session_state.dashboard_page = "prescriptions"
                            st.rerun()
                    st.markdown("---")
    else:
        st.info("No prescription requests yet")


def mark_prescription_complete(shared, patient):
    """Mark prescription as completed and record commission"""
    shared['status'] = 'completed'
    shared['completed_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Record commission for completed prescription
    record_pharmacy_commission(shared)

    st.session_state.app.save_data('prescription_pharmacy')

    # Send notification
    notification = {
        "id": st.session_state.app.generate_id("notif"),
        "patient_id": shared['patient_id'],
        "message": f"Your prescription has been completed by {st.session_state.current_user['name']}",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False,
        "type": "prescription_completed"
    }
    st.session_state.app.data['notifications'].append(notification)
    st.session_state.app.save_data('notifications')

    st.success("✅ Prescription marked as completed!")
    st.rerun()


def record_pharmacy_commission(shared_prescription):
    """Record 5% commission for completed prescription"""
    pharmacy_id = shared_prescription["pharmacy_id"]
    pharmacy = next((pharm for pharm in st.session_state.app.data['pharmacies'] if pharm['id'] == pharmacy_id), None)

    if pharmacy and shared_prescription.get('quotation_amount', 0) > 0:
        commission_amount = shared_prescription['quotation_amount'] * 0.05  # 5% commission

        commission_record = {
            "prescription_id": shared_prescription["prescription_id"],
            "patient_name": shared_prescription["patient_name"],
            "completion_date": shared_prescription.get("completed_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "quotation_amount": shared_prescription['quotation_amount'],
            "commission_amount": commission_amount,
            "commission_rate": "5%",
            "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if "commission_records" not in pharmacy:
            pharmacy["commission_records"] = []
        pharmacy["commission_records"].append(commission_record)
        st.session_state.app.save_data('pharmacies')


def pharmacy_commission_reports():
    """Pharmacy commission reports for completed prescriptions"""
    st.subheader("💰 Commission Reports")

    pharmacy = st.session_state.current_user
    commission_records = pharmacy.get("commission_records", [])

    if not commission_records:
        st.info("No commission records found. Complete prescriptions to earn commissions.")
        return

    # Monthly report
    st.write("### Monthly Commission Report")

    # Group commissions by month
    monthly_commissions = {}
    for record in commission_records:
        month_year = datetime.strptime(record["completion_date"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m")
        if month_year not in monthly_commissions:
            monthly_commissions[month_year] = []
        monthly_commissions[month_year].append(record)

    # Display monthly summary
    for month, month_commissions in sorted(monthly_commissions.items(), reverse=True):
        total_commission = sum(record["commission_amount"] for record in month_commissions)
        total_sales = sum(record["quotation_amount"] for record in month_commissions)

        with st.expander(f"📅 {datetime.strptime(month, '%Y-%m').strftime('%B %Y')} - Rs. {total_commission:.2f}"):
            st.write(f"**Total Prescriptions:** {len(month_commissions)}")
            st.write(f"**Total Sales:** Rs. {total_sales:.2f}")
            st.write(f"**Total Commission (5%):** Rs. {total_commission:.2f}")

            # Display individual commissions
            for record in month_commissions:
                st.write(
                    f"- {record['completion_date'][:10]}: {record['patient_name']} - Sales: Rs. {record['quotation_amount']:.2f}, Commission: Rs. {record['commission_amount']:.2f}")

    # Overall statistics
    st.write("### Overall Statistics")
    col1, col2, col3, col4 = st.columns(4)

    total_commission = sum(record["commission_amount"] for record in commission_records)
    total_sales = sum(record["quotation_amount"] for record in commission_records)
    total_prescriptions = len(commission_records)

    with col1:
        st.metric("Total Prescriptions", total_prescriptions)
    with col2:
        st.metric("Total Sales", f"Rs. {total_sales:.2f}")
    with col3:
        st.metric("Total Commission", f"Rs. {total_commission:.2f}")
    with col4:
        st.metric("Pending Commission", f"Rs. {total_commission:.2f}")


def manage_inventory():
    """Manage pharmacy inventory"""
    st.subheader("📦 Inventory Management")

    tab1, tab2, tab3 = st.tabs(["➕ Add Medicine", "📋 Current Inventory", "📊 Stock Analytics"])

    with tab1:
        add_medicine_to_inventory()

    with tab2:
        view_current_inventory()

    with tab3:
        show_inventory_analytics()


def add_medicine_to_inventory():
    """Add medicine to inventory"""
    st.write("### Add Medicine to Inventory")

    method = st.radio("Select Method:", ["Use Existing Medicine", "Add New Medicine"], horizontal=True)

    if method == "Use Existing Medicine":
        with st.form("add_existing_medicine_form"):
            col1, col2 = st.columns(2)

            with col1:
                # Search existing medicines
                medicine_search = st.text_input("🔍 Search Medicine by Name")
                if medicine_search:
                    filtered_medicines = [m for m in st.session_state.app.data['medicines']
                                          if medicine_search.lower() in m['name'].lower()]
                    if filtered_medicines:
                        medicine_options = {f"{m['name']} - {m['dose']} ({m['type']})": m for m in filtered_medicines}
                        selected_medicine_label = st.selectbox("Select Medicine",
                                                               list(medicine_options.keys()))
                        selected_medicine = medicine_options[selected_medicine_label]
                    else:
                        st.info("No matching medicines found")
                        selected_medicine = None
                else:
                    medicine_options = {f"{m['name']} - {m['dose']} ({m['type']})": m for m in
                                        st.session_state.app.data['medicines'][:20]}
                    selected_medicine_label = st.selectbox("Select Medicine", list(medicine_options.keys()))
                    selected_medicine = medicine_options[selected_medicine_label]

            with col2:
                quantity = st.number_input("Quantity*", min_value=1, value=1)
                unit_price = st.number_input("Unit Price (Rs.)*", min_value=0.0, value=0.0, step=0.5)
                expiry_date = st.date_input("Expiry Date*", min_value=datetime.now())
                batch_number = st.text_input("Batch Number (Optional)")

            submitted = st.form_submit_button("Add to Inventory", use_container_width=True, type="primary")

            if submitted:
                if not selected_medicine or quantity <= 0 or unit_price <= 0:
                    st.error("Please fill in all required fields")
                    return

                success, message = st.session_state.app.add_medicine_to_inventory(
                    st.session_state.current_user["id"],
                    selected_medicine["id"],
                    quantity,
                    unit_price,
                    expiry_date.strftime("%Y-%m-%d"),
                    batch_number
                )

                if success:
                    st.success("✅ " + message)
                else:
                    st.error("❌ " + message)

    else:  # Add New Medicine
        with st.form("add_new_medicine_form"):
            st.write("**Add New Medicine to System**")
            col1, col2 = st.columns(2)

            with col1:
                new_medicine_name = st.text_input("Medicine Name*")
                new_medicine_type = st.selectbox("Type*",
                                                 ["tablet", "capsule", "syrup", "injection", "ointment", "cream",
                                                  "inhaler", "drops", "spray", "other"])
                new_medicine_dose = st.text_input("Dose/Strength* (e.g., 500mg, 100ml)")
                new_medicine_category = st.selectbox("Category*", [
                    "Pain Relief", "Antibiotic", "Allergy", "Diabetes", "Cardiovascular",
                    "Gastrointestinal", "Respiratory", "Vitamin", "Antifungal", "Skin Care", "Other"
                ])

            with col2:
                new_medicine_price = st.number_input("Common Price (Rs.)*", min_value=0.0, value=0.0, step=0.5)
                quantity = st.number_input("Quantity*", min_value=1, value=1)
                unit_price = st.number_input("Your Price (Rs.)*", min_value=0.0, value=0.0, step=0.5)
                expiry_date = st.date_input("Expiry Date*", min_value=datetime.now())
                batch_number = st.text_input("Batch Number (Optional)")

            submitted = st.form_submit_button("Add New Medicine to Inventory",
                                              use_container_width=True, type="primary")

            if submitted:
                if not all([new_medicine_name, new_medicine_dose]):
                    st.error("Please fill in all required fields")
                    return

                # Create new medicine
                new_medicine_data = {
                    "name": new_medicine_name,
                    "type": new_medicine_type,
                    "dose": new_medicine_dose,
                    "category": new_medicine_category,
                    "common_price": new_medicine_price
                }

                success, message = st.session_state.app.add_new_medicine(new_medicine_data)

                if success:
                    # Get the newly created medicine ID
                    new_medicine = next((m for m in st.session_state.app.data["medicines"]
                                         if m['name'] == new_medicine_name and m['dose'] == new_medicine_dose),
                                        None)

                    if new_medicine:
                        # Add to inventory
                        inv_success, inv_message = st.session_state.app.add_medicine_to_inventory(
                            st.session_state.current_user["id"],
                            new_medicine["id"],
                            quantity,
                            unit_price,
                            expiry_date.strftime("%Y-%m-%d"),
                            batch_number
                        )

                        if inv_success:
                            st.success("✅ New medicine added to system and inventory!")
                        else:
                            st.error("❌ " + inv_message)
                    else:
                        st.error("❌ Failed to find the newly created medicine")
                else:
                    st.error("❌ " + message)


def view_current_inventory():
    """Display current inventory"""
    st.write("#### Current Inventory")
    pharmacy_inventory = [inv for inv in st.session_state.app.data['inventory']
                          if inv['pharmacy_id'] == st.session_state.current_user['id']]

    if not pharmacy_inventory:
        st.info("No items in inventory yet.")
        return

    # Search and filter
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 Search Medicine")
    with col2:
        stock_filter = st.selectbox("Stock Status", ["All", "In Stock", "Low Stock", "Out of Stock"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Quantity", "Price", "Expiry Date"])

    filtered_inventory = pharmacy_inventory
    if search_term:
        filtered_inventory = [inv for inv in filtered_inventory
                              if search_term.lower() in inv['medicine_name'].lower()]

    if stock_filter == "Low Stock":
        filtered_inventory = [inv for inv in filtered_inventory if 0 < inv['quantity'] <= 10]
    elif stock_filter == "Out of Stock":
        filtered_inventory = [inv for inv in filtered_inventory if inv['quantity'] == 0]
    elif stock_filter == "In Stock":
        filtered_inventory = [inv for inv in filtered_inventory if inv['quantity'] > 10]

    # Sort inventory
    if sort_by == "Name":
        filtered_inventory.sort(key=lambda x: x['medicine_name'])
    elif sort_by == "Quantity":
        filtered_inventory.sort(key=lambda x: x['quantity'])
    elif sort_by == "Price":
        filtered_inventory.sort(key=lambda x: x['unit_price'])
    elif sort_by == "Expiry Date":
        filtered_inventory.sort(key=lambda x: x.get('expiry_date', '9999-12-31'))

    # Display inventory
    for item in filtered_inventory:
        stock_status = "🟢" if item['quantity'] > 10 else "🟡" if item['quantity'] > 0 else "🔴"
        stock_text = "In Stock" if item['quantity'] > 10 else "Low Stock" if item['quantity'] > 0 else "Out of Stock"

        with st.expander(f"{stock_status} {item['medicine_name']} - {item['medicine_dose']} ({stock_text})"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**Quantity:** {item['quantity']}")
                st.write(f"**Type:** {item['medicine_type'].title()}")
                st.write(
                    f"**Category:** {next((m.get('category', 'Unknown') for m in st.session_state.app.data['medicines'] if m['id'] == item['medicine_id']), 'Unknown')}")

            with col2:
                st.write(f"**Unit Price:** Rs. {item['unit_price']:.2f}")
                st.write(f"**Expiry Date:** {item.get('expiry_date', 'Not set')}")
                if item.get('batch_number'):
                    st.write(f"**Batch No:** {item['batch_number']}")

            with col3:
                days_until_expiry = None
                if item.get('expiry_date'):
                    try:
                        expiry = datetime.strptime(item['expiry_date'], "%Y-%m-%d")
                        days_until_expiry = (expiry - datetime.now()).days
                        if days_until_expiry < 30:
                            st.error(f"⚠️ Expires in {days_until_expiry} days")
                        elif days_until_expiry < 90:
                            st.warning(f"📅 Expires in {days_until_expiry} days")
                        else:
                            st.success(f"✅ Expires in {days_until_expiry} days")
                    except:
                        pass

            # Quick actions
            col1, col2, col3 = st.columns(3)
            with col1:
                new_quantity = st.number_input("Update Quantity", value=item['quantity'],
                                               min_value=0, key=f"qty_{item['id']}")
            with col2:
                new_price = st.number_input("Update Price", value=float(item['unit_price']),
                                            min_value=0.0, step=0.5, key=f"price_{item['id']}")
            with col3:
                if st.button("Update", key=f"update_{item['id']}", type="primary"):
                    item['quantity'] = new_quantity
                    item['unit_price'] = new_price
                    item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.app.save_data('inventory')
                    st.success("✅ Inventory updated!")
                    st.rerun()


def show_inventory_analytics():
    """Show inventory analytics"""
    st.write("#### 📊 Inventory Analytics")

    pharmacy_inventory = [inv for inv in st.session_state.app.data['inventory']
                          if inv['pharmacy_id'] == st.session_state.current_user['id']]

    if not pharmacy_inventory:
        st.info("No inventory data to analyze.")
        return

    # Calculate metrics
    total_items = len(pharmacy_inventory)
    total_value = sum(inv['quantity'] * inv['unit_price'] for inv in pharmacy_inventory)
    low_stock_count = len([inv for inv in pharmacy_inventory if 0 < inv['quantity'] <= 10])
    out_of_stock_count = len([inv for inv in pharmacy_inventory if inv['quantity'] == 0])

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", total_items)
    with col2:
        st.metric("Total Inventory Value", f"Rs. {total_value:.2f}")
    with col3:
        st.metric("Low Stock Items", low_stock_count)
    with col4:
        st.metric("Out of Stock", out_of_stock_count)

    # Category distribution
    st.write("### 📈 Stock by Category")
    category_counts = {}

    for inv in pharmacy_inventory:
        medicine = next((m for m in st.session_state.app.data["medicines"] if m['id'] == inv["medicine_id"]), None)
        if medicine:
            category = medicine.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1

    if category_counts:
        for category, count in category_counts.items():
            st.write(f"- **{category}:** {count} items")
    else:
        st.info("No category data available.")


def view_shared_prescriptions_pharmacy():
    """View prescriptions shared with pharmacy"""
    st.subheader("📋 Prescription Requests")

    shared_prescriptions = [pp for pp in st.session_state.app.data["prescription_pharmacy"]
                            if pp["pharmacy_id"] == st.session_state.current_user['id']]

    if not shared_prescriptions:
        st.info("No prescription requests received yet.")
        return

    # Tabs for different statuses
    tab1, tab2, tab3 = st.tabs(["🆕 New Requests", "🔄 In Progress", "✅ Completed"])

    with tab1:
        new_prescriptions = [pp for pp in shared_prescriptions if pp['status'] == 'shared']
        if new_prescriptions:
            for shared in new_prescriptions:
                display_prescription_request(shared, "new")
        else:
            st.info("No new prescription requests.")

    with tab2:
        in_progress_prescriptions = [pp for pp in shared_prescriptions if
                                     pp['status'] in ['availability_checked', 'quotation_sent']]

        if in_progress_prescriptions:
            for shared in in_progress_prescriptions:
                display_prescription_request(shared, "in_progress")
        else:
            st.info("No prescriptions in progress.")

    with tab3:
        completed_prescriptions = [pp for pp in shared_prescriptions if pp['status'] == 'completed']
        if completed_prescriptions:
            for shared in completed_prescriptions:
                display_prescription_request(shared, "completed")
        else:
            st.info("No completed prescriptions.")


def display_prescription_request(shared, request_type):
    """Display prescription request with appropriate actions"""
    prescription = next((p for p in st.session_state.app.data['prescriptions']
                         if p['id'] == shared['prescription_id']), None)
    patient = next((p for p in st.session_state.app.data['patients']
                    if p['id'] == shared['patient_id']), None)

    if not prescription or not patient:
        return

    status_config = {
        'shared': {'color': 'red', 'icon': '🆕', 'text': 'New Request'},
        'availability_checked': {'color': 'orange', 'icon': '🔄', 'text': 'Availability Checked'},
        'quotation_sent': {'color': 'blue', 'icon': '💰', 'text': 'Quotation Sent'},
        'completed': {'color': 'green', 'icon': '✅', 'text': 'Completed'}
    }

    status_info = status_config.get(shared['status'], {'color': 'gray', 'icon': '⚪', 'text': shared['status']})

    with st.container():
        st.markdown(f"### {status_info['icon']} {patient['name']} - :{status_info['color']}[{status_info['text']}]")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**👤 Patient Information**")
            st.write(f"**Name:** {patient['name']}")
            st.write(f"**Contact:** {patient.get('phone', 'N/A')}")
            st.write(f"**Location:** {patient.get('city', 'N/A')}")
            st.write(f"**Request Date:** {shared['shared_date']}")

        with col2:
            st.write("**📄 Prescription Details**")
            st.write(f"**Doctor:** Dr. {prescription['doctor_name']}")
            st.write(f"**Date:** {prescription['date']}")
            st.write(f"**Medicines:** {len(prescription['medicines'])} items")
            if shared.get('quotation_amount', 0) > 0:
                st.write(f"**Quotation:** Rs. {shared['quotation_amount']:.2f}")

        # Medicine availability
        st.write("**💊 Medicine Availability & Pricing**")
        display_medicine_availability_pricing(prescription, shared)

        # Action buttons based on status
        if request_type == "new":
            st.write("**Actions:**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔍 Check Availability & Price", key=f"check_{shared['id']}", type="primary",
                             use_container_width=True):
                    check_and_update_availability(prescription, shared, patient)
            with col2:
                if st.button("💬 Send Message", key=f"msg_{shared['id']}", use_container_width=True):
                    st.session_state.selected_prescription_chat = shared
                    st.session_state.dashboard_page = "chats"
                    st.rerun()

        elif request_type == "in_progress":
            st.write("**Actions:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Update Availability", key=f"update_avail_{shared['id']}", use_container_width=True):
                    check_and_update_availability(prescription, shared, patient)
            with col2:
                if st.button("💰 Send Quotation", key=f"quote_{shared['id']}", type="primary", use_container_width=True):
                    generate_quotation(prescription, shared, patient)
            with col3:
                if st.button("✅ Mark Complete", key=f"complete_{shared['id']}", use_container_width=True):
                    mark_prescription_complete(shared, patient)

        elif request_type == "completed":
            st.success("✅ This prescription request has been completed.")
            if shared.get('pharmacy_comment'):
                st.write(f"**Final Note:** {shared['pharmacy_comment']}")

        st.markdown("---")


def display_medicine_availability_pricing(prescription, shared):
    """Display medicine availability with pricing information"""
    total_estimated = 0
    all_available = True

    for i, med in enumerate(prescription['medicines']):
        inventory_item = next((inv for inv in st.session_state.app.data['inventory']
                               if inv['pharmacy_id'] == st.session_state.current_user['id']
                               and inv['medicine_id'] == med['id']), None)

        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

        with col1:
            st.write(f"**{med['name']}**")
            st.write(f"**{med['dosage']}**")

        with col2:
            st.write(f"**Required:** {med['quantity']}")
            if inventory_item:
                st.write(f"**Available:** {inventory_item['quantity']}")
            else:
                st.write("**Available:** 0")

        with col3:
            if inventory_item:
                price = inventory_item['unit_price']
                st.write(f"**Price:** Rs. {price:.2f}")
            else:
                price = 0
                st.write("**Price:** N/A")

        with col4:
            if inventory_item:
                item_total = price * med['quantity']
                total_estimated += item_total
                if inventory_item['quantity'] >= med['quantity']:
                    st.success("✅ In Stock")
                    st.write(f"**Total:** Rs. {item_total:.2f}")
                else:
                    st.error(f"❌ Low Stock")
                    all_available = False
                    st.write(f"**Total:** Rs. {item_total:.2f}")
            else:
                st.error("❌ Out of Stock")
                all_available = False

        with col5:
            if inventory_item and inventory_item['quantity'] < med['quantity']:
                st.button("📦 Restock", key=f"restock_{shared['id']}_{i}",
                          on_click=lambda sid=shared['id']: handle_restock(sid))

    # Total estimation
    st.write(f"**💰 Estimated Total: Rs. {total_estimated:.2f}**")

    if not all_available:
        st.warning("⚠️ Some medicines are not fully available. Please check stock levels.")


def handle_restock(shared_id):
    """Handle restock action"""
    st.session_state.dashboard_page = "inventory"
    st.rerun()


def check_and_update_availability(prescription, shared, patient):
    """Check and update medicine availability"""
    is_available, unavailable_meds = st.session_state.app.check_medicine_availability(
        prescription['id'], st.session_state.current_user['id'])

    # Update status
    shared['status'] = 'availability_checked'
    if is_available:
        shared['pharmacy_comment'] = "All medicines are available and ready for purchase"
    else:
        shared['pharmacy_comment'] = f"Some medicines unavailable: {', '.join(unavailable_meds)}"

    shared['comment_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.session_state.app.save_data('prescription_pharmacy')

    # Send notification to patient
    notification = {
        "id": st.session_state.app.generate_id("notif"),
        "patient_id": shared['patient_id'],
        "message": f"{st.session_state.current_user['name']} checked your prescription availability",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False,
        "type": "availability_update"
    }

    st.session_state.app.data['notifications'].append(notification)
    st.session_state.app.save_data('notifications')

    st.success("✅ Availability checked and patient notified!")
    st.rerun()


def generate_quotation(prescription, shared, patient):
    """Generate quotation for prescription"""
    st.subheader("💰 Generate Quotation")

    total_price = 0
    quotation_items = []

    for med in prescription['medicines']:
        inventory_item = next((inv for inv in st.session_state.app.data['inventory']
                               if inv['pharmacy_id'] == st.session_state.current_user['id']
                               and inv['medicine_id'] == med['id']), None)

        if inventory_item and inventory_item['quantity'] >= med['quantity']:
            item_total = inventory_item['unit_price'] * med['quantity']
            total_price += item_total
            quotation_items.append({
                'medicine': med['name'],
                'dosage': med['dosage'],
                'quantity': med['quantity'],
                'unit_price': inventory_item['unit_price'],
                'total': item_total,
                'available': True
            })
        else:
            quotation_items.append({
                'medicine': med['name'],
                'dosage': med['dosage'],
                'quantity': med['quantity'],
                'unit_price': 0,
                'total': 0,
                'available': False
            })

    # Display quotation breakdown
    st.write("### Quotation Breakdown")
    for item in quotation_items:
        status = "✅ Available" if item['available'] else "❌ Not Available"
        st.write(
            f"**{item['medicine']}** ({item['dosage']}) - {item['quantity']} x Rs. {item['unit_price']:.2f} = Rs. {item['total']:.2f} - {status}")

    st.write(f"#### **Total Amount: Rs. {total_price:.2f}**")

    # Additional comments and delivery options
    col1, col2 = st.columns(2)
    with col1:
        comment = st.text_area("Additional Comments for Patient",
                               value=shared.get('pharmacy_comment', ''),
                               placeholder="E.g.: Ready for pickup, delivery available, etc.")
    with col2:
        delivery_option = st.selectbox("Delivery Option",
                                       ["Patient Pickup", "Home Delivery", "Both Options Available"])
        if delivery_option in ["Home Delivery", "Both Options Available"]:
            delivery_fee = st.number_input("Delivery Fee (Rs.)", min_value=0.0, value=0.0, step=50.0)
            total_price += delivery_fee
            st.write(f"**Final Total with Delivery: Rs. {total_price:.2f}**")

    if st.button("💰 Send Quotation to Patient", type="primary", use_container_width=True):
        # Update shared prescription
        shared['status'] = 'quotation_sent'
        shared['quotation_amount'] = total_price
        shared['pharmacy_comment'] = f"{comment} | Delivery: {delivery_option}"
        shared['comment_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.session_state.app.save_data('prescription_pharmacy')

        # Send chat message with quotation
        chat_msg = {
            "id": st.session_state.app.generate_id("chat"),
            "prescription_pharmacy_id": shared['id'],
            "sender_type": "pharmacy",
            "sender_id": st.session_state.current_user['id'],
            "message": f"Quotation for your prescription: Total Rs. {total_price:.2f}. {comment}. Delivery: {delivery_option}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_quotation": True,
            "quotation_amount": total_price
        }
        st.session_state.app.data['chats'].append(chat_msg)
        st.session_state.app.save_data('chats')

        # Send notification
        notification = {
            "id": st.session_state.app.generate_id("notif"),
            "patient_id": shared['patient_id'],
            "message": f"Quotation received from {st.session_state.current_user['name']}: Rs. {total_price:.2f}",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "read": False,
            "type": "quotation"
        }
        st.session_state.app.data['notifications'].append(notification)
        st.session_state.app.save_data('notifications')

        st.success("✅ Quotation sent to patient")
        st.rerun()


def manage_medicine_catalog():
    """Manage medicine catalog"""
    st.subheader("💊 Medicine Catalog")

    tab1, tab2 = st.tabs(["🔍 Browse Catalog", "🆕 Request New Medicine"])

    with tab1:
        browse_medicine_catalog()

    with tab2:
        request_new_medicine()


def browse_medicine_catalog():
    """Browse the medicine catalog"""
    st.write("### Available Medicines")

    # Search and filter
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 Search by name")
    with col2:
        category_filter = st.selectbox("Filter by Category",
                                       ["All"] + list(set(m.get('category', 'Unknown') for m in
                                                          st.session_state.app.data["medicines"])))
    with col3:
        type_filter = st.selectbox("Filter by Type",
                                   ["All"] + list(
                                       set(m.get('type', 'Unknown') for m in st.session_state.app.data["medicines"])))

    # Filter medicines
    filtered_medicines = st.session_state.app.data["medicines"]
    if search_term:
        filtered_medicines = [m for m in filtered_medicines if search_term.lower() in m['name'].lower()]
    if category_filter != "All":
        filtered_medicines = [m for m in filtered_medicines if m.get('category') == category_filter]
    if type_filter != "All":
        filtered_medicines = [m for m in filtered_medicines if m.get('type') == type_filter]

    # Display medicines
    for medicine in filtered_medicines[:50]:  # Limit to 50 for performance
        with st.expander(f"💊 {medicine['name']} - {medicine['dose']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Type:** {medicine.get('type', 'N/A').title()}")
                st.write(f"**Category:** {medicine.get('category', 'N/A')}")
                st.write(f"**Common Price:** Rs. {medicine.get('common_price', 0):.2f}")
            with col2:
                # Check if in inventory
                in_inventory = any(inv for inv in st.session_state.app.data['inventory']
                                   if inv['pharmacy_id'] == st.session_state.current_user['id']
                                   and inv['medicine_id'] == medicine['id'])
                if in_inventory:
                    inventory_item = next(inv for inv in st.session_state.app.data['inventory']
                                          if inv['pharmacy_id'] == st.session_state.current_user['id']
                                          and inv['medicine_id'] == medicine['id'])
                    st.success("✅ In Your Inventory")
                    st.write(f"**Your Stock:** {inventory_item['quantity']}")
                    st.write(f"**Your Price:** Rs. {inventory_item['unit_price']:.2f}")
                else:
                    st.info("📦 Not in Your Inventory")
                    if st.button("Add to Inventory", key=f"add_{medicine['id']}"):
                        st.session_state.medicine_to_add = medicine
                        st.session_state.dashboard_page = "inventory"
                        st.rerun()


def request_new_medicine():
    """Request to add new medicine to catalog"""
    st.write("### Request New Medicine")
    st.info("Can't find a medicine in our catalog? Request it to be added.")

    with st.form("request_medicine_form"):
        col1, col2 = st.columns(2)

        with col1:
            medicine_name = st.text_input("Medicine Name*")
            manufacturer = st.text_input("Manufacturer")
            medicine_type = st.selectbox("Type",
                                         ["tablet", "capsule", "syrup", "injection", "ointment", "cream", "other"])

        with col2:
            strength = st.text_input("Strength/Dose* (e.g., 500mg, 100ml)")
            category = st.selectbox("Category", [
                "Pain Relief", "Antibiotic", "Allergy", "Diabetes", "Cardiovascular",
                "Gastrointestinal", "Respiratory", "Vitamin", "Antifungal", "Skin Care", "Other"
            ])
            estimated_price = st.number_input("Estimated Price (Rs.)", min_value=0.0, value=0.0)

        reason = st.text_area("Why do you need this medicine added?")

        if st.form_submit_button("Submit Request", type="primary"):
            if medicine_name and strength:
                # In a real app, this would send to administrators
                st.success("✅ Medicine request submitted! We'll review it and add it to the catalog soon.")
            else:
                st.error("Please fill in required fields (Name and Strength)")


def view_pharmacy_chats():
    """View and manage patient chats"""
    st.subheader("💬 Patient Messages")

    # Get all shared prescriptions for this pharmacy
    shared_prescriptions = [pp for pp in st.session_state.app.data['prescription_pharmacy']
                            if pp['pharmacy_id'] == st.session_state.current_user['id']]

    if not shared_prescriptions:
        st.info("No active conversations yet.")
        return

    # Group by patient
    patient_conversations = {}

    for shared in shared_prescriptions:
        patient_id = shared['patient_id']
        if patient_id not in patient_conversations:
            patient = next((p for p in st.session_state.app.data['patients']
                            if p['id'] == patient_id), None)
            if patient:
                patient_conversations[patient_id] = {
                    'patient': patient,
                    'prescriptions': []
                }
        patient_conversations[patient_id]['prescriptions'].append(shared)

    for patient_id, conversation in patient_conversations.items():
        patient = conversation['patient']
        latest_prescription = max(conversation['prescriptions'], key=lambda x: x['shared_date'])

        # Get unread count
        unread_messages = len([chat for chat in st.session_state.app.data['chats']
                               if any(pp for pp in conversation['prescriptions']
                                      if pp['id'] == chat.get('prescription_pharmacy_id'))
                               and chat['sender_type'] == 'patient'
                               and not chat.get('read', False)])

        badge = f" 🔵 {unread_messages}" if unread_messages > 0 else ""

        with st.expander(f"👤 {patient['name']}{badge}"):
            # Display all prescriptions for this patient
            for shared in conversation['prescriptions']:
                prescription = next((p for p in st.session_state.app.data['prescriptions']
                                     if p['id'] == shared['prescription_id']), None)

                if prescription:
                    st.write(
                        f"**Prescription from {prescription['date']}** - {shared['status'].replace('_', ' ').title()}")

                # Get messages for this prescription
                chat_messages = [chat for chat in st.session_state.app.data['chats']
                                 if chat.get('prescription_pharmacy_id') == shared['id']]

                # Display chat messages
                chat_container = st.container()
                with chat_container:
                    for msg in sorted(chat_messages, key=lambda x: x['timestamp']):
                        # Mark as read if pharmacy is viewing
                        if msg['sender_type'] == 'patient' and not msg.get('read', False):
                            msg['read'] = True

                        if msg['sender_type'] == 'pharmacy':
                            st.write(f"**You** {msg['timestamp']}: {msg['message']}")
                            if msg.get('is_quotation'):
                                st.info(f"💰 Quotation: Rs. {msg.get('quotation_amount', 0):.2f}")
                        else:
                            st.write(f"**{patient['name']}** {msg['timestamp']}: {msg['message']}")

                # Send new message
                new_message = st.text_input("Type your message", key=f"msg_{shared['id']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Send", key=f"send_{shared['id']}", type="primary"):
                        if new_message:
                            chat_msg = {
                                "id": st.session_state.app.generate_id("chat"),
                                "prescription_pharmacy_id": shared['id'],
                                "sender_type": "pharmacy",
                                "sender_id": st.session_state.current_user['id'],
                                "message": new_message,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "read": True
                            }
                            st.session_state.app.data['chats'].append(chat_msg)
                            st.session_state.app.save_data('chats')
                            st.success("Message sent!")
                            st.rerun()
                with col2:
                    if st.button("View Prescription", key=f"view_{shared['id']}"):
                        st.session_state.selected_prescription = shared
                        st.session_state.dashboard_page = "prescriptions"
                        st.rerun()

                st.markdown("---")

    # Save read status
    st.session_state.app.save_data('chats')