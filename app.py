import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
import base64
import pandas as pd
from datetime import datetime
import os
# Configuración de la página
st.markdown(
    """
    <style>
    :root {
        --pucmm-blue: #003399;
        --pucmm-gray: #E6E6E6;
    }
    div.stButton>button {
        background-color: var(--pucmm-blue);
        color: white;
        border-radius: 8px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="Simulador de digestión y gel")

# encabezado con logo y texto
logo = Image.open("logo_pucmm.png")

def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_image_base64("logo_pucmm.png")

st.markdown(
    f"""
    <div style='text-align: center; line-height: 1.5; margin-bottom: 10px;'>
        <img src='data:image/png;base64,{logo_base64}' width='120'>
        <h4 style='margin: 8px 0 0 0;'>Pontificia Universidad Católica Madre y Maestra (PUCMM)</h4>
        <p style='margin: 4px 0;'>
            <b>Escuela de Ciencias Naturales y Exactas</b><br>
            Laboratorio de Biología Celular y Genética<br>
            <b>BIO211-P</b>
        </p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)
# Estilo para títulos
subtitle_style = "font-size: 1.5em; margin-top: 15px; margin-bottom: 5px; font-weight: 600;"

# Título principal
st.markdown(
    f"<h2 style='{subtitle_style}'>Simulador de digestión por enzimas de restricción</h2>",
    unsafe_allow_html=True
)
st.write("Simulador con IA: gel, explicación, preguntas personalizadas y tutor virtual")

# Base de datos de ADN y sitios de corte
adn_db = {
    "ADN lineal 4000 pb (1 sitio EcoRI)": {
        "tipo": "lineal",
        "longitud": 4000,
        "sitios": {"EcoRI": [2000]},
    },
    "ADN lineal 4000 pb (2 sitios EcoRI)": {
        "tipo": "lineal",
        "longitud": 4000,
        "sitios": {"EcoRI": [1000, 3000]},
    },
    "ADN circular 5000 pb (2 sitios EcoRI)": {
        "tipo": "circular",
        "longitud": 5000,
        "sitios": {"EcoRI": [1200, 3700]},
    },
    "ADN lineal 6000 pb (2 sitios HindIII)": {
        "tipo": "lineal",
        "longitud": 6000,
        "sitios": {"HindIII": [1500, 4500]},
    },
    "ADN circular 8000 pb (3 sitios BamHI)": {
        "tipo": "circular",
        "longitud": 8000,
        "sitios": {"BamHI": [1000, 4000, 7000]},
    },
    "ADN lineal 5000 pb (1 sitio HindIII, 1 sitio EcoRI)": {
        "tipo": "lineal",
        "longitud": 5000,
        "sitios": {"HindIII": [1200], "EcoRI": [3800]},
    },
    "ADN circular 7000 pb (1 sitio BamHI)": {
        "tipo": "circular",
        "longitud": 7000,
        "sitios": {"BamHI": [3500]},
    },
    "Plásmido pBR322 (4361 pb, 2 sitios EcoRI y 1 HindIII)": {
        "tipo": "circular",
        "longitud": 4361,
        "sitios": {"EcoRI": [600, 3200], "HindIII": [1500]},
    },
}

enzimas_disponibles = sorted({enz for adn in adn_db.values() for enz in adn["sitios"].keys()})

#UI de selección
adn_sel = st.selectbox("1. Elige la molécula de ADN", list(adn_db.keys()))
adn_info = adn_db[adn_sel]

enzimas_sel = st.multiselect(
    "2. Elige la(s) enzima(s) de restricción",
    enzimas_disponibles,
    default=[enzimas_disponibles[0]] if enzimas_disponibles else []
)

st.markdown(f"<h2 style='{subtitle_style}'>Resultado simulado</h2>", unsafe_allow_html=True)

