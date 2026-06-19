import serial
import threading
import paho.mqtt.client as mqtt

client_id = "python_bridge_gate"
arduino = serial.Serial("COM8", 9600, timeout=1)
# arduino = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)

SERIAL_MAP = {
    "DS:1": ("parking/disabled", "OCCUPIED"),
    "DS:0": ("parking/disabled", "FREE"),
}


# --- MQTT -> ARDUINO ---
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("parking/gate/entry", qos=1)
    client.subscribe("parking/gate/exit", qos=1)

def on_message(client, userdata, msg):
    try:
        command = msg.payload.decode('utf-8')
        print(f"Ricevuto: {command} su topic: {msg.topic}")
        arduino.write(command.encode('utf-8'))

    except Exception as e:
        print(f"Errore nel processare il messaggio: {e}")


# --- ARDUINO -> MQTT ---
def serial_reader():

    while True:
        try:
            line = arduino.readline().decode("utf-8").strip()
            if not line:
                continue

            if line in SERIAL_MAP:
                topic, payload = SERIAL_MAP[line]
                mqttc.publish(topic, payload, qos=1)
            else:
                print(f"Error serial_code_parsing: {line}")
        
        except Exception as e:
            print(f"Error serial_reader: {e}")


# --- Communication / Threading ---
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("127.0.0.1", 1883, 60)

reader_thread = threading.Thread(target=serial_reader, daemon=True)
reader_thread.start()

mqttc.loop_forever()