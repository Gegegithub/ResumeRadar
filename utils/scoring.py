# -*- coding: utf-8 -*-
"""
Scoring Hybride Multi-stage RAG pour ResumeRadar

Architecture : on passe d'un modele "Bi-Encoder" (similarite cosinus pure,
rapide mais aveugle au contexte metier) a une architecture de "Reranking"
en deux etapes :

  Stage 1 - Bi-Encoder (30% du score final) :
    Similarite cosinus entre embeddings du poste et des chunks du CV.
    Rapide, permet un premier filtrage de masse.
    Limite : la similarite mathematique ne comprend pas l'exclusion mutuelle.
    Un avocat et un developpeur peuvent partager du vocabulaire ("contrat",
    "livraison", "client") sans etre interchangeables.

  Stage 2 - LLM Reranker (70% du score final) :
    Le LLM lit le CV complet (jusqu'a DEFAULT_CONTEXT_WINDOW chars) et evalue
    le candidat sur 3 criteres metier avec des scores de 0 a 100 :
    - Adequation Metier : le candidat exerce-t-il le bon metier ?
    - Maitrise des Hard Skills : possede-t-il les competences techniques demandees ?
    - Experience Pertinente : a-t-il l'experience dans le domaine requis ?

  Score Final = (Score_Cosinus * 0.3) + (Score_LLM * 0.7)

Ce systeme elimine les "faux positifs" ou un juriste obtenait un score
eleve pour un poste tech simplement parce que les deux textes partagent
du vocabulaire general.
"""
import re
import json
from typing import List, Dict
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import (
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DEFAULT_CONTEXT_WINDOW,
    SCORE_WEIGHT_COSINE,
    SCORE_WEIGHT_LLM,
)


# Singleton pour le modele d'embeddings
_embeddings_instance = None


def get_embeddings():
    """Recupere l'instance singleton du modele d'embeddings"""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    return _embeddings_instance


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calcule la similarite cosinus entre deux vecteurs"""
    a = np.array(vec_a)
    b = np.array(vec_b)
    norm_product = np.linalg.norm(a) * np.linalg.norm(b)
    if norm_product == 0:
        return 0.0
    return float(np.dot(a, b) / norm_product)


def chunk_text(text: str) -> List[str]:
    """
    Decoupe le texte d'un CV en chunks avec chevauchement.
    Utilise RecursiveCharacterTextSplitter pour couper intelligemment
    aux frontieres de paragraphes/phrases plutot qu'au milieu d'un mot.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_text(text)
    return chunks if chunks else [text]


def compute_cosine_score(job_description: str, cv_text: str) -> float:
    """
    Stage 1 : Score cosinus sur chunks.
    Embede la description de poste et chaque chunk du CV separement,
    puis retourne le score moyen des top-3 chunks les plus similaires.
    Cela evite la perte d'information due a la troncature d'un embedding
    unique sur un document entier.
    """
    embeddings = get_embeddings()
    jd_embedding = embeddings.embed_query(job_description)

    chunks = chunk_text(cv_text)
    chunk_scores = []
    for chunk in chunks:
        chunk_embedding = embeddings.embed_query(chunk)
        score = cosine_similarity(jd_embedding, chunk_embedding)
        chunk_scores.append(score)

    # Moyenne des top-3 chunks les plus pertinents
    chunk_scores.sort(reverse=True)
    top_chunks = chunk_scores[:min(3, len(chunk_scores))]
    return sum(top_chunks) / len(top_chunks)


# --- Prompt de Reranking LLM ---

RERANKER_PROMPT = """Tu es un expert en recrutement. Tu dois evaluer objectivement si un candidat correspond a une offre d'emploi.

DESCRIPTION DU POSTE :
{job_description}

CV DU CANDIDAT ({candidate_name}) :
{cv_text}

Evalue ce candidat sur exactement 3 criteres. Pour chaque critere, donne un score de 0 a 100 et une justification courte avec des citations du CV.

Reponds UNIQUEMENT avec un JSON valide, sans texte avant ni apres, au format exact suivant :
{{
  "adequation_metier": {{
    "score": <0-100>,
    "justification": "<Le candidat exerce-t-il le bon metier pour ce poste ? Cite les elements du CV.>"
  }},
  "hard_skills": {{
    "score": <0-100>,
    "justification": "<Quelles competences techniques demandees sont presentes ou absentes ? Cite les technologies/outils trouves.>"
  }},
  "experience_pertinente": {{
    "score": <0-100>,
    "justification": "<Le candidat a-t-il de l'experience dans le domaine ou secteur requis ? Cite les postes/projets pertinents.>"
  }}
}}"""


