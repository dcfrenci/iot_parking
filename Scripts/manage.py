#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import os
import sys
import requests
import argparse
from datetime import date, timedelta, datetime

try:
    import argcomplete
except ImportError:
    argcomplete = None

# --- Configuration ---
BASE_URL    = os.getenv("API_URL",      "http://127.0.0.1:8000/v1")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL",  "admin@gmail.com")
ADMIN_PASS  = os.getenv("ADMIN_PASS",   "admin")

session = requests.Session()

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_account_id(email, password):
    try:
        res = session.post(f"{BASE_URL}/login", json={"email": email, "pass": password})
        if res.status_code == 200:
            return res.json()["account_id"]
        print(f"Login failed: {res.text}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Could not connect to {BASE_URL}. Is FastAPI running?")
        sys.exit(1)

def get_admin_account_id():
    return get_account_id(ADMIN_EMAIL, ADMIN_PASS)

def get_parkings():
    res = session.get(f"{BASE_URL}/parkings/all")
    return res.json() if res.status_code == 200 else []

def get_plates(account_id):
    res = session.get(f"{BASE_URL}/user/plates", params={"account_id": account_id})
    return res.json() if res.status_code == 200 else []

def get_active_sessions(account_id):
    res = session.get(f"{BASE_URL}/paying", params={"account_id": account_id})
    return res.json() if res.status_code == 200 else []

def register_user(name, email, password):
    res = session.post(f"{BASE_URL}/register", json={"name": name, "email": email, "pass": password})
    if res.status_code == 201:
        account_id = res.json()["account_id"]
        print(f"  -> Registered '{name}' (ID: {account_id})")
        return account_id
    elif res.status_code == 409:
        account_id = get_account_id(email, password)
        print(f"  -> '{name}' already exists (ID: {account_id})")
        return account_id
    print(f"  -> Failed to register '{name}': {res.text}")
    return None

def add_payment(account_id):
    res = session.post(f"{BASE_URL}/user/payment", json={
        "account_id": account_id,
        "payment": {"circuit": "VISA", "card_number": "4111111111111111"}
    })
    if res.status_code == 201:
        print(f"      payment registered")
    elif res.status_code == 400:
        print(f"      payment already exists")
    else:
        print(f"      payment failed: {res.text}")

def add_plate(account_id, plate_text, plate_name):
    res = session.post(f"{BASE_URL}/user/plates", json={
        "account_id": account_id,
        "plate_text": plate_text,
        "plate_name": plate_name,
    })
    if res.status_code == 201:
        print(f"      plate {plate_text} registered")
        return res.json()["plate_id"]
    elif res.status_code == 409:
        print(f"      plate {plate_text} already exists")
        for p in get_plates(account_id):
            if p["plate_text"] == plate_text:
                return p["plate_id"]
    else:
        print(f"      plate {plate_text} failed: {res.text}")
    return None

def set_disabled(account_id):
    res = session.patch(f"{BASE_URL}/user", json={"account_id": account_id, "is_disabled": True})
    if res.status_code == 200:
        print(f"      is_disabled = True")
    else:
        print(f"      set_disabled failed: {res.text}")

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
    print("\n--- Initializing Parkings ---")
    parkings = [
        {
            "parking_name": "Novi Park",
            "total_slot": 800, "available_slot": 350,
            "disabled_slot": 10, "available_disabled_slot": 10,
            "price_per_hour": 1.20,
            "lat": 44.651111, "lon": 10.921667,
            "address": "Viale Monte Kosica, 41121 Modena MO, Italy"
        },
        {
            "parking_name": "Parcheggio Sant'Agostino",
            "total_slot": 50, "available_slot": 47,
            "disabled_slot": 3, "available_disabled_slot": 3,
            "price_per_hour": 3.20,
            "lat": 44.648295, "lon": 10.921294,
            "address": "Largo Porta Sant'Agostino, 41121 Modena MO, Italy"
        },
        {
            "parking_name": "Parcheggio Ludovisi",
            "total_slot": 450, "available_slot": 120,
            "disabled_slot": 8, "available_disabled_slot": 8,
            "price_per_hour": 2.50,
            "lat": 41.905690, "lon": 12.487224,
            "address": "Via Ludovisi, 60, 00187 Roma RM, Italy"
        },
        {
            "parking_name": "Autosilo Diaz",
            "total_slot": 600, "available_slot": 200,
            "disabled_slot": 12, "available_disabled_slot": 12,
            "price_per_hour": 3.00,
            "lat": 45.461665, "lon": 9.189520,
            "address": "Piazza Armando Diaz, 6, 20123 Milano MI, Italy"
        },
    ]

    success = 0
    for p_data in parkings:
        res = session.post(f"{BASE_URL}/parkings", json={"parking": p_data})
        if res.status_code == 201:
            print(f"  -> Created: {p_data['parking_name']} "
                  f"(slot: {p_data['available_slot']}, slot H: {p_data['available_disabled_slot']})")
            success += 1
        else:
            print(f"  -> Failed: {p_data['parking_name']} - {res.text}")
    print(f"Completed! {success}/{len(parkings)} parkings created.")

