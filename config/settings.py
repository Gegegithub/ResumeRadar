"""
Configuration centralisee du projet ResumeRadar
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Ollama
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))

# Configuration Embeddings
# Migration de all-MiniLM-L6-v2 (256 tokens, anglais) vers
# paraphrase-multilingual-mpnet-base-v2 (128 dimensions, 768 tokens, multilingue).
# Raison : les CVs sont en francais et depassent largement 256 tokens.
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
)

# Chunking & Contexte
# Fenetre de contexte maximale envoyee au LLM par candidat (en caracteres).
# 2000 chars (~500 tokens) par candidat pour rester dans les limites
# d'une GPU 4-6 Go VRAM avec llama3.1:8b.
DEFAULT_CONTEXT_WINDOW = int(os.getenv("DEFAULT_CONTEXT_WINDOW", "2000"))

# Taille du context window Ollama (en tokens). 2048 = minimum viable
# pour une GPU 4-6 Go. Augmenter si GPU plus puissante.
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# Scoring Hybride
# Poids du score cosinus (filtrage rapide) vs score LLM (reranking expert).
# On passe d'un Bi-Encoder pur a une architecture de Reranking :
# la similarite mathematique seule ne comprend pas l'exclusion mutuelle
# (un avocat n'est pas un developpeur, meme s'ils partagent du vocabulaire).
SCORE_WEIGHT_COSINE = float(os.getenv("SCORE_WEIGHT_COSINE", "0.3"))
SCORE_WEIGHT_LLM = float(os.getenv("SCORE_WEIGHT_LLM", "0.7"))

# Configuration Review & Email
TOP_CANDIDATES = int(os.getenv("TOP_CANDIDATES", "5"))
EMAIL_SUBJECT = "Mise a jour de votre candidature"
EMAIL_BODY = """Bonjour,

Suite a l'examen de votre candidature, nous avons le plaisir de vous informer que votre profil a ete retenu pour la prochaine etape du recrutement

Cordialement,"""