#funciones de digestión
def digest_lineal(longitud, cortes):
    cortes_ordenados = sorted(cortes)
    fragmentos = []
    inicio = 0
    pasos = []
    for c in cortes_ordenados:
        frag = c - inicio
        fragmentos.append(frag)
        pasos.append(f"Fragmento desde {inicio} pb hasta {c} pb → {frag} pb")
        inicio = c
    ultimo = longitud - inicio
    fragmentos.append(ultimo)
    pasos.append(f"Fragmento desde {inicio} pb hasta {longitud} pb → {ultimo} pb")
    return fragmentos, pasos

def digest_circular(longitud, cortes):
    if len(cortes) == 1:
        pasos = [f"ADN circular con 1 corte en {cortes[0]} pb → se linealiza → 1 fragmento de {longitud} pb"]
        return [longitud], pasos
    cortes_ordenados = sorted(cortes)
    fragmentos = []
    pasos = []
    for i in range(len(cortes_ordenados)):
        actual = cortes_ordenados[i]
        siguiente = cortes_ordenados[(i + 1) % len(cortes_ordenados)]
        if siguiente > actual:
            frag = siguiente - actual
            desc = f"Segmento entre {actual} pb y {siguiente} pb → {frag} pb"
        else:
            frag = (longitud - actual) + siguiente
            desc = f"Segmento entre {actual} pb y fin ({longitud}) + inicio hasta {siguiente} pb → {frag} pb"
        fragmentos.append(frag)
        pasos.append(desc)
    return fragmentos, pasos

def digerir(adn, enzimas):
    cortes = []
    for e in enzimas:
        cortes.extend(adn["sitios"].get(e, []))
    if not cortes:
        return [], []
    if adn["tipo"] == "lineal":
        return digest_lineal(adn["longitud"], cortes)
    else:
        return digest_circular(adn["longitud"], cortes)

# función para generar imagen de gel
def generar_gel_multicarril(diccionario_carriles, ancho_carril=120, alto=400, espacio=20, scale=2):
    ancho_carril *= scale
    alto *= scale
    espacio *= scale

    marcador_fragmentos = [10000, 8000, 6000, 5000, 4000, 3000, 2000, 1000]
    carriles = {"Marcador": marcador_fragmentos}
    carriles.update(diccionario_carriles)

    n = len(carriles)
    ancho_total = n * ancho_carril + (n + 1) * espacio
    img = Image.new("RGB", (ancho_total, alto), "black")
    draw = ImageDraw.Draw(img)

    try:
        small_font = ImageFont.truetype("arial.ttf", 12 * scale)
    except:
        small_font = ImageFont.load_default()

    max_pb_global = max(max(frag) for frag in carriles.values() if frag)

    x_actual = espacio
    for nombre, fragmentos in carriles.items():
        x1 = x_actual
        x2 = x_actual + ancho_carril

        draw.rectangle(
            [x1 + ancho_carril*0.3, 30*scale, x2 - ancho_carril*0.3, alto - 30*scale],
            outline="grey",
            width=1*scale
        )

        if fragmentos:
            for f in sorted(fragmentos, reverse=True):
                rel = f / max_pb_global
                y = int(50*scale + (1 - rel) * (alto - 80*scale))

                if nombre not in ("Marcador", "Combinada"):
                    y += ((hash(nombre) % 8) - 4) * scale

                draw.rectangle([x1 + 15*scale, y - 4*scale, x2 - 15*scale, y + 4*scale], fill="white")

                if nombre == "Marcador":
                    draw.text((x2 + 5*scale, y - 6*scale), f"{f}", fill="white", font=small_font)

        draw.text((x1 + 5*scale, alto - 25*scale), nombre[:10], fill="white", font=small_font)

        x_actual += ancho_carril + espacio

    return img

