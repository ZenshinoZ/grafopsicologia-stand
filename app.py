import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64
import io

# Configuración institucional UMG
st.set_page_config(
    page_title="UMG | Laboratorio Pericial Grafopsicológico",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicialización de estado de sesión
if "analisis_listo" not in st.session_state:
    st.session_state.analisis_listo = False
    st.session_state.resultado_texto = ""
    st.session_state.foto_muestra = None
    st.session_state.turno_id = 0

# Estilos visuales institucionales
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
        padding: 22px 18px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
    }
    
    .umg-title {
        font-family: 'Cinzel', serif;
        font-size: 1.15rem;
        letter-spacing: 2px;
        color: #F8FAFC;
        margin: 0;
        text-transform: uppercase;
        font-weight: 700;
    }
    
    .umg-faculty {
        font-size: 0.95rem;
        color: #D4AF37;
        margin: 6px 0 2px 0;
        font-weight: 700;
        letter-spacing: 0.6px;
    }
    
    .umg-course {
        font-size: 0.85rem;
        color: #93C5FD;
        margin-bottom: 10px;
        font-weight: 500;
    }
    
    .umg-badge {
        display: inline-block;
        background: rgba(212, 175, 55, 0.15);
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 9999px;
        padding: 4px 16px;
        font-size: 0.72rem;
        color: #FEF08A;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .ethical-box {
        background: rgba(15, 23, 42, 0.04);
        border-left: 4px solid #1E3A8A;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 20px;
        font-size: 0.82rem;
        color: #475569;
        line-height: 1.45;
    }
    
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown("""
<div class="umg-card">
    <div class="umg-title">Universidad Mariano Gálvez de Guatemala</div>
    <div class="umg-faculty">Licenciatura en Psicología Industrial</div>
    <div class="umg-course">Cátedra: Introducción a la Psicología Forense</div>
    <div class="umg-badge">Laboratorio Pericial de Grafopsicología | Método Mauricio Xandró</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ethical-box">
    <strong>⚖️ Finalidad Didáctica y Deontológica:</strong><br>
    Módulo experimental y pedagógico desarrollado para la Feria Científica Forense. 
    Analiza la proyección grafonómica según los criterios clásicos de <em>Mauricio Xandró</em>. 
    <strong>No constituye una evaluación psicométrica clínica, peritaje judicial vinculante ni diagnóstico de salud mental, ni sustituye el dictamen de un profesional colegiado.</strong>
</div>
""", unsafe_allow_html=True)

# Clave API
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    with st.expander("🔑 Credenciales del Sistema"):
        api_key = st.text_input("Ingrese la clave API de Gemini:", type="password")

# Funciones auxiliares para compresión y reporte
def optimizar_imagen(img_entrada):
    """Convierte a RGB y ajusta tamaño a un límite pericial óptimo para procesar en 3-5 segundos."""
    if img_entrada.mode in ("RGBA", "P"):
        img_entrada = img_entrada.convert("RGB")
    img_opt = img_entrada.copy()
    img_opt.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
    return img_opt

def imagen_a_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode()

