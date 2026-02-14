# ResumeRadar - Logique Technique Complete

## Vue d'ensemble

ResumeRadar est un outil de tri de CVs qui classe des candidats par rapport a une offre d'emploi. Il fonctionne en **3 etapes** :

1. **Parsing** : on extrait le texte des CVs
2. **Scoring** : on note chaque candidat avec deux methodes complementaires (maths + LLM)
3. **Synthese** : le LLM redige un resume pour le recruteur

Le tout tourne **100% en local** (pas de cloud) avec Ollama + Streamlit.

---

## Etape 0 : L'interface utilisateur

Fichier : `app.py` (lignes 728-754)

L'utilisateur fait 3 choses dans l'interface Streamlit :
- **Upload les CVs** (PDF) via `st.file_uploader()` → stockes dans `uploaded_files`
- **Saisit la description du poste** via `st.text_area()` → stockee dans `job_description`
- **Choisit combien de candidats retenir** via `st.number_input()` → stocke dans `top_n`

Streamlit est un framework Python qui transforme un script Python en app web. Chaque `st.quelque_chose()` cree un element visuel (bouton, champ texte, etc.) dans le navigateur.

---

## Etape 1 : Parsing des CVs

Fichier : `app.py` (lignes 771-788)

Pour **chaque** PDF uploade, on fait 3 choses :

### 1a. Extraire le texte

Fichier : `app.py`, fonction `extract_text_from_pdf()` (lignes 628-636)

```python
reader = PdfReader(io.BytesIO(uploaded_file.getbuffer()))
text = ""
for page in reader.pages:
    text += page.extract_text() or ""
```

- `io.BytesIO` : Streamlit donne le fichier comme des bytes en memoire (pas un fichier sur disque). `BytesIO` le transforme en un objet qui se comporte comme un vrai fichier, car `PdfReader` attend un fichier.
- On parcourt chaque page et on concatene le texte dans une variable `text`.
- **Important** : chaque CV a **sa propre** variable `text`. On ne melange pas les CVs.

**Limites** : `pypdf` ne gere pas les PDFs scannes (images), les tableaux complexes, ni les colonnes multiples.

### 1b. Extraire l'email

Fichier : `utils/email_extractor.py`, fonction `extract_email()` (lignes 10-22)

On cherche un email dans le **texte du CV** avec une regex (expression reguliere) :
```python
pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
```
Ca matche tout ce qui ressemble a `quelquechose@domaine.com`. On retourne le premier trouve, ou une chaine vide si rien.

### 1c. Extraire le nom

Fichier : `utils/email_extractor.py`, fonction `extract_name_from_filename()` (lignes 25-39)

Le nom est deduit du **nom du fichier** (pas du contenu du CV) :
```
CV-Karim_Benali.pdf → retire .pdf → retire CV- → remplace _ par espace → Karim Benali
```

### Resultat de l'etape 1

On obtient une **liste de dictionnaires**. Chaque dictionnaire = un candidat :

```python
candidates = [
    {"name": "Karim Benali",   "text": "Ingenieur logiciel...", "email": "karim@gmail.com", ...},
    {"name": "Sara Moulin",    "text": "Developpeuse web...",   "email": "sara@outlook.com", ...},
    {"name": "Youssef Amrani", "text": "Data analyst...",       "email": "", ...},
]
```

C'est cette liste qui est envoyee au pipeline de scoring.

---

## Etape 2 : Scoring Hybride

Le scoring se fait en 2 sous-etapes (Stage 1 + Stage 2) qui se completent.

### Pourquoi deux methodes ?

Chacune a une **faiblesse** que l'autre compense :

- **Cosine seul** (Stage 1) : rapide mais bete. Un avocat et un developpeur utilisent les memes mots ("contrat", "client", "livraison"). Le cosine voit des mots similaires et donne un score eleve, alors qu'un avocat n'est pas un developpeur → **faux positif**.

- **LLM seul** (Stage 2) : intelligent mais lent. Si tu as 100 CVs, ca prendrait ~50 minutes de tout envoyer au LLM.

**Les deux ensemble** : c'est comme un recruteur qui **survole** d'abord 100 CVs en 5 minutes (cosine), puis **lit attentivement** les 10 meilleurs (LLM).

