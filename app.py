import streamlit as st
import google.generativeai as genai
from PIL import Image

# Configuración de página optimizada para móviles
st.set_page_config(
    page_title="Grafología Científica - Stand",
    page_icon="✍️",
    layout="centered"
)

# Estilo visual limpio y educativo
st.markdown("""
<style>
    .main-title { text-align: center; color: #1E3A8A; font-weight: 800; margin-bottom: 0px; }
    .subtitle { text-align: center; color: #4B5563; font-size: 0.95rem; margin-bottom: 20px; }
    .disclaimer { background-color: #F3F4F6; padding: 12px; border-radius: 8px; font-size: 0.85rem; color: #374151; margin-bottom: 20px; border-left: 4px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<h2 class="main-title">🔬 Estudio Grafopsicológico</h2>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Feria Científica | Fundamentación en los 8 Géneros de Mauricio Xandró</p>', unsafe_allow_html=True)

# Marco ético visible para jueces y visitantes
st.markdown("""
<div class="disclaimer">
    <strong>Aviso Metodológico y Ético:</strong> Este análisis constituye una aproximación proyectiva experimental basada en la grafonomía clásica de Mauricio Xandró. No representa un diagnóstico clínico, psicométrico ni de salud mental.
</div>
""", unsafe_allow_html=True)

# Obtención de la API Key (desde los Secrets de Streamlit o campo manual)
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    with st.expander("⚙️ Configuración de clave (solo si no está en Secrets)"):
        api_key = st.text_input("Ingresa tu Gemini API Key:", type="password")

# Selector de captura: Cámara en directo o subir foto
modo_captura = st.radio("Método de captura:", ["📷 Tomar foto con la cámara", "📁 Subir foto existente"], horizontal=True)

imagen_muestra = None
if modo_captura == "📷 Tomar foto con la cámara":
    imagen_muestra = st.camera_input("Enfoca la muestra (Nombre, fecha y firma en papel blanco)")
else:
    imagen_muestra = st.file_uploader("Selecciona la imagen de la muestra:", type=["jpg", "jpeg", "png"])

# Procesamiento del análisis
if imagen_muestra is not None:
    img = Image.open(imagen_muestra)
    st.image(img, caption="Muestra capturada", use_container_width=True)
    
    if st.button("🔍 Analizar Muestra Manuscrita", type="primary", use_container_width=True):
        if not api_key:
            st.error("Por favor ingresa una clave de API válida para continuar.")
        else:
            with st.spinner("Analizando los 8 géneros gráficos y confrontando Yo Social vs. Yo Íntimo..."):
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    prompt_xandro = """
                    Actúa como un perito grafopsicólogo y docente científico basándote estrictamente en el método y los 8 géneros gráficos de Mauricio Xandró.
                    Analiza la imagen adjunta que contiene: Nombre (texto) y Firma/Rúbrica.

                    REGLAS OBLIGATORIAS:
                    1. Cero esoterismo o efecto horóscopo (Efecto Forer). Cada rasgo de personalidad deducido DEBE citar el signo morfológico visible exacto (ej. "Inclinación a la derecha de aprox. 75°", "Tamaño inferior a 2mm en el óvalo de la 'a'").
                    2. Enfoque constructivo, pedagógico y prudente.
                    
                    ESTRUCTURA DE RESPUESTA EN FORMATO MARKDOWN:
                    
                    ### 1. Ficha Técnica de los 8 Géneros Gráficos
                    Para cada género, indica brevemente el rasgo visual observado y su correlato psicológico:
                    - **Tamaño:** (Grande / Mediano / Pequeño) -> Observación y significado.
                    - **Forma:** (Predominio Curvo / Predominio Anguloso) -> Observación y significado.
                    - **Inclinación:** (Dextrógira / Vertical / Sinistrógira) -> Observación y significado.
                    - **Dirección:** (Ascendente / Rectilínea / Descendente) -> Observación y significado.
                    - **Presión:** (Firme / Nutricia / Leve) -> Observación del calibre/huella y significado.
                    - **Velocidad:** (Rápida / Pausada / Mesurada) -> Observación en simplificaciones y significado.
                    - **Continuidad:** (Ligada / Agrupada / Desligada) -> Enlaces interletra y significado.
                    - **Orden:** (Distribución espacial, márgenes y claridad) -> Observación y significado.

                    ### 2. Confrontación Proyectiva: "Yo Social" vs. "Yo Íntimo"
                    - **El Texto (Yo Social):** Cómo se presenta el individuo en su rol público y académico/laboral.
                    - **La Firma y Rúbrica (Yo Íntimo):** Autoimagen personal, defensas afectivas y esfera privada.
                    - **Grado de Coherencia:** Compara si firma y texto coinciden o difieren en tamaño, inclinación y estilo, explicando qué revela esa relación.

                    ### 3. Síntesis y Conclusión Pedagógica
                    Un párrafo resumen con las tendencias actitudinales dominantes observadas.
                    """
                    
                    response = model.generate_content([prompt_xandro, img])
                    st.success("¡Análisis completado con éxito!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Error al procesar la imagen: {e}")
