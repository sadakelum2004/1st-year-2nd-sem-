# doctor.py
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
    phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
    return phone_clean.isdigit() and len(phone_clean) == 10


def validate_slmc_number(slmc):
    """Validate SLMC number contains exactly 4 digits"""
    slmc_clean = slmc.replace(" ", "").replace("-", "").replace("SLMC", "").upper()
    return slmc_clean.isdigit() and len(slmc_clean) == 4


def validate_nic(nic):
    """Validate NIC format (Sri Lankan National Identity Card)"""
    if not nic:
        return False
    nic_clean = nic.replace(" ", "").upper()
    if len(nic_clean) == 12 and nic_clean.isdigit():
        return True
    elif len(nic_clean) == 10:
        if nic_clean[:9].isdigit() and nic_clean[9] == 'V':
            return True
    return False


def doctor_registration():
    """Doctor registration page"""
    display_header()
    st.subheader("👨‍⚕️ Doctor Registration")

    if st.button("< Back to Main", key="back_to_main_doctor_reg"):
        st.session_state.page = "main"
        st.rerun()

    predefined_qualifications = [
        "MBBS", "MD", "MS", "MRCP", "FRCS", "FRCP", "Diploma", "Board Certified",
        "PhD", "MSc", "BDS", "FCPS", "MRCS", "FRACGP", "American Board Certified",
        "DCH", "DLO", "DOrtho", "DDerm", "DPharm", "BPharm", "BSc Nursing"
    ]

    specializations = [
        "General Practitioner", "Cardiologist", "Pediatrician", "Dermatologist",
        "Neurologist", "Psychiatrist", "Orthopedic Surgeon", "Gynecologist",
        "Obstetrician", "ENT Specialist", "Ophthalmologist", "Dentist",
        "Physician", "Surgeon", "Urologist", "Nephrologist", "Endocrinologist",
        "Gastroenterologist", "Pulmonologist", "Rheumatologist", "Oncologist",
        "Hematologist", "Immunologist", "Allergist", "Anesthesiologist",
        "Radiologist", "Pathologist", "Emergency Medicine", "Family Medicine",
        "Community Medicine", "Forensic Medicine", "Sports Medicine",
        "Ayurvedic Physician", "Homeopathic Doctor", "Other"
    ]

    with st.form("doctor_registration_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name*", key="doctor_name",
                                 help="Enter your full name as per medical registration")
            nic_passport = st.text_input("NIC*", key="doctor_nic",
                                         help="Sri Lankan NIC (12 digits or 9 digits + V) or Passport number")
            registration_category = st.multiselect("Registration Category*",
                                                   ["Clinic", "Home Visit", "Both"],
                                                   key="doctor_category",
                                                   help="Select all applicable practice types")
            slmc_registration = st.text_input("SLMC Registration Number*", key="doctor_slmc",
                                              max_chars=4,
                                              help="Must be exactly 4 digits (e.g., 1234 or SLMC-1234)")
            specialization = st.selectbox("Specialization*", specializations, key="doctor_specialization")

        with col2:
            st.write("Qualifications*")
            selected_qualifications = st.multiselect(
                "Select Qualifications",
                predefined_qualifications,
                key="doctor_qualifications_multiselect",
                help="Select all relevant medical qualifications"
            )
            custom_qualification = st.text_input("Add Custom Qualification (if not in list)",
                                                 key="doctor_custom_qualification",
                                                 help="Add any qualification not listed above")
            qualifications = selected_qualifications
            if custom_qualification.strip():
                qualifications.append(custom_qualification.strip())

            hospital_affiliation = st.text_input("Hospital/Clinic Affiliation*",
                                                 key="doctor_hospital",
                                                 help="Primary hospital or clinic name")
            all_cities = get_all_cities()
            city = st.selectbox("City*", ["Select"] + all_cities, key="doctor_city")
            phone = st.text_input("Contact Number*", key="doctor_phone",
                                  max_chars=10,
                                  help="Must be exactly 10 digits")
            email = st.text_input("Email*", key="doctor_email",
                                  help="Professional email address")
            password = st.text_input("Password*", type="password", key="doctor_password")
            confirm_password = st.text_input("Confirm Password*", type="password",
                                             key="doctor_confirm_password")

        submitted = st.form_submit_button("Register Doctor", use_container_width=True, type="primary")

        if submitted:
            validation_errors = []

            # Required fields validation
            required_fields = [name, phone, password, confirm_password, city, email]
            if not all(required_fields):
                validation_errors.append("Please fill in all required fields (*)")

            if not qualifications:
                validation_errors.append("Please select or add at least one qualification")

            if not registration_category:
                validation_errors.append("Please select at least one registration category")

            # NIC/Passport validation
            if not nic_passport:
                validation_errors.append("NIC/Passport is required")
            elif not validate_nic(nic_passport):
                validation_errors.append(
                    "Invalid NIC format. Should be 12 digits (new) or 9 digits followed by 'V' (old)")

            # Phone number validation
            if phone and not validate_phone(phone):
                validation_errors.append("Phone number must contain exactly 10 numeric digits")

            # SLMC Registration validation
            if not slmc_registration:
                validation_errors.append("SLMC Registration Number is required")
            elif not validate_slmc_number(slmc_registration):
                validation_errors.append("SLMC Registration Number must be exactly 4 digits (e.g., 1234 or SLMC-1234)")

            # Email validation
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

            # Enhanced password strength
            if password:
                has_upper = any(c.isupper() for c in password)
                has_lower = any(c.islower() for c in password)
                has_digit = any(c.isdigit() for c in password)

                if not (has_upper and has_lower and has_digit):
                    validation_errors.append(
                        "For stronger security, password should contain uppercase, lowercase letters and digits")

            # Clean data for duplicate checks
            phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "") if phone else ""
            nic_clean = nic_passport.replace(" ", "").upper() if nic_passport else ""
            slmc_clean = slmc_registration.replace(" ", "").replace("-", "").replace("SLMC",
                                                                                     "").upper() if slmc_registration else ""

            # Check if phone already exists
            if phone_clean and validate_phone(phone):
                if any(doctor.get("phone") == phone_clean for doctor in st.session_state.app.data["doctors"]):
                    validation_errors.append("Phone number already registered. Please login.")

            # Check if NIC already exists
            if nic_clean and validate_nic(nic_passport):
                if any(doctor.get("nic_passport") == nic_clean for doctor in st.session_state.app.data["doctors"]):
                    validation_errors.append("NIC/Passport already registered. Please login.")

            # Check if email already exists
            if email and validate_email(email):
                if any(doctor.get("email") == email for doctor in st.session_state.app.data["doctors"]):
                    validation_errors.append("Email already registered. Please login.")

            # Check if SLMC number already exists
            if slmc_clean and validate_slmc_number(slmc_registration):
                if any(doctor.get("slmc_registration") == slmc_clean for doctor in
                       st.session_state.app.data["doctors"]):
                    validation_errors.append("SLMC registration number already registered.")

            if validation_errors:
                for error in validation_errors:
                    st.error(error)
                return

            # Generate username and get coordinates
            username = st.session_state.app.generate_username(name, phone_clean)
            coordinates = get_city_coordinates(city)

            # Clean data for storage
            nic_storage = nic_clean
            slmc_storage = slmc_clean

            new_doctor = {
                "id": st.session_state.app.generate_id("doc"),
                "name": name.strip(),
                "nic_passport": nic_storage,
                "registration_category": registration_category,
                "slmc_registration": slmc_storage,
                "specialization": specialization,
                "qualifications": qualifications,
                "hospital_affiliation": hospital_affiliation.strip(),
                "city": city,
                "coordinates": coordinates,
                "phone": phone_clean,
                "email": email.lower(),
                "username": username,
                "password": password,
                "verified": True,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "earnings": []  # New field for tracking earnings
            }

            st.session_state.app.data['doctors'].append(new_doctor)
            st.session_state.app.save_data('doctors')

            st.success(f"✅ Doctor Registration Successful! Username: {username}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Go to Login", use_container_width=True, key="go_to_login_doctor", type="primary"):
                    st.session_state.page = "doctor_login"
                    st.rerun()
            with col2:
                if st.button("Back to Main", use_container_width=True, key="back_to_main_doctor"):
                    st.session_state.page = "main"
                    st.rerun()