---

### Stage 1 : Similarite Cosinus (30% du score final)

Fichier : `utils/scoring.py`, fonction `compute_cosine_score()` (lignes 87-108)

C'est une comparaison **mathematique**. On transforme du texte en nombres pour pouvoir le comparer.

#### Le modele d'embeddings

Modele : `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`

- **Taille** : ~1.1 Go sur disque
- **Langues** : 50+ (francais natif)
- **Dimensions** : transforme un texte en un vecteur de 768 nombres
- **Stockage** : telecharge une seule fois depuis Hugging Face, puis cache en local dans `C:\Users\LENOVO\.cache\huggingface\hub\`. Le warning "HF Hub" au lancement est normal — la librairie verifie s'il y a une mise a jour, mais utilise le cache local si pas d'internet. On peut forcer le mode offline avec `HF_HUB_OFFLINE=1` dans le `.env`.
- **Singleton** : le modele est charge une seule fois en memoire et reutilise pour tous les candidats

#### Ou tourne le modele d'embeddings ?

Le modele d'embeddings tourne sur **CPU + RAM**, pas sur GPU :

```
Disque dur (cache HF, ~1.1 Go) → charge en RAM au lancement → calcul sur CPU
```

Il ne consomme **aucune VRAM**. C'est configure explicitement dans le code :
```python
model_kwargs={'device': 'cpu'}
```

Ca veut dire que meme sans GPU, le Stage 1 fonctionne. Et ca laisse toute la VRAM disponible pour le LLM au Stage 2.

#### Le processus de scoring cosinus

**1. Chunking** : on decoupe le CV en morceaux de 500 caracteres avec 50 de chevauchement.

Le chevauchement, c'est quand deux chunks **partagent 50 caracteres** entre la fin de l'un et le debut du suivant. Ca evite de couper une idee en plein milieu. Exemple :

Sans chevauchement :
```
Chunk 1: "Developpeur Python avec 5 ans d'experi"
Chunk 2: "ence en machine learning et data scienc"
→ Le mot "experience" est coupe en deux, on perd le sens.
```

Avec 50 caracteres de chevauchement :
```
Chunk 1: "Developpeur Python avec 5 ans d'experience en mac"
Chunk 2: "ns d'experience en machine learning et data scien"
→ "experience en machine" apparait dans les deux chunks. Aucune information perdue.
```

Un CV typique de 3000 caracteres produit environ 6-7 chunks.

**2. Embeddings** : on transforme la description du poste ET chaque chunk du CV en vecteurs.

Le poste donne **1 seul vecteur** de 768 nombres. Le CV donne **plusieurs vecteurs** (1 par chunk). C'est parce que le CV est decoupe en chunks, pas le poste.

```
Poste : [0.12, -0.45, 0.78, ... 768 nombres] → 1 seul vecteur

CV chunk 1 : [0.34, -0.21, 0.55, ... 768 nombres]
CV chunk 2 : [0.11, -0.67, 0.43, ... 768 nombres]
CV chunk 3 : [0.56, -0.12, 0.29, ... 768 nombres]
...
```

Le vecteur du poste est genere **une seule fois** et reutilise pour comparer avec tous les chunks de tous les CVs.

**3. Calcul du cosinus** : on compare mathematiquement chaque chunk avec le poste.

Le cosinus mesure l'angle entre deux vecteurs : 1 = identiques, 0 = rien en commun. La formule :

```
cosinus(A, B) = (A . B) / (||A|| * ||B||)
```

Dans le code (`scoring.py`, lignes 61-68) :
```python
a = np.array(vec_a)    # vecteur du poste (768 nombres)
b = np.array(vec_b)    # vecteur d'un chunk (768 nombres)
np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

C'est une multiplication et division entre deux listes de 768 nombres. NumPy fait ca en **microsecondes** sur le CPU. Pas besoin de GPU.

**4. Top-3** : on trie les scores et on garde la moyenne des 3 meilleurs chunks.

Exemple :
```
CV chunk 1 : cosine = 0.82
CV chunk 2 : cosine = 0.75
CV chunk 3 : cosine = 0.71
CV chunk 4 : cosine = 0.55
CV chunk 5 : cosine = 0.48
CV chunk 6 : cosine = 0.40

Top 3 : (0.82 + 0.75 + 0.71) / 3 = 0.76 → score cosinus de ce CV
```

