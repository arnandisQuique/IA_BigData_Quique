import streamlit as st
import requests
from bs4 import BeautifulSoup


# --------------------------------------------------------
# Función para extraer texto desde una URL.
# Se usa cache_data para:
#  - evitar repetir descargas en la misma sesión
#  - acelerar la app
#  - reducir llamadas al servidor
# ttl=1800 → la caché dura 30 minutos
# --------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def extract_text_from_url(url: str) -> str:
    try:
        # --------------------------------------------------------
        # Descarga el HTML de la página con un timeout de 10s
        # --------------------------------------------------------
        html = requests.get(url, timeout=10).text

        # --------------------------------------------------------
        # Analiza el HTML usando BeautifulSoup
        # "html.parser" → parser estándar incluido en Python
        # --------------------------------------------------------
        soup = BeautifulSoup(html, "html.parser")

        # --------------------------------------------------------
        # Extrae todos los párrafos <p> y obtiene su contenido de texto
        # Cada elemento p.get_text() devuelve el texto plano sin etiquetas
        # --------------------------------------------------------
        paragraphs = [p.get_text() for p in soup.find_all("p")]

        # --------------------------------------------------------
        # Une todos los párrafos en un solo string
        # strip() quita espacios extremos
        # [:5000] limita a 5000 caracteres para evitar textos enormes
        # --------------------------------------------------------
        return " ".join(paragraphs).strip()[:5000]

    except Exception as e:
        # --------------------------------------------------------
        # Si ocurre cualquier error (URL inválida, timeout, no hay internet…)
        # devolvemos un mensaje entendible para el usuario
        # --------------------------------------------------------
        return f"Error extrayendo texto: {e}"
