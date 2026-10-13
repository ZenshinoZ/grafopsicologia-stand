import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración institucional UMG
st.set_page_config(
    page_title="UMG | Perfil Grafopsicológico Forense",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estética visual moderna, académica y accesible
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Banner Institucional UMG */
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
    
    /* Banner Deontológico */
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
    
    /* Botón Principal */
    .stButton>button {
        background: linear-gradient(135deg, #0284C7 0%, #1E3A8A 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(2, 132, 199, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown("""
<div class="umg-card">
    <div class="umg-title">Universidad Mariano Gálvez de Guatemala</div>
    <div class="umg-faculty">Licenciatura en Psicología Industrial</div>
    <div class="umg-course">Cátedra: Introducción a la Psicología Forense</div>
    <div class="umg-badge">Laboratorio Pericial de Grafopsicología | Método Xandró</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ethical-box">
    <strong>⚖️ Finalidad Académica y Formativa:</strong><br>
    Este demostrador proyectivo explora la relación entre la motricidad gráfica y las tendencias de personalidad según el método de <em>Mauricio Xandró</em>. Presenta un perfil reflexivo de autoconocimiento respaldado por un expediente pericial morfoscópico.
</div>
""", unsafe_allow_html=True)

# Clave API
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    with st.expander("🔑 Credenciales"):
        api_key = st.text_input("Ingrese su Gemini API Key:", type="password")

# Captura
st.markdown("### 📋 Registro de la Muestra")
st.caption("Consigna: En papel blanco liso, escribe tu nombre completo y coloca tu firma habitual.")

modo_captura = st.radio(
    "Fuente de entrada:",
    ["📷 Cámara del Dispositivo (Recomendado)", "📁 Cargar Imagen"],
    horizontal=True
)

muestra_img = None
if modo_captura == "📷 Cámara del Dispositivo (Recomendado)":
    muestra_img = st.camera_input("Enfoque la muestra de forma perpendicular y con buena luz:")
else:
    muestra_img = st.file_uploader("Seleccione una fotografía clara:", type=["jpg", "jpeg", "png"])

if muestra_img is not None:
    img_pil = Image.open(muestra_img)
    st.image(img_pil, caption="Muestra documental ingresada", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ Descubrir Mi Perfil de Personalidad", use_container_width=True):
        if not api_key:
            st.error("No se detectó la clave de API.")
        else:
            with st.spinner("Analizando tus trazos, midiendo morfometría y construyendo tu perfil..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # Detección y selección de modelo Flash eficiente
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
                    
                    prompt_xandro_dos_niveles = """
                    Actúa como un Especialista en Grafopsicología Forense de la Universidad Mariano Gálvez de Guatemala.
                    Analiza la imagen adjunta (nombre y firma/rúbrica) bajo la metodología clásica de Mauricio Xandró.

                    IMPORTANTE: Debes dividir tu respuesta exactamente en DOS SECCIONES separadas por el delimitador:
                    ---EXPEDIENTE_TECNICO---

                    ======================================================================
                    SECCIÓN 1 (ANTES DEL DELIMITADOR): PERFIL PARA EL ESTUDIANTE / VISITANTE
                    ======================================================================
                    Dirígete a la persona en segunda persona ("Tú"). El lenguaje debe ser fresco, empático, claro y atrapante para estudiantes de primer año universitario, pero con total rigor en las observaciones. Evita el horóscopo: fundamenta cada rasgo en lo que hace su mano.
                    
                    Estructura obligatoria:
                    # 🌟 TU PERFIL CONDUCTUAL Y DE PERSONALIDAD
                    *(Basado en la morfología de tu escritura y firma | Escuela de Mauricio Xandró)*

                    ### 🧭 En Pocas Palabras
                    Un resumen de 3 a 4 líneas que capture su estilo de ser esencial (cómo procesa el mundo, su ritmo y su temple).

                    ### 🟢 Tus "Luces" (Fortalezas Destacadas)
                    Menciona 3 fortalezas conductuales concretas que revelan sus trazos (ejemplo: capacidad de concentración por el tamaño controlado, asertividad por la presión firme, agilidad de ideas por la velocidad, etc.).

                    ### 🟡 Tus "Sombras" (Puntos Ciegos y Retos Personales)
                    Menciona 2 o 3 áreas donde debe tener cuidado de forma constructiva (ejemplo: tendencia a guardarse las cosas por óvalos cerrados, terquedad al debatir por trazos angulosos, dificultad para pedir ayuda por una firma muy aislada o rúbrica secante).

                    ### 👥 En lo Social y Académico (El "Yo Social" - Tu Nombre)
                    Explica en 2 párrafos sencillos cómo se muestra ante sus compañeros, maestros y en grupos según cómo escribió su nombre.

                    ### 🔒 En tu Esfera Íntima (El "Yo Íntimo" - Tu Firma)
                    Explica en 2 párrafos qué revela su firma sobre su verdadero mundo interior, cómo actúa bajo mucha presión y qué tan fácil o difícil es que alguien entre en su círculo de confianza.

                    ### 💡 Consejo de Crecimiento Personal
                    Un consejo formativo práctico para su vida profesional y estudiantil.

                    ---EXPEDIENTE_TECNICO---

                    ======================================================================
                    SECCIÓN 2 (DESPUÉS DEL DELIMITADOR): EXPEDIENTE TÉCNICO PERICIAL (PARA LA LICENCIADA)
                    ======================================================================
                    Lenguaje pericial formal, técnico, forense y detallado:
                    
                    # 📑 DICTAMEN GRAFONÓMICO PERICIAL
                    **Cátedra:** Introducción a la Psicología Forense (UMG)  
                    **Metodología:** Sistema Morfoscópico de Mauricio Xandró  

                    ### I. Matriz de los 8 Géneros Gráficos
                    - **Tamaño:** Medición estimada del cuerpo central vs. mayúsculas y significado proyectivo.
                    - **Forma:** Curvas vs. ángulos y significación de ductilidad/firmeza.
                    - **Inclinación:** Ángulo estimado del eje rector y apertura al entorno.
                    - **Dirección:** Línea base y estabilidad afectiva/volitiva.
                    - **Presión:** Tensión y calibre del surco, reserva energética.
                    - **Velocidad:** Ritmo gráfico y velocidad de asimilación conceptual.
                    - **Continuidad:** Tipo de coligamento y estilo de razonamiento (analítico vs intuitivo).
                    - **Orden:** Distribución de blancos y disciplina cognitiva.

                    ### II. Dialéctica "Yo Social" vs. "Yo Íntimo"
                    Confrontación de legibilidad y proporciones entre el texto (máscara pública) y la firma/rúbrica (autoimagen profunda y mecanismos de defensa inconscientes).

                    ### III. Conclusión Pericial Sintética
                    Juicio técnico sobre la coherencia psíquica y temperamento dominante.
                    """
                    
                    response = model.generate_content([prompt_xandro_dos_niveles, img_pil])
                    
                    # Separación en los dos niveles
                    partes = response.text.split("---EXPEDIENTE_TECNICO---")
                    perfil_estudiante = partes[0].strip()
                    expediente_pericial = partes[1].strip() if len(partes) > 1 else ""
                    
                    st.success("✅ ¡Tu análisis ha sido generado con éxito!")
                    
                    # Nivel 1: Para el Estudiante (Visible y Amigable)
                    st.markdown(perfil_estudiante)
                    
                    # Nivel 2: Para la Licenciada / Jurado (Acordeón Pericial Desplegable)
                    if expediente_pericial:
                        st.markdown("<br>", unsafe_allow_html=True)
                        with st.expander("🔬 Ver Expediente Pericial y Morfometría (Exclusivo Docente / Jurado)", expanded=False):
                            st.markdown(expediente_pericial)
                            
                except Exception as e:
                    st.error(f"Aviso técnico al procesar la muestra: {e}")