# función para explicar con IA
def explicar_con_ia(tipo_adn, enzimas, fragmentos, prediccion_estudiante=None):
    api_key = st.secrets.get("OPENAI_API_KEY")
    base = (
        "La(s) enzima(s) seleccionada(s) reconoce(n) sitios específicos en el ADN. "
        "Cada corte genera un fragmento nuevo. En ADN lineal: fragmentos = cortes + 1. "
        "En ADN circular: fragmentos = número de cortes (si es 1, se ve una sola banda). "
        "El carril marcador sirve para comparar tamaños."
    )
    if not api_key:
        return base

    feedback_part = ""
    if prediccion_estudiante is not None:
        feedback_part = f"""
El estudiante predijo {prediccion_estudiante} fragmentos.
El resultado real fue {len(fragmentos)} fragmentos.
Da retroalimentación breve, amable, diciendo si acertó o en qué se equivocó.
"""

    prompt = f"""
Eres un docente de biología molecular. Explica este resultado de digestión.
- Tipo de ADN: {tipo_adn}
- Enzimas usadas: {', '.join(enzimas) if enzimas else 'no especificadas'}
- Fragmentos obtenidos (pb): {fragmentos}
{feedback_part}
Incluye por qué el marcador ayuda a estimar tamaños.
Usa lenguaje sencillo para estudiantes de ciencias de la salud.
"""

    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.4
    }

    try:
        resp = requests.post(endpoint, headers=headers, json=body, timeout=10)
        data = resp.json()
        if "error" in data:
            # si hay error de cuota o modelo, devolvemos el base
            return base
        return data["choices"][0]["message"]["content"]
    except Exception:
        return base

# inicializar session_state para la retro
if "retro_ia" not in st.session_state:
    st.session_state["retro_ia"] = None

# lógica principal
if not enzimas_sel:
    st.warning("Selecciona al menos una enzima para simular.")
