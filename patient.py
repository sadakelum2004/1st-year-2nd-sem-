# patient.py
import streamlit as st
from utils import *
import re
from datetime import datetime

def validate_email(email):
    """Validate email format using regex"""
    if not email:  # Email is optional, so empty is valid
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number contains exactly 10 digits"""
    phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
    return phone_clean.isdigit() and len(phone_clean) == 10

def validate_nic(nic):
    """Validate NIC format (Sri Lankan National Identity Card)"""
    if not nic:
        return True  # NIC is optional
    nic_clean = nic.replace(" ", "").upper()
    if len(nic_clean) == 12 and nic_clean.isdigit():
        return True
    elif len(nic_clean) == 10:
        if nic_clean[:9].isdigit() and nic_clean[9] == 'V':
            return True
    return False

def patient_registration():
    """Patient registration page"""
    display_header()
    st.subheader("👤 Patient Registration")

    if st.button("< Back to Main", key="back_to_main_patient_reg"):
        st.session_state.page = "main"
        st.rerun()

    with st.form("patient_registration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name*", key="patient_name")
            nic_passport = st.text_input("NIC*", key="patient_nic",
                                        help="Enter 12 digits (new) or 9 digits followed by 'V' (old)")
            birth_date = st.date_input("Date of Birth*", min_value=datetime(1900, 1, 1),
                                      key="patient_dob")
            gender = st.selectbox("Gender*", ["Male", "Female"], key="patient_gender")

        with col2:
            phone = st.text_input("Mobile Number*", key="patient_phone",
                                max_chars=10,
                                help="Must be exactly 10 digits")
            email = st.text_input("Email (Optional)", key="patient_email")

        # City selection
        all_cities = get_all_cities()
        city = st.selectbox("City*", ["Select"] + all_cities, key="patient_city")

        password = st.text_input("Password*", type="password", key="patient_password")
        confirm_password = st.text_input("Confirm Password*", type="password",
                                        key="patient_confirm_password")

        submitted = st.form_submit_button("Register Patient", use_container_width=True, type="primary")

        if submitted:
            validation_errors = []

            # Required fields validation
            if not all([name, phone, password, confirm_password, city]):
                validation_errors.append("Please fill in all required fields (*)")

            # NIC/Passport validation
            if nic_passport and not validate_nic(nic_passport):
                validation_errors.append(
                    "Invalid NIC format. Should be 12 digits (new) or 9 digits followed by 'V' (old)")

            # Phone number validation - exactly 10 digits
            if phone and not validate_phone(phone):
                validation_errors.append("Phone number must contain exactly 10 numeric digits")

            # Email validation (optional)
            if email and not validate_email(email):
                validation_errors.append("Please enter a valid email address (e.g., example@domain.com)")

            # City validation
            if city == "Select":
                validation_errors.append("Please select city")

            # Password validation
            if password != confirm_password:
                validation_errors.append("Passwords do not match")

            if len(password) < 6:
                validation_errors.append("Password must be at least 6 characters long")

            # Clean phone number for duplicate check
            phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "") if phone else ""

            # Check if phone already exists (using cleaned version)
            if phone_clean and validate_phone(phone):
                if any(patient.get("phone") == phone_clean for patient in st.session_state.app.data['patients']):
                    validation_errors.append("Phone number already registered. Please login.")

            # Check if email already exists (if provided)
            if email and validate_email(email):
                if any(patient.get("email") == email for patient in st.session_state.app.data['patients']):
                    validation_errors.append("Email already registered. Please login.")

            # Check if NIC already exists (if provided)
            if nic_passport and validate_nic(nic_passport):
                nic_clean = nic_passport.replace(" ", "").upper()
                if any(patient.get("nic_passport") == nic_clean for patient in st.session_state.app.data['patients']):
                    validation_errors.append("NIC already registered.")

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                return

            # Generate username and get coordinates
            username = st.session_state.app.generate_username(name, phone_clean)
            coordinates = get_city_coordinates(city)

            # Clean NIC for storage (if provided)
            nic_storage = nic_passport.replace(" ", "").upper() if nic_passport else ""

            new_patient = {
                "id": st.session_state.app.generate_id("pat"),
                "name": name,
                "nic_passport": nic_storage,
                "birth_date": birth_date.strftime("%Y-%m-%d"),
                "age": st.session_state.app.calculate_age(birth_date),
                "gender": gender,
                "phone": phone_clean,  # Store cleaned phone number
                "email": email,
                "city": city,
                "coordinates": coordinates,
                "username": username,
                "password": password,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "favorite_doctors": []
            }

            st.session_state.app.data['patients'].append(new_patient)
            st.session_state.app.save_data('patients')

            st.success(f"✅ Registration Successful! Username: {username}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Go to Login", use_container_width=True, key="go_to_login_patient", type="primary"):
                    st.session_state.page = "patient_login"
                    st.rerun()
            with col2:
                if st.button("Back to Main", use_container_width=True, key="back_to_main_patient"):
                    st.session_state.page = "main"
                    st.rerun()

def patient_login():
    """Patient login page"""
    display_header()
    st.subheader("👤 Patient Login")

    if st.button("< Back to Main", key="back_to_main_patient_login"):
        st.session_state.page = "main"
        st.rerun()

    if st.button("New Patient? Register Here", key="new_patient_register"):
        st.session_state.page = "patient_register"
        st.rerun()

    with st.form("patient_login_form"):
        login_input = st.text_input("Mobile Number or Username", key="patient_login_input")
        password = st.text_input("Password", type="password", key="patient_login_password")

        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            if not login_input or not password:
                st.error("Please enter both username/mobile and password")
                return

            patient = None
            for p in st.session_state.app.data['patients']:
                if (p.get("phone") == login_input or p.get("username") == login_input) and p.get("password") == password:
                    patient = p
                    break

            if patient:
                st.session_state.current_user = patient
                st.session_state.user_type = "patient"
                st.session_state.page = "patient_dashboard"
                st.success(f"Welcome back, {patient['name']}! 👤")
                st.rerun()
            else:
                st.error("Invalid login credentials")

def patient_dashboard():
    """Patient dashboard"""
    display_header()

    st.sidebar.title(f"👤 {st.session_state.current_user['name']}")
    st.sidebar.subheader("Patient Dashboard")

    nav_options = {
        "📊 Home Page": "overview",
        "🔍 Find & Book Doctor": "find_doctor",
        "⭐ Favorite Doctors": "favorite_doctors",
        "📅 My Appointments": "my_appointments",
        "💊 My Prescriptions": "my_prescriptions",
        "📤 Share Prescription": "share_prescription",
        "💬 Pharmacy Messages": "pharmacy_messages",
        "🔔 Notifications": "notifications",
        "⏱️ Appointment Status": "appointment_status"
    }

    for option, page in nav_options.items():
        if st.sidebar.button(option, use_container_width=True, key=f"pat_nav_{page}"):
            st.session_state.dashboard_page = page

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True, key="patient_logout"):
        st.session_state.current_user = None
        st.session_state.user_type = None
        st.session_state.page = "main"
        st.rerun()

    # Display selected page
    if st.session_state.dashboard_page == "overview":
        patient_dashboard_overview()
    elif st.session_state.dashboard_page == "find_doctor":
        find_and_book_doctor()
    elif st.session_state.dashboard_page == "favorite_doctors":
        view_favorite_doctors()
    elif st.session_state.dashboard_page == "my_appointments":
        view_patient_appointments()
    elif st.session_state.dashboard_page == "my_prescriptions":
        view_patient_prescriptions()
    elif st.session_state.dashboard_page == "share_prescription":
        share_prescription_with_pharmacy()
    elif st.session_state.dashboard_page == "pharmacy_messages":
        view_pharmacy_messages()
    elif st.session_state.dashboard_page == "notifications":
        view_notifications()
    elif st.session_state.dashboard_page == "appointment_status":
        view_appointment_status()

def patient_dashboard_overview():
    """Patient dashboard overview"""
    st.subheader("📊 Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        appointments = [app for app in st.session_state.app.data['appointments']
                      if app["patient_id"] == st.session_state.current_user["id"]]
        scheduled = len([a for a in appointments if a['status'] == 'scheduled'])
        st.metric("Scheduled Appointments", scheduled)

    with col2:
        completed = len([a for a in appointments if a['status'] == 'completed'])
        st.metric("Completed Appointments", completed)

    with col3:
        prescriptions = len([p for p in st.session_state.app.data['prescriptions']
                           if p["patient_id"] == st.session_state.current_user["id"]])
        st.metric("Total Prescriptions", prescriptions)

    with col4:
        favorite_doctors = len(st.session_state.current_user.get('favorite_doctors', []))
        st.metric("Favorite Doctors", favorite_doctors)

    # Recent Appointments
    st.subheader("Recent Appointments")
    if appointments:
        recent_appointments = sorted(appointments, key=lambda x: x['date'], reverse=True)[:5]
        for app in recent_appointments:
            status_color = "🟡" if app['status'] == 'scheduled' else "🟢" if app['status'] == 'completed' else "🔴"
            st.write(f"{status_color} **Dr. {app['doctor_name']}** - {app['date']} ({app['status'].title()})")
    else:
        st.info("No appointments found")

    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📅 Book New Appointment", use_container_width=True):
            st.session_state.dashboard_page = "find_doctor"
            st.rerun()

    with col2:
        if st.button("⭐ Favorite Doctors", use_container_width=True):
            st.session_state.dashboard_page = "favorite_doctors"
            st.rerun()

    with col3:
        if st.button("📤 Share Prescription", use_container_width=True):
            st.session_state.dashboard_page = "share_prescription"
            st.rerun()

def find_and_book_doctor():
    """Combined find nearby doctors and book appointment"""
    st.subheader("🔍 Find & Book Doctor")

    tab1, tab2 = st.tabs(["📍 Find & Book Doctors", "📋 All Available Sessions"])

    with tab1:
        find_nearby_doctors()

    with tab2:
        view_all_sessions()

def find_nearby_doctors():
    """Find nearby doctors using location"""
    st.write("### Find & Book Doctors Near You")

    # Location selection options
    location_method = st.radio("Choose Location Method:",
                             ["Use My Registered Location", "Choose Different Location"],
                             horizontal=True)

    patient_lat, patient_lon = None, None
    selected_city = None

    if location_method == "Use My Registered Location":
        selected_city = st.session_state.current_user.get('city', 'Colombo 1')
        st.info(f"Using your registered location: {selected_city}")
        patient_lat, patient_lon = get_city_coordinates(selected_city)
    else:
        all_cities = get_all_cities()
        selected_city = st.selectbox("Select Your Location", all_cities)
        patient_lat, patient_lon = get_city_coordinates(selected_city)

    if st.button("Find Doctors in This Area", type="primary"):
        if patient_lat and patient_lon:
            nearby_doctors = st.session_state.app.get_nearby_doctors(patient_lat, patient_lon)

            if nearby_doctors:
                st.success(f"Found {len(nearby_doctors)} doctors near {selected_city}")
                display_doctors_list_with_booking(nearby_doctors)
            else:
                st.warning(f"No doctors found near {selected_city}. Try a different location.")
        else:
            st.error("Could not determine location coordinates")

def display_doctors_list_with_booking(doctors):
    """Display list of doctors with direct booking option"""
    for doctor in doctors:
        with st.expander(f"Dr. {doctor['name']} - {doctor.get('specialization', 'General Practitioner')}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Specialization:** {doctor.get('specialization', 'N/A')}")
                st.write(f"**Qualifications:** {doctor.get('qualifications', 'N/A')}")
                st.write(f"**Hospital:** {doctor.get('hospital_affiliation', 'N/A')}")
                st.write(f"**Location:** {doctor.get('city', 'N/A')}")
                st.write(f"**Contact:** {doctor.get('phone', 'N/A')}")

            with col2:
                if st.button("⭐ Add to Favorites", key=f"fav_{doctor['id']}"):
                    if 'favorite_doctors' not in st.session_state.current_user:
                        st.session_state.current_user['favorite_doctors'] = []

                    if doctor['id'] not in st.session_state.current_user['favorite_doctors']:
                        st.session_state.current_user['favorite_doctors'].append(doctor['id'])
                        st.session_state.app.save_data('patients')
                        st.success("Doctor added to favorites!")
                    else:
                        st.info("Doctor already in favorites")

            # Show available sessions
            today = datetime.now().strftime("%Y-%m-%d")
            available_sessions = [s for s in st.session_state.app.data['sessions']
                                if s['doctor_id'] == doctor['id'] and s['date'] >= today]

            if available_sessions:
                st.write("**Available Sessions for Direct Booking:**")
                for session in available_sessions[:3]:
                    booked_count = len([a for a in st.session_state.app.data['appointments']
                                      if a.get('session_id') == session['id']])
                    available_slots = session.get('max_patients', 0) - booked_count

                    if available_slots > 0 or session.get('max_patients', 0) == 0:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"- **{session['date']}** {session.get('start_time', '')} "
                                   f"({available_slots} slots available)")
                        with col2:
                            if st.button("Book Now", key=f"book_{session['id']}", type="primary"):
                                st.session_state.selected_session = session
                                st.session_state.selected_doctor = doctor
                                st.rerun()
            else:
                st.info("No available sessions at the moment")

    # Show booking form if session is selected
    if st.session_state.get('selected_session') and st.session_state.get('selected_doctor'):
        session = st.session_state.selected_session
        doctor = st.session_state.selected_doctor
        book_appointment_form(session, doctor)

def book_appointment_form(session, doctor):
    """Display appointment booking form"""
    st.subheader(f"Book Appointment with Dr. {doctor['name']}")

    # Get booked appointment numbers
    booked_appointments = [app for app in st.session_state.app.data['appointments']
                         if app['doctor_id'] == doctor['id'] and app['date'] == session['date']]
    booked_numbers = [app.get("appointment_number", 0) for app in booked_appointments]

    # Generate available appointment numbers
    max_patients = session.get("max_patients", 20)
    available_numbers = [num for num in range(1, max_patients + 1) if num not in booked_numbers]

    if not available_numbers:
        st.error("No available appointment numbers for this session")
        return

    with st.form(f"appointment_form_{session['id']}"):
        # Appointment for self or someone else
        appointment_for = st.radio("Appointment for:", ["Myself", "Someone else"])

        patient_details = {}

        if appointment_for == "Myself":
            patient_details = {
                "name": st.session_state.current_user["name"],
                "age": st.session_state.current_user.get("age", ""),
                "gender": st.session_state.current_user.get("gender", ""),
                "phone": st.session_state.current_user.get("phone", ""),
                "nic": st.session_state.current_user.get("nic_passport", ""),
            }
            st.info(f"Appointment for: {patient_details['name']}")
        else:
            st.write("**Enter Patient Details:**")
            col1, col2 = st.columns(2)
            with col1:
                patient_details["name"] = st.text_input("Patient Name*")
                patient_details["age"] = st.number_input("Patient Age*", min_value=0, max_value=120)
                patient_details["nic"] = st.text_input("NIC Number (Optional)")

            with col2:
                patient_details["gender"] = st.selectbox("Gender*", ["Male", "Female"])
                patient_details["phone"] = st.text_input("Contact Number*")

        # Let patient choose preferred appointment number
        preferred_number = st.selectbox("Choose Appointment Number*", available_numbers)

        # Display session details
        st.write("**Appointment Details:**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Doctor:** Dr. {doctor['name']}")
            st.write(f"**Date:** {session['date']}")
            st.write(f"**Time:** {session.get('start_time', 'N/A')}")

        with col2:
            st.write(f"**Appointment Number:** {preferred_number}")
            st.write(f"**Type:** {session.get('type', 'clinic').title()} Visit")
            st.write(f"**Location:** {session.get('location', 'Clinic')}")

        submitted = st.form_submit_button("Confirm Booking", type="primary")

        if submitted:
            # Validation for "Someone else" appointments
            if appointment_for == "Someone else":
                if not all([patient_details["name"], patient_details["phone"]]):
                    st.error("Please fill in all required patient details")
                    return

            # Create appointment
            new_appointment = {
                "id": st.session_state.app.generate_id("app"),
                "appointment_number": preferred_number,
                "patient_id": st.session_state.current_user["id"] if appointment_for == "Myself" else f"guest_{st.session_state.app.generate_id('guest')}",
                "patient_name": patient_details["name"],
                "patient_age": patient_details["age"],
                "patient_gender": patient_details["gender"],
                "patient_contact": patient_details["phone"],
                "patient_nic": patient_details.get("nic", ""),
                "patient_city": st.session_state.current_user.get("city", ""),
                "doctor_id": session["doctor_id"],
                "doctor_name": doctor["name"],
                "session_id": session["id"],
                "type": session.get("type", "clinic"),
                "date": session["date"],
                "time_slot": session.get("start_time", ""),
                "status": "scheduled",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "booked_for_others": appointment_for == "Someone else"
            }

            st.session_state.app.data['appointments'].append(new_appointment)
            st.session_state.app.save_data('appointments')

            # Create reminder notification
            reminder = {
                "id": st.session_state.app.generate_id("notif"),
                "patient_id": st.session_state.current_user["id"],
                "message": f"Reminder: Appointment with Dr. {doctor['name']} on {session['date']} at {session.get('start_time', '')}. Your appointment number is {preferred_number}.",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "read": False,
                "type": "reminder"
            }

            st.session_state.app.data['notifications'].append(reminder)
            st.session_state.app.save_data('notifications')

            st.success(f"✅ Appointment booked successfully! Your appointment number is {preferred_number}")

            # Show next steps
            st.info(f"""
            **Next Steps:**
            - Arrive 15 minutes before your appointment time
            - Bring your NIC/Passport for verification
            - Your appointment number: **{preferred_number}**
            - Doctor: **Dr. {doctor['name']}**
            - Date: **{session['date']}**
            - Time: **{session.get('start_time', '')}**
            """)

            # Clear selection
            st.session_state.selected_session = None
            st.session_state.selected_doctor = None

            if st.button("Back to Doctor List"):
                st.rerun()

def view_all_sessions():
    """View all available sessions with search"""
    st.write("### All Available Sessions")

    # Search functionality
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("Search by Doctor Name", placeholder="Enter doctor name...")
    with col2:
        specialization_filter = st.selectbox("Specialization", ["All"] + list(set([
            doc.get('specialization', 'General') for doc in st.session_state.app.data['doctors']
        ])))

    # Get all available sessions
    today = datetime.now().strftime("%Y-%m-%d")
    available_sessions = []

    for session in st.session_state.app.data['sessions']:
        session_date = session.get("date", "")
        if session_date >= today:
            doctor = next((doc for doc in st.session_state.app.data['doctors']
                         if doc["id"] == session["doctor_id"]), None)

            if doctor:
                # Apply filters
                if search_term and search_term.lower() not in doctor['name'].lower():
                    continue
                if specialization_filter != "All" and doctor.get('specialization') != specialization_filter:
                    continue

                booked_count = len([app for app in st.session_state.app.data['appointments']
                                  if app.get("session_id") == session["id"]])
                available_slots = session.get("max_patients", 0) - booked_count

                if available_slots > 0 or session.get("max_patients", 0) == 0:
                    session["booked_count"] = booked_count
                    session["available_slots"] = available_slots
                    session["doctor_name"] = doctor["name"]
                    session["doctor_specialization"] = doctor.get("specialization", "General")
                    session["doctor"] = doctor
                    available_sessions.append(session)

    if not available_sessions:
        st.warning("No available sessions found matching your criteria.")
        return

    # Display sessions
    for session in available_sessions:
        with st.expander(f"Dr. {session['doctor_name']} - {session['date']} {session.get('start_time', '')}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Doctor:** Dr. {session['doctor_name']}")
                st.write(f"**Specialization:** {session.get('doctor_specialization', 'N/A')}")
                st.write(f"**Date:** {session['date']}")
                st.write(f"**Time:** {session.get('start_time', 'N/A')} - {session.get('end_time', 'N/A')}")

            with col2:
                st.write(f"**Type:** {session.get('type', 'clinic').title()} Visit")
                st.write(f"**Available Slots:** {session['available_slots']}")
                st.write(f"**Location:** {session.get('location', 'Clinic')}")

            if st.button(f"Book Appointment", key=f"book_session_{session['id']}", type="primary"):
                st.session_state.selected_session = session
                st.session_state.selected_doctor = session["doctor"]
                st.rerun()

    # Show booking form if session is selected
    if st.session_state.get('selected_session') and st.session_state.get('selected_doctor'):
        session = st.session_state.selected_session
        doctor = st.session_state.selected_doctor
        book_appointment_form(session, doctor)

def view_favorite_doctors():
    """View and manage favorite doctors"""
    st.subheader("⭐ My Favorite Doctors")

    favorite_doctors = st.session_state.current_user.get('favorite_doctors', [])

    if not favorite_doctors:
        st.info("You haven't added any doctors to your favorites yet.")
        st.write("Visit the 'Find & Book Doctor' section to add doctors to your favorites.")
        return

    # Display favorite doctors with their available sessions
    for doctor_id in favorite_doctors:
        doctor = next((doc for doc in st.session_state.app.data["doctors"]
                     if doc["id"] == doctor_id), None)

        if doctor:
            with st.expander(f"Dr. {doctor['name']} - {doctor.get('specialization', 'General Practitioner')}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Specialization:** {doctor.get('specialization', 'N/A')}")
                    st.write(f"**Qualifications:** {doctor.get('qualifications', 'N/A')}")
                    st.write(f"**Hospital:** {doctor.get('hospital_affiliation', 'N/A')}")
                    st.write(f"**Location:** {doctor.get('city', 'N/A')}")
                    st.write(f"**Contact:** {doctor.get('phone', 'N/A')}")

                with col2:
                    if st.button("Remove", key=f"remove_{doctor['id']}"):
                        st.session_state.current_user['favorite_doctors'].remove(doctor['id'])
                        st.session_state.app.save_data('patients')
                        st.success("Doctor removed from favorites!")
                        st.rerun()

                # Show available sessions for favorite doctor
                today = datetime.now().strftime("%Y-%m-%d")
                available_sessions = [s for s in st.session_state.app.data['sessions']
                                    if s['doctor_id'] == doctor['id'] and s['date'] >= today]

                if available_sessions:
                    st.write("**Available Sessions:**")
                    for session in available_sessions[:3]:
                        booked_count = len([a for a in st.session_state.app.data['appointments']
                                          if a.get('session_id') == session['id']])
                        available_slots = session.get('max_patients', 0) - booked_count

                        if available_slots > 0 or session.get('max_patients', 0) == 0:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"- **{session['date']}** {session.get('start_time', '')} "
                                       f"({available_slots} slots available)")
                            with col2:
                                if st.button("Book", key=f"fav_book_{session['id']}", type="primary"):
                                    st.session_state.selected_session = session
                                    st.session_state.selected_doctor = doctor
                                    st.rerun()
                else:
                    st.info("No available sessions at the moment")

    # Show booking form if session is selected
    if st.session_state.get('selected_session') and st.session_state.get('selected_doctor'):
        session = st.session_state.selected_session
        doctor = st.session_state.selected_doctor
        book_appointment_form(session, doctor)

def view_appointment_status():
    """View current appointment status"""
    st.subheader("⏱️ Current Appointment Status")

    appointments = [app for app in st.session_state.app.data['appointments']
                  if app["patient_id"] == st.session_state.current_user["id"]
                  and app["status"] == "scheduled"]

    if not appointments:
        st.info("No scheduled appointments found.")
        return

    for appointment in appointments:
        with st.expander(f"Appointment #{appointment.get('appointment_number', 'N/A')} - Dr. {appointment['doctor_name']} - {appointment['date']}"):
            status_info = st.session_state.app.get_current_appointment_status(appointment["id"])

            if status_info:
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Current Position in Queue:** {status_info['current_position']}")
                    st.write(f"**Total Patients in Queue:** {status_info['total_in_queue']}")
                    st.write(f"**Session Start Time:** {status_info['session_start_time']}")

                with col2:
                    st.write(f"**Estimated Wait Time:** {status_info['estimated_wait_time']} minutes")
                    st.write(f"**Time per Patient:** {status_info['min_time_per_patient']} minutes")

                # Calculate estimated time
                if status_info['current_position'] == 1:
                    st.success("🎉 You are next in line!")
                else:
                    estimated_minutes = (status_info['current_position'] - 1) * status_info['min_time_per_patient']
                    st.info(f"⏰ Estimated wait: {estimated_minutes} minutes")
            else:
                st.info("Status information not available for this appointment")

def view_patient_appointments():
    """View patient appointments"""
    st.subheader("📅 My Appointments")

    appointments = [app for app in st.session_state.app.data['appointments']
                  if app["patient_id"] == st.session_state.current_user["id"]]

    if not appointments:
        st.info("No appointments found.")
        return

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "Completed", "Cancelled"])
    with col2:
        sort_option = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Doctor Name"])

    # Apply filters
    filtered_appointments = appointments
    if status_filter != "All":
        filtered_appointments = [app for app in filtered_appointments if app['status'].lower() == status_filter.lower()]

    # Apply sorting
    if sort_option == "Date (Newest)":
        filtered_appointments.sort(key=lambda x: x['date'], reverse=True)
    elif sort_option == "Date (Oldest)":
        filtered_appointments.sort(key=lambda x: x['date'])
    elif sort_option == "Doctor Name":
        filtered_appointments.sort(key=lambda x: x['doctor_name'])

    # Display appointments
    for appointment in filtered_appointments:
        with st.expander(f"Appointment #{appointment.get('appointment_number', 'N/A')} - Dr. {appointment['doctor_name']} - {appointment['date']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Doctor:** Dr. {appointment['doctor_name']}")
                st.write(f"**Date:** {appointment['date']}")
                st.write(f"**Time:** {appointment.get('time_slot', 'N/A')}")
                if appointment.get('booked_for_others'):
                    st.write("**Booked For:** Someone else")
                else:
                    st.write("**Booked For:** Yourself")

            with col2:
                st.write(f"**Type:** {appointment['type'].title()} Visit")
                status_color = "green" if appointment['status'] == 'scheduled' else "blue" if appointment['status'] == 'completed' else "red"
                st.write(f"**Status:** :{status_color}[{appointment['status'].title()}]")
                st.write(f"**Appointment Number:** {appointment.get('appointment_number', 'N/A')}")

def view_patient_prescriptions():
    """View patient prescriptions"""
    st.subheader("💊 My Prescriptions")

    prescriptions = [pres for pres in st.session_state.app.data["prescriptions"]
                   if pres["patient_id"] == st.session_state.current_user["id"]]

    if not prescriptions:
        st.info("No prescriptions found.")
        return

    for prescription in prescriptions:
        # Determine prescription type and sharing eligibility
        prescription_type = prescription.get('prescription_type', 'clinical')
        can_share = prescription_type in ['pharmacy', 'both']

        prescription_type_display = {
            'clinical': 'Clinical Use Only',
            'pharmacy': 'Pharmacy Use',
            'both': 'Clinical & Pharmacy Use'
        }.get(prescription_type, 'Clinical Use Only')

        with st.expander(f"Prescription - {prescription['date']} - Dr. {prescription['doctor_name']} - {prescription_type_display}"):
            st.write(f"**Doctor:** Dr. {prescription['doctor_name']}")
            st.write(f"**Date:** {prescription['date']}")
            st.write(f"**Patient Age:** {prescription.get('patient_age', 'N/A')}")
            st.write(f"**Prescription Type:** {prescription_type_display}")

            st.write("**Medicines:**")
            for med in prescription['medicines']:
                with st.container():
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**{med['name']}** ({med['type']})")
                        st.write(f"Dosage: {med['dosage']}")
                        st.write(f"Quantity: {med['quantity']}")

                    with col2:
                        st.write(f"Duration: {med.get('duration', 'N/A')} days")
                        st.write(f"Daily Usage: {med.get('daily_usage', 'N/A')}")
                        meal_info = "Before Meal" if med.get('before_meal') else "After Meal" if med.get('before_meal') is False else "Anytime"
                        st.write(f"Timing: {meal_info}")

                    if med.get('instructions'):
                        st.write(f"Instructions: {med['instructions']}")

                st.markdown("---")

            # Show additional instructions if any
            if prescription.get('additional_instructions'):
                st.write(f"**Additional Instructions:** {prescription['additional_instructions']}")

            # Check if this prescription has been shared with any pharmacies
            shared_records = [pp for pp in st.session_state.app.data['prescription_pharmacy']
                            if pp['prescription_id'] == prescription['id']]

            if shared_records:
                st.write("**Shared With Pharmacies:**")
                for record in shared_records:
                    pharmacy = next((ph for ph in st.session_state.app.data['pharmacies']
                                  if ph['id'] == record['pharmacy_id']), None)
                    if pharmacy:
                        status_info = {
                            'shared': ('🟡', 'Shared - Waiting for response'),
                            'availability_checked': ('🟠', 'Availability Checked'),
                            'quotation_sent': ('🔵', 'Quotation Sent'),
                            'completed': ('🟢', 'Completed')
                        }.get(record['status'], ('⚪', record['status']))

                        st.write(f"{status_info[0]} **{pharmacy['name']}** - {status_info[1]}")

                        # Show pharmacy comments if available
                        if record.get('pharmacy_comment'):
                            st.write(f"*Pharmacy Comment:* {record['pharmacy_comment']}")

                        # Show quotation if available
                        if record.get('quotation_amount', 0) > 0:
                            st.write(f"*Quotation:* Rs. {record['quotation_amount']:.2f}")

                        # Show action buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("💬 Message", key=f"msg_{record['id']}"):
                                st.session_state.selected_shared_prescription = record
                                st.session_state.dashboard_page = "pharmacy_messages"
                                st.rerun()
                        with col2:
                            if record["status"] == 'quotation_sent':
                                if st.button("✅ Accept", key=f"accept_{record['id']}"):
                                    record["status"] = 'completed'
                                    st.session_state.app.save_data('prescription_pharmacy')
                                    st.success("Quotation accepted! Visit the pharmacy to collect your medicines.")
                                    st.rerun()

            # Share button - only show for pharmacy-type prescriptions
            if can_share:
                if st.button("📤 Share with Pharmacy", key=f"share_{prescription['id']}", type="primary"):
                    st.session_state.selected_prescription = prescription
                    st.session_state.dashboard_page = "share_prescription"
                    st.rerun()
            else:
                st.info("ℹ️ This prescription is for clinical use only and cannot be shared with pharmacies")

def share_prescription_with_pharmacy():
    """Dedicated prescription sharing with pharmacies"""
    st.subheader("📤 Share Prescription with Pharmacy")

    # Get pharmacy-type prescriptions
    prescriptions = [pres for pres in st.session_state.app.data['prescriptions']
                   if pres["patient_id"] == st.session_state.current_user["id"]
                   and pres.get('prescription_type') in ['pharmacy', 'both']]

    if not prescriptions:
        st.info("No pharmacy prescriptions available to share.")
        st.write("Only prescriptions marked for 'Pharmacy Use' or 'Both' can be shared with pharmacies.")

        # Show explanation of prescription types
        with st.expander("ℹ️ Understanding Prescription Types"):
            st.write("""
            **Prescription Types:**

            - **Clinical Use Only**: For medical procedures and treatments at the clinic/hospital
            - **Pharmacy Use**: For medicines that can be obtained from pharmacies
            - **Both**: Contains both clinical procedures and pharmacy medicines

            Only **Pharmacy Use** and **Both** type prescriptions can be shared with pharmacies.
            """)
        return

    # Select prescription to share
    if not st.session_state.get('selected_prescription'):
        st.write("### Select Prescription to Share")
        prescription_options = {f"{pres['date']} - Dr. {pres['doctor_name']} - {len(pres['medicines'])} medicines": pres
                              for pres in prescriptions}
        selected_prescription_label = st.selectbox("Choose Prescription",
                                                 list(prescription_options.keys()))
        selected_prescription = prescription_options[selected_prescription_label]

        # Show prescription summary
        st.write("**Prescription Summary:**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Doctor:** Dr. {selected_prescription['doctor_name']}")
            st.write(f"**Date:** {selected_prescription['date']}")
        with col2:
            st.write(f"**Medicines:** {len(selected_prescription['medicines'])}")
            prescription_type = selected_prescription.get('prescription_type', 'clinical')
            type_display = "Pharmacy Use" if prescription_type == 'pharmacy' else "Clinical & Pharmacy Use"
            st.write(f"**Type:** {type_display}")

        if st.button("Select This Prescription", type="primary"):
            st.session_state.selected_prescription = selected_prescription
            st.rerun()
    else:
        selected_prescription = st.session_state.selected_prescription
        st.write(f"### Sharing Prescription from {selected_prescription['date']}")

        # Display prescription details
        st.write("**Prescription Details:**")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Doctor:** Dr. {selected_prescription['doctor_name']}")
            st.write(f"**Date:** {selected_prescription['date']}")

        with col2:
            st.write(f"**Medicines:** {len(selected_prescription['medicines'])}")
            prescription_type = selected_prescription.get('prescription_type', 'clinical')
            type_display = "Pharmacy Use" if prescription_type == 'pharmacy' else "Clinical & Pharmacy Use"
            st.write(f"**Type:** {type_display}")

        # Show medicine list
        st.write("**Medicines in this prescription:**")
        for i, med in enumerate(selected_prescription["medicines"]):
            st.write(f"{i + 1}. **{med['name']}** - {med['dosage']} - Qty: {med['quantity']}")

        if st.button("< Choose Different Prescription"):
            st.session_state.selected_prescription = None
            st.rerun()

        # Find nearby pharmacies
        st.write("### Find Nearby Pharmacies")

        # Location selection for pharmacy search
        location_method = st.radio("Search pharmacies near:",
                                 ["My Registered Location", "Choose Different Location"],
                                 horizontal=True,
                                 key="pharmacy_location")

        patient_lat, patient_lon = None, None
        search_location = None

        if location_method == "My Registered Location":
            search_location = st.session_state.current_user.get('city', 'Colombo 1')
            st.info(f"Searching pharmacies near: {search_location}")
            patient_lat, patient_lon = get_city_coordinates(search_location)
        else:
            all_cities = get_all_cities()
            search_location = st.selectbox("Select Location", all_cities, key="pharmacy_city")
            patient_lat, patient_lon = get_city_coordinates(search_location)

        if st.button("Find Nearby Pharmacies", type="primary"):
            if patient_lat and patient_lon:
                nearby_pharmacies = st.session_state.app.get_nearby_pharmacies(patient_lat, patient_lon)

                if nearby_pharmacies:
                    st.success(f"Found {len(nearby_pharmacies)} pharmacies near {search_location}")
                    display_pharmacies_for_sharing(nearby_pharmacies, selected_prescription)
                else:
                    st.warning(f"No pharmacies found near {search_location}. Try a different location.")
            else:
                st.error("Could not determine location coordinates")

def display_pharmacies_for_sharing(pharmacies, prescription):
    """Display pharmacies with sharing options"""
    for pharmacy in pharmacies:
        with st.expander(f"🏪 {pharmacy['name']} - {pharmacy.get('city', 'N/A')}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Pharmacy Name:** {pharmacy['name']}")
                st.write(f"**Owner:** {pharmacy.get('owner_name', 'N/A')}")
                st.write(f"**Location:** {pharmacy.get('city', 'N/A')}")
                st.write(f"**Address:** {pharmacy.get('address', 'N/A')}")
                st.write(f"**Contact:** {pharmacy.get('phone', 'N/A')}")
                st.write(f"**Email:** {pharmacy.get('email', 'N/A')}")

                # Check medicine availability
                is_available, unavailable_meds = st.session_state.app.check_medicine_availability(
                    prescription["id"], pharmacy["id"]
                )

                availability_status = "✅ All medicines available" if is_available else f"⚠️ Some medicines unavailable: {', '.join(unavailable_meds)}"
                st.write(f"**Medicine Availability:** {availability_status}")

            with col2:
                if st.button("📤 Share Prescription", key=f"share_{pharmacy['id']}", type="primary"):
                    share_prescription_with_selected_pharmacy(prescription, pharmacy)

def share_prescription_with_selected_pharmacy(prescription, pharmacy):
    """Share prescription with selected pharmacy"""

    # Create prescription-pharmacy link
    prescription_pharmacy = {
        "id": st.session_state.app.generate_id("pp"),
        "prescription_id": prescription["id"],
        "pharmacy_id": pharmacy["id"],
        "patient_id": st.session_state.current_user["id"],
        "patient_name": st.session_state.current_user["name"],
        "patient_contact": st.session_state.current_user.get("phone", ""),
        "shared_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "shared",
        "pharmacy_comment": "",
        "comment_date": "",
        "quotation_amount": 0,
        "quotation_sent": False
    }

    # Initialize prescription_pharmacy data if it doesn't exist
    if 'prescription_pharmacy' not in st.session_state.app.data:
        st.session_state.app.data['prescription_pharmacy'] = []

    st.session_state.app.data['prescription_pharmacy'].append(prescription_pharmacy)
    st.session_state.app.save_data('prescription_pharmacy')

    # Check availability
    is_available, unavailable_meds = st.session_state.app.check_medicine_availability(
        prescription["id"], pharmacy["id"]
    )

    # Create notifications
    pharmacy_notification = {
        "id": st.session_state.app.generate_id("notif"),
        "pharmacy_id": pharmacy["id"],
        "message": f"New prescription shared by {st.session_state.current_user['name']}",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False,
        "type": "prescription_shared"
    }

    availability_msg = "All medicines are available ✅" if is_available else f"Some medicines unavailable: {', '.join(unavailable_meds)} ⚠️"

    patient_notification = {
        "id": st.session_state.app.generate_id("notif"),
        "patient_id": st.session_state.current_user["id"],
        "message": f"Prescription shared with {pharmacy['name']}. {availability_msg}",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read": False,
        "type": "prescription_update"
    }

    # Initialize notifications data if it doesn't exist
    if 'notifications' not in st.session_state.app.data:
        st.session_state.app.data['notifications'] = []

    st.session_state.app.data['notifications'].extend([pharmacy_notification, patient_notification])
    st.session_state.app.save_data('notifications')

    # Create initial chat message
    chat_msg = {
        "id": st.session_state.app.generate_id("chat"),
        "prescription_pharmacy_id": prescription_pharmacy['id'],
        "sender_type": "patient",
        "sender_id": st.session_state.current_user['id'],
        "message": f"Hello, I've shared my prescription from {prescription['date']}. Please let me know about medicine availability and prices.",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Initialize chats data if it doesn't exist
    if 'chats' not in st.session_state.app.data:
        st.session_state.app.data['chats'] = []

    st.session_state.app.data['chats'].append(chat_msg)
    st.session_state.app.save_data('chats')

    st.success(f"✅ Prescription shared successfully with {pharmacy['name']}!")
    st.info(f"**Availability Status:** {availability_msg}")
    st.info(f"""
    **What happens next:**
    1. The pharmacy will check medicine availability
    2. They will send you a quotation with prices
    3. You can chat with the pharmacy for any questions
    4. Visit the pharmacy to collect your medicines
    """)

    st.session_state.selected_prescription = None
    st.rerun()

def view_pharmacy_messages():
    """View and manage pharmacy messages"""
    st.subheader("💬 Pharmacy Messages")

    # Get all shared prescriptions for this patient
    shared_prescriptions = [pp for pp in st.session_state.app.data['prescription_pharmacy']
                          if pp['patient_id'] == st.session_state.current_user['id']]

    if not shared_prescriptions:
        st.info("No active pharmacy conversations yet.")
        st.write("Share a prescription with a pharmacy to start messaging.")
        return

    # Group by pharmacy
    pharmacy_conversations = {}
    for shared in shared_prescriptions:
        pharmacy_id = shared['pharmacy_id']
        if pharmacy_id not in pharmacy_conversations:
            pharmacy = next((ph for ph in st.session_state.app.data['pharmacies']
                          if ph['id'] == pharmacy_id), None)
            if pharmacy:
                pharmacy_conversations[pharmacy_id] = {
                    'pharmacy': pharmacy,
                    'prescriptions': []
                }
        pharmacy_conversations[pharmacy_id]['prescriptions'].append(shared)

    # Display conversations
    for pharmacy_id, conversation in pharmacy_conversations.items():
        pharmacy = conversation['pharmacy']
        latest_prescription = max(conversation['prescriptions'], key=lambda x: x['shared_date'])

        # Get unread count
        unread_messages = len([chat for chat in st.session_state.app.data['chats']
                             if any(pp for pp in conversation['prescriptions']
                                    if pp['id'] == chat.get('prescription_pharmacy_id'))
                             and chat['sender_type'] == 'pharmacy'
                             and not chat.get('read', False)])

        badge = f" 🔵 {unread_messages}" if unread_messages > 0 else ""

        with st.expander(f"🏪 {pharmacy['name']}{badge}"):
            # Display all prescriptions for this pharmacy
            for shared in conversation['prescriptions']:
                prescription = next((p for p in st.session_state.app.data['prescriptions']
                                  if p['id'] == shared['prescription_id']), None)

                if prescription:
                    st.write(f"**Prescription from {prescription['date']}** - {shared['status'].replace('_', ' ').title()}")

                # Show pharmacy comments
                if shared.get('pharmacy_comment'):
                    st.info(f"**Pharmacy Comment:** {shared['pharmacy_comment']}")

                # Show quotation if available
                if shared.get('quotation_amount', 0) > 0:
                    st.success(f"**Quotation Amount:** Rs. {shared['quotation_amount']:.2f}")

                # Get messages for this prescription
                chat_messages = [chat for chat in st.session_state.app.data['chats']
                               if chat.get('prescription_pharmacy_id') == shared['id']]

                # Display chat messages
                chat_container = st.container()
                with chat_container:
                    for msg in sorted(chat_messages, key=lambda x: x['timestamp']):
                        # Mark as read if patient is viewing
                        if msg['sender_type'] == 'pharmacy' and not msg.get('read', False):
                            msg['read'] = True

                        if msg['sender_type'] == 'patient':
                            st.write(f"**You** {msg['timestamp']}: {msg['message']}")
                        else:
                            st.write(f"**{pharmacy['name']}** {msg['timestamp']}: {msg['message']}")
                        if msg.get('is_quotation'):
                            st.info(f"💰 Quotation: Rs. {msg.get('quotation_amount', 0):.2f}")

                # Send new message
                new_message = st.text_input("Type your message", key=f"msg_{shared['id']}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Send", key=f"send_{shared['id']}", type="primary"):
                        if new_message:
                            chat_msg = {
                                "id": st.session_state.app.generate_id("chat"),
                                "prescription_pharmacy_id": shared['id'],
                                "sender_type": "patient",
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
                        st.session_state.selected_prescription = next(
                            (p for p in st.session_state.app.data['prescriptions']
                             if p["id"] == shared['prescription_id']), None)
                        st.session_state.dashboard_page = "my_prescriptions"
                        st.rerun()

                st.markdown("---")

    # Save read status
    st.session_state.app.save_data('chats')