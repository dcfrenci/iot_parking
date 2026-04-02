#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import os
import sys
import requests
import argparse
from datetime import date, timedelta

try:
    import argcomplete
except ImportError:
    argcomplete = None

# --- Configuration ---
# Adjust this if your FastAPI server does not use the /v1 prefix
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000/v1")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")

session = requests.Session()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_admin_account_id():
    """Logs in as admin and returns the account_id."""
    try:
        res = session.post(f"{BASE_URL}/login", json={"email": ADMIN_EMAIL, "pass": ADMIN_PASS})
        if res.status_code == 200:
            return res.json()["account_id"]
        print(f"Login failed (Admin might not exist): {res.text}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to {BASE_URL}. Is FastAPI running?")
        sys.exit(1)

def get_parkings():
    """Fetches all parkings."""
    res = session.get(f"{BASE_URL}/parkings/all")
    return res.json() if res.status_code == 200 else []

def get_plates(account_id):
    """Fetches all plates for a specific account."""
    res = session.get(f"{BASE_URL}/user/plates", params={"account_id": account_id})
    return res.json() if res.status_code == 200 else []

def get_active_sessions(account_id):
    """Fetches active parking sessions for an account."""
    res = session.get(f"{BASE_URL}/paying", params={"account_id": account_id})
    return res.json() if res.status_code == 200 else []

# ==========================================
# COMMAND FUNCTIONS
# ==========================================

def cmd_create_admin():
    print("\n--- Creating Admin User ---")
    payload = {"name": "Admin", "email": ADMIN_EMAIL, "pass": ADMIN_PASS}
    try:
        res = session.post(f"{BASE_URL}/register", json=payload)
        if res.status_code == 201:
            print(f"Success! Admin created (Account ID: {res.json().get('account_id')})")
        elif res.status_code == 409:
            print("Notice: Admin user already exists.")
        else:
            print(f"Failed: HTTP {res.status_code} - {res.text}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Connection failed.")

def cmd_delete_admin():
    print("\n--- Deleting Admin User ---")
    account_id = get_admin_account_id()
    if not account_id: return
    
    res = session.delete(f"{BASE_URL}/user", params={"account_id": account_id})
    if res.status_code == 200:
        print("Success! Admin user permanently deleted.")
    else:
        print(f"Failed to delete admin: {res.text}")

def cmd_init_parkings():
    print("\n--- Initializing Italian Parkings ---")
    italian_parkings = [
        {"parking_name": "Novi Park", "total_slot": 800, "available_slot": 350, "price_per_hour": 1.20, "lat": 44.651111, "lon": 10.921667, "address": "Viale Monte Kosica, 41121 Modena MO, Italy"},
        {"parking_name": "Parcheggio Sant'Agostino", "total_slot": 50, "available_slot": 47, "price_per_hour": 3.20, "lat": 44.648295, "lon": 10.921294, "address": "Largo Porta Sant'Agostino, 41121 Modena MO, Italy"},
        {"parking_name": "Parcheggio Ludovisi", "total_slot": 450, "available_slot": 120, "price_per_hour": 2.50, "lat": 41.905690, "lon": 12.487224, "address": "Via Ludovisi, 60, 00187 Roma RM, Italy"},
        {"parking_name": "Autosilo Diaz", "total_slot": 600, "available_slot": 200, "price_per_hour": 3.00, "lat": 45.461665, "lon": 9.189520, "address": "Piazza Armando Diaz, 6, 20123 Milano MI, Italy"}
    ]
    
    success = 0
    for p_data in italian_parkings:
        res = session.post(f"{BASE_URL}/parkings", json={"parking": p_data})
        if res.status_code == 201:
            print(f"  -> Created: {p_data['parking_name']}")
            success += 1
        else:
            print(f"  -> Failed: {p_data['parking_name']} - {res.text}")
    print(f"Completed! {success}/{len(italian_parkings)} parkings created.")

def cmd_create_cars():
    print("\n--- Creating Cars for Admin ---")
    account_id = get_admin_account_id()
    if not account_id: return

    cars = [
        {"account_id": account_id, "plate_text": "AA111AA", "plate_name": "Mini Cooper R53"},
        {"account_id": account_id, "plate_text": "BB222BB", "plate_name": "Volkswagen Passat"},
        {"account_id": account_id, "plate_text": "CC333CC", "plate_name": "Land Rover Discovery II"},
        {"account_id": account_id, "plate_text": "DD444DD", "plate_name": "Toyota Yaris"}
    ]
    
    for car in cars:
        res = session.post(f"{BASE_URL}/user/plates", json=car)
        if res.status_code == 201:
            print(f"  -> Created: {car['plate_name']} ({car['plate_text']})")
        elif res.status_code == 409:
            print(f"  -> Skipped: {car['plate_text']} already exists.")
        else:
            print(f"  -> Failed: {res.text}")

def cmd_delete_cars():
    print("\n--- Deleting ALL Cars for Admin ---")
    account_id = get_admin_account_id()
    if not account_id: return
    
    plates = get_plates(account_id)
    if not plates:
        print("No cars found to delete.")
        return
        
    for plate in plates:
        p_id = plate["plate_id"]
        res = session.delete(f"{BASE_URL}/user/plates", params={"account_id": account_id, "plate_id": p_id})
        
        if res.status_code == 200:
            print(f"  -> Deleted Car: {plate['plate_name']} ({plate['plate_text']})")
        else:
            print(f"  -> Failed to delete {plate['plate_text']}: HTTP {res.status_code} - {res.text}")

