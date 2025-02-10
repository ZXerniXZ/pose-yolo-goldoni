import chromadb
import ollama
from sentence_transformers import SentenceTransformer

# 🔹 1. Caricare il database ChromaDB
chroma_client = chromadb.PersistentClient(path="goldoni_db")  # Assicurati di avere un DB salvato
collection = chroma_client.get_or_create_collection(name="goldoni_knowledge")

# 🔹 2. Caricare il modello di embedding
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Modello veloce e leggero

def cerca_informazioni(query, n_results=3):
    """
    Cerca le informazioni più rilevanti in ChromaDB usando il modello di embedding.
    """
    query_vector = embedding_model.encode(query).tolist()  # Converte la domanda in un embedding
    risultati = collection.query(query_embeddings=[query_vector], n_results=n_results)

    if risultati["documents"]:
        return "\n\n".join([doc[0] for doc in risultati["documents"]])  # Ritorna più documenti
    else:
        return "Mi dispiace, non ho trovato informazioni a riguardo."

def genera_risposta(query):
    """
    Cerca le informazioni pertinenti nel database e genera una risposta con Mistral 7B.
    """
    contesto = cerca_informazioni(query)
    
    prompt = f"""
    Sei Carlo Goldoni, il celebre drammaturgo italiano. Rispondi alla domanda con il tuo stile ironico e colto.
    
    Ecco alcune informazioni per aiutarti:
    {contesto}

    Domanda: {query}
    Rispondi con il tono tipico di Goldoni, la risposta deve essere breve e incisiva.:
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    
    return response["message"]["content"]

# 🔹 5. Testare il chatbot
if __name__ == "__main__":
    while True:
        domanda = input("\n🎭 Chiedi qualcosa a Goldoni (o scrivi 'esci' per terminare): ")
        if domanda.lower() == "esci":
            break
        risposta = genera_risposta(domanda)
        print("\n🤖 Goldoni:", risposta)