def doctor_login():
    """Doctor login page"""
    display_header()
    st.subheader("👨‍⚕️ Doctor Login")

    if st.button("< Back to Main", key="back_to_main_doctor_login"):
        st.session_state.page = "main"
        st.rerun()

    if st.button("New Doctor? Register Here", key="new_doctor_register"):
        st.session_state.page = "doctor_register"
        st.rerun()

    with st.form("doctor_login_form"):
        login_id = st.text_input("Phone Number or SLMC Registration Number", key="doctor_login_input")
        password = st.text_input("Password", type="password", key="doctor_login_password")

        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:
            if not login_id or not password:
                st.error("Please enter both login ID and password")
                return

            doctor = None
            for doc in st.session_state.app.data['doctors']:
                if (doc.get("phone") == login_id or doc.get("slmc_registration") == login_id) and doc.get(
                        "password") == password:
                    doctor = doc
                    break

            if doctor:
                st.session_state.current_user = doctor
                st.session_state.user_type = "doctor"
                st.session_state.page = "doctor_dashboard"
                st.success(f"Welcome back, Dr. {doctor['name']}! 👨‍⚕️")
                st.rerun()
            else:
                st.error("Invalid login credentials")


def doctor_dashboard():
    """Doctor dashboard"""
    display_header()

    st.sidebar.title(f"👨‍⚕️ Dr. {st.session_state.current_user['name']}")
    st.sidebar.subheader("Doctor Dashboard")

    nav_options = {
        "📊 Home Page": "overview",
        "📅 My Appointments": "my_appointments",
        "➕ Create Session": "create_session",
        "📋 My Sessions": "my_sessions",
        "📝 Create Prescription": "create_prescription",
        "📜 Prescription History": "prescription_history",
        "👥 Add Patient to Session": "add_patient",
        "💰 Appointment Payments": "payment_reports"  # Renamed tab
    }

    for option, page in nav_options.items():
        if st.sidebar.button(option, use_container_width=True, key=f"doc_nav_{page}"):
            st.session_state.dashboard_page = page

    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", use_container_width=True, key="doctor_logout"):
        st.session_state.current_user = None
        st.session_state.user_type = None
        st.session_state.page = "main"
        st.rerun()

    if st.session_state.dashboard_page == "overview":
        doctor_dashboard_overview()
    elif st.session_state.dashboard_page == "my_appointments":
        view_doctor_appointments()
    elif st.session_state.dashboard_page == "create_session":
        create_appointment_session()
    elif st.session_state.dashboard_page == "my_sessions":
        view_doctor_sessions()
    elif st.session_state.dashboard_page == "create_prescription":
        create_enhanced_prescription()
    elif st.session_state.dashboard_page == "prescription_history":
        view_prescription_history()
    elif st.session_state.dashboard_page == "add_patient":
        add_patient_to_session()
    elif st.session_state.dashboard_page == "payment_reports":
        doctor_payment_reports()


