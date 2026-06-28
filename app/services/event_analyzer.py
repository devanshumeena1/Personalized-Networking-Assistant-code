import logging
from typing import List
import os

logger = logging.getLogger(__name__)

USE_MOCK_ML = os.getenv("USE_MOCK_ML", "True").lower() in ("true", "1", "yes")
THEME_EXTRACTOR_MODEL = os.getenv("THEME_EXTRACTOR_MODEL", "typeform/distilbert-base-uncased-mnli")

theme_classifier = None

def get_theme_classifier():
    global theme_classifier, USE_MOCK_ML
    if USE_MOCK_ML:
        return None
    if theme_classifier is None:
        try:
            from transformers import pipeline
            logger.info(f"Loading theme classifier model: {THEME_EXTRACTOR_MODEL}")
            theme_classifier = pipeline(
                "zero-shot-classification",
                model=THEME_EXTRACTOR_MODEL
            )
        except Exception as e:
            logger.warning(f"Failed to load theme classifier. Falling back to mock. Error: {e}")
            USE_MOCK_ML = True
    return theme_classifier

def extract_topics(description: str, interests: List[str]) -> List[str]:
    """
    Extract topics from event description and interests using zero-shot classification (DistilBERT).
    """
    classifier = get_theme_classifier()
    if classifier is None:
        return _mock_extract_topics(description, interests)

    try:
        candidate_labels = list(set([i.lower() for i in interests] + [
            "technology", "sustainability", "business", "innovation", 
            "finance", "healthcare", "education", "design", "marketing"
        ]))
        result = classifier(description, candidate_labels=candidate_labels)
        top_labels = result["labels"][:3]
        return [label.title() for label in top_labels]
    except Exception as e:
        logger.error(f"Error during theme extraction: {e}. Falling back to mock.")
        return _mock_extract_topics(description, interests)

def _mock_extract_topics(description: str, interests: List[str]) -> List[str]:
    words = description.lower().replace(",", " ").replace(".", " ").replace("-", " ").split()
    stopwords = {
        "for", "the", "and", "in", "of", "to", "a", "an", "with", "at", "on", 
        "by", "is", "are", "about", "how", "using", "from", "with", "our"
    }
    candidates = [w.capitalize() for w in words if w not in stopwords and len(w) > 3]
            
    topics = []
    for interest in interests:
        if interest.lower() in description.lower():
            topics.append(interest.title())
            
    for c in candidates:
        if c not in topics:
            topics.append(c)
            
    default_fallbacks = ["AI", "Sustainability", "Innovation", "Networking", "Technology"]
    for f in default_fallbacks:
        if len(topics) < 3 and f not in topics:
            topics.append(f)
            
    return list(dict.fromkeys(topics))[:3]