def cmd_create_users():
    print("\n--- Creating Users and Plates ---")

    # AA111AA — normale, pagamento OK → ENTRA
    print("\n  [AA111AA] Mario Rossi — normale, pagamento OK → ENTRA")
    id1 = register_user("Mario Rossi", "mario@test.com", "mario123")
    if id1:
        add_payment(id1)
        add_plate(id1, "AA111AA", "Fiat Punto")

    # BB222BB — normale, SENZA pagamento → BLOCCATO
    print("\n  [BB222BB] Luigi Bianchi — normale, nessun pagamento → BLOCCATO")
    id2 = register_user("Luigi Bianchi", "luigi@test.com", "luigi123")
    if id2:
        add_plate(id2, "BB222BB", "Ford Focus")

    # CC333CC — disabile, pagamento OK → ENTRA posto H
    print("\n  [CC333CC] Giuseppe Verdi — disabile, pagamento OK → ENTRA posto H")
    id3 = register_user("Giuseppe Verdi", "giuseppe@test.com", "giuseppe123")
    if id3:
        set_disabled(id3)
        add_payment(id3)
        add_plate(id3, "CC333CC", "Fiat Panda")

    # DD444DD — Admin, pagamento OK → ENTRA
    print("\n  [DD444DD] Admin — pagamento OK → ENTRA")
    id_admin = get_admin_account_id()
    if id_admin:
        add_payment(id_admin)
        add_plate(id_admin, "DD444DD", "Admin Car")

def cmd_delete_users():
    print("\n--- Deleting Test Users ---")
    for email, password in [
        ("mario@test.com",    "mario123"),
        ("luigi@test.com",    "luigi123"),
        ("giuseppe@test.com", "giuseppe123"),
    ]:
        account_id = get_account_id(email, password)
        if account_id:
            res = session.delete(f"{BASE_URL}/user", params={"account_id": account_id})
            print(f"  -> {'Deleted' if res.status_code == 200 else 'Failed'}: {email}")

def cmd_delete_cars():
    print("\n--- Deleting ALL Cars for Admin ---")
    account_id = get_admin_account_id()
    if not account_id: return

    plates = get_plates(account_id)
    if not plates:
        print("No cars found to delete.")
        return

    for plate in plates:
        res = session.delete(f"{BASE_URL}/user/plates",
                             params={"account_id": account_id, "plate_id": plate["plate_id"]})
        if res.status_code == 200:
            print(f"  -> Deleted: {plate['plate_name']} ({plate['plate_text']})")
        else:
            print(f"  -> Failed to delete {plate['plate_text']}: {res.text}")

