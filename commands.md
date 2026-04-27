# COMMANDS

# Server test startup
*  Mosquitto broker startup (cmd administrator):
```bash
mosquitto -v
```
* Backend startup:
```bash
uvicorn backend:app --reload
```
* DB init:
```bash
python manage.py init-database
```

# Gate setup
1. init database
2. GET /v1/parkings/all (via Swagger UI)
3. assign the id of the selected parking by writing it in the .env file (change the .env.example)