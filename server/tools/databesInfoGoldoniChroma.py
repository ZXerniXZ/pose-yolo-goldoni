import chromadb
from sentence_transformers import SentenceTransformer

# Inizializziamo ChromaDB
chroma_client = chromadb.PersistentClient(path="goldoni_db")

# Creiamo una raccolta di documenti
collection = chroma_client.get_or_create_collection(name="goldoni_knowledge")

# Carichiamo il modello per trasformare il testo in vettori
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Leggiamo i dati
with open("goldoni_data.txt", "r", encoding="utf-8") as f:
    documenti = f.readlines()

# Inseriamo i dati nel database
for i, doc in enumerate(documenti):
    vector = embedding_model.encode(doc).tolist()
    collection.add(ids=[str(i)], documents=[doc], embeddings=[vector])

print("✅ Database vettoriale creato con successo!")
