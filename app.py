import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de página con título formal
st.set_page_config(
    page_title="UMG | Sistema Pericial Grafopsicológico",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS de nivel pericial / institucional
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Cabecera Institucional */
    .umg-header {
        background: linear-gradient(135deg, #0A192F 0%, #172A45 50%, #0F172A 100%);
        border: 1px solid #1E3A8A;
        border-radius: 12px;
        padding: 24px;
        color: #F8FAFC;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(2, 12, 27, 0.5);
    }
    
    .umg-title {
        font-family: 'Cinzel', serif;
        font-size: 1.15rem;
        letter-spacing: 2px;
        color: #93C5FD;
        margin: 0;
        text-transform: uppercase;
        font-weight: 700;
    }
    
    .umg-faculty {
        font-size: 0.95rem;
        color: #E2E8F0;
        margin: 6px 0 2px 0;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .umg-course {
        font-size: 0.85rem;
        color: #38BDF8;
        margin-bottom: 12px;
        font-weight: 500;
    }
    
    .umg-project {
        display: inline-block;
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 9999px;
        padding: 4px 16px;
        font-size: 0.78rem;
        color: #BAE6FD;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Panel Deontológico / Ético */
    .ethical-card {
        background: #F8FAFC;
        border-left: 5px solid #1E3A8A;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 24px;
        font-size: 0.83rem;
        color: #334155;
        line-height: 1.5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Botón de Acción Principal */
    .stButton>button {
        background: linear-gradient(135deg, #1E3A8A 0%, #0284C7 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 14px 28px !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.5px !important;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(2, 132, 199, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown("""
<div class="umg-header">
    <div class="umg-title">Universidad Mariano Gálvez de Guatemala</div>
    <div class="umg-faculty">Licenciatura en Psicología Industrial</div>
    <div class="umg-course">Cátedra: Introducción a la Psicología Forense</div>
    <div class="umg-project">Laboratorio Pericial de Grafopsicología Científica | Método Mauricio Xandró</div>
</div>
""", unsafe_allow_html=True)

# Blindaje Deontológico visible para docentes y jurados
st.markdown("""
<div class="ethical-card">
    <strong>⚖️ Marco Epistemológico y Deontológico:</strong><br>
    Este sistema constituye una herramienta experimental de análisis proyectivo-morfoscópico fundamentada en la grafonomía estandarizada de <em>Mauricio Xandró</em>. 
    Se apega al principio de objetividad grafológica: cada indicador actitudinal se deriva de variables medibles (presión, inclinación, continuidad, coligamento). 
    No reemplaza un peritaje caligráfico forense de autenticidad documental ni una batería psicométrica estandarizada.
</div>
""", unsafe_allow_html=True)

# Gestión de Credenciales
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    with st.expander("🔑 Credencial de Conexión"):
        api_key = st.text_input("Ingrese la clave API de Gemini:", type="password")

# Interfaz de Entrada
st.markdown("### 📄 Registro y Captura de la Muestra")
st.caption("Consigna para la muestra: Nombre completo, fecha y firma/rúbrica en papel bond blanco liso sin renglones.")

tipo_captura = st.radio(
    "Modalidad de ingreso:",
    ["📷 Captura en directo con la cámara", "📁 Cargar archivo de imagen"],
    horizontal=True
)

muestra_img = None
if tipo_captura == "📷 Captura en directo con la cámara":
    muestra_img = st.camera_input("Enfoque la muestra de forma perpendicular y con buena iluminación:")
else:
    muestra_img = st.file_uploader("Seleccione el archivo digitalizado (JPG / PNG):", type=["jpg", "jpeg", "png"])

if muestra_img is not None:
    imagen_pil = Image.open(muestra_img)
    st.image(imagen_pil, caption="Muestra recibida para inspección grafonómica", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    ejecutar_analisis = st.button("⚖️ Emitir Dictamen Grafopsicológico Forense", use_container_width=True)
    
    if ejecutar_analisis:
        if not api_key:
            st.error("No se ha configurado la clave API. Por favor añádala en los Secrets de Streamlit.")
        else:
            with st.spinner("Ejecutando medición morfoscópica, vectores de inclinación y dialéctica de Xandró..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # FILTRADO ESTRICTO: Solo modelos FLASH gratuitos (Nunca modelos Pro para evitar error 429)
                    modelos_disponibles = [
                        m.name for m in genai.list_models()
                        if "generateContent" in m.supported_generation_methods
                    ]
                    
                    # Prioridad exclusiva en variantes Flash
                    candidatos_flash = [
                        "gemini-1.5-flash",
                        "gemini-1.5-flash-latest",
                        "gemini-2.0-flash",
                        "gemini-1.5-flash-8b",
                        "gemini-1.5-flash-001"
                    ]
                    
                    modelo_final = None
                    for cand in candidatos_flash:
                        for m in modelos_disponibles:
                            if cand in m and "pro" not in m.lower():
                                modelo_final = m
                                break
                        if modelo_final:
                            break
                    
                    # Fallback de seguridad estricto a Flash
                    if not modelo_final:
                        for m in modelos_disponibles:
                            if "flash" in m.lower() and "pro" not in m.lower():
                                modelo_final = m
                                break
                                
                    if not modelo_final:
                        modelo_final = "models/gemini-1.5-flash"

                    model = genai.GenerativeModel(modelo_final)
                    
                    prompt_xandro = """
                    Actúa como un Perito Grafopsicólogo Docente en el marco de la cátedra de Introducción a la Psicología Forense de la Universidad Mariano Gálvez de Guatemala.
                    Tu análisis debe fundamentarse estrictamente en el método proyectivo y la morfología clásica de Mauricio Xandró.

                    DOCUMENTO EN EVALUACIÓN: Muestra que contiene texto manuscrito espontáneo (nombre/datos) y firma/rúbrica.

                    REGLAS DE MÁXIMO RIGOR CIENTÍFICO:
                    1. PROHIBICIÓN TOTAL DEL EFECTO FORER (horóscopos, frases genéricas aplicables a cualquiera).
                    2. CADA rasgo conductual deducido DEBE acompañarse de la evidencia visual observable exacta (ej.: "inclinación dextrógira de aproximadamente 80°", "hampas sobrealzadas", "óvalos cerrados en doble vuelta", "rúbrica envolvente envolviendo el nombre", "calibre de presión pastoso").
                    3. Utiliza la terminología técnica de Xandró: grafonomía, tensión del trazo, coligamento, equilibrio trizonal (zona superior, media e inferior), ritmo y espontaneidad.

                    ESTRUCTURA OBLIGATORIA DEL DICTAMEN EN FORMATO MARKDOWN:

                    # ⚖️ DICTAMEN GRAFOPSICOLÓGICO FORENSE EXPERIMENTAL
                    **Cátedra:** Introducción a la Psicología Forense | Licenciatura en Psicología Industrial (UMG)  
                    **Metodología:** Sistema Grafonómico de Mauricio Xandró  

                    ---

                    ## I. MATRIZ DE LOS 8 GÉNEROS GRÁFICOS (XANDRÓ)
                    Describe para cada género el signo morfológico visible y su significado grafopsicológico:
                    1. **Tamaño:** (Micrografía / Mediana / Macrografía - Altura en mm del cuerpo medio. Significado: autoestimación, necesidad de reconocimiento o introversión).
                    2. **Forma:** (Predominio de curvas, ángulos, simplificada o caligráfica. Significado: adaptabilidad, afabilidad, intransigencia o practicidad).
                    3. **Inclinación:** (Dextrógira, vertical, sinistrógira o irregular - Grados estimados. Significado: sociabilidad y extraversión vs. autocontrol y repliegue).
                    4. **Dirección de las Líneas:** (Ascendente, rectilínea horizontal, descendente, sinuosa. Significado: iniciativa, estabilidad del ánimo, fatiga o desánimo).
                    5. **Presión:** (Firme, neta, ligera o pastosa. Significado: fuerza biológica, vitalidad, asertividad o hipersensibilidad).
                    6. **Velocidad:** (Rápida, mesurada, precipitada o lenta. Significado: velocidad de procesamiento cognitivo y ritmo ejecutivo).
                    7. **Continuidad / Coligamento:** (Ligada, agrupada o desligada. Significado: razonamiento lógico-deductivo vs. agilidad intuitiva).
                    8. **Orden y Distribución Espacial:** (Claridad, márgenes, distribución de blancos. Significado: claridad mental, respeto a la jerarquía y estructura mental).

                    ---

                    ## II. ANÁLISIS DE SUBASPECTOS Y GESTOS TIPO
                    - **Morfología de Óvalos (Zona Media):** (Abiertos, cerrados, cerrados con bucle. Significado: permeabilidad comunicativa, discreción o reserva).
                    - **Prolongaciones Verticales:** (Desarrollo de hampas/intelecto vs. jambas/instinto-materialidad).
                    - **Puntuación y Barras Auxiliares:** (Punto de la 'i' y travesaño de la 't': ubicación, altura y firmeza).

                    ---

                    ## III. DIALÉCTICA PROYECTIVA: "YO SOCIAL" vs. "Yo ÍNTIMO"
                    *(Confrontación técnica entre el texto formal y la firma/rúbrica)*
                    - **El Texto (El Yo Social):** Rol exterior, conducta académica/laboral y adaptación al medio social formal.
                    - **La Firma y Rúbrica (El Yo Íntimo):** Autoimagen profunda, mecanismos de defensa afectiva y personalidad en la esfera privada.
                    - **Grado de Coherencia Grafonómica:** Contrastar tamaño, inclinación y estilo entre ambos elementos. Señalar si existe autenticidad (coincidencia) o mecanismos de defensa/compensación (ej. firma desproporcionadamente mayor, rúbrica envolvente o tachadura).

                    ---

                    ## IV. SÍNTESIS INTEGRATIVA Y PERFIL ACTITUDINAL
                    Presenta en dos párrafos concisos y de alto nivel pericial las fortalezas destacadas, las competencias de afrontamiento y las conclusiones finales sobre la muestra evaluada.
                    """
                    
                    response = model.generate_content([prompt_xandro, imagen_pil])
                    st.success("✅ Dictamen pericial generado satisfactoriamente.")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Aviso técnico en el procesamiento: {e}")