def formatear_markdown_a_html(texto_md):
    """Convierte formato de texto en bloques HTML estructurados para el informe impreso."""
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
    
    # Botón superior para atender de inmediato a la siguiente persona
    col_reset, col_esp = st.columns([1, 1])
    with col_reset:
        if st.button("🔄 Evaluar a Siguiente Persona", type="secondary", use_container_width=True):
            st.session_state.analisis_listo = False
            st.session_state.resultado_texto = ""
            st.session_state.foto_muestra = None
            st.session_state.turno_id += 1
            st.rerun()

    # Muestra evaluada
    if st.session_state.foto_muestra is not None:
        st.image(st.session_state.foto_muestra, caption="Muestra analizada en el stand", use_container_width=True)
    
    # Desglose de los dos niveles
    partes = st.session_state.resultado_texto.split("---EXPEDIENTE_TECNICO---")
    perfil_estudiante = partes[0].strip()
    expediente_pericial = partes[1].strip() if len(partes) > 1 else ""

    # Nivel 1: Para el Estudiante (Visible y Claro)
    st.markdown(perfil_estudiante)

    # Nivel 2: Para la Docente / Jurado (Acordeón Pericial Desplegable)
    if expediente_pericial:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔬 Ver Expediente Pericial y Morfometría (Exclusivo Docente / Jurado)", expanded=False):
            st.markdown(expediente_pericial)

    # Generación de la Ficha Descargable / Imprimible
    st.markdown("---")
    st.markdown("### 🖨️ Ficha Digital de la Feria Forense")
    st.caption("Descarga la ficha membretada oficial con la fotografía de tus trazos y tu perfil pericial.")

    img_b64 = imagen_a_base64(st.session_state.foto_muestra) if st.session_state.foto_muestra else ""
    cuerpo_html = formatear_markdown_a_html(perfil_estudiante)

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
                max-width: 260px;
                max-height: 160px;
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
            <h3>Laboratorio Experimental de Grafopsicología | Feria Científica Forense</h3>
        </div>

        <div class="photo-box">
            <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">Muestra Manuscrita Evaluada:</div>
            <img src="data:image/jpeg;base64,{img_b64}" alt="Muestra Evaluada">
        </div>

        {cuerpo_html}

        <div class="disclaimer">
            <strong>AVISO LEGAL Y DEONTOLÓGICO:</strong> Esta ficha constituye el resultado de una práctica demostrativa y pedagógica realizada en el marco de la Feria Científica Forense de la Universidad Mariano Gálvez de Guatemala. El análisis se fundamenta en la grafonomía analítica de Mauricio Xandró. <strong>No representa un diagnóstico clínico, peritaje judicial vinculante ni evaluación psicométrica estandarizada, y no sustituye la opinión calificada de un profesional de la psicología.</strong>
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
# VISTA 2: CAPTURA PARA NUEVO ESTUDIANTE
# ==============================================================================
else:
    st.markdown("### 📋 Registro de la Muestra")
    st.caption("Consigna: En un cuarto de hoja blanca lisa, escribe una palabra, tu año de nacimiento y tu firma habitual.")

    modo_captura = st.radio(
        "Fuente de entrada:",
        ["📷 Cámara del Dispositivo (Recomendado)", "📁 Cargar Archivo de Imagen"],
        horizontal=True
    )

    muestra_img = None
    if modo_captura == "📷 Cámara del Dispositivo (Recomendado)":
        muestra_img = st.camera_input(
            "Enfoque perpendicular a la muestra con luz homogénea:",
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
        
        # Optimización inmediata en memoria para velocidad de procesamiento
        img_pil = optimizar_imagen(img_original)
        st.image(img_pil, caption="Muestra optimizada para inspección", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ Descubrir Mi Perfil de Personalidad", type="primary", use_container_width=True):
            if not api_key:
                st.error("No se detectó la clave de API.")
            else:
                with st.spinner("Analizando tus trazos, midiendo morfometría y construyendo tu perfil..."):
                    try:
                        genai.configure(api_key=api_key)
                        
                        # Detección y selección de modelos Flash
                        modelos_disponibles = []
                        try:
                            for m in genai.list_models():
                                if "generateContent" in m.supported_generation_methods:
                                    modelos_disponibles.append(m.name)
                        except Exception:
                            pass
                        
                        modelo_final = None
                        prioridades = ["flash-latest", "2.5-flash", "2.0-flash", "flash"]
                        for p in prioridades:
                            for m in modelos_disponibles:
                                if p in m.lower() and "pro" not in m.lower():
                                    modelo_final = m
                                    break
                            if modelo_final:
                                break
                        
                        if not modelo_final:
                            modelo_final = "gemini-flash-latest"

                        model = genai.GenerativeModel(modelo_final)
                        
                        prompt_xandro = """
                        Actúa como un Especialista en Grafopsicología Forense de la Universidad Mariano Gálvez de Guatemala.
                        Analiza la muestra manuscrita adjunta (palabra, año y firma/rúbrica) bajo la metodología de Mauricio Xandró.

                        Divide tu respuesta obligatoriamente en DOS SECCIONES con este separador exacto:
                        ---EXPEDIENTE_TECNICO---

                        SECCIÓN 1 (PERFIL FORMATIVO PARA EL ESTUDIANTE):
                        En segunda persona ("Tú"), lenguaje accesible, empático y honesto. Sin horóscopo: fundamentado en los trazos visibles.
                        
                        # 🌟 TU PERFIL CONDUCTUAL Y DE PERSONALIDAD
                        *(Basado en la morfología de tu escritura y firma | Escuela de Mauricio Xandró)*

                        ### 🧭 En Pocas Palabras
                        Resumen de 3 a 4 líneas de su ritmo, temple y forma de procesar el entorno.

                        ### 🟢 Tus "Luces" (Fortalezas Destacadas)
                        Menciona 3 fortalezas conductuales concretas que revelan sus trazos (ej. capacidad de concentración, asertividad, agilidad de ideas, perseverancia).

                        ### 🟡 Tus "Sombras" (Puntos Ciegos y Retos Personales)
                        Menciona 2 o 3 áreas donde debe tener cuidado de forma constructiva (ej. tendencia a reservarse excesivamente, terquedad, autoexigencia desmedida, filtro estricto para confiar).

                        ### 👥 En lo Social y Académico (El "Yo Social" - Tu Palabra y Números)
                        Cómo se proyecta ante compañeros, profesores y grupos según su palabra escrita y cifras.

                        ### 🔒 En tu Esfera Íntima (El "Yo Íntimo" - Tu Firma)
                        Qué revela su firma sobre su mundo privado, sus defensas y su temple bajo presión.

                        ### 💡 Consejo de Crecimiento Personal
                        Un consejo constructivo para su carrera y desarrollo estudiantil.

                        ---EXPEDIENTE_TECNICO---

                        SECCIÓN 2 (EXPEDIENTE PERICIAL PARA LA LICENCIADA Y JURADO):
                        # 📑 DICTAMEN GRAFONÓMICO PERICIAL
                        **Cátedra:** Introducción a la Psicología Forense (UMG)  
                        **Metodología:** Sistema Morfoscópico de Mauricio Xandró  

                        ### I. Matriz de los 8 Géneros Gráficos
                        - Tamaño (mm de óvalos vs prolongaciones).
                        - Forma (curvas vs ángulos y coligamento).
                        - Inclinación (grados estimados y eje rector).
                        - Dirección (línea base y oscilaciones).
                        - Presión (tensión del surco y energía).
                        - Velocidad (ritmo y resolución).
                        - Continuidad (enlaces interletra).
                        - Orden (claridad y distribución).

                        ### II. Dialéctica "Yo Social" vs. "Yo Íntimo"
                        Confrontación de legibilidad y proporciones entre el texto/números y la rúbrica.

                        ### III. Conclusión Pericial Sintética
                        Síntesis final del temperamento y balance neurovegetativo del trazo.
                        """
                        
                        response = model.generate_content([prompt_xandro, img_pil])
                        
                        # Persistencia en sesión
                        st.session_state.resultado_texto = response.text
                        st.session_state.foto_muestra = img_pil
                        st.session_state.analisis_listo = True
                        st.rerun()
                                
                    except Exception as e:
                        st.error(f"Aviso técnico al procesar la muestra: {e}")