def cmd_create_bookings():
    print("\n--- Creating 5 Bookings for Admin ---")
    account_id = get_admin_account_id()
    if not account_id: return
    
    parkings = get_parkings()
    plates = get_plates(account_id)
    
    if not parkings or not plates:
        print("Error: You need at least 1 parking and 1 car to create bookings.")
        return
        
    p_id = parkings[0]["parking_id"]
    plate_id = plates[0]["plate_id"]
    today = date.today()
    
    configs = [
        {"name": "Booking Today", "start": today, "days": 1, "slot": 101},
        {"name": "Booking Tomorrow", "start": today + timedelta(days=1), "days": 3, "slot": 102},
        {"name": "Booking Next Week", "start": today + timedelta(days=7), "days": 2, "slot": 103},
        {"name": "Booking Getaway", "start": today + timedelta(days=14), "days": 4, "slot": 104},
        {"name": "Booking Next Month", "start": today + timedelta(days=30), "days": 7, "slot": 105},
    ]
    
    for cfg in configs:
        payload = {
            "account_id": account_id,
            "booking": {
                "booking_name": cfg["name"],
                "parking": {"parking_id": p_id},
                "plate": {"plate_id": plate_id},
                "date": cfg["start"].strftime("%Y-%m-%d"),
                "days": cfg["days"],
                "slot_code": cfg["slot"]
            }
        }
        res = session.post(f"{BASE_URL}/bookings", json=payload)
        if res.status_code == 201:
            print(f"  -> Success: {cfg['name']} (ID: {res.json()['booking_id']})")
        else:
            print(f"  -> Failed: {res.text}")

def cmd_delete_bookings():
    print("\n--- Deleting ALL Bookings for Admin ---")
    account_id = get_admin_account_id()
    if not account_id: return
    
    res = session.get(f"{BASE_URL}/bookings", params={"account_id": account_id})
    if res.status_code != 200:
        print("Failed to fetch bookings.")
        return
        
    bookings = res.json()
    if not bookings:
        print("No bookings found to delete.")
        return
        
    for b in bookings:
        b_id = b["booking_id"]
        del_res = session.delete(f"{BASE_URL}/bookings", params={"account_id": account_id, "booking_id": b_id})
        if del_res.status_code == 200:
            print(f"  -> Deleted Booking ID: {b_id}")
        else:
            print(f"  -> Failed to delete ID {b_id}: {del_res.text}")

def cmd_create_session():
    print("\n--- Creating a Parking Session ---")
    account_id = get_admin_account_id()
    if not account_id: return
    
    parkings = get_parkings()
    plates = get_plates(account_id)
    active = get_active_sessions(account_id)
    
    if not parkings or not plates:
        print("Error: Need parkings and plates to create a session.")
        return
        
    parked_plates = [s["plate"]["plate_text"] for s in active]
    free_plate = next((p["plate_text"] for p in plates if p["plate_text"] not in parked_plates), None)
    
    if not free_plate:
        print("All registered cars are currently parked!")
        return
        
    payload = {
        "account_id": account_id,
        "parking_id": parkings[0]["parking_id"],
        "plate_number": free_plate
    }
    
    res = session.post(f"{BASE_URL}/paying", json=payload)
    if res.status_code in [200, 201]:
        print(f"Success! Session started for plate {free_plate}")
    else:
        print(f"Failed to create session: {res.text}")

def cmd_delete_session():
    print("\n--- Deleting the first active Parking Session ---")
    account_id = get_admin_account_id()
    if not account_id: return
    
    active = get_active_sessions(account_id)
    if not active:
        print("No active sessions to delete.")
        return
        
    s_id = active[0].get("id")
    if not s_id:
        print("Error: Could not extract session ID.")
        return
        
    res = session.delete(f"{BASE_URL}/paying", params={"session_id": s_id})
    if res.status_code == 200:
        print(f"Success! Deleted session {s_id}")
    else:
        print(f"Failed: {res.text}")

def cmd_init_database():
    """Runs the full initialization sequence."""
    print("\n========== STARTING DATABASE INITIALIZATION ==========")
    cmd_init_parkings()
    cmd_create_admin()
    cmd_create_cars()
    cmd_create_bookings()
    cmd_create_session()
    print("\n========== DATABASE INITIALIZATION COMPLETE ==========")

# ==========================================
# CLI ENTRY POINT
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="IoT Parking Management CLI")
    
    # List of all available commands
    commands = {
        "admin-create": cmd_create_admin,
        "admin-delete": cmd_delete_admin,
        "parkings-init": cmd_init_parkings,
        "cars-create": cmd_create_cars,
        "cars-delete": cmd_delete_cars,
        "bookings-create": cmd_create_bookings,
        "bookings-delete": cmd_delete_bookings,
        "session-create": cmd_create_session,
        "session-delete": cmd_delete_session,
        "init-database": cmd_init_database,
    }
    
    parser.add_argument(
        "command", 
        choices=list(commands.keys()), 
        help="The action you want to perform"
    )

    # Enable argcomplete if installed
    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # Execute the selected function
    commands[args.command]()

if __name__ == "__main__":
    main()