def doctor_dashboard_overview():
    """Doctor dashboard overview"""
    st.subheader("📊 Dashboard Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        appointments = [app for app in st.session_state.app.data["appointments"]
                        if app["doctor_id"] == st.session_state.current_user["id"]]
        scheduled = len([a for a in appointments if a['status'] == 'scheduled'])
        st.metric("Scheduled Appointments", scheduled)

    with col2:
        completed = len([a for a in appointments if a['status'] == 'completed'])
        st.metric("Completed Appointments", completed)

    with col3:
        sessions = len([s for s in st.session_state.app.data["sessions"]
                        if s["doctor_id"] == st.session_state.current_user["id"]])
        st.metric("Total Sessions", sessions)

    with col4:
        prescriptions = len([p for p in st.session_state.app.data["prescriptions"]
                             if p["doctor_id"] == st.session_state.current_user["id"]])
        st.metric("Prescriptions Written", prescriptions)

    # Recent Appointments
    st.subheader("Recent Appointments")
    if appointments:
        recent_appointments = sorted(appointments, key=lambda x: x['date'], reverse=True)[:5]
        for app in recent_appointments:
            status_color = "🟡" if app['status'] == 'scheduled' else "🟢" if app['status'] == 'completed' else "🔴"
            st.write(f"{status_color} **{app['patient_name']}** - {app['date']} ({app['status'].title()})")
    else:
        st.info("No appointments found")

    # Quick Actions
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Create Session", use_container_width=True):
            st.session_state.dashboard_page = "create_session"
            st.rerun()

    with col2:
        if st.button("Create Prescription", use_container_width=True):
            st.session_state.dashboard_page = "create_prescription"
            st.rerun()

    with col3:
        if st.button("Add Patient", use_container_width=True):
            st.session_state.dashboard_page = "add_patient"
            st.rerun()


