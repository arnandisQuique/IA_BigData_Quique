import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st

from app.services.language import analyze_text
from app.services.heuristics import detect_red_flags, classify_article
from app.utils.extractor import extract_text_from_url


st.set_page_config(page_title="📰 Analizador de Noticias", page_icon="🧠")

st.title("🧠 Analizador / Verificador de Noticias (Azure Language)")

tab1, tab2, tab3 = st.tabs(["📝 URL / Texto", "📊 Informe", "🕓 Historial"])


with tab1:
    input_type = st.radio("Tipo de entrada", ["Texto manual", "URL de noticia"])

    text = ""
    if input_type == "Texto manual":
        text = st.text_area("Escribe o pega la noticia aquí:", height=200)
    else:
        url = st.text_input("Introduce la URL:")
        if st.button("Extraer texto") and url.strip():
            extracted = extract_text_from_url(url)
            st.session_state["extracted_text"] = extracted
            st.text_area("Texto extraído:", extracted, height=200)

        elif "extracted_text" in st.session_state:
            st.text_area("Texto extraído:", st.session_state["extracted_text"], height=200)
            text = st.session_state["extracted_text"]

    if "history" not in st.session_state:
        st.session_state["history"] = []

    if st.button("Analizar noticia") and text.strip():
        with st.spinner("🔍 Analizando texto con Azure..."):
            result = analyze_text(text)

        if "error" in result:
            st.error("❌ No se pudo analizar el texto. Revisa tus credenciales o el servicio de Azure.")
        else:
            flags = detect_red_flags(text)
            classification = classify_article(text)

            total_sentences = len(result.get("sentences", []))
            if total_sentences > 0:
                positive_count = sum(1 for _, s in result["sentences"] if s == "positive")
                neutral_count = sum(1 for _, s in result["sentences"] if s == "neutral")
                negative_count = sum(1 for _, s in result["sentences"] if s == "negative")

                positive_pct = round((positive_count / total_sentences) * 100, 1)
                neutral_pct = round((neutral_count / total_sentences) * 100, 1)
                negative_pct = round((negative_count / total_sentences) * 100, 1)
            else:
                positive_pct = neutral_pct = negative_pct = 0.0

            st.session_state["analysis"] = result
            st.session_state["flags"] = flags
            st.session_state["classification"] = classification

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

            st.success("✅ Análisis completado. Revisa el informe o el historial.")



with tab2:
    if "analysis" not in st.session_state:
        st.warning("Primero analiza una noticia en la pestaña anterior.")
    else:
        result = st.session_state["analysis"]
        st.subheader("📋 Informe de Análisis")
        st.write(f"**Idioma detectado:** {result['language']}")
        st.write(f"**Sentimiento global:** {result['sentiment']}")
        st.write(f"**Clasificación heurística:** {st.session_state['classification']}")

        total_sentences = len(result.get("sentences", []))
        if total_sentences > 0:
            positive_count = sum(1 for _, s in result["sentences"] if s == "positive")
            neutral_count = sum(1 for _, s in result["sentences"] if s == "neutral")
            negative_count = sum(1 for _, s in result["sentences"] if s == "negative")

            positive_pct = round((positive_count / total_sentences) * 100, 1)
            neutral_pct = round((neutral_count / total_sentences) * 100, 1)
            negative_pct = round((negative_count / total_sentences) * 100, 1)
        else:
            positive_pct = neutral_pct = negative_pct = 0.0

        st.markdown("### 💯 Distribución de sentimientos en el texto")
        st.write(f"🟢 **Positivas:** {positive_pct}%")
        st.write(f"🟡 **Neutras:** {neutral_pct}%")
        st.write(f"🔴 **Negativas:** {negative_pct}%")

        st.markdown("### 🧩 Resumen")
        st.info(result["summary"])

        st.markdown("### 💬 Evidencias de sentimiento")
        for sentence, sent in result["sentences"]:
            emoji = "😊" if sent == "positive" else "😐" if sent == "neutral" else "😠"
            st.write(f"{emoji} *{sent}*: {sentence}")

        st.markdown("### ⚠️ Red Flags")
        st.warning(", ".join(st.session_state["flags"]))



with tab3:
    st.subheader("🕓 Historial de análisis anteriores")
    if "history" in st.session_state and st.session_state["history"]:
        for i, h in enumerate(reversed(st.session_state["history"]), 1):
            st.markdown(f"**{i}.** 🗞️ *{h['texto']}*")
            st.write(f"- Idioma: {h['idioma']}")
            st.write(f"- Sentimiento global: {h['sentimiento']}")
            st.write(f"- 🟢 Positivas: {h['positive_pct']}% | 🟡 Neutras: {h['neutral_pct']}% | 🔴 Negativas: {h['negative_pct']}%")
            st.write(f"- Clasificación: {h['clasificación']}")
            st.write(f"- Red Flags: {h['flags']}")
            st.divider()
    else:
        st.info("Aún no hay análisis guardados.")
