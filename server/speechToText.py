import paho.mqtt.client as mqtt
import ollama
import chromadb
import os
from dotenv import load_dotenv

# 📌 Configurazione MQTT
MQTT_BROKER = "localhost"  # Cambia con l'IP pubblico del tuo server MQTT se necessario
MQTT_PORT = 1883
MQTT_TOPIC_INPUT = "goldoni/voce"
MQTT_TOPIC_OUTPUT = "goldoni/output"

# 🔹 Configura il database ChromaDB
client_chroma = chromadb.PersistentClient(path="goldoni_db")
collection = client_chroma.get_collection("goldoni_knowledge")

def cerca_informazioni(query):
    """Cerca nei dati con ChromaDB e restituisce il testo più rilevante."""
    try:
        risultati = collection.query(query_texts=[query], n_results=1)
        if risultati["documents"]:
            return risultati["documents"][0][0]
        else:
            return "Mi dispiace, non ho trovato informazioni a riguardo."
    except Exception as e:
        return f"Errore durante la ricerca nel database: {e}"

def genera_risposta(query):
    """Cerca nel database e genera una risposta con Mistral 7B."""
    contesto = cerca_informazioni(query)
    
    prompt = f"Rispondi come se tu fossi Carlo Goldoni, in prima persona, nel suo modo ironico ma al col tempo elegante, in modo breve ma incisivo, usando questo contesto:\n\n{contesto}\n\nDomanda: {query}\nRisposta:"
    
    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        return f"Errore durante la generazione della risposta: {e}"

# 📌 Callback quando riceviamo un messaggio su MQTT
def on_message(client, userdata, msg):
    domanda = msg.payload.decode()
    print(f"📥 Ricevuto da MQTT: {domanda}")

    if "esci" in domanda.lower():
        print("👋 Arrivederci!")
        return

    # Genera risposta e pubblica su MQTT
    risposta = genera_risposta(domanda)
    print(f"🤖 Goldoni: {risposta}")

    mqtt_client.publish(MQTT_TOPIC_OUTPUT, risposta)
    print(f"📤 Pubblicato su MQTT: {risposta}")

# 📌 Connessione al broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connesso al broker MQTT")
        client.subscribe(MQTT_TOPIC_INPUT)
    else:
        print(f"❌ Errore di connessione MQTT. Codice: {rc}")

# Inizializza il client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever()
