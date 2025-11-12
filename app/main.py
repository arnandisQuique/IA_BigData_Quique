import sys, os
# Añade al PATH la carpeta padre del archivo actual, para permitir imports del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st  # Librería para crear la interfaz web

# Importamos las funciones principales del proyecto
from app.services.language import analyze_text            # Azure Language API
from app.services.heuristics import detect_red_flags, classify_article  # Heurísticas (clickbait, sesgo…)
from app.utils.extractor import extract_text_from_url     # Extracción de texto desde una URL


# -----------------------------
# CONFIGURACIÓN DE STREAMLIT
# -----------------------------
st.set_page_config(page_title="📰 Analizador de Noticias", page_icon="🧠")

# Título principal en pantalla
st.title("🧠 Analizador / Verificador de Noticias (Azure Language)")

# Creamos las tres pestañas principales (inputs, informe, historial)
tab1, tab2, tab3 = st.tabs(["📝 URL / Texto", "📊 Informe", "🕓 Historial"])


# =====================================================
# 📝 TAB 1 — Entrada de texto o URL
# =====================================================
with tab1:

    # Selector para elegir si la entrada será texto o URL
    input_type = st.radio("Tipo de entrada", ["Texto manual", "URL de noticia"])

    text = ""  # Variable donde almacenaremos el texto final a analizar

    # -----------------------------
    # Entrada tipo: Texto manual
    # -----------------------------
    if input_type == "Texto manual":
        text = st.text_area("Escribe o pega la noticia aquí:", height=200)

    # -----------------------------
    # Entrada tipo: URL
    # -----------------------------
    else:
        url = st.text_input("Introduce la URL:")

        # Cuando el usuario pulsa "Extraer texto"
        if st.button("Extraer texto") and url.strip():
            extracted = extract_text_from_url(url)  # Llama a la función que extrae texto de la web
            st.session_state["extracted_text"] = extracted  # Guarda el texto en la sesión
            st.text_area("Texto extraído:", extracted, height=200)

        # Si ya existe un texto extraído previamente, se muestra de nuevo
        elif "extracted_text" in st.session_state:
            st.text_area("Texto extraído:", st.session_state["extracted_text"], height=200)
            text = st.session_state["extracted_text"]  # Usamos este texto para análisis

    # -----------------------------
    # Inicialización del historial
    # -----------------------------
    if "history" not in st.session_state:
        st.session_state["history"] = []  # Crea lista vacía si no existe

    # -----------------------------
    # Botón para analizar la noticia
    # -----------------------------
    if st.button("Analizar noticia") and text.strip():

        # Spinner de carga mientras Azure procesa el texto
        with st.spinner("🔍 Analizando texto con Azure..."):
            result = analyze_text(text)  # Llamada al servicio de Azure

        # Si Azure devuelve un error, lo mostramos
        if "error" in result:
            st.error("❌ No se pudo analizar el texto. Revisa tus credenciales o el servicio de Azure.")

        # Si la respuesta es válida, procesamos los datos
        else:
            # Aplicamos heurísticas (clickbait, sesgo, clasificación)
            flags = detect_red_flags(text)
            classification = classify_article(text)

            # -----------------------------
            # Procesamos el sentimiento
            # -----------------------------
            total_sentences = len(result.get("sentences", []))

            if total_sentences > 0:
                # Contamos frases por tipo de sentimiento
                positive_count = sum(1 for _, s in result["sentences"] if s == "positive")
                neutral_count  = sum(1 for _, s in result["sentences"] if s == "neutral")
                negative_count = sum(1 for _, s in result["sentences"] if s == "negative")

                # Calculamos porcentajes
                positive_pct = round((positive_count / total_sentences) * 100, 1)
                neutral_pct  = round((neutral_count  / total_sentences) * 100, 1)
                negative_pct = round((negative_count / total_sentences) * 100, 1)

            else:
                positive_pct = neutral_pct = negative_pct = 0.0

            # -----------------------------
            # Guardamos datos en session_state
            # -----------------------------
            st.session_state["analysis"] = result
            st.session_state["flags"] = flags
            st.session_state["classification"] = classification

            # Guardamos un resumen para el historial
            st.session_state["history"].append({
                "texto": text[:120] + "...",
                "idioma": result.get("language", "Desconocido"),
                "sentimiento": result.get("sentiment", "Desconocido"),
                "clasificación": classification,
                "flags": ", ".join(flags),
                "positive_pct": positive_pct,
                "neutral_pct": neutral_pct,
                "negative_pct": negative_pct
            })

            # Mensaje de éxito
            st.success("✅ Análisis completado. Revisa el informe o el historial.")


