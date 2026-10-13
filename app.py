import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64
import io
import random

# ==============================================================================
# CONFIGURACIÓN INSTITUCIONAL UMG
# ==============================================================================
st.set_page_config(
    page_title="UMG | Laboratorio Grafopsicológico Forense",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicializar memoria de sesión
if "analisis_listo" not in st.session_state:
    st.session_state.analisis_listo = False
    st.session_state.resultado_texto = ""
    st.session_state.foto_muestra = None
    st.session_state.turno_id = 0

# ==============================================================================
# ESTILOS VISUALES INSTITUCIONALES (CSS)
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .umg-card {
        background: linear-gradient(135deg, #091E3A 0%, #112A4F 60%, #1A365D 100%);
        border: 1px solid #D4AF37;
        border-radius: 14px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 8px 20px -4px rgba(0, 0, 0, 0.35);
        margin-bottom: 18px;
    }
    
    .umg-title {
        font-family: 'Cinzel', serif;
        font-size: 1.1rem;
        letter-spacing: 2px;
        color: #F8FAFC;
        margin: 0;
        text-transform: uppercase;
        font-weight: 700;
    }
    
    .umg-faculty {
        font-size: 0.92rem;
        color: #D4AF37;
        margin: 5px 0 2px 0;
        font-weight: 700;
        letter-spacing: 0.6px;
    }
    
    .umg-course {
        font-size: 0.82rem;
        color: #93C5FD;
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    .umg-badge {
        display: inline-block;
        background: rgba(212, 175, 55, 0.15);
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 9999px;
        padding: 4px 14px;
        font-size: 0.70rem;
        color: #FEF08A;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .ethical-box {
        background: rgba(15, 23, 42, 0.04);
        border-left: 4px solid #1E3A8A;
        border-radius: 6px;
        padding: 10px 14px;
        margin-bottom: 18px;
        font-size: 0.80rem;
        color: #475569;
        line-height: 1.4;
    }
    
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional UMG
st.markdown("""
<div class="umg-card">
    <div class="umg-title">Universidad Mariano Gálvez de Guatemala</div>
    <div class="umg-faculty">Licenciatura en Psicología Industrial</div>
    <div class="umg-course">Cátedra: Introducción a la Psicología Forense</div>
    <div class="umg-badge">Feria Científica Forense | Método Mauricio Xandró</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ethical-box">
    <strong>⚖️ Finalidad Didáctica y Deontológica:</strong><br>
    Práctica formativa experimental de grafonomía proyectiva sustentada en el método de <em>Mauricio Xandró</em>. 
    <strong>No constituye una evaluación psicométrica estandarizada, peritaje judicial vinculante ni diagnóstico de salud mental, ni sustituye el dictamen de un profesional colegiado.</strong>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# GESTIÓN INTELIGENTE DE CREDENCIALES (API KEYS)
# ==============================================================================
claves_cfg = st.secrets.get("GEMINI_API_KEYS", None)
if not claves_cfg:
    clave_indiv = st.secrets.get("GEMINI_API_KEY", "")
    lista_claves = [clave_indiv] if clave_indiv else []
elif isinstance(claves_cfg, list):
    lista_claves = [k for k in claves_cfg if k]
else:
    lista_claves = [k.strip() for k in str(claves_cfg).split(",") if k.strip()]

if not lista_claves:
    with st.expander("🔑 Credenciales del Sistema"):
        manual_key = st.text_input("Ingrese la clave API de Gemini:", type="password")
        if manual_key:
            lista_claves = [manual_key]

# ==============================================================================
# FUNCIONES AUXILIARES (OPTIMIZACIÓN Y REPORTE)
# ==============================================================================
def optimizar_imagen(img_entrada):
    """Ajusta la resolución de forma óptima para transferencias inmediatas de 2 a 3 segundos."""
    if img_entrada.mode in ("RGBA", "P"):
        img_entrada = img_entrada.convert("RGB")
    img_opt = img_entrada.copy()
    img_opt.thumbnail((1000, 1000), Image.Resampling.LANCZOS)
    return img_opt

def imagen_a_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode()

def formatear_markdown_a_html(texto_md):
    lineas = texto_md.split("\n")
    bloques = []
    for l in lineas:
        l_str = l.strip()
        if not l_str:
            continue
        if l_str.startswith("# "):
            bloques.append(f"<h2 style='color:#091E3A; border-bottom:2px solid #D4AF37; padding-bottom:4px; margin-top:14px; font-size:16px;'>{l_str[2:]}</h2>")
        elif l_str.startswith("### "):
            bloques.append(f"<h4 style='color:#0284C7; margin-top:10px; margin-bottom:4px; font-size:13px;'>{l_str[4:]}</h4>")
        elif l_str.startswith("- ") or l_str.startswith("* "):
            cuerpo = l_str[2:]
            partes = cuerpo.split("**")
            fmt = "".join([f"<strong>{p}</strong>" if i % 2 == 1 else p for i, p in enumerate(partes)])
            bloques.append(f"<div style='margin-left:14px; margin-bottom:4px; font-size:12px;'>• {fmt}</div>")
        else:
            partes = l_str.split("**")
            fmt = "".join([f"<strong>{p}</strong>" if i % 2 == 1 else p for i, p in enumerate(partes)])
            bloques.append(f"<p style='margin:4px 0; font-size:12px;'>{fmt}</p>")
    return "\n".join(bloques)

# ==============================================================================
# VISTA 1: RESULTADO DEL ANÁLISIS GENERADO
# ==============================================================================
if st.session_state.analisis_listo:
    col_reset, col_esp = st.columns([1, 1])
    with col_reset:
        if st.button("🔄 Evaluar a Siguiente Persona", type="secondary", use_container_width=True):
            st.session_state.analisis_listo = False
            st.session_state.resultado_texto = ""
            st.session_state.foto_muestra = None
            st.session_state.turno_id += 1
            st.rerun()

    if st.session_state.foto_muestra is not None:
        st.image(st.session_state.foto_muestra, caption="Muestra analizada en el stand", use_container_width=True)

    # Mostrar directamente el perfil grafopsicológico anclado morfológicamente
    st.markdown(st.session_state.resultado_texto)

    # Generación de la Ficha Descargable / Imprimible en PDF
    st.markdown("---")
    st.markdown("### 🖨️ Ficha Digital Oficial de la Feria")
    st.caption("Descarga la ficha membretada oficial con la fotografía de tus trazos y tu dictamen pericial.")

    img_b64 = imagen_a_base64(st.session_state.foto_muestra) if st.session_state.foto_muestra else ""
    cuerpo_html = formatear_markdown_a_html(st.session_state.resultado_texto)

    ficha_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Ficha Grafopsicológica - UMG</title>
        <style>
            body {{
                font-family: 'Helvetica Neue', Arial, sans-serif;
                margin: 24px;
                color: #1e293b;
                line-height: 1.45;
            }}
            .header {{
                border-bottom: 2px solid #091E3A;
                padding-bottom: 10px;
                text-align: center;
                margin-bottom: 16px;
            }}
            .header h1 {{
                font-size: 16px;
                color: #091E3A;
                margin: 0;
                text-transform: uppercase;
            }}
            .header h2 {{
                font-size: 13px;
                color: #b45309;
                margin: 3px 0;
            }}
            .header h3 {{
                font-size: 11px;
                color: #64748b;
                margin: 0;
            }}
            .photo-box {{
                text-align: center;
                margin: 14px 0;
                background-color: #f8fafc;
                padding: 10px;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
            }}
            .photo-box img {{
                max-width: 250px;
                max-height: 150px;
                border-radius: 6px;
                border: 1px solid #cbd5e1;
            }}
            .disclaimer {{
                margin-top: 22px;
                border: 1px solid #94a3b8;
                background-color: #f1f5f9;
                padding: 10px;
                border-radius: 6px;
                font-size: 10px;
                color: #475569;
                text-align: justify;
            }}
            @media print {{
                body {{ margin: 10px; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Universidad Mariano Gálvez de Guatemala</h1>
            <h2>Licenciatura en Psicología Industrial | Introducción a la Psicología Forense</h2>
            <h3>Laboratorio Pericial de Grafopsicología | Feria Científica Forense</h3>
        </div>

        <div class="photo-box">
            <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">Muestra Manuscrita Evaluada:</div>
            <img src="data:image/jpeg;base64,{img_b64}" alt="Muestra Evaluada">
        </div>

        {cuerpo_html}

        <div class="disclaimer">
            <strong>AVISO LEGAL Y DEONTOLÓGICO:</strong> Esta ficha constituye el resultado de una práctica demostrativa y pedagógica realizada en el marco de la Feria Científica Forense de la Universidad Mariano Gálvez de Guatemala. El análisis se fundamenta en la grafonomía analítica de Mauricio Xandró. <strong>No representa un diagnóstico clínico, peritaje judicial vinculante ni evaluación psicométrica estandarizada, y no sustituye la opinión calificada de un profesional colegiado de la psicología.</strong>
        </div>
        
        <script>
            window.onload = function() {{ window.print(); }}
        </script>
    </body>
    </html>
    """

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        st.download_button(
            label="📥 Descargar Ficha (HTML / PDF)",
            data=ficha_html,
            file_name="Ficha_Grafopsicologica_UMG.html",
            mime="text/html",
            use_container_width=True
        )
    with col_btn2:
        if st.button("🔄 Evaluar a Otra Persona", type="primary", use_container_width=True):
            st.session_state.analisis_listo = False
            st.session_state.resultado_texto = ""
            st.session_state.foto_muestra = None
            st.session_state.turno_id += 1
            st.rerun()

# ==============================================================================
# VISTA 2: CAPTURA DE NUEVA MUESTRA
# ==============================================================================
else:
    st.markdown("### 📋 Registro de la Muestra")
    st.markdown("""
    **Instrucciones para la persona evaluada (en un cuarto de hoja bond lisa):**
    1. Responde en 1 o 2 renglones a la pregunta: *¿Qué es lo que más te motiva en tu vida o carrera?* (o escribe tu lema personal).
    2. Anota abajo tu año de nacimiento.
    3. Estampa tu firma y rúbrica habitual.
    """)

    modo_captura = st.radio(
        "Fuente de entrada:",
        ["📷 Cámara del Dispositivo (Recomendado)", "📁 Cargar Archivo de Imagen"],
        horizontal=True
    )

    muestra_img = None
    if modo_captura == "📷 Cámara del Dispositivo (Recomendado)":
        muestra_img = st.camera_input(
            "Enfoque perpendicular a 90° con buena iluminación:",
            key=f"cam_{st.session_state.turno_id}"
        )
    else:
        muestra_img = st.file_uploader(
            "Seleccione una fotografía clara:",
            type=["jpg", "jpeg", "png"],
            key=f"file_{st.session_state.turno_id}"
        )

    if muestra_img is not None:
        img_original = Image.open(muestra_img)
        img_pil = optimizar_imagen(img_original)
        st.image(img_pil, caption="Muestra lista para evaluación pericial", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ Descubrir Mi Perfil Grafopsicológico", type="primary", use_container_width=True):
            if not lista_claves:
                st.error("No se detectó ninguna clave de API configurada en Secrets.")
            else:
                with st.spinner("Analizando morfología gráfica bajo el método Mauricio Xandró..."):
                    claves_intento = list(lista_claves)
                    random.shuffle(claves_intento)
                    
                    respuesta_exitosa = None
                    ultimo_error = None
                    
                    # PROMPT ANTI-HORÓSCOPO CON ANCLAJE MORFOSCÓPICO ESTRICTO
                    prompt_xandro = """
                    Actúa como Perito en Grafopsicología Forense de la Universidad Mariano Gálvez de Guatemala.
                    Evalúa la muestra manuscrita adjunta bajo la doctrina estricta de Mauricio Xandró y el simbolismo espacial de Max Pulver.

                    REGLA ESTRICTA ANTI-HORÓSCOPO (BLINDAJE CONTRA EL EFECTO FORER):
                    QUEDA ROTUNDAMENTE PROHIBIDO emitir descripciones genéricas, adulaciones o frases ambiguas que apliquen a cualquiera.
                    CADA AFIRMACIÓN PSICOLÓGICA DEBE ESTAR VINCULADA OBLIGATORIAMENTE A UN SIGNO FÍSICO VISIBLE EN LA FOTO.
                    Fórmula obligatoria: [Signo visible medible] ➔ [Mecanismo psicológico] ➔ [Conducta real en el día a día].
                    Sé directo, conciso, contundente y pericialmente exacto.

                    Estructura obligatoria de respuesta:

                    # 🌟 PERFIL CONDUCTUAL Y MORFOLÓGICO
                    *(Laboratorio de Grafopsicología Forense UMG | Método Mauricio Xandró)*

                    ### 🧭 Eje Temperamental Dominante
                    (2 a 3 líneas donde definas su temperamento central vinculando el tamaño relativo de la letra, la presión y la velocidad del trazo con su ritmo de acción).

                    ### 🟢 Tus "Luces" (Fortalezas con Evidencia Gráfica)
                    - **[Fortaleza 1]:** Comienza citando el signo exacto (ej. presión firme del trazo, barras de la 't' adelantadas, renglón ascendente, óvalos regulares) y explica la conducta concreta observable que genera.
                    - **[Fortaleza 2]:** Comienza citando el signo exacto (ej. enlaces fluidos, hampas verticales y desarrolladas, márgenes ordenados) y explica la fortaleza conductual.
                    - **[Fortaleza 3]:** Comienza citando el signo exacto (ej. simplificación caligráfica, coligamento continuo) y explica la fortaleza conductual.

                    ### 🟡 Tus "Sombras" (Retos Reales y Puntos Ciegos)
                    - **[Punto Ciego 1]:** Comienza citando el rasgo morfológico que lo delata (ej. coligamento en ángulo, base rígida, óvalos con nudo cerrado, rúbrica envolvente o tachante) y explica la dificultad real (rigidez de criterio, hermetismo, desconfianza o susceptibilidad).
                    - **[Punto Ciego 2]:** Comienza citando el signo gráfico y explica la conducta a vigilar bajo presión.

                    ### 👥 Tu "Yo Social" (La Frase y Cifras Escritas)
                    Evalúa la legibilidad, distancia entre palabras y dirección de línea en la frase y año. Explica cómo se comporta ante compañeros, docentes y figuras de autoridad en público.

                    ### 🔒 Tu "Yo Íntimo" (Tu Firma y Rúbrica)
                    Confronta la firma con el texto: compara tamaño relativo, legibilidad y presencia de rúbrica. Explica su filtro para dar confianza, su autopercepción profunda y sus defensas cuando se siente vulnerable.

                    ### 💡 Orientación de Crecimiento Conductual
                    Un señalamiento formativo y constructivo sobre qué hábito actitudinal debe trabajar según las tensiones o frenos detectados en su trazo.
                    """

                    for key_actual in claves_intento:
                        try:
                            genai.configure(api_key=key_actual)
                            
                            # Prioridad a Flash Lite (500 consultas/día y 15/minuto)
                            modelos_disponibles = []
                            try:
                                for m in genai.list_models():
                                    if "generateContent" in m.supported_generation_methods:
                                        modelos_disponibles.append(m.name)
                            except Exception:
                                pass
                            
                            modelo_final = None
                            prioridades = ["3.5-flash-lite", "3.1-flash-lite", "flash-lite", "2.5-flash-lite"]
                            for p in prioridades:
                                for m in modelos_disponibles:
                                    if p in m.lower():
                                        modelo_final = m
                                        break
                                if modelo_final:
                                    break
                            
                            if not modelo_final:
                                modelo_final = "gemini-3.5-flash-lite"
                            
                            model = genai.GenerativeModel(modelo_final)
                            respuesta_exitosa = model.generate_content([prompt_xandro, img_pil])
                            break
                            
                        except Exception as e:
                            ultimo_error = e
                            if "429" in str(e):
                                continue
                            else:
                                break
                    
                    if respuesta_exitosa:
                        st.session_state.resultado_texto = respuesta_exitosa.text
                        st.session_state.foto_muestra = img_pil
                        st.session_state.analisis_listo = True
                        st.rerun()
                    else:
                        st.error(f"Aviso técnico al procesar la muestra: {ultimo_error}")
