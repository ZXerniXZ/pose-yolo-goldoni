import paho.mqtt.client as mqtt
import pyttsx3

# 🔹 Configura il server MQTT
MQTT_BROKER = "80.116.191.172"  # Cambia con l'IP del tuo server MQTT
MQTT_PORT = 1883
MQTT_TOPIC = "goldoni/output"  # Il topic su cui il bot pubblica le risposte

# 🔹 Inizializza il sintetizzatore vocale
engine = pyttsx3.init()

def on_connect(client, userdata, flags, rc):
    """Callback per la connessione al broker MQTT."""
    if rc == 0:
        print(f"✅ Connesso al broker MQTT! In ascolto su: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Errore di connessione: codice {rc}")

def on_message(client, userdata, msg):
    """Callback per la ricezione di un messaggio su MQTT."""
    risposta = msg.payload.decode("utf-8")  # Decodifica il testo
    print(f"📥 Ricevuto messaggio: {risposta}")

    # 🔊 Riproduce il testo con sintesi vocale
    engine.say(risposta)
    engine.runAndWait()

# 🔹 Configura il client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 🔹 Connessione al broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 🔹 Mantiene l'ascolto in un loop infinito
print(f"🎧 In ascolto sul topic: {MQTT_TOPIC}")
client.loop_forever()