# =====================================================
# 📊 TAB 2 — Informe detallado
# =====================================================
with tab2:

    # Si no se ha analizado nada, se avisa al usuario
    if "analysis" not in st.session_state:
        st.warning("Primero analiza una noticia en la pestaña anterior.")

    else:
        result = st.session_state["analysis"]  # Recuperamos el análisis guardado

        st.subheader("📋 Informe de Análisis")
        st.write(f"**Idioma detectado:** {result['language']}")
        st.write(f"**Sentimiento global:** {result['sentiment']}")
        st.write(f"**Clasificación heurística:** {st.session_state['classification']}")

        # Repetimos el cálculo porcentual para mostrarlo en esta pestaña
        total_sentences = len(result.get("sentences", []))

        if total_sentences > 0:
            positive_count = sum(1 for _, s in result["sentences"] if s == "positive")
            neutral_count  = sum(1 for _, s in result["sentences"] if s == "neutral")
            negative_count = sum(1 for _, s in result["sentences"] if s == "negative")

            positive_pct = round((positive_count / total_sentences) * 100, 1)
            neutral_pct  = round((neutral_count  / total_sentences) * 100, 1)
            negative_pct = round((negative_count / total_sentences) * 100, 1)

        else:
            positive_pct = neutral_pct = negative_pct = 0.0

        # Mostramos porcentajes
        st.markdown("### 💯 Distribución de sentimientos en el texto")
        st.write(f"🟢 **Positivas:** {positive_pct}%")
        st.write(f"🟡 **Neutras:** {neutral_pct}%")
        st.write(f"🔴 **Negativas:** {negative_pct}%")

        # Mostramos el resumen generado por Azure
        st.markdown("### 🧩 Resumen")
        st.info(result["summary"])

        # Mostramos cada frase con su sentimiento correspondiente
        st.markdown("### 💬 Evidencias de sentimiento")
        for sentence, sent in result["sentences"]:
            emoji = "😊" if sent == "positive" else "😐" if sent == "neutral" else "😠"
            st.write(f"{emoji} *{sent}*: {sentence}")

        # Red flags identificadas
        st.markdown("### ⚠️ Red Flags")
        st.warning(", ".join(st.session_state["flags"]))


# =====================================================
# 🕓 TAB 3 — Historial de análisis anteriores
# =====================================================
with tab3:
    st.subheader("🕓 Historial de análisis anteriores")

    # Si hay historial, lo recorremos del más reciente al más antiguo
    if "history" in st.session_state and st.session_state["history"]:
        for i, h in enumerate(reversed(st.session_state["history"]), 1):
            st.markdown(f"**{i}.** 🗞️ *{h['texto']}*")
            st.write(f"- Idioma: {h['idioma']}")
            st.write(f"- Sentimiento global: {h['sentimiento']}")
            st.write(f"- 🟢 Positivas: {h['positive_pct']}% | 🟡 Neutras: {h['neutral_pct']}% | 🔴 Negativas: {h['negative_pct']}%")
            st.write(f"- Clasificación: {h['clasificación']}")
            st.write(f"- Red Flags: {h['flags']}")
            st.divider()  # Línea separadora visual entre análisis

    else:
        st.info("Aún no hay análisis guardados.")