else:
    # carriles por enzima
    carriles_exp = {}
    for enz in enzimas_sel:
        frags_enz, _ = digerir(adn_info, [enz])
        carriles_exp[enz] = frags_enz

    # carril combinado
    frags_comb, pasos_comb = digerir(adn_info, enzimas_sel)
    if frags_comb:
        carriles_exp["Combinada"] = frags_comb
        st.success(f"Digestión combinada → {len(frags_comb)} fragmento(s): {', '.join(str(f)+' pb' for f in frags_comb)}")
    else:
        st.warning("Para esta combinación no hay sitios definidos en el prototipo.")

    # mostrar gel
    img = generar_gel_multicarril(carriles_exp, scale=2)
    st.image(
        img,
        caption="Gel de agarosa simulado (Marcador + carriles de digestión)",
        use_container_width=False,
        width=500
    )

   #predicción del estudiante
    st.markdown(f"<h2 style='{subtitle_style}'> Tu predicción</h2>", unsafe_allow_html=True)

    pred = st.number_input(
        "¿Cuántos fragmentos creías que iban a salir en la digestión combinada?",
        min_value=0,
        step=1,
        value=len(frags_comb) if frags_comb else 0,
        key="pred_fragmentos"
    )

    if st.button("Evaluar mi respuesta con IA", key="btn_retro_ia"):
        st.session_state["retro_ia"] = explicar_con_ia(
            adn_info["tipo"],
            enzimas_sel,
            frags_comb if frags_comb else [],
            pred
        )

    if st.session_state["retro_ia"]:
        st.write(st.session_state["retro_ia"])

    # explicación paso a paso
    with st.expander("📐 Ver explicación paso a paso"):
        st.write(f"**Molécula:** {adn_sel}")
        st.write(f"**Enzimas:** {', '.join(enzimas_sel)}")
        for paso in pasos_comb:
            st.write("• " + paso)
        st.write("La suma de los fragmentos debe dar la longitud total del ADN.")
    
    # función para llamar a OpenAI
    def call_openai(messages, temperature=0.4):
        api_key = st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            return None  # indicamos que no hay IA
        
        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        body = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": temperature
        }
        try:
            resp = requests.post(endpoint, headers=headers, json=body, timeout=15)
            data = resp.json()
            if "error" in data:
                st.error(f"Error de la API: {data['error'].get('message')}")
                return None
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"No se pudo conectar a la API: {e}")
            return None
   #preguntas generadas por IA
    st.markdown(f"<h2 style='{subtitle_style}'> Preguntas generadas por IA sobre este experimento</h2>", unsafe_allow_html=True)
    # inicializamos en session_state
    if "preguntas_ia" not in st.session_state:
        st.session_state["preguntas_ia"] = ""

    if st.button("Generar preguntas nuevas"):
        contexto = f"""
ADN seleccionado: {adn_sel}
Tipo de ADN: {adn_info['tipo']}
Enzimas usadas: {', '.join(enzimas_sel) if enzimas_sel else 'ninguna'}
Fragmentos obtenidos: {frags_comb if frags_comb else 'sin cortes'}
"""
        
        resp = call_openai([
            {
                "role": "system",
                "content": "Eres un profesor de biología molecular que crea ejercicios cortos y claros."
            },
            {
                "role": "user",
                "content": f"""
Con el siguiente contexto de una práctica de digestión con enzimas de restricción:

{contexto}

Genera de 3 a 4 preguntas diferentes cada vez.
- Mezcla tipos de pregunta: definición, aplicación, '¿qué pasaría si...?', e interpretación del gel.
- Después de cada pregunta escribe la respuesta correcta en una línea aparte.
- Usa este formato exactamente:

P1: ...
R1: ...
P2: ...
R2: ...
P3: ...
R3: ...
P4: ...
R4: ...

No expliques, solo preguntas y respuestas.
"""
            }
        ])

        if resp:
            st.session_state["preguntas_ia"] = resp
        else:
            # fallback sin IA
            st.session_state["preguntas_ia"] = (
                "P1: ¿Cuántos fragmentos se obtienen si hay dos cortes en un ADN lineal?\n"
                "R1: Se obtienen 3 fragmentos.\n"
                "P2: ¿Para qué sirve el marcador de peso molecular?\n"
                "R2: Para estimar el tamaño de los fragmentos.\n"
                "P3: Si una enzima no tiene sitio en el ADN elegido, ¿qué ocurre?\n"
                "R3: No hay digestión con esa enzima."
            )

    # mostrar lo último generado
    if st.session_state["preguntas_ia"]:
        st.text(st.session_state["preguntas_ia"])


    # comparación de enzimas
    st.markdown(f"<h2 style='{subtitle_style}'> Comparación de enzimas en esta molécula</h2>", unsafe_allow_html=True)
    st.write("Así cortarían las enzimas que sí tienen sitio definido en este ADN:")
    for e, sitios in adn_info["sitios"].items():
        fr_e, _ = digerir(adn_info, [e])
        st.write(f"- **{e}** → {len(sitios)} sitio(s) → {len(fr_e)} fragmento(s): {', '.join(str(x)+' pb' for x in fr_e)}")

    # tutor virtual contextual
    st.markdown(f"<h2 style='{subtitle_style}'>💬 Tutor virtual contextual</h2>", unsafe_allow_html=True)
    st.write("Haz una pregunta sobre este resultado (por ejemplo: por qué hay 3 fragmentos si son 2 enzimas).")
    pregunta_est = st.text_input("Tu pregunta al tutor")
    if st.button("Preguntar a la IA"):
        if pregunta_est.strip():
            contexto = f"ADN: {adn_sel}. Tipo: {adn_info['tipo']}. Enzimas: {', '.join(enzimas_sel)}. Fragmentos: {frags_comb}."
            resp = call_openai([
                {"role": "system", "content": "Eres un tutor de biología molecular, paciente y claro."},
                {"role": "user", "content": f"Contexto del experimento: {contexto}"},
                {"role": "user", "content": f"Pregunta del estudiante: {pregunta_est}"}
            ])
            if resp:
                st.write(resp)
            else:
                st.write("No pude consultar a la IA, pero: en un ADN lineal, fragmentos = cortes + 1.")
        else:
            st.warning("Escribe una pregunta primero.")
            

# recogemos satisfacción y uso de IA
st.markdown(f"<h3 style='{subtitle_style}'>📝 Evalúa esta práctica</h3>", unsafe_allow_html=True)
satisfaccion = st.slider("¿Qué tan útil te pareció la explicación de la app/IA?", 1, 5, 4)
uso_ia = st.checkbox("Usé alguna función de IA (tutor, preguntas, explicación)", value=True)