def view_doctor_appointments():
    """View doctor appointments"""
    st.subheader("My Appointments")

    appointments = [app for app in st.session_state.app.data['appointments']
                    if app["doctor_id"] == st.session_state.current_user["id"]]

    if not appointments:
        st.info("No appointments found.")
        return

    for appointment in appointments:
        with st.expander(
                f"Appointment #{appointment.get('appointment_number', 'N/A')} - {appointment['patient_name']} - {appointment['date']}"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Patient:** {appointment['patient_name']}")
                st.write(f"**Age:** {appointment.get('patient_age', 'N/A')}")
                st.write(f"**Contact:** {appointment.get('patient_contact', 'N/A')}")
                st.write(
                    f"**Location:** {appointment.get('patient_district', 'N/A')}, {appointment.get('patient_city', 'N/A')}")

            with col2:
                st.write(f"**Date:** {appointment['date']}")
                st.write(f"**Time:** {appointment.get('time_slot', 'N/A')}")
                status_color = "green" if appointment['status'] == 'scheduled' else "blue" if appointment[
                                                                                                  'status'] == 'completed' else "red"
                st.write(f"**Status:** :{status_color}[{appointment['status'].title()}]")

            # Update status button
            if appointment['status'] == 'scheduled':
                if st.button("Mark as Completed", key=f"complete_{appointment['id']}", type="primary"):
                    appointment["status"] = "completed"
                    # Record earning for completed appointment
                    record_doctor_earning(appointment)
                    st.session_state.app.save_data('appointments')
                    st.success("Appointment marked as completed!")
                    st.rerun()


def record_doctor_earning(appointment):
    """Record Rs. 50 earning for completed appointment"""
    doctor_id = appointment["doctor_id"]
    doctor = next((doc for doc in st.session_state.app.data['doctors'] if doc['id'] == doctor_id), None)

    if doctor:
        earning_record = {
            "appointment_id": appointment["id"],
            "patient_name": appointment["patient_name"],
            "date": appointment["date"],
            "amount": 50.0,
            "type": "appointment_fee",
            "recorded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if "earnings" not in doctor:
            doctor["earnings"] = []
        doctor["earnings"].append(earning_record)
        st.session_state.app.save_data('doctors')


def doctor_payment_reports():
    """Doctor payment reports for completed appointments - Improved version"""
    st.subheader("💰 Appointment Payments")

    doctor = st.session_state.current_user
    earnings = doctor.get("earnings", [])

    if not earnings:
        st.info("No payment records found. Complete appointments to earn Rs. 50 per appointment.")
        return

    # Group earnings by month
    monthly_earnings = {}
    for earning in earnings:
        month_year = datetime.strptime(earning["date"], "%Y-%m-%d").strftime("%Y-%m")
        if month_year not in monthly_earnings:
            monthly_earnings[month_year] = []
        monthly_earnings[month_year].append(earning)

    # Create monthly summary table
    st.write("### Monthly Appointment Payments")

    monthly_data = []
    for month, month_earnings in sorted(monthly_earnings.items(), reverse=True):
        total_appointments = len(month_earnings)
        total_amount = total_appointments * 50  # Rs. 50 per appointment

        monthly_data.append({
            "Month": datetime.strptime(month, '%Y-%m').strftime('%B %Y'),
            "Appointments": total_appointments,
            "Amount (Rs.)": f"Rs. {total_amount:.2f}"
        })

    # Display as table
    if monthly_data:
        st.table(monthly_data)
    else:
        st.info("No payment records available.")

    # Overall statistics
    st.write("### Payment Summary")
    col1, col2, col3 = st.columns(3)

    total_earnings = sum(earn["amount"] for earn in earnings)
    total_appointments = len(earnings)

    with col1:
        st.metric("Total Appointments", total_appointments)
    with col2:
        st.metric("Total Payable Amount", f"Rs. {total_earnings:.2f}")
    with col3:
        st.metric("Amount per Appointment", "Rs. 50.00")


def create_appointment_session():
    """Create appointment session"""
    st.subheader("➕ Create Appointment Session")

    with st.form("create_session_form"):
        col1, col2 = st.columns(2)

        with col1:
            session_date = st.date_input("Session Date", min_value=datetime.now())
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")

            registration_categories = st.session_state.current_user.get('registration_category', [])
            if "Both" in registration_categories:
                session_type = st.selectbox("Session Type", ["Clinic", "Home Visit"])
            elif "Home Visit" in registration_categories:
                session_type = "Home Visit"
            else:
                session_type = "Clinic"

            st.write(f"**Session Type:** {session_type}")

        with col2:
            max_patients = st.number_input("Maximum Patients", min_value=0, value=10,
                                           help="Set to 0 for no limit")
            min_time_per_patient = st.number_input("Minimum Time per Patient (minutes)",
                                                   min_value=5, max_value=60, value=15)

            location = st.text_input("Location/Address",
                                     value=st.session_state.current_user.get('hospital_affiliation',
                                                                             '') if session_type == "Clinic" else "")

            session_notice = st.text_area("Session Notice/Announcement (Optional)",
                                          help="This notice will be visible to patients when booking this session")

        submitted = st.form_submit_button("Create Session", use_container_width=True, type="primary")

        if submitted:
            new_session = {
                "id": st.session_state.app.generate_id("sess"),
                "doctor_id": st.session_state.current_user["id"],
                "date": session_date.strftime("%Y-%m-%d"),
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "type": session_type.lower().replace(" ", "_"),
                "max_patients": max_patients,
                "min_time_per_patient": min_time_per_patient,
                "location": location,
                "notice": session_notice,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            st.session_state.app.data['sessions'].append(new_session)
            st.session_state.app.save_data('sessions')

            if session_notice:
                doctor_appointments = [app for app in st.session_state.app.data['appointments']
                                       if app['doctor_id'] == st.session_state.current_user["id"]]
                patient_ids = set([app['patient_id'] for app in doctor_appointments])

                for patient_id in patient_ids:
                    notification = {
                        "id": st.session_state.app.generate_id("notif"),
                        "patient_id": patient_id,
                        "message": f"New session notice from Dr. {st.session_state.current_user['name']}: {session_notice}",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "read": False,
                        "type": "session_notice"
                    }
                    st.session_state.app.data['notifications'].append(notification)

                st.session_state.app.save_data('notifications')

            st.success("✅ Appointment session created successfully!")


def view_doctor_sessions():
    """View and manage doctor sessions"""
    st.subheader("📋 My Sessions")

    sessions = [s for s in st.session_state.app.data['sessions']
                if s["doctor_id"] == st.session_state.current_user["id"]]

    if not sessions:
        st.info("No sessions created yet.")
        return

    sessions.sort(key=lambda x: x['date'], reverse=True)

    today = datetime.now().strftime("%Y-%m-%d")
    tab1, tab2 = st.tabs(["Upcoming Sessions", "Past Sessions"])

    with tab1:
        upcoming_sessions = [s for s in sessions if s['date'] >= today]
        if not upcoming_sessions:
            st.info("No upcoming sessions.")
        else:
            for session in upcoming_sessions:
                with st.expander(f"Session - {session['date']} {session.get('start_time', '')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Date:** {session['date']}")
                        st.write(f"**Time:** {session.get('start_time', 'N/A')} - {session.get('end_time', 'N/A')}")
                        st.write(f"**Type:** {session.get('type', 'clinic').title()}")
                        st.write(f"**Max Patients:** {session.get('max_patients', 'No limit')}")

                    with col2:
                        st.write(f"**Time per Patient:** {session.get('min_time_per_patient', 15)} minutes")
                        st.write(f"**Location:** {session.get('location', 'N/A')}")

                    appointments = [app for app in st.session_state.app.data['appointments']
                                    if app.get('session_id') == session['id']]
                    booked_count = len(appointments)
                    st.write(f"**Booked Appointments:** {booked_count}")

                    if session.get('notice'):
                        st.info(f"**Session Notice:** {session['notice']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Edit Session", key=f"edit_{session['id']}"):
                            edit_session(session)
                    with col2:
                        if st.button("Delete Session", key=f"delete_{session['id']}"):
                            if booked_count > 0:
                                st.warning("Cannot delete session with booked appointments")
                            else:
                                st.session_state.app.data['sessions'].remove(session)
                                st.session_state.app.save_data('sessions')
                                st.success("Session deleted successfully!")
                                st.rerun()

    with tab2:
        past_sessions = [s for s in sessions if s['date'] < today]
        if not past_sessions:
            st.info("No past sessions.")
        else:
            for session in past_sessions:
                with st.expander(f"Session - {session['date']} {session.get('start_time', '')}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Date:** {session['date']}")
                        st.write(f"**Time:** {session.get('start_time', 'N/A')} - {session.get('end_time', 'N/A')}")
                        st.write(f"**Type:** {session.get('type', 'clinic').title()}")

                    with col2:
                        st.write(f"**Max Patients:** {session.get('max_patients', 'No limit')}")

                    appointments = [app for app in st.session_state.app.data['appointments']
                                    if app.get('session_id') == session['id']]
                    booked_count = len(appointments)
                    st.write(f"**Completed Appointments:** {booked_count}")


def edit_session(session):
    """Edit an existing session"""
    st.subheader("✏️ Edit Session")

    with st.form(f"edit_session_form_{session['id']}"):
        col1, col2 = st.columns(2)

        with col1:
            session_date = st.date_input("Session Date",
                                         value=datetime.strptime(session['date'], "%Y-%m-%d"),
                                         min_value=datetime.now(),
                                         key=f"edit_date_{session['id']}")

            start_time = st.time_input("Start Time",
                                       value=datetime.strptime(session.get('start_time', '09:00'), "%H:%M").time(),
                                       key=f"edit_start_{session['id']}")

            end_time = st.time_input("End Time",
                                     value=datetime.strptime(session.get('end_time', '17:00'), "%H:%M").time(),
                                     key=f"edit_end_{session['id']}")

        with col2:
            max_patients = st.number_input("Maximum Patients",
                                           min_value=0,
                                           value=session.get('max_patients', 10),
                                           key=f"edit_max_{session['id']}")

            min_time_per_patient = st.number_input("Minimum Time per Patient (minutes)",
                                                   min_value=5,
                                                   max_value=60,
                                                   value=session.get('min_time_per_patient', 15),
                                                   key=f"edit_time_{session['id']}")

            location = st.text_input("Location/Address",
                                     value=session.get('location', ''),
                                     key=f"edit_loc_{session['id']}")

            session_notice = st.text_area("Session Notice/Announcement",
                                          value=session.get('notice', ''),
                                          key=f"edit_notice_{session['id']}")

        submitted = st.form_submit_button("Update Session", use_container_width=True, type="primary")

        if submitted:
            session['date'] = session_date.strftime("%Y-%m-%d")
            session['start_time'] = start_time.strftime("%H:%M")
            session['end_time'] = end_time.strftime("%H:%M")
            session['max_patients'] = max_patients
            session['min_time_per_patient'] = min_time_per_patient
            session['location'] = location
            session['notice'] = session_notice

            st.session_state.app.save_data('sessions')

            if session_notice:
                doctor_appointments = [app for app in st.session_state.app.data['appointments']
                                       if app['doctor_id'] == st.session_state.current_user['id']]
                patient_ids = set([app['patient_id'] for app in doctor_appointments])

                for patient_id in patient_ids:
                    notification = {
                        "id": st.session_state.app.generate_id("notif"),
                        "patient_id": patient_id,
                        "message": f"Updated session notice from Dr. {st.session_state.current_user['name']}: {session_notice}",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "read": False,
                        "type": "session_notice"
                    }
                    st.session_state.app.data['notifications'].append(notification)

                st.session_state.app.save_data('notifications')

            st.success("✅ Session updated successfully!")
            st.rerun()


def create_enhanced_prescription():
    """Enhanced prescription creation with improved completion flow"""
    st.subheader("📝 Create Prescription")

    appointments = [app for app in st.session_state.app.data['appointments']
                    if app['doctor_id'] == st.session_state.current_user['id']
                    and app['status'] == "scheduled"]

    if not appointments:
        st.info("No scheduled appointments found.")
        return

    appointment_options = {f"{app['patient_name']} - {app['date']}": app for app in appointments}
    selected_appointment_label = st.selectbox("Select Appointment", list(appointment_options.keys()))
    selected_appointment = appointment_options[selected_appointment_label]

    st.write("**Patient Details:**")
    st.write(f"Name: {selected_appointment['patient_name']}")
    st.write(f"Age: {selected_appointment.get('patient_age', 'N/A')}")
    st.write(f"Contact: {selected_appointment.get('patient_contact', 'N/A')}")

    # Prescription type selection
    prescription_type = st.radio("Prescription Type",
                                 ["Clinical Use", "Pharmacy", "Both"],
                                 horizontal=True)

    # Medicine selection
    st.write("### Add Medicines")

    if 'selected_medicines' not in st.session_state:
        st.session_state.selected_medicines = []

    tab1, tab2 = st.tabs(["Quick Select", "Manage Medicines"])

    with tab1:
        st.write("**Quick Medicine Selection**")

        favorite_meds = [fm for fm in st.session_state.app.data['favorite_medicines']
                         if fm.get('doctor_id') == st.session_state.current_user['id']]

        if favorite_meds:
            st.write("**Your Favorite Medicines:**")
            for fav in favorite_meds:
                med = next((m for m in st.session_state.app.data['medicines'] if m['id'] == fav['medicine_id']), None)
                if med:
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{med['name']}** ({med['type']}) - {med['dose']}")
                    with col2:
                        with st.form(f"quick_add_{med['id']}"):
                            dosage = st.text_input("Dosage", value=med['dose'], key=f"qd_{med['id']}")
                            quantity = st.number_input("Quantity", min_value=1, value=1, key=f"qq_{med['id']}")
                            if st.form_submit_button("Add to Prescription"):
                                st.session_state.selected_medicines.append({
                                    "id": med["id"],
                                    "name": med["name"],
                                    "type": med["type"],
                                    "dosage": dosage,
                                    "quantity": quantity,
                                    "duration": 7,
                                    "daily_usage": "2 times a day",
                                    "before_meal": True,
                                    "instructions": ""
                                })
                                st.success(f"Added {med['name']}")

        st.write("**Search Other Medicines:**")
        search_term = st.text_input("Search Medicine")
        all_medicines = st.session_state.app.data["medicines"]
        filtered_meds = [med for med in all_medicines if
                         search_term.lower() in med['name'].lower()] if search_term else all_medicines[:5]

        for med in filtered_meds:
            with st.expander(f"{med['name']} - {med['dose']}"):
                with st.form(f"med_form_{med['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        dosage = st.text_input("Dosage", value=med['dose'], key=f"dosage_{med['id']}")
                        quantity = st.number_input("Quantity", min_value=1, value=1, key=f"qty_{med['id']}")
                        duration = st.number_input("Duration (days)", min_value=1, value=7, key=f"dur_{med['id']}")
                    with col2:
                        daily_usage = st.selectbox("Times per day", ["1 time", "2 times", "3 times", "4 times"],
                                                   key=f"usage_{med['id']}")
                        before_meal = st.radio("Take", ["Before Meal", "After Meal", "Anytime"],
                                               key=f"meal_{med['id']}")
                        instructions = st.text_area("Instructions", key=f"inst_{med['id']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Add to Prescription"):
                            st.session_state.selected_medicines.append({
                                "id": med["id"],
                                "name": med["name"],
                                "type": med["type"],
                                "dosage": dosage,
                                "quantity": quantity,
                                "duration": duration,
                                "daily_usage": daily_usage,
                                "before_meal": before_meal == "Before Meal",
                                "instructions": instructions
                            })
                            st.success(f"Added {med['name']}")
                    with col2:
                        if st.form_submit_button("Add to Favorites"):
                            if not any(fm["medicine_id"] == med['id'] for fm in favorite_meds):
                                favorite_med = {
                                    "id": st.session_state.app.generate_id("fav"),
                                    "doctor_id": st.session_state.current_user["id"],
                                    "medicine_id": med["id"],
                                    "medicine_name": med["name"],
                                    "added_date": datetime.now().strftime("%Y-%m-%d")
                                }
                                st.session_state.app.data["favorite_medicines"].append(favorite_med)
                                st.session_state.app.save_data("favorite_medicines")
                                st.success("Added to favorites!")

    with tab2:
        st.write("**Manage Medicine List**")

        with st.expander("Add New Medicine"):
            with st.form("add_medicine_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_name = st.text_input("Medicine Name*")
                    new_type = st.selectbox("Type",
                                            ["tablet", "capsule", "syrup", "injection", "ointment", "cream", "inhaler"])
                    new_dose = st.text_input("Dose* (e.g., 500mg, 100ml)")
                with col2:
                    new_category = st.selectbox("Category", [
                        "Pain Relief", "Antibiotic", "Allergy", "Diabetes", "Cardiovascular",
                        "Gastrointestinal", "Respiratory", "Vitamin", "Antifungal", "Other"
                    ])
                    new_price = st.number_input("Common Price (Rs.)", min_value=0.0, value=0.0)

                if st.form_submit_button("Add Medicine", type="primary"):
                    if new_name and new_dose:
                        medicine_data = {
                            "name": new_name,
                            "type": new_type,
                            "dose": new_dose,
                            "category": new_category,
                            "common_price": new_price
                        }
                        success, message = st.session_state.app.add_new_medicine(medicine_data)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

        st.write("**Current Medicines:**")
        for med in st.session_state.app.data["medicines"]:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{med['name']}** - {med['dose']} ({med['type']})")
            with col2:
                st.write(f"Category: {med.get('category', 'N/A')}")
            with col3:
                if st.button("Delete", key=f"del_{med['id']}"):
                    success, message = st.session_state.app.delete_medicine(med['id'])
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # Display selected medicines
    if st.session_state.selected_medicines:
        st.write("### Selected Medicines")
        for i, med in enumerate(st.session_state.selected_medicines):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{med['name']}** - {med['dosage']}")
                    st.write(f"Usage: {med['daily_usage']}, {med['duration']} days")
                with col2:
                    st.write(f"Quantity: {med['quantity']}")
                    meal_time = "Before meal" if med['before_meal'] else "After meal" if med[
                                                                                             'before_meal'] is not None else "Anytime"
                    st.write(f"Timing: {meal_time}")
                with col3:
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.selected_medicines.pop(i)
                        st.rerun()
                st.markdown("---")

    additional_instructions = st.text_area("Additional Instructions for Patient")

    if st.session_state.selected_medicines and st.button("Create Prescription", use_container_width=True,
                                                         type="primary"):
        prescription_data = {
            "id": st.session_state.app.generate_id("pres"),
            "appointment_id": selected_appointment["id"],
            "patient_id": selected_appointment["patient_id"],
            "patient_name": selected_appointment["patient_name"],
            "patient_age": selected_appointment.get("patient_age", "N/A"),
            "doctor_id": st.session_state.current_user["id"],
            "doctor_name": st.session_state.current_user["name"],
            "doctor_qualifications": st.session_state.current_user.get("qualifications", ""),
            "doctor_slmc": st.session_state.current_user.get("slmc_registration", ""),
            "medicines": st.session_state.selected_medicines,
            "additional_instructions": additional_instructions,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "prescription_type": prescription_type.lower().replace(" ", "_")
        }

        st.session_state.app.data['prescriptions'].append(prescription_data)
        st.session_state.app.save_data('prescriptions')

        # Don't automatically mark appointment as completed here
        # Wait for doctor's confirmation

        notification = {
            "id": st.session_state.app.generate_id("notif"),
            "patient_id": selected_appointment["patient_id"],
            "message": f"Your prescription from Dr. {st.session_state.current_user['name']} is ready",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "read": False,
            "type": "prescription_ready"
        }

        st.session_state.app.data['notifications'].append(notification)
        st.session_state.app.save_data('notifications')

        st.session_state.selected_medicines = []

        st.success("✅ Prescription created successfully!")

        # Ask if doctor wants to complete the session and create another prescription
        st.info("Would you like to complete this session and create another prescription for the same patient?")

        # FIXED: Properly update the appointment status when "Complete Session" is clicked
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Complete Session", use_container_width=True, type="primary"):
                # Find and update the appointment in the main appointments list
                for appointment in st.session_state.app.data['appointments']:
                    if appointment['id'] == selected_appointment['id'] and appointment['status'] == 'scheduled':
                        appointment["status"] = "completed"
                        # Record earning for completed appointment
                        record_doctor_earning(appointment)
                        st.session_state.app.save_data('appointments')
                        st.success("Session completed successfully! You can now create a new prescription.")
                        st.rerun()

        with col2:
            if st.button("Continue Session", use_container_width=True):
                st.success("✅ Prescription saved. You can continue the session.")
                st.rerun()

    # Handle pharmacy prescription creation flow
    if st.session_state.get('create_pharmacy_prescription') and st.session_state.get('pharmacy_patient'):
        st.info("Creating Pharmacy Prescription for the same patient")

        # Pre-fill patient details
        patient = st.session_state.pharmacy_patient
        st.write(f"**Patient:** {patient['patient_name']}")
        st.write(f"**Age:** {patient.get('patient_age', 'N/A')}")

        # Create pharmacy prescription
        if st.session_state.selected_medicines and st.button("Create Pharmacy Prescription", use_container_width=True,
                                                             type="primary"):
            prescription_data = {
                "id": st.session_state.app.generate_id("pres"),
                "appointment_id": patient["id"],
                "patient_id": patient["patient_id"],
                "patient_name": patient["patient_name"],
                "patient_age": patient.get("patient_age", "N/A"),
                "doctor_id": st.session_state.current_user["id"],
                "doctor_name": st.session_state.current_user["name"],
                "doctor_qualifications": st.session_state.current_user.get("qualifications", ""),
                "doctor_slmc": st.session_state.current_user.get("slmc_registration", ""),
                "medicines": st.session_state.selected_medicines,
                "additional_instructions": additional_instructions,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "status": "active",
                "prescription_type": "pharmacy"
            }

            st.session_state.app.data['prescriptions'].append(prescription_data)
            st.session_state.app.save_data('prescriptions')

            notification = {
                "id": st.session_state.app.generate_id("notif"),
                "patient_id": patient["patient_id"],
                "message": f"Your pharmacy prescription from Dr. {st.session_state.current_user['name']} is ready",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "read": False,
                "type": "prescription_ready"
            }

            st.session_state.app.data['notifications'].append(notification)
            st.session_state.app.save_data('notifications')

            st.session_state.selected_medicines = []
            st.session_state.create_pharmacy_prescription = False
            st.session_state.pharmacy_patient = None

            st.success("✅ Pharmacy prescription created successfully!")


def view_prescription_history():
    """View prescription history with edit capability for today's prescriptions"""
    st.subheader("📜 Prescription History")

    prescriptions = [p for p in st.session_state.app.data['prescriptions']
                     if p["doctor_id"] == st.session_state.current_user["id"]]

    if not prescriptions:
        st.info("No prescriptions found.")
        return

    # Check if we're in edit mode
    if st.session_state.get('editing_prescription'):
        edit_prescription(st.session_state.editing_prescription)
        return

    prescription_dates = sorted(set([p['date'] for p in prescriptions]), reverse=True)
    today = datetime.now().strftime("%Y-%m-%d")

    for date in prescription_dates:
        date_prescriptions = [p for p in prescriptions if p['date'] == date]

        with st.expander(f"📅 {date} - {len(date_prescriptions)} prescriptions"):
            for pres in date_prescriptions:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**Patient:** {pres['patient_name']}")
                        st.write(f"**Type:** {pres.get('prescription_type', 'clinical').title()}")
                    with col2:
                        st.write(f"**Medicines:** {len(pres['medicines'])}")
                        st.write(f"**Status:** {pres['status']}")
                    with col3:
                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.button("View", key=f"view_{pres['id']}"):
                                st.session_state.selected_prescription = pres
                        with col_btn2:
                            # Allow editing only for today's prescriptions
                            if pres['date'] == today:
                                if st.button("Edit", key=f"edit_{pres['id']}"):
                                    st.session_state.editing_prescription = pres
                                    st.rerun()

                    st.markdown("---")

    if st.session_state.get('selected_prescription'):
        pres = st.session_state.selected_prescription
        st.write("### Prescription Details")
        st.write(f"**Date:** {pres['date']}")
        st.write(f"**Patient:** {pres['patient_name']} (Age: {pres.get('patient_age', 'N/A')})")
        st.write(f"**Type:** {pres.get('prescription_type', 'clinical').title()}")

        st.write("**Medicines:**")
        for med in pres['medicines']:
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{med['name']}** ({med['type']})")
                    st.write(f"Dosage: {med['dosage']}")
                    st.write(f"Quantity: {med['quantity']}")
                with col2:
                    st.write(f"Duration: {med.get('duration', 'N/A')} days")
                    st.write(f"Daily Usage: {med.get('daily_usage', 'N/A')}")
                    meal_info = "Before Meal" if med.get('before_meal') else "After Meal" if med.get(
                        'before_meal') is False else "Anytime"
                    st.write(f"Timing: {meal_info}")

                if med.get('instructions'):
                    st.write(f"Instructions: {med['instructions']}")

                st.markdown("---")

        if pres.get('additional_instructions'):
            st.write(f"**Additional Instructions:** {pres['additional_instructions']}")

        if st.button("Back to List"):
            del st.session_state.selected_prescription
            st.rerun()


def edit_prescription(prescription):
    """Edit an existing prescription"""
    st.subheader("✏️ Edit Prescription")

    st.write(f"**Editing prescription for:** {prescription['patient_name']}")
    st.write(f"**Date:** {prescription['date']}")
    st.write(f"**Type:** {prescription.get('prescription_type', 'clinical').title()}")

    # Initialize session state for editing if not exists
    if 'editing_medicines' not in st.session_state:
        st.session_state.editing_medicines = prescription['medicines'].copy()

    # Display current medicines with remove option
    st.write("### Current Medicines")
    for i, med in enumerate(st.session_state.editing_medicines):
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{med['name']}** - {med['dosage']}")
                st.write(f"Usage: {med['daily_usage']}, {med['duration']} days")
            with col2:
                st.write(f"Quantity: {med['quantity']}")
                meal_time = "Before meal" if med['before_meal'] else "After meal" if med[
                                                                                         'before_meal'] is not None else "Anytime"
                st.write(f"Timing: {meal_time}")
            with col3:
                if st.button("Remove", key=f"remove_edit_{i}"):
                    st.session_state.editing_medicines.pop(i)
                    st.rerun()
            st.markdown("---")

    # Add new medicine section
    st.write("### Add New Medicine")

    search_term = st.text_input("Search Medicine to Add")
    all_medicines = st.session_state.app.data["medicines"]
    filtered_meds = [med for med in all_medicines if
                     search_term.lower() in med['name'].lower()] if search_term else all_medicines[:5]

    for med in filtered_meds:
        with st.expander(f"{med['name']} - {med['dose']}"):
            with st.form(f"add_med_form_{med['id']}"):
                col1, col2 = st.columns(2)
                with col1:
                    dosage = st.text_input("Dosage", value=med['dose'], key=f"add_dosage_{med['id']}")
                    quantity = st.number_input("Quantity", min_value=1, value=1, key=f"add_qty_{med['id']}")
                    duration = st.number_input("Duration (days)", min_value=1, value=7, key=f"add_dur_{med['id']}")
                with col2:
                    daily_usage = st.selectbox("Times per day", ["1 time", "2 times", "3 times", "4 times"],
                                               key=f"add_usage_{med['id']}")
                    before_meal = st.radio("Take", ["Before Meal", "After Meal", "Anytime"],
                                           key=f"add_meal_{med['id']}")
                    instructions = st.text_area("Instructions", key=f"add_inst_{med['id']}")

                if st.form_submit_button("Add Medicine"):
                    new_medicine = {
                        "id": med["id"],
                        "name": med["name"],
                        "type": med["type"],
                        "dosage": dosage,
                        "quantity": quantity,
                        "duration": duration,
                        "daily_usage": daily_usage,
                        "before_meal": before_meal == "Before Meal",
                        "instructions": instructions
                    }
                    st.session_state.editing_medicines.append(new_medicine)
                    st.success(f"Added {med['name']}")
                    st.rerun()

    # Additional instructions
    current_instructions = prescription.get('additional_instructions', '')
    additional_instructions = st.text_area("Additional Instructions", value=current_instructions)

    # Save/Cancel buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Save Changes", type="primary", use_container_width=True):
            # Update prescription
            prescription['medicines'] = st.session_state.editing_medicines
            prescription['additional_instructions'] = additional_instructions
            prescription['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.session_state.app.save_data('prescriptions')

            # Clear editing state
            del st.session_state.editing_medicines
            del st.session_state.editing_prescription

            st.success("✅ Prescription updated successfully!")
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            # Clear editing state
            if 'editing_medicines' in st.session_state:
                del st.session_state.editing_medicines
            if 'editing_prescription' in st.session_state:
                del st.session_state.editing_prescription
            st.rerun()

    with col3:
        if st.button("Back to History", use_container_width=True):
            # Clear editing state
            if 'editing_medicines' in st.session_state:
                del st.session_state.editing_medicines
            if 'editing_prescription' in st.session_state:
                del st.session_state.editing_prescription
            st.session_state.dashboard_page = "prescription_history"
            st.rerun()


def add_patient_to_session():
    """Allow doctors to add patients directly to sessions"""
    st.subheader("👥 Add Patient to Session")

    today = datetime.now().strftime("%Y-%m-%d")
    upcoming_sessions = [s for s in st.session_state.app.data['sessions']
                         if s["doctor_id"] == st.session_state.current_user["id"] and s["date"] >= today]

    if not upcoming_sessions:
        st.info("No upcoming sessions found. Please create a session first.")
        return

    session_options = {f"{s['date']} {s.get('start_time', '')} - {s.get('location', 'Clinic')}": s for s in
                       upcoming_sessions}
    selected_session_label = st.selectbox("Select Session", list(session_options.keys()))
    selected_session = session_options[selected_session_label]

    st.write(f"**Selected Session:** {selected_session['date']} {selected_session.get('start_time', '')}")
    st.write(f"**Location:** {selected_session.get('location', 'Clinic')}")

    st.write("#### Patient Information")

    col1, col2 = st.columns(2)

    with col1:
        patient_name = st.text_input("Patient Name*")
        patient_age = st.number_input("Patient Age*", min_value=0, max_value=120)
        patient_gender = st.selectbox("Gender*", ["Male", "Female"])

    with col2:
        patient_contact = st.text_input("Contact Number*")
        patient_nic = st.text_input("NIC Number (Optional)")
        patient_city = st.selectbox("City", get_all_cities())

    booked_appointments = [app for app in st.session_state.app.data["appointments"]
                           if app["doctor_id"] == st.session_state.current_user["id"]
                           and app["date"] == selected_session["date"]]
    booked_numbers = [app.get("appointment_number", 0) for app in booked_appointments]

    next_available = 1
    while next_available in booked_numbers:
        next_available += 1

    st.write(f"**Next Available Appointment Number:** {next_available}")

    if st.button("Add Patient to Session", type="primary"):
        if not all([patient_name, patient_contact]):
            st.error("Please fill in all required fields (*)")
            return

        new_appointment = {
            "id": st.session_state.app.generate_id("app"),
            "appointment_number": next_available,
            "patient_id": f"direct_{st.session_state.app.generate_id('direct')}",
            "patient_name": patient_name,
            "patient_age": patient_age,
            "patient_gender": patient_gender,
            "patient_contact": patient_contact,
            "patient_nic": patient_nic,
            "patient_city": patient_city,
            "doctor_id": selected_session["doctor_id"],
            "doctor_name": st.session_state.current_user["name"],
            "session_id": selected_session["id"],
            "type": selected_session.get("type", "clinic"),
            "date": selected_session["date"],
            "time_slot": selected_session.get("start_time", ""),
            "status": "scheduled",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "added_directly": True
        }

        st.session_state.app.data["appointments"].append(new_appointment)
        st.session_state.app.save_data('appointments')

        st.success(f"✅ Patient {patient_name} added successfully to session! Appointment number: {next_available}")