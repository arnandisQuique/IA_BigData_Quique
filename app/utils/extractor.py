import streamlit as st
import requests
from bs4 import BeautifulSoup

@st.cache_data(ttl=1800, show_spinner=False)
def extract_text_from_url(url: str) -> str:
    try:
        html = requests.get(url, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        return " ".join(paragraphs).strip()[:5000]
    except Exception as e:
        return f"Error extrayendo texto: {e}"