Ca capture les parties pertinentes (competences, experience) sans etre pollue par le bruit (adresse, loisirs).

**Important** : le Stage 1 utilise le **CV entier** (tous les chunks). Il n'y a pas de troncature ici — c'est uniquement le Stage 2 (LLM) qui tronque a 2000 caracteres.

#### Vitesse du Stage 1

~10 secondes pour 10 CVs. Rapide car c'est du calcul mathematique pur sur CPU. Le plus "lourd" c'est la generation des embeddings (~100ms par chunk), pas le calcul du cosinus lui-meme.

#### Pas de base vectorielle (ChromaDB, FAISS...)

Avec 6-20 CVs par session (~42 embeddings), une comparaison brute force prend moins de 100ms. Un index vectoriel serait inutilement complexe.

---

### Stage 2 : Reranking par LLM (70% du score final)

Fichier : `utils/scoring.py`, fonction `compute_llm_score()` (lignes 140-182)

Ici, pas de vecteurs ni de maths. Le LLM **lit** le CV et donne des scores.

#### Comment le LLM "comprend" un CV

Le LLM ne "comprend" pas vraiment comme un humain. Il **predit le mot suivant** le plus probable, base sur des **milliards de textes** vus pendant son entrainement. Quand il voit "avocat" pour un poste "developpeur Python", il a vu assez d'exemples pour savoir que ca ne correspond pas. C'est du **pattern matching statistique tres avance**, pas de la comprehension — mais le resultat est suffisamment bon pour evaluer un CV.

#### Ou tourne le LLM ?

Le LLM tourne sur **GPU (VRAM)**, via Ollama :

```
Disque dur (cache Ollama, ~4.7 Go) → charge en VRAM au lancement → inference sur GPU
```

Modele : `llama3.1:8b` (8 milliards de parametres)
Stockage : `C:\Users\LENOVO\.ollama\models\`
VRAM necessaire : ~3.5-4 Go

C'est pour ca que le LLM est lent (~20-40s par appel) mais "intelligent" : l'inference sur GPU est bien plus complexe qu'un simple calcul cosinus.

#### Pourquoi tronquer le CV a 2000 caracteres ?

Le LLM a une fenetre de contexte de **2048 tokens**. Mais ces tokens doivent contenir **tout**, pas juste le CV :

```
2048 tokens au total
├── Le prompt systeme ("Tu es un expert en recrutement...")  ~100 tokens
├── La description du poste                                  ~200-400 tokens
├── Le CV du candidat                                        ~500 tokens (2000 chars)
├── Les instructions JSON                                    ~100 tokens
└── La reponse du LLM (scores + justifications)              ~300-500 tokens
                                                             ─────────────
                                                             ~1200-1600 tokens