# datos anónimos
nombre_est = st.text_input("Las respuestas son anónimas", value="anónimo")

if st.button("Guardar mi resultado"):
    registro = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "estudiante": nombre_est,
        "adn": adn_sel,
        "enzimas": ", ".join(enzimas_sel),
        "fragmentos_reales": len(frags_comb) if frags_comb else 0,
        "prediccion": pred,
        "acierto": int(pred == (len(frags_comb) if frags_comb else 0)),
        "satisfaccion": satisfaccion,
        "uso_ia": int(uso_ia),
    }

    if os.path.exists("resultados_app.csv"):
        df_prev = pd.read_csv("resultados_app.csv")
        df_new = pd.concat([df_prev, pd.DataFrame([registro])], ignore_index=True)
    else:
        df_new = pd.DataFrame([registro])

    df_new.to_csv("resultados_app.csv", index=False)
    st.success("✅ Resultado guardado")


st.markdown(f"<h2 style='{subtitle_style}'>📊 Resultados del piloto / indicadores</h2>", unsafe_allow_html=True)

if os.path.exists("resultados_app.csv"):
    df = pd.read_csv("resultados_app.csv")

    # valores base
    total_registros = len(df)
    aciertos_pct = df["acierto"].mean() * 100 if "acierto" in df.columns else 0
    satisf_prom = df["satisfaccion"].mean() if "satisfaccion" in df.columns else 0
    adopcion_pct = df["uso_ia"].mean() * 100 if "uso_ia" in df.columns else 0

    # fila de métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Simulaciones registradas", total_registros)
    with col2:
        st.metric("Aciertos en predicción", f"{aciertos_pct:.1f} %")
    with col3:
        st.metric("Satisfacción media", f"{satisf_prom:.2f} / 5")
    with col4:
        st.metric("Uso de IA", f"{adopcion_pct:.1f} %")

    st.markdown(f"<h3 style='{subtitle_style}'>📈 Barras de progreso</h3>", unsafe_allow_html=True)
    st.write("Nivel de logro respecto a la meta propuesta (ej. 70% aciertos, 60% uso IA).")
    st.write("Aciertos")
    st.progress(min(int(aciertos_pct), 100))
    st.write("Uso de IA")
    st.progress(min(int(adopcion_pct), 100))

    st.markdown(f"<h3 style='{subtitle_style}'>🧬 ADN más usado</h3>", unsafe_allow_html=True)
    if "adn" in df.columns:
        st.dataframe(df["adn"].value_counts().head(5).reset_index().rename(
            columns={"index": "ADN", "adn": "veces"}
        ))
    else:
        st.write("No hay datos de ADN aún.")

    st.markdown(f"<h3 style='{subtitle_style}'> Enzimas más usadas</h3>", unsafe_allow_html=True)
    if "enzimas" in df.columns:
        st.dataframe(df["enzimas"].value_counts().head(5).reset_index().rename(
            columns={"index": "Enzimas", "enzimas": "veces"}
        ))
    else:
        st.write("No hay datos de enzimas aún.")

else:
    st.info("Aún no hay datos guardados. Cuando los estudiantes usen la app y se guarden los resultados, aquí verás el panel.")

# Solo mostrar el enlace de descarga si el archivo existe
if os.path.exists("resultados_app.csv"):
    with open("resultados_app.csv", "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="resultados_app.csv">Haz clic aquí para descargar el archivo CSV</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Aún no hay archivo de resultados en este servidor. Vuelve a generar datos y luego descárgalos.")
    st.caption("⚠️ Recuerda: en Streamlit Cloud el archivo se borra cuando el servidor se reinicia o pasa tiempo sin uso.")


st.caption("Prototipo educativo con Streamlit + IA (explicación, retroalimentación, preguntas y tutor).")
st.markdown("""
<hr>
<center>
<b>Desarrollado por:</b> Natalia Fernández · Pontificia Universidad Católica Madre y Maestra (PUCMM)<br>
<i>Simulador académico con IA — Laboratorio de Biología Celular y Genética (BIO211-P)</i>
</center>
""", unsafe_allow_html=True)








