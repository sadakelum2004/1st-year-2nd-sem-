# utils.py
import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import uuid
import re
from typing import Dict, List, Any, Optional
import random
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import base64

# Sri Lankan Cities with approximate coordinates (flattened list)
SRI_LANKAN_CITIES = {
    # Colombo District
    "Colombo 1": (6.9271, 79.8612),
    "Colombo 2": (6.9271, 79.8612),
    "Colombo 3": (6.9271, 79.8612),
    "Colombo 4": (6.9271, 79.8612),
    "Colombo 5": (6.9271, 79.8612),
    "Colombo 6": (6.9271, 79.8612),
    "Colombo 7": (6.9271, 79.8612),
    "Colombo 8": (6.9271, 79.8612),
    "Colombo 9": (6.9271, 79.8612),
    "Colombo 10": (6.9271, 79.8612),
    "Colombo 11": (6.9271, 79.8612),
    "Colombo 12": (6.9271, 79.8612),
    "Colombo 13": (6.9271, 79.8612),
    "Colombo 14": (6.9271, 79.8612),
    "Colombo 15": (6.9271, 79.8612),
    "Dehiwala": (6.8557, 79.8630),
    "Mount Lavinia": (6.8279, 79.8648),
    "Ratmalana": (6.8214, 79.8863),
    "Moratuwa": (6.7824, 79.8800),

    # Gampaha District
    "Gampaha": (7.0917, 79.9997),
    "Negombo": (7.2086, 79.8357),
    "Ja-Ela": (7.0744, 79.8919),
    "Wattala": (6.9890, 79.8833),
    "Kadawatha": (6.9847, 79.9775),
    "Ragama": (7.0303, 79.9178),
    "Kelaniya": (6.9600, 79.8978),
    "Minuwangoda": (7.1733, 79.9619),
    "Divulapitiya": (7.2547, 80.0006),
    "Mirigama": (7.2425, 80.1308),
    "Veyangoda": (7.1517, 80.1000),

    # Kalutara District
    "Kalutara": (6.5894, 79.9573),
    "Panadura": (6.7133, 79.9042),
    "Horana": (6.7156, 80.0606),
    "Bandaragama": (6.7114, 79.9847),
    "Matugama": (6.5228, 80.1142),
    "Agalawatta": (6.5419, 80.1569),

    # Kandy District
    "Kandy": (7.2906, 80.6337),
    "Peradeniya": (7.2544, 80.5972),
    "Gampola": (7.1647, 80.5761),
    "Nawalapitiya": (7.0500, 80.5333),
    "Kadugannawa": (7.2542, 80.5278),
    "Pilimatalawa": (7.2694, 80.5458),

    # Matale District
    "Matale": (7.4675, 80.6234),
    "Dambulla": (7.8575, 80.6519),
    "Galewela": (7.8167, 80.6000),

    # Nuwara Eliya District
    "Nuwara Eliya": (6.9497, 80.7891),
    "Hatton": (6.8917, 80.5958),
    "Talawakele": (6.9375, 80.6583),
    "Ginigathena": (6.9833, 80.4833),

    # Galle District
    "Galle": (6.0535, 80.2210),
    "Ambalangoda": (6.2358, 80.0539),
    "Hikkaduwa": (6.1403, 80.1017),
    "Elpitiya": (6.2889, 80.1569),
    "Karapitiya": (6.0833, 80.2167),

    # Matara District
    "Matara": (5.9480, 80.5353),
    "Weligama": (5.9747, 80.4294),
    "Dikwella": (5.9667, 80.6833),
    "Hakmana": (6.0833, 80.5667),

    # Hambantota District
    "Hambantota": (6.1249, 81.1187),
    "Tangalle": (6.0231, 80.7889),
    "Ambalantota": (6.1167, 81.0333),
    "Tissamaharama": (6.2833, 81.2833),

    # Jaffna District
    "Jaffna": (9.6615, 80.0255),
    "Chavakachcheri": (9.6667, 80.1500),
    "Point Pedro": (9.8167, 80.2333),

    # Kilinochchi District
    "Kilinochchi": (9.3964, 80.3983),

    # Mannar District
    "Mannar": (8.9776, 79.9099),

    # Mullaitivu District
    "Mullaitivu": (9.2671, 80.8142),

    # Vavuniya District
    "Vavuniya": (8.7524, 80.4985),

    # Trincomalee District
    "Trincomalee": (8.5874, 81.2152),

    # Batticaloa District
    "Batticaloa": (7.7168, 81.6924),
    "Kattankudy": (7.6833, 81.7333),

    # Ampara District
    "Ampara": (7.2975, 81.6820),
    "Kalmunai": (7.4167, 81.8167),

    # Badulla District
    "Badulla": (6.9934, 81.0550),
    "Bandarawela": (6.8258, 80.9981),
    "Welimada": (6.9000, 80.9833),
    "Hali-Ela": (6.9667, 81.0333),

    # Monaragala District
    "Monaragala": (6.8724, 81.3509),

    # Ratnapura District
    "Ratnapura": (6.7057, 80.3847),
    "Embilipitiya": (6.3436, 80.8489),
    "Balangoda": (6.6500, 80.7000),

    # Kegalle District
    "Kegalle": (7.2513, 80.3464),
    "Mawanella": (7.2500, 80.4500),
    "Warakapola": (7.2167, 80.1667),

    # Polonnaruwa District
    "Polonnaruwa": (7.9329, 81.0081),
    "Kaduruwela": (7.7833, 81.1333),

    # Anuradhapura District
    "Anuradhapura": (8.3114, 80.4037),
    "Medawachchiya": (8.5500, 80.5000)
}


