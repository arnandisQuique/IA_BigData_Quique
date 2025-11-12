import streamlit as st
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.exceptions import HttpResponseError


# --------------------------------------------------------
# get_secret()
# Obtiene una variable primero desde .streamlit/secrets.toml
# y si no existe, intenta obtenerla como variable de entorno.
#
# Esto permite:
#   - Usar credenciales en producción (Streamlit Cloud)
#   - Usar variables locales en desarrollo
#   - Evitar exponer claves en el código
# --------------------------------------------------------
def get_secret(name, default=None):
    """Obtiene la credencial desde Streamlit Cloud o variable de entorno."""
    try:
        # 🔹 Primero intenta leer desde Streamlit Cloud
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass

    # 🔹 Si falla (por ejemplo, en Docker o local), busca en variables del sistema
    return os.getenv(name, default)

# --------------------------------------------------------
# Cargamos endpoint y key desde las funciones anteriores
# ENDPOINT → URL del servicio Azure Language
# KEY      → Clave privada del servicio
#
# Si faltan, el cliente no podrá inicializarse correctamente.
# --------------------------------------------------------
ENDPOINT = get_secret("AZURE_LANGUAGE_ENDPOINT")
KEY = get_secret("AZURE_LANGUAGE_KEY")

if not ENDPOINT or not KEY:
    st.error("❌ No se encontraron credenciales válidas. Verifica los secrets o variables de entorno.")

# --------------------------------------------------------
# get_client()
# Crea una instancia del cliente de Azure Language SDK.
#
# @st.cache_resource:
#   - Se ejecuta una sola vez
#   - Mantiene el cliente cargado para ahorrar tiempo
#   - show_spinner=False → no mostrar spinner al inicializar
# --------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_client():
    """Crea y cachea el cliente de Azure Language."""

    # Si no hay credenciales, se muestra error
    if not (ENDPOINT and KEY):
        st.error("❌ Faltan credenciales en `.streamlit/secrets.toml`")
        return None

    # Crea el objeto de autenticación de Azure
    credential = AzureKeyCredential(KEY)

    # Devuelve el cliente configurado
    return TextAnalyticsClient(endpoint=ENDPOINT, credential=credential)


# --------------------------------------------------------
# analyze_text()
# Realiza:
#   1️⃣ Detección de idioma
#   2️⃣ Análisis de sentimiento
#   3️⃣ Resumen extractivo
#
# @st.cache_data(ttl=3600)
#   - Cachea resultados durante 1 hora
#   - Evita pagar múltiples llamadas innecesarias a Azure
# --------------------------------------------------------
@st.cache_data(ttl=3600)
def analyze_text(text: str):
    """Analiza idioma, sentimiento y resumen con Azure Language SDK."""

    # Inicializa cliente (desde caché si ya existe)
    client = get_client()

    # Si no se puede crear cliente, devolvemos error
    if client is None:
        return {"error": "missing_credentials"}

    try:
        # --------------------------------------------------------
        # 1️⃣ DETECCIÓN DE IDIOMA
        # Azure detecta automáticamente el idioma del texto.
        # text → documento único dentro de una lista
        # --------------------------------------------------------
        lang_result = client.detect_language(documents=[text])[0]
        language = lang_result.primary_language.name  # Nombre del idioma ("Spanish")
        lang_code = lang_result.primary_language.iso6391_name  # Código ISO 639-1 ("es")

        # --------------------------------------------------------
        # 2️⃣ ANÁLISIS DE SENTIMIENTO
        # Devuelve:
        #   - sentimiento global del texto
        #   - sentimiento de cada frase
        # --------------------------------------------------------
        sent_result = client.analyze_sentiment(
            documents=[text],
            language=lang_code
        )[0]

        sentiment = sent_result.sentiment  # "positive" / "neutral" / "negative"

        # Creamos una lista de tuplas: (frase, sentimiento)
        sentences = [(s.text, s.sentiment) for s in sent_result.sentences]

        # --------------------------------------------------------
        # 3️⃣ RESUMEN EXTRACTIVO
        # Azure selecciona las frases más importantes del texto.
        # begin_extract_summary() → operación asíncrona que requiere poller
        # --------------------------------------------------------
        poller = client.begin_extract_summary(
            documents=[text],
            language=lang_code
        )

        summary_result = poller.result()  # Espera al resultado

        # Extraemos las frases seleccionadas por Azure
        summary_sentences = [
            sentence.text
            for doc in summary_result
            for sentence in doc.sentences
        ]

        # Unimos las 3 frases más relevantes para construir un resumen final
        summary = (
            " ".join(summary_sentences[:3])
            if summary_sentences
            else "No se pudo generar resumen."
        )

        # --------------------------------------------------------
        # Devolvemos un diccionario estructurado con todos los resultados
        # --------------------------------------------------------
        return {
            "language": language,
            "sentiment": sentiment,
            "summary": summary,
            "sentences": sentences
        }

    # --------------------------------------------------------
    # Manejo de errores específicos de Azure
    # --------------------------------------------------------
    except HttpResponseError as e:
        st.error(f"⚠️ Error en Azure Language SDK: {e.message}")
        return {"error": str(e)}

    # --------------------------------------------------------
    # Manejo de errores generales
    # --------------------------------------------------------
    except Exception as e:
        st.error(f"⚠️ Error inesperado: {e}")
        return {"error": str(e)}
