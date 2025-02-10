import os
import paho.mqtt.client as mqtt
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# Configura la tua API Key di ElevenLabs
ELEVEN_API_KEY = "sk_5f4f7a707e7f7cc62e04640534ceebe88d2954acfda765ff"
MQTT_BROKER = "80.116.191.172"  # Cambia con l'IP del tuo broker se è su un'altra macchina
MQTT_TOPIC = "chatbot/response"

# Inizializza il client di ElevenLabs
client_eleven = ElevenLabs(api_key=ELEVEN_API_KEY)

# Callback quando si riceve un messaggio MQTT
def on_message(client, userdata, msg):
    risposta = msg.payload.decode("utf-8")
    print(f"📥 Ricevuto messaggio: {risposta}")
    
    try:
        # Genera la voce con ElevenLabs
        audio = client_eleven.text_to_speech.convert(
            text=risposta,
            voice_id="W71zT1VwIFFx3mMGH2uZ",  # Cambia con un voice ID valido
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        # Riproduce l'audio
        play(audio)
    except Exception as e:
        print(f"❌ Errore nella sintesi vocale: {e}")

# Configura il client MQTT
client_mqtt = mqtt.Client()
client_mqtt.on_message = on_message

print(f"📡 Connessione a MQTT Broker: {MQTT_BROKER}")
client_mqtt.connect(MQTT_BROKER, 1883, 60)
client_mqtt.subscribe(MQTT_TOPIC)

print(f"🎧 In ascolto sul topic: {MQTT_TOPIC}")
client_mqtt.loop_forever()
