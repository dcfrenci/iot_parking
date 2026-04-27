import serial
import paho.mqtt.client as mqtt

client_id = "python_bridge_gate"
arduino = serial.Serial("COM8", 9600)


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("parking/gate/entry", qos=1)

def on_message(client, userdata, msg):

    try:
        command = msg.payload.decode('utf-8')
        print(f"Ricevuto: {command} su topic: {msg.topic}")

        arduino.write(command.encode('utf-8'))

    except Exception as e:
        print(f"Errore nel processare il messaggio: {e}")
    command = msg.payload.decode('utf-8') + '\n'
    
    print(msg.topic+" "+str(msg.payload))


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("127.0.0.1", 1883, 60)

mqttc.loop_forever()