import re

CLICKBAIT = [
    r"no creerás", r"increíble", r"impactante", r"asombroso", r"descubre",
    r"lo que pasó", r"sorprendente", r"inesperado"
]

SESGO = ["terrible", "escándalo", "fantástico", "vergonzoso", "brillante"]

def detect_red_flags(text: str):
    flags = []
    for pat in CLICKBAIT:
        if re.search(pat, text, re.IGNORECASE):
            flags.append("Posible clickbait")
            break
    for w in SESGO:
        if re.search(rf"\\b{w}\\b", text, re.IGNORECASE):
            flags.append("Lenguaje sesgado")
            break
    return flags or ["Sin red flags detectadas"]

def classify_article(text: str):
    """Clasifica el texto como fake, sátira o informativo (heurística básica)."""
    t = text.lower()
    if any(w in t for w in ["parodia", "broma", "satírico", "humor", "elmundotoday"]):
        return "Sátira o humor"
    elif any(w in t for w in ["fake", "engaño", "mentira", "falso", "desinformación"]):
        return "Posible fake news"
    else:
        return "Informativo o neutral"
