import logging
from typing import List
import os

logger = logging.getLogger(__name__)

# Config flags
USE_MOCK_ML = os.getenv("USE_MOCK_ML", "True").lower() in ("true", "1", "yes")
THEME_EXTRACTOR_MODEL = os.getenv("THEME_EXTRACTOR_MODEL", "typeform/distilbert-base-uncased-mnli")
STARTER_GENERATOR_MODEL = os.getenv("STARTER_GENERATOR_MODEL", "gpt2")

# Lazy-loaded pipeline variables
theme_classifier = None
starter_generator = None

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

def get_starter_generator():
    global starter_generator, USE_MOCK_ML
    if USE_MOCK_ML:
        return None
    if starter_generator is None:
        try:
            from transformers import pipeline
            logger.info(f"Loading starter generator model: {STARTER_GENERATOR_MODEL}")
            starter_generator = pipeline(
                "text-generation",
                model=STARTER_GENERATOR_MODEL,
                device=-1  # Force CPU
            )
        except Exception as e:
            logger.warning(f"Failed to load starter generator. Falling back to mock. Error: {e}")
            USE_MOCK_ML = True
    return starter_generator

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

def generate_suggestions(description: str, topics: List[str], interests: List[str]) -> List[str]:
    """
    Generate tailored conversation suggestion starters using GPT-2.
    """
    generator = get_starter_generator()
    if generator is None:
        return _mock_generate_suggestions(description, topics, interests)

    try:
        suggestions = []
        topic_str = ", ".join(topics)
        
        for interest in interests[:2]:
            prompt = (
                f"Event: {description}. Topics: {topic_str}. Interest: {interest}.\n"
                f"Generate a professional, polite, and engaging conversation starter question:\n\""
            )
            outputs = generator(
                prompt,
                max_new_tokens=40,
                num_return_sequences=1,
                pad_token_id=50256,
                temperature=0.7,
                do_sample=True
            )
            generated_text = outputs[0]["generated_text"]
            question_part = generated_text[len(prompt):].strip()
            cleaned = _cleanup_generated_suggestion(question_part)
            if len(cleaned) > 15:
                suggestions.append(cleaned)
        
        if len(suggestions) < 2:
            fillers = _mock_generate_suggestions(description, topics, interests)
            for f in fillers:
                if f not in suggestions:
                    suggestions.append(f)
                    
        return suggestions[:3]
    except Exception as e:
        logger.error(f"Error during starter generation: {e}. Falling back to mock.")
        return _mock_generate_suggestions(description, topics, interests)

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

def _mock_generate_suggestions(description: str, topics: List[str], interests: List[str]) -> List[str]:
    topic_lead = topics[0] if topics else "Innovation"
    interest_lead = interests[0] if interests else "networking opportunities"
    
    suggestions = [
        f"Hi! I noticed the event highlights {topic_lead.lower()}. How do you think this theme intersects with your interests in {interest_lead.lower()}?",
        f"Regarding '{description}', what specific session or aspect of {topic_lead} has caught your attention today?",
        f"I'm curious: given your interest in {interest_lead.lower()}, what are the key challenges you're hoping to address in the context of {topic_lead.lower()}?"
    ]
    
    if len(interests) > 1:
        suggestions[1] = f"Since you're involved in both {interests[0].lower()} and {interests[1].lower()}, how do you see those combining in the context of {topic_lead.lower()}?"
        
    return suggestions

def _cleanup_generated_suggestion(text: str) -> str:
    text = text.replace('"', '').replace('\'', '').strip()
    end_marks = ["?", ".", "!"]
    first_end = len(text)
    for mark in end_marks:
        pos = text.find(mark)
        if pos != -1 and pos < first_end:
            first_end = pos + 1
            
    text = text[:first_end].strip()
    question_words = ["how", "what", "why", "are", "do", "is", "can", "would", "could", "should"]
    if text and not text.endswith("?") and any(text.lower().startswith(w) for w in question_words):
        text += "?"
    return text
