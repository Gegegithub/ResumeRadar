# Resume

## Apercu
**Application 100% locale pour analyser et trier des CVs par rapport a une description de poste**

https://github.com/user-attachments/assets/b5de7757-b348-43a4-91a7-6d87c61330c3



![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Ollama](https://img.shields.io/badge/Ollama-Llama_3.1-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-red)

---

## Problematique

Les recruteurs perdent du temps a lire manuellement des dizaines de CVs. Cette application automatise le tri :

1. Upload des CVs + description du poste
2. Scoring hybride : similarite cosinus (30%) + evaluation LLM (70%)
3. Le LLM explique pourquoi chaque candidat correspond (ou pas)
4. Navigation dans les CVs et contact des candidats en un clic

---

## Fonctionnalites

- **100% Local** - Aucune donnee envoyee vers le cloud
- **Scoring hybride** - Combinaison d'embeddings mathematiques et d'evaluation LLM sur 3 criteres metier
- **Analyse detaillee** - Adequation metier, hard skills et experience pertinente notes de 0 a 100
- **Synthese LLM** - Resume global redige par le LLM pour le recruteur
- **Apercu PDF** - Consultation des CVs directement dans l'interface
- **Contact groupe** - Lien mailto avec tous les candidats retenus en BCC

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit UI                           │
│  ┌───────────────────┐  ┌─────────────────────────────────┐ │
│  │  Mode Analyse     │  │  Mode CVs & Contact             │ │
│  │  Upload + Score   │  │  Carrousel PDF + Mailto          │ │
│  └───────────────────┘  └─────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   Pipeline de Scoring                       │
│                                                             │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────┐ │
│  │ PDF Parser  │  │ Stage 1 (30%)    │  │ Stage 2 (70%)  │ │
│  │ (pypdf)     │  │ Embeddings       │  │ LLM Reranker   │ │
│  │ Extraction  │  │ (multilingual    │  │ (Ollama)       │ │
│  │ texte+email │  │  mpnet) → cosine │  │ 3 criteres     │ │
│  └─────────────┘  └──────────────────┘  └────────────────┘ │
│                                                             │
│           Score Final = 0.3*cosine + 0.7*LLM                │
│                          │                                  │
│                          ▼                                  │
│                 ┌─────────────────┐                         │
│                 │ Stage 3         │                         │
│                 │ Synthese LLM    │                         │
│                 └─────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequis

- Python 3.10+
- [Ollama](https://ollama.com/download) installe
- 8GB RAM minimum (16GB recommande)
- GPU avec 4GB+ VRAM recommande (ex: RTX 3050 Ti)

### Etapes

```bash
# 1. Cloner le repository
git clone <url>
cd resumeradar

# 2. Creer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Installer les dependances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env

# 5. Telecharger un modele Ollama
ollama pull llama3.1:8b

# 6. Lancer l'application
streamlit run app.py
```

Ouvrir http://localhost:8501

---

## Structure du Projet

```
resumeradar/
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration (modeles, poids, limites)
├── utils/
│   ├── __init__.py
│   ├── email_extractor.py   # Extraction email + nom depuis les CVs
│   └── scoring.py           # Scoring hybride (cosinus + LLM reranker)
├── app.py                   # Interface Streamlit (Analyse + CVs & Contact)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Stack Technique

| Composant | Technologie | Execution |
|-----------|-------------|-----------|
| LLM | Ollama (Llama 3.1 8B) | GPU (VRAM) |
| Embeddings | sentence-transformers (paraphrase-multilingual-mpnet-base-v2) | CPU (RAM) |
| Scoring | Cosinus (30%) + LLM reranking (70%) | CPU + GPU |
| Frontend | Streamlit 1.41+ | CPU |
| PDF Parsing | pypdf | CPU |

---