```

Les 500 tokens (~2000 caracteres) pour le CV, c'est ce qui **reste** apres avoir reserve de la place pour le prompt, le poste, les instructions et la reponse.

Un caractere = une seule lettre, chiffre, espace ou symbole ("Bonjour" = 7 caracteres). Un token c'est souvent un morceau de mot ("developpeur" = 11 caracteres mais ~3-4 tokens). D'ou : 2000 caracteres ≈ 500 tokens.

**Oui, on perd de la matiere.** Un CV fait souvent 3000-5000 caracteres. Avec 2000, on perd la fin (souvent formations, langues, loisirs). Mais c'est un compromis : si on envoie trop, soit ca plante (VRAM insuffisante), soit le LLM "oublie" le debut du texte. Et ce que le LLM rate, le cosine du Stage 1 le capture (car lui a le CV entier).

On pourrait augmenter `OLLAMA_NUM_CTX` a 4096 tokens pour envoyer plus de CV (~1500 tokens / 6000 chars), mais ca consommerait plus de VRAM. Avec la RTX 3050 Ti (4 Go VRAM), on est deja a la limite.

#### Le processus de scoring LLM

1. On **tronque** le CV a 2000 caracteres (ligne 156) :
```python
truncated_cv = cv_text[:DEFAULT_CONTEXT_WINDOW]
```

2. On envoie au LLM un **prompt** contenant : description du poste + texte du CV

3. Le LLM evalue sur **3 criteres** (chacun note de 0 a 100) :
   - **Adequation Metier** : le candidat exerce-t-il le bon metier ?
   - **Hard Skills** : a-t-il les competences techniques demandees ?
   - **Experience Pertinente** : a-t-il travaille dans un domaine similaire ?

4. Le LLM repond en **JSON** structure :
```json
{
  "adequation_metier": {"score": 85, "justification": "..."},
  "hard_skills": {"score": 70, "justification": "..."},
  "experience_pertinente": {"score": 60, "justification": "..."}
}
```

**Parsing robuste** (`_parse_llm_response()`, lignes 185-250) : les LLMs locaux ne respectent pas toujours le format. Le parser extrait le JSON meme si le LLM ajoute du texte autour, et retourne des valeurs par defaut si le JSON est invalide.

**Fallback GPU** : si le LLM crash (erreur CUDA, VRAM insuffisante), le score LLM tombe a 0 pour ce candidat et seul le cosine compte, avec un warning pour le recruteur.

#### Vitesse du Stage 2 : le goulot d'etranglement

C'est **~90% du temps total** d'analyse. Chaque appel LLM prend 20-40 secondes, et les appels sont **sequentiels** (un par un, pas en parallele).

Pour 10 CVs = 10 appels × ~30s = **3-6 minutes** rien que pour le Stage 2.

C'est lent non pas a cause du materiel, mais parce que le LLM genere sa reponse **token par token** (un mot a la fois). C'est la nature meme de l'inference LLM.

---

### Score Final

```
Score = (Score Cosinus * 0.30) + (Score LLM * 0.70)
```

| Composante | Poids | Role |
|---|---|---|
| Score Cosinus | 30% | Rapide, objectif, deterministe. Sert de garde-fou si le LLM hallucine |
| Score LLM | 70% | Comprend le contexte metier, elimine les faux positifs |

Les candidats sont tries par score decroissant et on garde les `top_n` meilleurs.

---

## Etape 3 : Synthese Finale

Fichier : `app.py` (lignes 808-848)

Un **dernier appel LLM** genere un texte lisible pour le recruteur.

**Important** : le LLM ne relit PAS les CVs. Il recoit uniquement les **scores et justifications** du Stage 2 :

```python
llm_prompt = f"""Tu es un expert en recrutement...
POSTE : {job_description}
RESULTATS :
{candidates_summary}
Redige une synthese concise pour le recruteur..."""

llm_analysis = llm.invoke(llm_prompt)
```

Ca evite de depasser la limite de contexte du modele et elimine les confusions entre candidats.

**Vitesse** : ~20-40 secondes (1 seul appel LLM).

---

## Nombre total d'appels LLM

Pour N candidats, le LLM est appele **N + 1 fois** :
- **N appels** au Stage 2 (1 par candidat)
- **1 appel** au Stage 3 (synthese)

Exemple avec 10 CVs = **11 appels LLM**. C'est pour ca que l'analyse prend ~5 minutes.

---

## Ou s'execute quoi : resume materiel

| Composant | Stockage (disque) | Execution | Memoire utilisee |
|---|---|---|---|
| Modele d'embeddings (~1.1 Go) | Cache Hugging Face | **CPU** | **RAM** |
| LLM llama3.1:8b (~4.7 Go) | Cache Ollama | **GPU** | **VRAM** |
| Calcul cosinus (NumPy) | — | **CPU** | **RAM** (negligeable) |
| Texte des CVs, scores | — | **CPU** | **RAM** (negligeable) |
| Interface Streamlit | — | **CPU** | **RAM** |

Au lancement, les modeles sont **charges du disque dur vers la memoire** (RAM ou VRAM). Le traitement se fait ensuite entierement en memoire. Quand on ferme l'app, tout est libere.

---

## Contraintes materielles : RTX 3050 Ti (4 Go VRAM)

Fichier : `config/settings.py`

La RTX 3050 Ti a **4 Go de VRAM**. Le systeme est configure pour rester dans cette limite :

| Parametre | Valeur | Raison |
|---|---|---|
| `OLLAMA_NUM_CTX` | 2048 tokens | Limite l'allocation KV-cache en VRAM (~3.5 Go utilises) |
| `DEFAULT_CONTEXT_WINDOW` | 2000 chars (~500 tokens) | Ce qui reste pour le CV apres le prompt, le poste et la reponse |
| `CHUNK_SIZE` | 500 chars | Taille optimale pour les embeddings |
| `CHUNK_OVERLAP` | 50 chars | Evite de couper les idees entre chunks |
| `OLLAMA_TEMPERATURE` | 0.1 | Reponses deterministes, peu de creativite |
| `SCORE_WEIGHT_COSINE` | 0.3 | Poids du score mathematique |
| `SCORE_WEIGHT_LLM` | 0.7 | Poids du score LLM |

**Marge de manoeuvre** : on pourrait monter `OLLAMA_NUM_CTX` a 4096 tokens (→ ~1500 tokens / 6000 chars de CV), ce qui utiliserait ~3.8 Go de VRAM. Ca couvrirait la quasi-totalite d'un CV. Mais au-dela, on risque de depasser les 4 Go et de crasher.

Le modele d'embeddings tourne sur **CPU** et ne consomme pas de VRAM, donc toute la VRAM est reservee au LLM.

---

## Pipeline Complet (Flux de Donnees)

```
[Upload PDFs + Description du poste + Nombre de candidats]
                        |
                        v