def compute_llm_score(
    llm,
    job_description: str,
    candidate_name: str,
    cv_text: str,
) -> Dict:
    """
    Stage 2 : Reranking par LLM.
    Le LLM evalue le candidat sur 3 criteres metier et retourne
    des scores structures avec justifications.

    Returns:
        Dict avec 'score' (0-1), 'details' (les 3 criteres), 'evidence', 'warnings'
    """
    # Tronquer le CV a DEFAULT_CONTEXT_WINDOW pour rester dans les limites
    # du modele local, tout en envoyant beaucoup plus que les 800 chars d'avant
    truncated_cv = cv_text[:DEFAULT_CONTEXT_WINDOW]

    prompt = RERANKER_PROMPT.format(
        job_description=job_description,
        candidate_name=candidate_name,
        cv_text=truncated_cv,
    )

    try:
        raw_response = llm.invoke(prompt)
    except Exception as e:
        error_msg = str(e).lower()
        if "cuda" in error_msg or "500" in error_msg or "memory" in error_msg:
            return {
                "score": 0.0,
                "details": {
                    "adequation_metier": {"score": 0, "justification": "GPU VRAM insuffisante"},
                    "hard_skills": {"score": 0, "justification": "GPU VRAM insuffisante"},
                    "experience_pertinente": {"score": 0, "justification": "GPU VRAM insuffisante"},
                },
                "evidence": [],
                "warnings": [f"Reranking echoue (CUDA/memoire) pour {candidate_name}. Score base sur cosinus uniquement."],
            }
        raise

    # Parser la reponse JSON du LLM
    return _parse_llm_response(raw_response)


def _parse_llm_response(raw_response: str) -> Dict:
    """
    Parse la reponse JSON du LLM reranker.
    Gere les cas ou le LLM ajoute du texte autour du JSON
    ou retourne un format invalide.
    """
    default = {
        "score": 0.0,
        "details": {
            "adequation_metier": {"score": 0, "justification": "Evaluation impossible"},
            "hard_skills": {"score": 0, "justification": "Evaluation impossible"},
            "experience_pertinente": {"score": 0, "justification": "Evaluation impossible"},
        },
        "evidence": [],
        "warnings": ["Le LLM n'a pas pu evaluer ce candidat"],
    }

    try:
        # Extraire le JSON de la reponse (le LLM peut ajouter du texte autour)
        json_match = re.search(r'\{[\s\S]*\}', raw_response)
        if not json_match:
            return default

        data = json.loads(json_match.group())

        # Extraire les scores des 3 criteres
        scores = {}
        evidence = []
        warnings = []

        for key in ["adequation_metier", "hard_skills", "experience_pertinente"]:
            if key in data and isinstance(data[key], dict):
                score_val = data[key].get("score", 0)
                # S'assurer que le score est un nombre entre 0 et 100
                score_val = max(0, min(100, int(score_val)))
                scores[key] = score_val

                justification = data[key].get("justification", "")
                if justification:
                    evidence.append(f"{key}: {justification}")

                # Detecter les points de vigilance (score < 40)
                if score_val < 40:
                    labels = {
                        "adequation_metier": "Adequation metier faible",
                        "hard_skills": "Hard skills insuffisantes",
                        "experience_pertinente": "Experience non pertinente",
                    }
                    warnings.append(f"{labels[key]} ({score_val}/100) : {justification}")
            else:
                scores[key] = 0

        # Score LLM = moyenne des 3 criteres, normalise entre 0 et 1
        avg_score = sum(scores.values()) / (3 * 100)

        return {
            "score": avg_score,
            "details": {k: data.get(k, {"score": 0, "justification": ""}) for k in scores},
            "evidence": evidence,
            "warnings": warnings,
        }

    except (json.JSONDecodeError, ValueError, KeyError):
        return default


def score_candidates(
    job_description: str,
    candidates: List[Dict],
    top_n: int = 5,
    llm=None,
) -> List[Dict]:
    """
    Scoring hybride multi-stage.

    Stage 1 : Score cosinus sur chunks (filtrage rapide, poids 30%)
    Stage 2 : Reranking LLM sur 3 criteres metier (poids 70%)
    Score Final = (cosinus * 0.3) + (llm * 0.7)

    Args:
        job_description: Texte de la description de poste
        candidates: Liste de dicts avec 'name', 'email', 'text', 'filename'
        top_n: Nombre de candidats a retenir
        llm: Instance du LLM Ollama pour le reranking

    Returns:
        Liste des top_n candidats tries par score hybride decroissant,
        enrichis avec les justifications du LLM
    """
    # Stage 1 : Score cosinus par chunks
    for candidate in candidates:
        candidate["score_cosine"] = compute_cosine_score(
            job_description, candidate["text"]
        )

    # Stage 2 : Reranking LLM (si le LLM est fourni)
    if llm is not None:
        for candidate in candidates:
            llm_result = compute_llm_score(
                llm,
                job_description,
                candidate["name"],
                candidate["text"],
            )
            candidate["score_llm"] = llm_result["score"]
            candidate["llm_details"] = llm_result["details"]
            candidate["evidence"] = llm_result["evidence"]
            candidate["warnings"] = llm_result["warnings"]

        # Score hybride (fallback cosinus seul si LLM a echoue pour ce candidat)
        for candidate in candidates:
            if candidate["score_llm"] > 0:
                candidate["score"] = (
                    candidate["score_cosine"] * SCORE_WEIGHT_COSINE
                    + candidate["score_llm"] * SCORE_WEIGHT_LLM
                )
            else:
                candidate["score"] = candidate["score_cosine"]
    else:
        # Fallback : cosinus seul si pas de LLM
        for candidate in candidates:
            candidate["score"] = candidate["score_cosine"]
            candidate["score_llm"] = 0.0
            candidate["llm_details"] = {}
            candidate["evidence"] = []
            candidate["warnings"] = ["Reranking LLM non disponible"]

    # Trier par score hybride decroissant
    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:top_n]
