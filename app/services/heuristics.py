import re

# -----------------------------
# 1. LISTAS AMPLIADAS DE PATRONES
# -----------------------------

# Patrones comunes en titulares de clickbait reales
CLICKBAIT_PATTERNS = [
    r"no creer[aá]s", r"no te imaginas", r"te sorprender[aá]", r"incre[ií]ble",
    r"impactante", r"asombroso", r"alucinante", r"impresionante", r"lo que pas[oó]",
    r"esto cambiar[aá] tu vida", r"tienes que ver esto", r"no sab[ií]as que",
    r"lo que nadie te dijo", r"el secreto que", r"inesperado", r"sorprendente",
    r"revelado", r"nadie se esperaba", r"se volvió viral", r"viral",
    r"alerta", r"última hora", r"urgente", r"lo que descubrieron",
    r"te dejar[aá] sin palabras", r"as[ií] reaccion[oó]", r"mira c[oó]mo",
    r"quedarás helado", r"descubre la verdad", r"mira lo que hizo",
    r"así fue", r"el resultado te sorprenderá"
]

# Palabras que indican sesgo emocional, ideológico o valoración extrema
BIAS_WORDS = [
    # Sesgo negativo
    "terrible", "escándalo", "escandaloso", "vergonzoso", "indignante",
    "pésimo", "desastroso", "atroz", "criminal", "repugnante", "horrible",
    # Sesgo positivo extremo
    "brillante", "fantástico", "maravilloso", "glorioso", "épico", "extraordinario",
    # Polarización e ideología
    "corrupto", "manipulado", "adoctrinamiento", "propaganda",
    "dictadura", "traición", "patriota", "antipatriota",
    # Sesgo emocional y moralizador
    "vergüenza", "culpa", "héroe", "villano", "peligroso", "amenaza",
]

# Expresiones que suelen aparecer en contenido humorístico o satírico
SATIRE_CUES = [
    "parodia", "broma", "humor", "satírico", "elmundotoday", "rocambolesco",
    "ficción humorística", "sarcasmo", "ironía", "burla", "chiste"
]

# Indicadores fuertes de falsedad o desinformación
FAKE_NEWS_CUES = [
    "fake", "engaño", "mentira", "falso", "desinformación", "hoax",
    "estafa", "conspiración", "bulo", "manipulado", "inventado",
    # verbos comunes en bulos
    "difunden", "circula un rumor", "cadena de whatsapp"
]

# -----------------------------
# 2. DETECTOR DE RED FLAGS
# -----------------------------

def detect_red_flags(text: str):
    """Detecta señales de clickbait o sesgo emocional usando listas ampliadas."""
    flags = []

    # Detectar clickbait usando patrones amplios y robustos
    for pat in CLICKBAIT_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            flags.append("Posible clickbait")
            break

    # Detectar lenguaje sesgado
    for word in BIAS_WORDS:
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            flags.append("Lenguaje sesgado o emocional")
            break

    return flags or ["Sin señales de manipulación detectadas"]

# -----------------------------
# 3. CLASIFICADOR DE FIABILIDAD
# -----------------------------

def classify_article(text: str):
    """
    Clasificación heurística mejorada:
    - Sátira: palabras clave de humor/parodia.
    - Fake news: patrones comunes de bulos y desinformación.
    - Informativo: si no se detecta nada anómalo.
    """
    t = text.lower()

    if any(w in t for w in SATIRE_CUES):
        return "Sátira o contenido humorístico"

    if any(w in t for w in FAKE_NEWS_CUES):
        return "Posible fake news o desinformación"

    if any(re.search(pat, t) for pat in CLICKBAIT_PATTERNS):
        return "Contenido informativo con fuerte clickbait"

    return "Informativo o neutral"