[Etape 1 : Parsing]
  Pour chaque PDF :
    - pypdf : extraction du texte (CPU + RAM)
    - regex : extraction de l'email
    - nom de fichier : extraction du nom
  Resultat : liste de {name, text, email}
                        |
                        v
[Stage 1 : Cosinus (30%)] — CPU + RAM
  Pour chaque CV (texte entier, pas de troncature) :
    - Decoupage en chunks de 500 chars (avec 50 de chevauchement)
    - Transformation en vecteurs de 768 nombres (embeddings, ~100ms/chunk)
    - Calcul cosinus entre chaque chunk et le poste (microsecondes)
    - Moyenne des top-3 chunks
  Resultat : score cosinus par candidat
  Vitesse : ~10 secondes pour 10 CVs
                        |
                        v
[Stage 2 : LLM Reranking (70%)] — GPU + VRAM
  Pour chaque CV (sequentiel, ~30s/CV) :
    - Troncature a 2000 chars (~500 tokens)
    - Envoi au LLM : prompt + poste + CV tronque
    - Evaluation sur 3 criteres (0-100)
    - Reponse en JSON structure
  Resultat : score LLM par candidat
  Vitesse : ~3-6 minutes pour 10 CVs (goulot d'etranglement)
                        |
                        v
[Score Hybride = 0.3 * cosinus + 0.7 * LLM]
  Tri decroissant → garder top_n candidats
                        |
                        v
[Stage 3 : Synthese LLM] — GPU + VRAM
  1 appel LLM avec les scores/justifications (pas les CVs)
  Resultat : texte de synthese pour le recruteur
  Vitesse : ~20-40 secondes
                        |
                        v
[Affichage Streamlit : tableau + details + synthese]
```

**Temps total pour 10 CVs : ~4-7 minutes** (dont ~90% au Stage 2)

---

## Architecture des Fichiers

```
resumeradar/
  app.py                    # Interface Streamlit + orchestration du pipeline
  config/
    settings.py             # Configuration centralisee (modeles, poids, limites)
  utils/
    scoring.py              # Scoring hybride (cosinus + LLM reranker)
    email_extractor.py      # Extraction email et nom depuis les CVs
```

---

## Differences avec un RAG Classique

| Aspect | RAG Classique (chatbot) | ResumeRadar |
|---|---|---|
| Volume de documents | Milliers/millions | 6-20 par session |
| Persistance | Base vectorielle permanente | En memoire, jetable |
| Index vectoriel | ChromaDB, FAISS, PgVector | Aucun (brute force) |
| Retrieval | Top-k similarity search | Top-3 chunks par CV |
| Generation | Reponse en langage naturel | Scores structures (JSON) |
| Reranking | Optionnel | Obligatoire (coeur du systeme) |
