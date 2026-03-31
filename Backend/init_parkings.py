import requests

# URL for your backend endpoint (adjust port if necessary)
API_URL = "http://127.0.0.1:8000/v1/parkings"

# Expanded parking data across Italian cities
italian_parkings = [
    # --- Modena & Surrounding Cities (Emilia-Romagna) ---
    {
        "parking_name": "Novi Park",
        "total_slot": 800,
        "available_slot": 350,
        "price_per_hour": 1.20,
        "lat": 44.651111,
        "lon": 10.921667,
        "address": "Viale Monte Kosica, 41121 Modena MO, Italy"
    },
    {
        "parking_name": "Parcheggio Sant'Agostino",
        "total_slot": 50,
        "available_slot": 47,
        "price_per_hour": 3.20,
        "lat": 44.648295,
        "lon": 10.921294,
        "address": "Largo Porta Sant'Agostino, 41121 Modena MO, Italy"
    },
    {
        "parking_name": "Parcheggio ex Mercato Ortofrutticolo",
        "total_slot": 100,
        "available_slot": 14,
        "price_per_hour": 3.00,
        "lat": 44.648295,
        "lon": 10.921294,
        "address": "Via Vincenzo Borelli, 41121 Modena MO, Italy"
    },
    {
        "parking_name": "Garage Ferrari",
        "total_slot": 150,
        "available_slot": 47,
        "price_per_hour": 7.00,
        "lat": 44.642523,
        "lon": 10.933230,
        "address": "Viale Trento Trieste, 41124 Modena MO, Italy"
    },
    {
        "parking_name": "Parcheggio Caserma Zucchi",
        "total_slot": 850,
        "available_slot": 420,
        "price_per_hour": 1.50,
        "lat": 44.698688,
        "lon": 10.625345,
        "address": "Viale Isonzo, 42121 Reggio Emilia RE, Italy"
    },
    {
        "parking_name": "Parcheggio Toschi",
        "total_slot": 500,
        "available_slot": 115,
        "price_per_hour": 2.00,
        "lat": 44.805542,
        "lon": 10.328105,
        "address": "Viale Toschi, 2, 43121 Parma PR, Italy"
    },
    {
        "parking_name": "Parcheggio Piazza VIII Agosto",
        "total_slot": 980,
        "available_slot": 210,
        "price_per_hour": 2.60,
        "lat": 44.500582,
        "lon": 11.344445,
        "address": "Piazza dell'8 Agosto, 40126 Bologna BO, Italy"
    },

    # --- Main Italian Cities ---
    {
        "parking_name": "Parcheggio Ludovisi",
        "total_slot": 450,
        "available_slot": 120,
        "price_per_hour": 2.50,
        "lat": 41.905690,
        "lon": 12.487224,
        "address": "Via Ludovisi, 60, 00187 Roma RM, Italy"
    },
    {
        "parking_name": "Parcheggio Villa Borghese",
        "total_slot": 1800,
        "available_slot": 650,
        "price_per_hour": 2.20,
        "lat": 41.911854,
        "lon": 12.484439,
        "address": "Viale del Galoppatoio, 33, 00197 Roma RM, Italy"
    },
    {
        "parking_name": "Autosilo Diaz",
        "total_slot": 600,
        "available_slot": 200,
        "price_per_hour": 3.00,
        "lat": 45.461665,
        "lon": 9.189520,
        "address": "Piazza Armando Diaz, 6, 20123 Milano MI, Italy"
    },
    {
        "parking_name": "Garage San Marco",
        "total_slot": 150,
        "available_slot": 45,
        "price_per_hour": 4.00,
        "lat": 43.769560,
        "lon": 11.255814,
        "address": "Via dei Neri, 50122 Firenze FI, Italy"
    },
    {
        "parking_name": "Parcheggio Stazione SMN",
        "total_slot": 900,
        "available_slot": 310,
        "price_per_hour": 3.00,
        "lat": 43.775231,
        "lon": 11.248102,
        "address": "Piazza della Stazione, 50123 Firenze FI, Italy"
    },
    {
        "parking_name": "Parcheggio Brin",
        "total_slot": 300,
        "available_slot": 80,
        "price_per_hour": 1.50,
        "lat": 40.854060,
        "lon": 14.280145,
        "address": "Via Benedetto Brin, 80142 Napoli NA, Italy"
    },
    {
        "parking_name": "Parcheggio Roma San Carlo",
        "total_slot": 850,
        "available_slot": 240,
        "price_per_hour": 2.50,
        "lat": 45.068153,
        "lon": 7.682121,
        "address": "Piazza San Carlo, 10121 Torino TO, Italy"
    },
    {
        "parking_name": "Autorimessa Comunale Piazzale Roma",
        "total_slot": 2000,
        "available_slot": 150,
        "price_per_hour": 3.50,
        "lat": 45.438255,
        "lon": 12.318182,
        "address": "Santa Croce, 396, 30135 Venezia VE, Italy"
    }
]

def initialize_database():
    print(f"Connecting to {API_URL}...\n")
    
    success_count = 0
    
    for p_data in italian_parkings:
        payload = {
            "parking": p_data
        }
        
        try:
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 201:
                print(f"SUCCESS: Created parking '{p_data['parking_name']}'")
                success_count += 1
            else:
                print(f"FAILED to create '{p_data['parking_name']}'.")
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("ERROR: Could not connect to the backend. Make sure the FastAPI server is running.")
            return

    print(f"\nInitialization complete! Successfully created {success_count}/{len(italian_parkings)} parkings.")

if __name__ == "__main__":
    initialize_database()