def cmd_create_bookings():
    print("\n--- Creating 5 Bookings for Admin ---")
    account_id = get_admin_account_id()
    if not account_id: return

    parkings = get_parkings()
    plates   = get_plates(account_id)

    if not parkings or not plates:
        print("Error: You need at least 1 parking and 1 car to create bookings.")
        return

    p_id     = parkings[0]["parking_id"]
    plate_id = plates[0]["plate_id"]
    today    = date.today()

    configs = [
        {"name": "Booking Today",      "start": today,                      "days": 1, "slot": 101},
        {"name": "Booking Tomorrow",   "start": today + timedelta(days=1),  "days": 3, "slot": 102},
        {"name": "Booking Next Week",  "start": today + timedelta(days=7),  "days": 2, "slot": 103},
        {"name": "Booking Getaway",    "start": today + timedelta(days=14), "days": 4, "slot": 104},
        {"name": "Booking Next Month", "start": today + timedelta(days=30), "days": 7, "slot": 105},
    ]

    for cfg in configs:
        payload = {
            "account_id": account_id,
            "booking": {
                "booking_name": cfg["name"],
                "parking": {"parking_id": p_id},
                "plate":   {"plate_id":   plate_id},
                "date":    cfg["start"].strftime("%Y-%m-%d"),
                "days":    cfg["days"],
                "slot_code": cfg["slot"],
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
        b_id    = b["booking_id"]
        del_res = session.delete(f"{BASE_URL}/bookings",
                                 params={"account_id": account_id, "booking_id": b_id})
        if del_res.status_code == 200:
            print(f"  -> Deleted Booking ID: {b_id}")
        else:
            print(f"  -> Failed to delete ID {b_id}: {del_res.text}")

def cmd_create_session():
    print("\n--- Creating a Parking Session (via gate/entry) ---")
    account_id = get_admin_account_id()
    if not account_id: return

    parkings = get_parkings()
    plates   = get_plates(account_id)
    active   = get_active_sessions(account_id)

    if not parkings or not plates:
        print("Error: Need parkings and plates to create a session.")
        return

    parked_plates = [s["plate"]["plate_text"] for s in active]
    free_plate    = next(
        (p["plate_text"] for p in plates if p["plate_text"] not in parked_plates), None
    )

    if not free_plate:
        print("All registered cars are currently parked!")
        return

    res = session.post(f"{BASE_URL}/gate/entry", json={"plate_text": free_plate})
    if res.status_code == 200:
        data = res.json()
        msg  = f"Success! Session started for plate {free_plate}"
        if data.get("used_disabled_slot"):
            msg += " [posto disabile]"
        print(msg)
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
    
def cmd_init_history():
    print("\n--- Generating and Uploading Parking History (via API) ---")
    import random
    
    HISTORY_DAYS = 180
    
    parkings_res = session.get(f"{BASE_URL}/parkings/all")
    if parkings_res.status_code != 200:
        print("Error: Could not fetch parkings. Run parkings-init first.")
        return
    
    parkings = parkings_res.json()
    
    for p_summary in parkings:
        PARKING_ID = p_summary["parking_id"]
        
        res = session.get(f"{BASE_URL}/parkings", params={"parking_id": PARKING_ID})
        if res.status_code != 200:
            print(f"  -> Skip parking {PARKING_ID}: not found")
            continue
            
        parking = res.json()
        total_slots = parking["total_slot"]
        disabled_slots = parking["disabled_slot"]
        
        print(f"\n  -> Generating {HISTORY_DAYS} days for '{parking['parking_name']}' (ID: {PARKING_ID})...")
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=HISTORY_DAYS)
        current_time = start_time
        payload_data = []
        
        while current_time <= end_time:
            hour = current_time.hour
            is_weekend = current_time.weekday() >= 5
            
            if 9 <= hour <= 18:
                base_dis = 0.50 if not is_weekend else 0.30
            else:
                base_dis = 0.10
            dec_dis = max(0.0, min(1.0, base_dis + random.uniform(-0.10, 0.10)))
            disabled_occupied = int(dec_dis * disabled_slots)
            
            if not is_weekend:
                if 8 <= hour <= 12: base_norm = 0.85
                elif 13 <= hour <= 17: base_norm = 0.70
                elif 18 <= hour <= 22: base_norm = 0.40
                else: base_norm = 0.15
            else:
                if 17 <= hour <= 23: base_norm = 0.65
                elif 10 <= hour <= 16: base_norm = 0.35
                else: base_norm = 0.08
            dec_norm = max(0.0, min(1.0, base_norm + random.uniform(-0.15, 0.15)))
            occupied = int(dec_norm * total_slots)
            
            payload_data.append({
                "timestamp": current_time.isoformat(),
                "occupied_slots": occupied,
                "disabled_occupied_slots": disabled_occupied
            })
            current_time += timedelta(hours=1)
        
        print(f"  -> Sending {len(payload_data)} records...")
        res = session.post(f"{BASE_URL}/parkings/{PARKING_ID}/history", json=payload_data)
        
        if res.status_code == 201:
            print(f"  -> Success!")
        else:
            print(f"  -> Failed: {res.status_code} - {res.text}")

def cmd_init_database():
    print("\n========== STARTING DATABASE INITIALIZATION ==========")
    cmd_init_parkings()
    cmd_create_admin()
    cmd_create_users()
    cmd_create_bookings()
    print("\n  Riepilogo targhe per i test:")
    print("  AA111AA → Mario Rossi    | pagamento SI | normale  → ENTRA")
    print("  BB222BB → Luigi Bianchi  | pagamento NO | normale  → BLOCCATO")
    print("  CC333CC → Giuseppe Verdi | pagamento SI | disabile → ENTRA posto H")
    print("  DD444DD → Admin          | pagamento SI | normale  → ENTRA")
    print("\n========== DATABASE INITIALIZATION COMPLETE ==========")

# ==========================================
# CLI ENTRY POINT
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="IoT Parking Management CLI")

    commands = {
        "admin-create":    cmd_create_admin,
        "admin-delete":    cmd_delete_admin,
        "parkings-init":   cmd_init_parkings,
        "history-init":    cmd_init_history,
        "users-create":    cmd_create_users,
        "users-delete":    cmd_delete_users,
        "cars-delete":     cmd_delete_cars,
        "bookings-create": cmd_create_bookings,
        "bookings-delete": cmd_delete_bookings,
        "session-create":  cmd_create_session,
        "session-delete":  cmd_delete_session,
        "init-database":   cmd_init_database,
    }

    parser.add_argument(
        "command",
        choices=list(commands.keys()),
        help="The action you want to perform"
    )

    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()
    commands[args.command]()

if __name__ == "__main__":
    main()
