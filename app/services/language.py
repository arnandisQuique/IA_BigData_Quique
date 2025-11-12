import streamlit as st
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.exceptions import HttpResponseError


def get_secret(name, default=None):
    return st.secrets.get(name) or os.getenv(name, default)


ENDPOINT = get_secret("AZURE_LANGUAGE_ENDPOINT")
KEY = get_secret("AZURE_LANGUAGE_KEY")


@st.cache_resource(show_spinner=False)
def get_client():
    """Crea y cachea el cliente de Azure Language."""
    if not (ENDPOINT and KEY):
        st.error("❌ Faltan credenciales en `.streamlit/secrets.toml`")
        return None
    credential = AzureKeyCredential(KEY)
    return TextAnalyticsClient(endpoint=ENDPOINT, credential=credential)


@st.cache_data(ttl=3600)
def analyze_text(text: str):
    """Analiza idioma, sentimiento y resumen con Azure Language SDK."""
    client = get_client()
    if client is None:
        return {"error": "missing_credentials"}

    try:
        # 1️⃣ Detección de idioma
        lang_result = client.detect_language(documents=[text])[0]
        language = lang_result.primary_language.name
        lang_code = lang_result.primary_language.iso6391_name

        # 2️⃣ Análisis de sentimiento
        sent_result = client.analyze_sentiment(documents=[text], language=lang_code)[0]
        sentiment = sent_result.sentiment
        sentences = [(s.text, s.sentiment) for s in sent_result.sentences]

        # 3️⃣ Resumen extractivo
        poller = client.begin_extract_summary(documents=[text], language=lang_code)
        summary_result = poller.result()
        summary_sentences = [
            sentence.text for doc in summary_result for sentence in doc.sentences
        ]
        summary = " ".join(summary_sentences[:3]) if summary_sentences else "No se pudo generar resumen."

        return {
            "language": language,
            "sentiment": sentiment,
            "summary": summary,
            "sentences": sentences
        }

    except HttpResponseError as e:
        st.error(f"⚠️ Error en Azure Language SDK: {e.message}")
        return {"error": str(e)}
    except Exception as e:
        st.error(f"⚠️ Error inesperado: {e}")
        return {"error": str(e)}
