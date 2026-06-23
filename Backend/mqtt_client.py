import paho.mqtt.client as mqtt
import os
import threading
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.normpath(os.path.join(BASE_DIR, "..", ".env"))
load_dotenv(ENV_PATH)

MQTT_BROKER = os.getenv("MQTT_BROKER", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

class MQTTManager:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iotparking")
        self.connected = False

    def _on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.connected = True
            self.client.subscribe("parking/disabled", qos=1)
        else:
            print(f"[mqtt] Connection failed: {rc}")

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        self.connected = False

    def start(self, on_message_callback=None):
        if on_message_callback:
            self.client.on_message = on_message_callback
        
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            thread = threading.Thread(target=self.client.loop_forever, daemon=True)
            thread.start()
        except Exception as e:
            print(f"[mqtt] Broker not reachable: {e}")

    def publish(self, topic: str, payload: str):
        if not self.connected:
            return
        try:
            self.client.publish(topic, payload, qos=1)
        except Exception as e:
            print(f"[mqtt] Publish error: {e}")

mqtt_manager = MQTTManager()