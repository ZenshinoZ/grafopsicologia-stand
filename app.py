import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64
import io
import random

# Configuración institucional UMG
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
    Práctica formativa experimental de grafonomía proyectiva basada en <em>Mauricio Xandró</em>. 
    <strong>No constituye una evaluación psicométrica clínica ni diagnóstico de salud mental, ni sustituye el dictamen de un profesional colegiado.</strong>
</div>
""", unsafe_allow_html=True)

# Gestión inteligente de API Keys (soporta clave única o lista de claves)
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

# Optimización rápida de imagen
def optimizar_imagen(img_entrada):
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
            bloques.append(f"<h2 style='color:#091E3A; border-bottom:2px solid #D4AF37; padding-bottom:4px; margin-top:12px; font-size:15px;'>{l_str[2:]}</h2>")
        elif l_str.startswith("### "):
            bloques.append(f"<h4 style='color:#0284C7; margin-top:8px; margin-bottom:3px; font-size:13px;'>{l_str[4:]}</h4>")
        elif l_str.startswith("- ") or l_str.startswith("* "):
            cuerpo = l_str[2:]
            partes = cuerpo.split("**")
            fmt = "".join([f"<strong>{p}</strong>" if i % 2 == 1 else p for i, p in enumerate(partes)])
            bloques.append(f"<div style='margin-left:12px; margin-bottom:3px; font-size:11.5px;'>• {fmt}</div>")
        else:
            partes = l_str.split("**")
            fmt = "".join([f"<strong>{p}</strong>" if i % 2 == 1 else p for i, p in enumerate(partes)])
            bloques.append(f"<p style='margin:3px 0; font-size:11.5px;'>{fmt}</p>")
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
    
    partes = st.session_state.resultado_texto.split("---EXPEDIENTE_TECNICO---")
    perfil_estudiante = partes[0].strip()
    expediente_pericial = partes[1].strip() if len(partes) > 1 else ""

    # Nivel 1: Para el Estudiante (Visible)
    st.markdown(perfil_estudiante)

    # Nivel 2: Para la Docente (Acordeón)
    if expediente_pericial:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("🔬 Ver Expediente Pericial y Morfometría (Exclusivo Docente / Jurado)", expanded=False):
            st.markdown(expediente_pericial)

    # Ficha Descargable Oficial
    st.markdown("---")
    st.markdown("### 🖨️ Ficha Digital Oficial")
    
    img_b64 = imagen_a_base64(st.session_state.foto_muestra) if st.session_state.foto_muestra else ""
    cuerpo_html = formatear_markdown_a_html(perfil_estudiante)

    ficha_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Ficha Grafopsicológica - UMG</title>
        <style>
            body {{ font-family: 'Helvetica Neue', Arial, sans-serif; margin: 20px; color: #1e293b; line-height: 1.4; }}
            .header {{ border-bottom: 2px solid #091E3A; padding-bottom: 8px; text-align: center; margin-bottom: 14px; }}
            .header h1 {{ font-size: 15px; color: #091E3A; margin: 0; text-transform: uppercase; }}
            .header h2 {{ font-size: 12px; color: #b45309; margin: 2px 0; }}
            .photo-box {{ text-align: center; margin: 10px 0; background-color: #f8fafc; padding: 8px; border-radius: 6px; border: 1px solid #e2e8f0; }}
            .photo-box img {{ max-width: 240px; max-height: 140px; border-radius: 4px; border: 1px solid #cbd5e1; }}
            .disclaimer {{ margin-top: 18px; border: 1px solid #94a3b8; background-color: #f1f5f9; padding: 8px; border-radius: 6px; font-size: 10px; color: #475569; text-align: justify; }}
            @media print {{ body {{ margin: 5px; }} }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Universidad Mariano Gálvez de Guatemala</h1>
            <h2>Licenciatura en Psicología Industrial | Psicología Forense</h2>
        </div>
        <div class="photo-box">
            <div style="font-size: 10px; color: #64748b; margin-bottom: 4px;">Muestra Manuscrita Evaluada:</div>
            <img src="data:image/jpeg;base64,{img_b64}" alt="Muestra">
        </div>
        {cuerpo_html}
        <div class="disclaimer">
            <strong>AVISO DIDÁCTICO:</strong> Ficha experimental generada en la Feria Forense UMG. Análisis basado en Mauricio Xandró. No representa diagnóstico clínico ni peritaje judicial.
        </div>
        <script>window.onload = function() {{ window.print(); }}</script>
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
    st.caption("Consigna: En un cuarto de hoja blanca, escribe una palabra, tu año de nacimiento y tu firma habitual.")

    modo_captura = st.radio(
        "Fuente de entrada:",
        ["📷 Cámara del Dispositivo (Recomendado)", "📁 Cargar Archivo de Imagen"],
        horizontal=True
    )

    muestra_img = None
    if modo_captura == "📷 Cámara del Dispositivo (Recomendado)":
        muestra_img = st.camera_input(
            "Enfoque perpendicular con buena luz:",
            key=f"cam_{st.session_state.turno_id}"
        )
    else:
        muestra_img = st.file_uploader(
            "Seleccione la imagen:",
            type=["jpg", "jpeg", "png"],
            key=f"file_{st.session_state.turno_id}"
        )

    if muestra_img is not None:
        img_original = Image.open(muestra_img)
        img_pil = optimizar_imagen(img_original)
        st.image(img_pil, caption="Muestra lista para evaluación", use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✨ Descubrir Mi Perfil de Personalidad", type="primary", use_container_width=True):
            if not lista_claves:
                st.error("No se detectó ninguna clave de API configurada.")
            else:
                with st.spinner("Analizando tus trazos bajo el método Xandró (Gemini 3.5 Flash Lite)..."):
                    # Barajar claves para balancear tráfico si hay varias
                    claves_intento = list(lista_claves)
                    random.shuffle(claves_intento)
                    
                    respuesta_exitosa = None
                    ultimo_error = None
                    
                    prompt_xandro = """
                    Actúa como Especialista en Grafopsicología Forense de la Universidad Mariano Gálvez de Guatemala.
                    Analiza la muestra manuscrita adjunta (palabra, año y firma/rúbrica) bajo la metodología clásica de Mauricio Xandró.

                    IMPORTANTE: Sé directo, conciso y puntual. Evita párrafos largos; usa viñetas breves de 1 o 2 líneas.
                    Divide tu respuesta obligatoriamente con este separador exacto:
                    ---EXPEDIENTE_TECNICO---

                    SECCIÓN 1 (PERFIL FORMATIVO PARA EL ESTUDIANTE):
                    En segunda persona ("Tú"). Claro, empático, honesto y sustentado en los trazos visibles:
                    
                    # 🌟 TU PERFIL CONDUCTUAL Y DE PERSONALIDAD
                    *(Basado en la morfología de tu escritura | Escuela de Mauricio Xandró)*

                    ### 🧭 En Pocas Palabras
                    (2 líneas sobre tu temperamento esencial y ritmo de acción).

                    ### 🟢 Tus "Luces" (Fortalezas Destacadas)
                    - **Fortaleza 1:** (1 línea sobre el rasgo y su origen morfológico).
                    - **Fortaleza 2:** (1 línea sobre el rasgo y su origen morfológico).
                    - **Fortaleza 3:** (1 línea sobre el rasgo y su origen morfológico).

                    ### 🟡 Tus "Sombras" (Puntos Ciegos y Retos)
                    - **Reto 1:** (1 línea constructiva sobre un hábito a vigilar).
                    - **Reto 2:** (1 línea constructiva sobre un hábito a vigilar).

                    ### 👥 En lo Social y Académico (El "Yo Social" - Tu Palabra y Números)
                    (3 líneas sobre tu proyección ante compañeros y docentes).

                    ### 🔒 En tu Esfera Íntima (El "Yo Íntimo" - Tu Firma)
                    (3 líneas sobre tu mundo privado y defensas bajo presión).

                    ### 💡 Consejo de Crecimiento
                    (1 frase formativa para tu éxito estudiantil y profesional).

                    ---EXPEDIENTE_TECNICO---

                    SECCIÓN 2 (EXPEDIENTE PERICIAL PARA LA DOCENTE Y JURADO):
                    # 📑 DICTAMEN GRAFONÓMICO PERICIAL
                    **Cátedra:** Introducción a la Psicología Forense (UMG) | **Método:** Mauricio Xandró

                    ### I. Matriz de los 8 Géneros Gráficos
                    - **Tamaño:** (mm estimados del cuerpo medio y significado).
                    - **Forma:** (Curva / ángulo / coligamento y significado).
                    - **Inclinación:** (Grados del eje rector y apertura relacional).
                    - **Dirección:** (Trayectoria del renglón y estabilidad anímica).
                    - **Presión:** (Calibre/firmeza y potencial energético).
                    - **Velocidad:** (Ritmo gráfico y agilidad cognitiva).
                    - **Continuidad:** (Tipo de enlace y estilo de pensamiento).
                    - **Orden:** (Claridad espacial y jerarquía mental).

                    ### II. Dialéctica "Yo Social" vs. "Yo Íntimo"
                    (Confrontación de legibilidad y proporciones entre palabra/cifras y la rúbrica).

                    ### III. Conclusión Pericial Sintética
                    (Juicio técnico breve sobre el balance y coherencia del trazo).
                    """

                    for key_actual in claves_intento:
                        try:
                            genai.configure(api_key=key_actual)
                            
                            # Detección de modelos con prioridad absoluta a 3.5 Flash Lite y 3.1 Flash Lite (500 RPD / 15 RPM)
                            modelos_disponibles = []
                            try:
                                for m in genai.list_models():
                                    if "generateContent" in m.supported_generation_methods:
                                        modelos_disponibles.append(m.name)
                            except Exception:
                                pass
                            
                            modelo_final = None
                            # Prioridades específicas de alta cuota (500 RPD)
                            prioridades = ["3.5-flash-lite", "3.1-flash-lite", "flash-lite", "2.5-flash-lite"]
                            for p in prioridades:
                                for m in modelos_disponibles:
                                    if p in m.lower():
                                        modelo_final = m
                                        break
                                if modelo_final:
                                    break
                            
                            # Si no lo encuentra por coincidencia exacta de lista, usa el identificador directo
                            if not modelo_final:
                                modelo_final = "gemini-3.5-flash-lite"
                            
                            model = genai.GenerativeModel(modelo_final)
                            respuesta_exitosa = model.generate_content([prompt_xandro, img_pil])
                            break # Éxito: salir del bucle
                            
                        except Exception as e:
                            ultimo_error = e
                            if "429" in str(e):
                                continue # Si una clave topa su minuto, prueba inmediatamente la siguiente
                            else:
                                break
                    
                    if respuesta_exitosa:
                        st.session_state.resultado_texto = respuesta_exitosa.text
                        st.session_state.foto_muestra = img_pil
                        st.session_state.analisis_listo = True
                        st.rerun()
                    else:
                        st.error(f"Aviso técnico al procesar la muestra: {ultimo_error}")