def set_background():
    """Modern transparent medical-style Streamlit UI without white overlay"""
    st.markdown("""  
    <style>
/* Global Background — Enhanced for readability */
.stApp {
    background: 
        linear-gradient(rgba(0, 30, 60, 0.85), rgba(0, 30, 60, 0.85)),
        url('https://hips.hearstapps.com/hmg-prod/images/types-of-doctors-1600114658.jpg?crop=1.00xw:1.00xh;0,0&resize=1800:*');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    min-height: 100vh;
    color: #f0f4f8;
}

/* Title with Enhanced Contrast */
.main-header {
    font-size: 4rem;
    text-align: center;
    margin-bottom: 2.5rem;
    font-weight: 800;
    color: #ffffff;
    text-shadow: 0 0 15px rgba(59,130,246,0.8), 0 0 25px rgba(37,99,235,0.6), 0 2px 4px rgba(0,0,0,0.5);
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-top: 2rem;
    background: rgba(0, 30, 60, 0.8);
    padding: 1rem 2rem;
    border-radius: 20px;
    display: inline-block;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.15);
}

/* Enhanced Glass Cards with Reduced Transparency */
.form-container {
    background: rgba(0, 20, 40, 0.9);
    backdrop-filter: blur(15px);
    padding: 2.5rem;
    border-radius: 24px;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5),
                inset 0 0 25px rgba(255, 255, 255, 0.08);
    transition: all 0.3s ease-in-out;
    color: #f0f4f8;
}

.form-container:hover {
    background: rgba(0, 30, 60, 0.95);
    transform: translateY(-5px);
    box-shadow: 0 15px 50px rgba(0, 0, 0, 0.6),
                inset 0 0 30px rgba(255, 255, 255, 0.1);
}

/* Sub-Header with Better Contrast */
.sub-header {
    font-size: 1.8rem;
    text-align: center;
    font-weight: 700;
    color: #a5b4fc;
    text-shadow: 0 0 12px rgba(59,130,246,0.8), 0 2px 4px rgba(0,0,0,0.3);
    margin-bottom: 1.5rem;
    background: rgba(0, 20, 40, 0.85);
    padding: 0.5rem 1.5rem;
    border-radius: 12px;
    display: inline-block;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Enhanced Buttons with Reduced Transparency */
.dashboard-button {
    width: 100%;
    margin: 10px 0;
    padding: 16px 22px;
    font-size: 17px;
    font-weight: 600;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.3);
    color: #ffffff;
    background: rgba(59,130,246,0.45);
    backdrop-filter: blur(12px);
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

.dashboard-button:hover {
    background: rgba(59,130,246,0.6);
    border-color: rgba(59,130,246,0.7);
    box-shadow: 0 0 20px rgba(59,130,246,0.7);
    transform: translateY(-3px);
    color: #ffffff;
}

.dashboard-button:active {
    transform: scale(0.98);
    box-shadow: 0 0 10px rgba(59,130,246,0.5);
}

/* Enhanced Status Boxes with Reduced Transparency */
.success-box {
    background: rgba(16,185,129,0.35);
    border: 1px solid rgba(16,185,129,0.5);
    color: #d1fae5;
    border-left: 5px solid #10b981;
    backdrop-filter: blur(15px);
    border-radius: 18px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 0 20px rgba(16,185,129,0.4);
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

.info-box {
    background: rgba(59,130,246,0.35);
    border: 1px solid rgba(59,130,246,0.5);
    color: #dbeafe;
    border-left: 5px solid #3b82f6;
    backdrop-filter: blur(15px);
    border-radius: 18px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 0 20px rgba(59,130,246,0.4);
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

.warning-box {
    background: rgba(245,158,11,0.35);
    border: 1px solid rgba(245,158,11,0.5);
    color: #fef3c7;
    border-left: 5px solid #f59e0b;
    backdrop-filter: blur(15px);
    border-radius: 18px;
    padding: 1.5rem 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 0 20px rgba(245,158,11,0.4);
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

/* Enhanced Medicine Card with Reduced Transparency */
.medicine-card {
    background: rgba(0, 20, 40, 0.85);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    margin: 1rem 0;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    color: #f0f4f8;
}

.medicine-card:hover {
    background: rgba(0, 30, 60, 0.9);
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(0,0,0,0.5);
    border-color: rgba(59,130,246,0.5);
}

/* Enhanced Inputs with Reduced Transparency */
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stSelectbox>div>div>select {
    background: rgba(0, 20, 40, 0.9) !important;
    color: #f0f4f8 !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease-in-out !important;
}

.stTextInput>div>div>input:focus,
.stNumberInput>div>div>input:focus,
.stSelectbox>div>div>select:focus {
    border-color: #60a5fa !important;
    background: rgba(59,130,246,0.4) !important;
    box-shadow: 0 0 8px rgba(59,130,246,0.7) !important;
    color: #ffffff !important;
}

/* Labels for inputs */
.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    color: #e2e8f0 !important;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

/* Enhanced Sidebar with Reduced Transparency */
[data-testid="stSidebar"] {
    background: rgba(0, 10, 20, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255,255,255,0.2) !important;
}

[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stText {
    color: #f0f4f8 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

/* Enhanced Status Badges with Reduced Transparency */
.status-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0 4px;
    border: 1px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(10px);
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

.badge-success { 
    background: rgba(16,185,129,0.4); 
    color: #a7f3d0; 
    border-color: rgba(16,185,129,0.6);
}
.badge-warning { 
    background: rgba(245,158,11,0.4); 
    color: #fde68a; 
    border-color: rgba(245,158,11,0.6);
}
.badge-info { 
    background: rgba(59,130,246,0.4); 
    color: #bfdbfe; 
    border-color: rgba(59,130,246,0.6);
}

/* Enhanced Divider Line */
.section-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(59,130,246,0.9), transparent);
    margin: 2.5rem 0;
    border: none;
    box-shadow: 0 0 10px rgba(59,130,246,0.4);
}

/* Additional text elements */
.stMarkdown, .stText {
    color: #f0f4f8 !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.4);
}

/* Table enhancements with Reduced Transparency */
.stTable {
    background: rgba(0, 20, 40, 0.9) !important;
    backdrop-filter: blur(10px);
    border-radius: 12px;
    overflow: hidden;
}

.stTable th {
    background: rgba(59,130,246,0.5) !important;
    color: #ffffff !important;
    font-weight: 700;
}

.stTable td {
    background: rgba(255,255,255,0.1) !important;
    color: #f0f4f8 !important;
    border-bottom: 1px solid rgba(255,255,255,0.15) !important;
}

/* Additional container for any custom content */
.content-container {
    background: rgba(0, 20, 40, 0.9);
    backdrop-filter: blur(15px);
    border-radius: 18px;
    padding: 2rem;
    margin: 1.5rem 0;
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
</style>
    """, unsafe_allow_html=True)


