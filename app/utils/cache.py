import streamlit as st


# --------------------------------------------------------
# http_session()
# Esta función crea y devuelve una sesión HTTP persistente.
#
# Se usa @st.cache_resource para:
#   - Crear la sesión UNA sola vez
#   - Reutilizar la misma conexión en lugar de crear nuevas
#   - Mejorar la eficiencia de la app
#   - Evitar overhead innecesario en requests
#
# show_spinner=False → No mostrar un spinner cuando se carga la sesión.
# --------------------------------------------------------
@st.cache_resource(show_spinner=False)
def http_session():
    # Importamos aquí requests para que solo se cargue cuando se llame la función
    import requests

    # --------------------------------------------------------
    # Creamos una sesión persistente de requests.
    # Una Session:
    #   - Mantiene cookies
    #   - Reutiliza la conexión HTTP
    #   - Reduce latencia y carga
    # --------------------------------------------------------
    s = requests.Session()

    # --------------------------------------------------------
    # Añadimos un User-Agent personalizado.
    # Esto ayuda a:
    #   - Evitar bloqueos por parte de algunos servidores
    #   - Identificar la aplicación en logs
    #   - Evitar restricciones de bots muy estrictas
    # --------------------------------------------------------
    s.headers.update({"User-Agent": "analizador-noticias/1.0"})

    # Devuelve la sesión lista para usarse en otras funciones
    return s
