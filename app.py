import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración institucional
st.set_page_config(
    page_title="UMG | Laboratorio Pericial Grafopsicológico",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estética pericial académica de alta gama
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Escudo / Banner Institucional UMG */
    .umg-card {
        background: linear-gradient(135deg, #091E3A 0%, #112A4F 60%, #1A365D 100%);
        border: 1px solid #D4AF37;
        border-radius: 14px;
        padding: 24px 20px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        margin-bottom: 22px;
    }
    
    .umg-title {
        font-family: 'Cinzel', serif;
        font-size: 1.15rem;
        letter-spacing: 2px;
        color: #F8FAFC;
        margin: 0;
        text-transform: uppercase;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    
    .umg-faculty {
        font-size: 0.98rem;
        color: #D4AF37;
        margin: 8px 0 3px 0;
        font-weight: 700;
        letter-spacing: 0.8px;
    }
    
    .umg-course {
        font-size: 0.86rem;
        color: #93C5FD;
        margin-bottom: 12px;
        font-weight: 500;
    }
    
    .umg-badge {
        display: inline-block;
        background: rgba(212, 175, 55, 0.15);
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 9999px;
        padding: 5px 18px;
        font-size: 0.74rem;
        color: #FEF08A;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    
    /* Resguardo Metodológico */
    .ethical-box {
        background: rgba(30, 41, 59, 0.4);
        border-left: 4px solid #D4AF37;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 24px;
        font-size: 0.82rem;
        color: #CBD5E1;
        line-height: 1.5;
    }
    
    /* Botón pericial interactivo */
    .stButton>button {
        background: linear-gradient(135deg, #0284C7 0%, #1E3A8A 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.6px !important;
        box-shadow: 0 4px 16px rgba(2, 132, 199, 0.35) !important;
        transition: all 0.25s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(2, 132, 199, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado Institucional
st.markdown("""
<div class="umg-card">
    <div class="umg-title">Universidad Mariano Gálvez de Guatemala</div>
    <div class="umg-faculty">Licenciatura en Psicología Industrial</div>
    <div class="umg-course">Cátedra: Introducción a la Psicología Forense</div>
    <div class="umg-badge">Sistema Pericial Grafopsicológico | Mauricio Xandró</div>
</div>
""", unsafe_allow_html=True)

# Resguardo Deontológico
st.markdown("""
<div class="ethical-box">
    <strong>⚖️ Marco Deontológico y Epistemológico:</strong><br>
    Sistema de análisis morfoscópico proyectivo experimental fundamentado en la grafonomía analítica de <em>Mauricio Xandró</em>. 
    Se evalúan estrictamente los 8 géneros gráficos y la dialéctica entre el Yo Social y el Yo Íntimo. 
    No sustituye un peritaje caligráfico forense documentológico ni una evaluación psicométrica clínica.
</div>
""", unsafe_allow_html=True)

# Clave API desde Secrets o manual
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    with st.expander("🔑 Credenciales de Conexión"):
        api_key = st.text_input("Ingrese la clave API de Gemini:", type="password")

# Selector de Entrada
st.markdown("### 📋 Captura del Manuscrito")
st.caption("Consigna: Hoja bond blanca lisa. Nombre manuscrito, fecha y firma/rúbrica con bolígrafo estándar.")

modo_captura = st.radio(
    "Fuente de entrada:",
    ["📷 Cámara del Dispositivo (Recomendado)", "📁 Cargar Archivo de Imagen"],
    horizontal=True
)

muestra_img = None
if modo_captura == "📷 Cámara del Dispositivo (Recomendado)":
    muestra_img = st.camera_input("Enfoque perpendicular a la muestra con luz homogénea:")
else:
    muestra_img = st.file_uploader("Subir imagen de la muestra (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"])

if muestra_img is not None:
    img_pil = Image.open(muestra_img)
    st.image(img_pil, caption="Muestra documental recibida para inspección", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⚖️ Ejecutar Dictamen Pericial Grafopsicológico", use_container_width=True):
        if not api_key:
            st.error("No se detectó la clave de API en los Secrets de Streamlit.")
        else:
            with st.spinner("Inspeccionando morfometría, vectores axiales y dialéctica de Mauricio Xandró..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # DETECCIÓN DINÁMICA DE MODELOS ACTIVOS EN LA CUENTA
                    modelos_disponibles = []
                    try:
                        for m in genai.list_models():
                            if "generateContent" in m.supported_generation_methods:
                                modelos_disponibles.append(m.name)
                    except Exception:
                        pass
                    
                    # Selección del modelo Flash óptimo (sin usar jamás modelos Pro)
                    modelo_final = None
                    prioridades = ["flash-latest", "2.5-flash", "2.0-flash", "flash"]
                    
                    for p in prioridades:
                        for m in modelos_disponibles:
                            if p in m.lower() and "pro" not in m.lower():
                                modelo_final = m
                                break
                        if modelo_final:
                            break
                    
                    # Si la lista no devolvió nombres, usar el alias canónico seguro
                    if not modelo_final:
                        modelo_final = "gemini-flash-latest"

                    model = genai.GenerativeModel(modelo_final)
                    
                    prompt_xandro = """
                    Actúa como un Perito Grafopsicólogo y Catedrático especializado en la doctrina clásica de Mauricio Xandró, en el marco académico de la Universidad Mariano Gálvez de Guatemala (Psicología Forense y Psicología Industrial).

                    MUESTRA EN EVALUACIÓN: Documento manuscrito con texto espontáneo (nombre/datos) y firma/rúbrica.

                    REGLAS DE MÁXIMO RIGOR CIENTÍFICO:
                    1. PROHIBICIÓN DEL EFECTO FORER: Quedan vetadas afirmaciones vagas o tipo horóscopo. CADA rasgo conductual inferido DEBE sustentar su origen en un signo morfológico visible y medible (ej.: "inclinación dextrógira de aprox. 75°", "hampas sobrealzadas de 5 mm", "jambas reducidas", "óvalos cerrados en doble vuelta", "rúbrica envolvente", "presión apoyada/firme").
                    2. Utiliza la terminología técnica de Xandró: grafonomía, tensión del trazo, coligamento, equilibrio trizonal (zona superior, media e inferior), ritmo y espontaneidad.

                    ESTRUCTURA OBLIGATORIA DEL DICTAMEN EN FORMATO MARKDOWN:

                    # ⚖️ DICTAMEN GRAFOPSICOLÓGICO FORENSE EXPERIMENTAL
                    **Institución:** Universidad Mariano Gálvez de Guatemala  
                    **Cátedra:** Introducción a la Psicología Forense | Licenciatura en Psicología Industrial  
                    **Metodología:** Sistema Morfoscópico y Proyectivo de Mauricio Xandró  

                    ---

                    ## I. MATRIZ DE LOS 8 GÉNEROS GRÁFICOS (MAURICIO XANDRÓ)
                    Detalla minuciosamente para cada género el signo observado y su interpretación psicológica:
                    1. **Tamaño:** (Magnitud del cuerpo central en mm. Significado: autoestimación, expansión yoica, introversión o meticulosidad).
                    2. **Forma:** (Curva, ángulo, simplificada o caligráfica. Significado: empatía, ductilidad vs. combatividad, sentido práctico y firmeza).
                    3. **Inclinación:** (Dextrógira, vertical, sinistrógira o irregular - Grados estimados. Significado: orientación hacia los demás y el entorno vs. reserva, autocontrol y desconfianza).
                    4. **Dirección:** (Horizontal, ascendente, descendente, sinuosa. Significado: estabilidad anímica, iniciativa de logro o fatiga temporal).
                    5. **Presión:** (Firme, neta, leve o pastosa. Significado: vitalidad biológica, asertividad, volumen energético o hipersensibilidad).
                    6. **Velocidad:** (Rápida, mesurada, precipitada o pausada. Significado: agilidad cognitiva, resolución práctica y ritmo laboral).
                    7. **Continuidad (Coligamento):** (Ligada, agrupada o desligada. Significado: pensamiento deductivo y continuidad lógica vs. intuición asociativa).
                    8. **Orden y Distribución:** (Claridad, márgenes y distribución de blancos. Significado: orden mental, sentido de la jerarquía y disciplina).

                    ---

                    ## II. ANÁLISIS DE SUBASPECTOS Y GESTOS TIPO
                    - **Morfología de Óvalos (Zona Media):** (Abiertos, cerrados, cegados. Significado: permeabilidad afectiva, discreción o hermetismo).
                    - **Desarrollo Trizonal:** (Zona Superior/intelecto vs. Zona Media/afectividad vs. Zona Inferior/instintos y practicidad).
                    - **Gestos de Cohesión:** (Puntos sobre las 'i' y barras de la 't': ubicación, altura y firmeza).

                    ---

                    ## III. DIALÉCTICA PROYECTIVA: "YO SOCIAL" vs. "YO ÍNTIMO"
                    *(Confrontación técnica y pericial entre el texto y la firma)*
                    - **El Texto (El Yo Social):** Conducta exteriorizada, rol formal académico/laboral y adaptación pública.
                    - **La Firma y Rúbrica (El Yo Íntimo):** Autoimagen inconsciente, esfera privada y defensas del Yo.
                    - **Confrontación Morfométrica:** Evalúa si coinciden o discrepan en tamaño, inclinación y estilo. Explica si revela congruencia personal o mecanismos compensatorios/defensivos (rúbrica envolvente = coraza protectora; firma tachada = autocrítica severa; firma mayor = sobrecompensación del ego).

                    ---

                    ## IV. SÍNTESIS INTEGRATIVA Y PERFIL ACTITUDINAL
                    Dos párrafos de síntesis pericial concluyendo las principales competencias conductuales, estilo de afrontamiento ante la presión y balance general de la muestra.
                    """
                    
                    respuesta = model.generate_content([prompt_xandro, img_pil])
                    st.success("✅ Dictamen pericial generado exitosamente bajo el método Mauricio Xandró.")
                    st.markdown(respuesta.text)
                    
                except Exception as e:
                    st.error(f"Aviso técnico en el procesamiento: {e}")
