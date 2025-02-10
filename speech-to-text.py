import speech_recognition as sr
import paho.mqtt.client as mqtt
import time

# 🔹 Configura il riconoscitore vocale
r = sr.Recognizer()

# 🔹 Configura il client MQTT
MQTT_BROKER = "80.116.191.172"  # 🔹 Cambia con il tuo IP se il broker è su un altro PC
MQTT_PORT = 1883
MQTT_TOPIC = "goldoni/voce"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

def record_voice():
    """Riconosce la voce e pubblica il testo su MQTT."""
    with sr.Microphone() as source:
        print("🎤 Parla, sto ascoltando...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source)
            text = r.recognize_google(audio, language="it-IT")
            print(f"🗣️ Hai detto: {text}")

            # Pubblica il testo su MQTT
            client.publish(MQTT_TOPIC, text)
            print(f"📡 Messaggio inviato a {MQTT_TOPIC}")

        except sr.UnknownValueError:
            print("❌ Non ho capito, puoi ripetere?")
        except sr.RequestError:
            print("❌ Errore nel riconoscimento vocale.")

# 🔹 Loop per ascoltare continuamente
while True:
    record_voice()
    time.sleep(1)