class MyDoctorApp:
    def __init__(self):
        self.data_dir = "my_doctor_data"
        self.files = {
            'patients': "patients.json",
            'doctors': "doctors.json",
            'pharmacies': "pharmacies.json",
            'appointments': "appointments.json",
            'prescriptions': "prescriptions.json",
            'medicines': "medicines.csv",
            'notifications': "notifications.json",
            'sessions': "sessions.json",
            'inventory': "inventory.json",
            'prescription_pharmacy': "prescription_pharmacy.json",
            'favorite_medicines': "favorite_medicines.json",
            'chats': "chats.json",
            'notices': "notices.json"
        }

        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Initialize data files
        self.initialize_data_files()

        # Load all data
        self.data = {}

        for key, filename in self.files.items():
            if key == 'medicines':
                self.data[key] = self.load_medicines_data(os.path.join(self.data_dir, filename))
            else:
                self.data[key] = self.load_data(os.path.join(self.data_dir, filename))

    def initialize_data_files(self):
        """Initialize data files with sample data"""
        # Enhanced medicine list with 100+ common medicines
        sample_medicines = [
            # Painkillers and Anti-inflammatory (1-20)
            {"id": "med001", "name": "Paracetamol", "common_price": 50.0, "type": "tablet", "dose": "500mg",
             "category": "Pain Relief"},
            {"id": "med002", "name": "Ibuprofen", "common_price": 90.0, "type": "tablet", "dose": "400mg",
             "category": "Pain Relief"},
            {"id": "med003", "name": "Aspirin", "common_price": 45.0, "type": "tablet", "dose": "300mg",
             "category": "Pain Relief"},
            {"id": "med004", "name": "Diclofenac", "common_price": 120.0, "type": "tablet", "dose": "50mg",
             "category": "Pain Relief"},
            {"id": "med005", "name": "Naproxen", "common_price": 150.0, "type": "tablet", "dose": "250mg",
             "category": "Pain Relief"},

            # Antibiotics (21-40)
            {"id": "med006", "name": "Amoxicillin", "common_price": 80.0, "type": "capsule", "dose": "500mg",
             "category": "Antibiotic"},
            {"id": "med007", "name": "Ciprofloxacin", "common_price": 95.0, "type": "tablet", "dose": "500mg",
             "category": "Antibiotic"},
            {"id": "med008", "name": "Doxycycline", "common_price": 110.0, "type": "capsule", "dose": "100mg",
             "category": "Antibiotic"},
            {"id": "med009", "name": "Azithromycin", "common_price": 200.0, "type": "tablet", "dose": "500mg",
             "category": "Antibiotic"},

            # Allergy (41-50)
            {"id": "med010", "name": "Cetirizine", "common_price": 40.0, "type": "tablet", "dose": "10mg",
             "category": "Allergy"},
            {"id": "med011", "name": "Loratadine", "common_price": 45.0, "type": "tablet", "dose": "10mg",
             "category": "Allergy"},

            # Diabetes (51-60)
            {"id": "med012", "name": "Metformin", "common_price": 60.0, "type": "tablet", "dose": "500mg",
             "category": "Diabetes"},
            {"id": "med013", "name": "Glibenclamide", "common_price": 55.0, "type": "tablet", "dose": "5mg",
             "category": "Diabetes"},

            # Cardiovascular (61-70)
            {"id": "med014", "name": "Atenolol", "common_price": 35.0, "type": "tablet", "dose": "50mg",
             "category": "Cardiovascular"},
            {"id": "med015", "name": "Amlodipine", "common_price": 40.0, "type": "tablet", "dose": "5mg",
             "category": "Cardiovascular"},

            # Gastrointestinal (71-80)
            {"id": "med016", "name": "Omeprazole", "common_price": 75.0, "type": "capsule", "dose": "20mg",
             "category": "Gastrointestinal"},
            {"id": "med017", "name": "Ranitidine", "common_price": 50.0, "type": "tablet", "dose": "150mg",
             "category": "Gastrointestinal"},

            # Respiratory (81-90)
            {"id": "med018", "name": "Salbutamol", "common_price": 120.0, "type": "inhaler", "dose": "100mcg",
             "category": "Respiratory"},
            {"id": "med019", "name": "Montelukast", "common_price": 85.0, "type": "tablet", "dose": "10mg",
             "category": "Respiratory"},

            # Vitamins (91-100)
            {"id": "med020", "name": "Vitamin C", "common_price": 25.0, "type": "tablet", "dose": "500mg",
             "category": "Vitamin"},
            {"id": "med021", "name": "Vitamin D", "common_price": 30.0, "type": "capsule", "dose": "1000IU",
             "category": "Vitamin"}
        ]

        for key, filename in self.files.items():
            file_path = os.path.join(self.data_dir, filename)
            if not os.path.exists(file_path):
                if key == 'medicines':
                    self.save_medicines_to_csv(file_path, sample_medicines)
                else:
                    default_data = []
                    with open(file_path, 'w') as f:
                        json.dump(default_data, f, indent=4)

    def load_data(self, file_path):
        """Load data from JSON file with error handling"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def load_medicines_data(self, file_path):
        """Load medicines data from CSV file"""
        try:
            medicines = []
            with open(file_path, 'r', newline="", encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['common_price'] = float(row['common_price'])
                    medicines.append(row)
            return medicines
        except (FileNotFoundError, KeyError, ValueError):
            return []

    def save_medicines_to_csv(self, file_path, medicines):
        """Save medicines data to CSV file"""
        try:
            with open(file_path, 'w', newline="", encoding='utf-8') as f:
                if medicines:
                    fieldnames = medicines[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(medicines)
        except Exception as e:
            st.error(f"Error saving medicines: {e}")

    def save_data(self, key):
        """Save data to appropriate file format"""
        file_path = os.path.join(self.data_dir, self.files[key])
        if key == 'medicines':
            self.save_medicines_to_csv(file_path, self.data[key])
        else:
            with open(file_path, 'w') as f:
                json.dump(self.data[key], f, indent=4)

    def generate_id(self, prefix):
        """Generate a unique ID"""
        return f"{prefix}_{str(uuid.uuid4())[:8]}"

    def calculate_age(self, birth_date):
        """Calculate age from birth date"""
        try:
            if isinstance(birth_date, str):
                birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        except:
            return None

    def get_appointment_number(self, doctor_id, date):
        """Generate sequential appointment number"""
        appointments = [app for app in self.data['appointments']
                        if app["doctor_id"] == doctor_id and app["date"] == date]
        return len(appointments) + 1

    def check_medicine_availability(self, prescription_id, pharmacy_id):
        """Check medicine availability for a prescription"""
        prescription = next((p for p in self.data['prescriptions'] if p["id"] == prescription_id), None)
        if not prescription:
            return False, []

        inventory = [inv for inv in self.data['inventory'] if inv["pharmacy_id"] == pharmacy_id]
        unavailable_medicines = []

        for med in prescription["medicines"]:
            available = any(inv for inv in inventory
                            if inv["medicine_id"] == med["id"] and inv["quantity"] >= med["quantity"])
            if not available:
                unavailable_medicines.append(med["name"])
        return len(unavailable_medicines) == 0, unavailable_medicines

    def get_current_appointment_status(self, appointment_id):
        """Get current appointment status with queue information"""
        appointment = next((app for app in self.data['appointments'] if app["id"] == appointment_id), None)
        if not appointment:
            return None

        session_id = appointment.get("session_id")
        if not session_id or session_id == "direct":
            return None

        session_appointments = [app for app in self.data['appointments']
                                if app.get("session_id") == session_id and app["status"] == "scheduled"]

        session_appointments.sort(key=lambda x: x.get("appointment_number", 0))

        current_position = None
        for i, app in enumerate(session_appointments, 1):
            if app["id"] == appointment_id:
                current_position = i
                break

        if current_position:
            session = next((sess for sess in self.data['sessions'] if sess["id"] == session_id), None)
            if session:
                return {
                    "current_position": current_position,
                    "total_in_queue": len(session_appointments),
                    "estimated_wait_time": current_position * session.get("min_time_per_patient", 15),
                    "session_start_time": session.get("start_time", ""),
                    "min_time_per_patient": session.get("min_time_per_patient", 15)
                }
        return None

    def generate_username(self, name, phone):
        """Generate username from name and phone"""
        base_username = name.lower().replace(" ", "") + phone[-4:]
        return base_username

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        R = 6371  # Earth radius in kilometers
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) * math.sin(delta_lat / 2) +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) * math.sin(delta_lon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def get_nearby_doctors(self, patient_lat, patient_lon, max_distance_km=50):
        """Get nearby doctors based on patient location"""
        nearby_doctors = []
        for doctor in self.data['doctors']:
            # Get doctor's city coordinates
            if 'city' in doctor and doctor['city'] in SRI_LANKAN_CITIES:
                doc_coords = SRI_LANKAN_CITIES[doctor['city']]
                doc_lat, doc_lon = doc_coords

                # Add small random offset to simulate different locations within city
                doc_lat += random.uniform(-0.05, 0.05)
                doc_lon += random.uniform(-0.05, 0.05)

                distance = self.calculate_distance(
                    patient_lat, patient_lon,
                    doc_lat, doc_lon
                )
                if distance <= max_distance_km:
                    doctor_copy = doctor.copy()
                    doctor_copy['distance'] = round(distance, 2)
                    doctor_copy['latitude'] = doc_lat
                    doctor_copy['longitude'] = doc_lon
                    nearby_doctors.append(doctor_copy)

        nearby_doctors.sort(key=lambda x: x['distance'])
        return nearby_doctors

    def get_nearby_pharmacies(self, patient_lat, patient_lon, max_distance_km=50):
        """Get nearby pharmacies based on patient location"""
        nearby_pharmacies = []
        for pharmacy in self.data['pharmacies']:
            # Get pharmacy's city coordinates
            if 'city' in pharmacy and pharmacy['city'] in SRI_LANKAN_CITIES:
                pharm_coords = SRI_LANKAN_CITIES[pharmacy['city']]
                pharm_lat, pharm_lon = pharm_coords

                # Add small random offset to simulate different locations within city
                pharm_lat += random.uniform(-0.05, 0.05)
                pharm_lon += random.uniform(-0.05, 0.05)

                distance = self.calculate_distance(
                    patient_lat, patient_lon,
                    pharm_lat, pharm_lon
                )
                if distance <= max_distance_km:
                    pharmacy_copy = pharmacy.copy()
                    pharmacy_copy['distance'] = round(distance, 2)
                    pharmacy_copy['latitude'] = pharm_lat
                    pharmacy_copy['longitude'] = pharm_lon
                    nearby_pharmacies.append(pharmacy_copy)

        nearby_pharmacies.sort(key=lambda x: x['distance'])
        return nearby_pharmacies

    def add_medicine_to_inventory(self, pharmacy_id, medicine_id, quantity, unit_price, expiry_date, batch_number=""):
        """Add medicine to pharmacy inventory"""
        medicine = next((med for med in self.data['medicines'] if med['id'] == medicine_id), None)
        if not medicine:
            return False, "Medicine not found"

        existing_item = next((inv for inv in self.data['inventory']
                              if inv['pharmacy_id'] == pharmacy_id and inv['medicine_id'] == medicine_id), None)

        if existing_item:
            existing_item['quantity'] += quantity
            existing_item['unit_price'] = unit_price
            existing_item['expiry_date'] = expiry_date
            if batch_number:
                existing_item['batch_number'] = batch_number
            existing_item['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            new_item = {
                "id": self.generate_id("inv"),
                "pharmacy_id": pharmacy_id,
                "medicine_id": medicine_id,
                "medicine_name": medicine['name'],
                "medicine_type": medicine['type'],
                "medicine_dose": medicine['dose'],
                "quantity": quantity,
                "unit_price": unit_price,
                "expiry_date": expiry_date,
                "batch_number": batch_number,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.data['inventory'].append(new_item)

        self.save_data('inventory')
        return True, "Medicine added to inventory successfully"

    def add_new_medicine(self, medicine_data):
        """Add new medicine to the medicine list"""
        medicine_data["id"] = self.generate_id("med")
        self.data['medicines'].append(medicine_data)
        self.save_data('medicines')
        return True, "Medicine added successfully"

    def delete_medicine(self, medicine_id):
        """Delete medicine from the medicine list"""
        medicine = next((med for med in self.data['medicines'] if med['id'] == medicine_id), None)
        if medicine:
            self.data['medicines'].remove(medicine)
            self.save_data('medicines')
            return True, "Medicine deleted successfully"
        return False, "Medicine not found"


def init_session_state():
    """Initialize session state variables"""
    if 'app' not in st.session_state:
        st.session_state.app = MyDoctorApp()
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_type' not in st.session_state:
        st.session_state.user_type = None
    if 'page' not in st.session_state:
        st.session_state.page = "main"
    if 'dashboard_page' not in st.session_state:
        st.session_state.dashboard_page = "overview"
    if 'selected_prescription' not in st.session_state:
        st.session_state.selected_prescription = None
    if 'selected_doctor' not in st.session_state:
        st.session_state.selected_doctor = None
    if 'selected_pharmacy' not in st.session_state:
        st.session_state.selected_pharmacy = None
    if 'selected_session' not in st.session_state:
        st.session_state.selected_session = None
    if 'selected_shared_prescription' not in st.session_state:
        st.session_state.selected_shared_prescription = None
    if 'selected_prescription_chat' not in st.session_state:
        st.session_state.selected_prescription_chat = None
    if 'selected_inventory_item' not in st.session_state:
        st.session_state.selected_inventory_item = None
    if 'medicine_to_add' not in st.session_state:
        st.session_state.medicine_to_add = None


def display_header():
    """Display the main header"""
    set_background()
    st.markdown('<h1 class="main-header">🏥Your Doctor Appointment System</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; color: #4b5563; font-size: 1.2rem;">Connecting Patients, Doctors & Pharmacies in Sri Lanka</p>',
        unsafe_allow_html=True)


def main_page():
    """Display the main page with login and registration options"""
    display_header()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("👤 Patient")
        if st.button("Patient Login", use_container_width=True, key="patient_login_main", type="primary"):
            st.session_state.page = "patient_login"
        if st.button("Patient Registration", use_container_width=True, key="patient_register_main"):
            st.session_state.page = "patient_register"

    with col2:
        st.subheader("👨‍⚕️ Doctor")
        if st.button("Doctor Login", use_container_width=True, key="doctor_login_main", type="primary"):
            st.session_state.page = "doctor_login"
        if st.button("Doctor Registration", use_container_width=True, key="doctor_register_main"):
            st.session_state.page = "doctor_register"

    with col3:
        st.subheader("💊 Pharmacy")
        if st.button("Pharmacy Login", use_container_width=True, key="pharmacy_login_main", type="primary"):
            st.session_state.page = "pharmacy_login"
        if st.button("Pharmacy Registration", use_container_width=True, key="pharmacy_register_main"):
            st.session_state.page = "pharmacy_register"

    # Display statistics
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Patients", len(st.session_state.app.data['patients']))
    with col2:
        st.metric("Total Doctors", len(st.session_state.app.data['doctors']))
    with col3:
        st.metric("Total Pharmacies", len(st.session_state.app.data['pharmacies']))


def view_notifications():
    """View notifications"""
    st.subheader("🔔 Notifications")

    if st.session_state.user_type == "patient":
        notifications = [notif for notif in st.session_state.app.data['notifications']
                         if notif.get("patient_id") == st.session_state.current_user["id"]]
    elif st.session_state.user_type == "pharmacy":
        notifications = [notif for notif in st.session_state.app.data['notifications']
                         if notif.get("pharmacy_id") == st.session_state.current_user["id"]]
    elif st.session_state.user_type == "doctor":
        notifications = [notif for notif in st.session_state.app.data['notifications']
                         if notif.get("doctor_id") == st.session_state.current_user["id"]]
    else:
        notifications = []

    if not notifications:
        st.info("No notifications found.")
        return

    unread_count = sum(1 for notif in notifications if not notif.get("read", False))
    st.write(f"**Unread notifications:** {unread_count}")

    # Mark all as read button
    if unread_count > 0 and st.button("Mark All as Read"):
        for notification in notifications:
            notification["read"] = True
        st.session_state.app.save_data('notifications')
        st.success("All notifications marked as read!")
        st.rerun()

    # Display notifications
    for notification in sorted(notifications, key=lambda x: x['date'], reverse=True):
        read_status = "🔴" if not notification.get("read", False) else "⚪"
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(f"{read_status} {notification['message']}")
                st.write(f"Date: {notification['date']}")

            with col2:
                if not notification.get("read", False):
                    if st.button("Mark Read", key=f"read_{notification['id']}"):
                        notification["read"] = True
                        st.session_state.app.save_data('notifications')
                        st.rerun()

            st.markdown("---")


def get_all_cities():
    """Get all cities from SRI_LANKAN_CITIES"""
    return sorted(SRI_LANKAN_CITIES.keys())


def get_city_coordinates(city):
    """Get coordinates for a city"""
    return SRI_LANKAN_CITIES.get(city, (6.9271, 79.8612))  # Colombo default if city not found


def main():
    init_session_state()

    if st.session_state.page == "main":
        main_page()
    # Other page handling would go here...


if __name__ == "__main__":
    main()