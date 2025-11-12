import streamlit as st

@st.cache_resource(show_spinner=False)
def http_session():
    import requests
    s = requests.Session()
    s.headers.update({"User-Agent": "analizador-noticias/1.0"})
    return s
