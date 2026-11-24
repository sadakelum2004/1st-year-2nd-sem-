# this is main.py
import streamlit as st
from patient import *
from doctor import *
from pharmacy import *
from utils import *


def main():
    """Main application function"""
    init_session_state()

    # Page routing
    if st.session_state.page == "main":
        main_page()
    elif st.session_state.page == "patient_register":
        patient_registration()
    elif st.session_state.page == "patient_login":
        patient_login()
    elif st.session_state.page == "doctor_register":
        doctor_registration()
    elif st.session_state.page == "doctor_login":
        doctor_login()
    elif st.session_state.page == "pharmacy_register":
        pharmacy_registration()
    elif st.session_state.page == "pharmacy_login":
        pharmacy_login()
    elif st.session_state.page == "patient_dashboard" and st.session_state.current_user:
        patient_dashboard()
    elif st.session_state.page == "doctor_dashboard" and st.session_state.current_user:
        doctor_dashboard()
    elif st.session_state.page == "pharmacy_dashboard" and st.session_state.current_user:
        pharmacy_dashboard()
    else:
        main_page()


if __name__ == "__main__":
    main()

    # Display conversations


