import paho.mqtt.client as mqtt
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# 🔹 Configura il server MQTT
MQTT_BROKER = "80.116.191.172"  # Cambia con l'IP del tuo server MQTT
MQTT_PORT = 1883
MQTT_TOPIC = "goldoni/output"  # Il topic su cui il bot pubblica le risposte

# 🔹 Configura la tua API Key di ElevenLabs
ELEVEN_API_KEY = "sk_5f4f7a707e7f7cc62e04640534ceebe88d2954acfda765ff"

# 🔹 Inizializza il client ElevenLabs
client_eleven = ElevenLabs(api_key=ELEVEN_API_KEY)

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

    try:
        # 🔊 Genera la voce con ElevenLabs
        audio = client_eleven.text_to_speech.convert(
            text=risposta,
            voice_id="W71zT1VwIFFx3mMGH2uZ",  # Cambia con un voice ID valido
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        # 🔊 Riproduce l'audio
        play(audio)
        print("🔊 Audio riprodotto con successo.")

    except Exception as e:
        print(f"❌ Errore nella sintesi vocale: {e}")

# 🔹 Configura il client MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 🔹 Connessione al broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# 🔹 Mantiene l'ascolto in un loop infinito
print(f"🎧 In ascolto sul topic: {MQTT_TOPIC}")
client.loop_forever()
