import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import os
import json

st.set_page_config(page_title="Seldon", page_icon="logo.png", layout="wide")

if os.path.exists("logo.png"):
    st.logo("logo.png")

MATRIX_CSS = """
<style>
    /* Absolute transparency for all Streamlit layers */
    div[data-testid="stAppViewContainer"], 
    .main, 
    .stApp, 
    [data-testid="stHeader"],
    [data-testid="stAppViewBlockContainer"] {
        background: transparent !important;
    }
    
    /* Ensure the body of the iframe is also transparent */
    iframe {
        background: transparent !important;
    }

    [data-testid="stSidebar"] {
        background: rgba(0, 20, 0, 0.9) !important;
        border-right: 2px solid #00ff41 !important;
    }
    
    .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, label, .stText {
        color: #00ff41 !important;
        text-shadow: 0 0 5px #00ff41;
    }
    
    [data-baseweb="input"], [data-baseweb="textarea"] {
        background: black !important;
        border-color: #00ff41 !important;
    }
    
    [data-baseweb="input"] input, textarea {
        color: #00ff41 !important;
    }
    
    [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {
        background: black !important;
        border: 2px solid #00ff41 !important;
        color: #00ff41 !important;
        box-shadow: 0 0 10px #00ff41 !important;
        font-weight: bold !important;
    }
    
    [data-testid="baseButton-secondary"]:hover, [data-testid="baseButton-primary"]:hover {
        background: #00ff41 !important;
        color: black !important;
    }
    
    [data-testid="stAlert"] {
        background: rgba(0, 40, 0, 0.9) !important;
        border: 1px solid #00ff41 !important;
        color: #00ff41 !important;
    }
    
    [data-testid="stDataFrame"] {
        border: 1px solid #00ff41 !important;
        background: black !important;
    }

    /* Surgical sidebar adjustments */
    [data-testid="stSidebarHeader"] {
        display: none !important; /* Hide default Streamlit logo header to avoid icons text */
    }
    
    /* NEW: Hide Streamlit's internal menu and deploy button to clear top-right area */
    header, [data-testid="stHeader"] {
        visibility: hidden !important;
        display: none !important;
    }
    
    footer {
        visibility: hidden !important;
    }

    #MainMenu {
        visibility: hidden !important;
    }
    
    [data-baseweb="select"] > div {
        background: black !important;
        color: #00ff41 !important;
        border-color: #00ff41 !important;
    }

    /* Condition to hide canvas if not in Inicio */
    body:not(.matrix-home) #matrixCanvas {
        display: none !important;
        visibility: hidden !important;
    }
    body.matrix-home #matrixCanvas {
        display: block !important;
        visibility: visible !important;
    }
</style>
"""
st.markdown(MATRIX_CSS, unsafe_allow_html=True)

# Use st.sidebar.image which is MORE robust than st.logo for custom sizing/display
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=220)
else:
    st.sidebar.title("SELDON")

MATRIX_JS = """
<script>
    const parentDoc = window.parent.document;
    
    // Set parent body background to black 
    parentDoc.body.style.backgroundColor = 'black';

    if (!parentDoc.getElementById('matrixCanvas')) {
        const canvas = parentDoc.createElement('canvas');
        canvas.id = 'matrixCanvas';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '-100'; 
        canvas.style.pointerEvents = 'none';
        
        parentDoc.body.insertBefore(canvas, parentDoc.body.firstChild);
        
        const ctx = canvas.getContext('2d');
        let width = parentDoc.documentElement.clientWidth;
        let height = parentDoc.documentElement.clientHeight;
        canvas.width = width;
        canvas.height = height;
        
        const chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ';
        const fontSize = 16;
        let columns = Math.ceil(width / fontSize);
        let rainDrops = Array(columns).fill(1);
        
        function draw() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, width, height);
            
            ctx.fillStyle = '#0F0';
            ctx.font = fontSize + 'px monospace';
            
            for(let i = 0; i < rainDrops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);
                
                if(rainDrops[i] * fontSize > height && Math.random() > 0.985) {
                    rainDrops[i] = 0;
                }
                rainDrops[i]++;
            }
        }
        
        setInterval(draw, 35);
        
        window.parent.addEventListener('resize', () => {
            width = parentDoc.documentElement.clientWidth;
            height = parentDoc.documentElement.clientHeight;
            canvas.width = width;
            canvas.height = height;
            columns = Math.ceil(width / fontSize);
            rainDrops = Array(columns).fill(1);
        });
    }
</script>
"""
components.html(MATRIX_JS, height=0, width=0)

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Navigation Menu
menu = ["[ SYS ] Inicio", "[ DATA ] Catálogo e Ingesta", "[ REGS ] Tablas Registradas", "[ NEUR ] Consultas Inteligentes"]
choice = st.sidebar.radio("Navegación del Sistema", menu)

# JS conditional for Matrix Rain on Home page only
if "Inicio" in choice:
    components.html('<script>window.parent.document.body.classList.add("matrix-home");</script>', height=0, width=0)
else:
    components.html('<script>window.parent.document.body.classList.remove("matrix-home");</script>', height=0, width=0)

# Homepage / Cover
if "Inicio" in choice:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00ff41; font-size: 6rem; text-shadow: 0 0 20px #00ff41;'>SELDON</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #00ff41; font-size: 2rem;'>[ NEURAL INTERFACE ACTIVATED ]</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid #00ff41;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.5rem;'>Bienvenido a la terminal de gestión de metadatos.</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Utilice el menú lateral para acceder a los módulos de BigQuery.</p>", unsafe_allow_html=True)

# Catalog Module
elif "Catálogo" in choice:
    st.header("[ REGS ] Registrar Nueva Tabla de BigQuery")
    
    col1, col2 = st.columns(2)
    with col1:
        full_table_id = st.text_input("ID de Tabla (proyecto.dataset.tabla)", placeholder="data-exp-contactcenter.100x100.mi_tabla")
    with col2:
        short_name = st.text_input("Nombre Corto (para SQL local)", placeholder="ventas_2024")
    
    if st.button("[ SCAN ] Analizar Esquema e IA"):
        if full_table_id and short_name:
            with st.spinner("Analizando tabla y generando descripción..."):
                response = requests.post(f"{BACKEND_URL}/tables/analyze", json={"full_table_id": full_table_id, "short_name": short_name})
                if response.status_code == 200:
                    data = response.json()
                    st.session_state['temp_schema'] = data['schema']
                    st.session_state['temp_desc'] = data['suggested_description']
                    st.success("Análisis completado.")
                else:
                    st.error(f"Error: {response.text}")
        else:
            st.warning("Por favor completa los campos.")

    if 'temp_schema' in st.session_state:
        st.subheader("Esquema Detectado")
        st.write(pd.DataFrame(st.session_state['temp_schema']))
        
        st.subheader("Descripción Sugerida por IA")
        final_description = st.text_area("Puedes refinar la descripción aquí:", value=st.session_state['temp_desc'], height=150)
        
        if st.button("[ SAVE ] Guardar en Catálogo e Ingestar Datos"):
            with st.spinner("Ingestando datos y guardando metadatos..."):
                save_resp = requests.post(
                    f"{BACKEND_URL}/tables/save", 
                    json={
                        "full_table_id": full_table_id,
                        "short_name": short_name,
                        "description": final_description,
                        "schema": st.session_state['temp_schema']
                    }
                )
                if save_resp.status_code == 200:
                    st.success(f"Tabla '{short_name}' registrada con éxito. {save_resp.json()['rows_ingested']} filas ingestadas.")
                    del st.session_state['temp_schema']
                    del st.session_state['temp_desc']
                else:
                    st.error(f"Error al guardar: {save_resp.text}")

# Smart Queries Module
elif "Consultas" in choice:
    st.header("[ NEUR ] Generar Queries con IA sobre el Catálogo")
    
    tables_resp = requests.get(f"{BACKEND_URL}/tables")
    if tables_resp.status_code == 200:
        available_tables = tables_resp.json()
        if not available_tables:
            st.info("No hay tablas en el catálogo. Registra una primero.")
        else:
            st.write("Tablas disponibles:", ", ".join([t['short_name'] for t in available_tables]))
            
            user_prompt = st.text_area("¿Qué información necesitas?", placeholder="Ej: Dame el total de ventas por región para el último mes.")
            
            if st.button("[ GEN ] Generar Query SQL"):
                with st.spinner("La IA está redactando la query..."):
                    gen_resp = requests.post(f"{BACKEND_URL}/queries/generate", json={"prompt": user_prompt})
                    if gen_resp.status_code == 200:
                        st.session_state['generated_sql'] = gen_resp.json()['sql']
                    else:
                        st.error(f"Error: {gen_resp.text}")
            
            if 'generated_sql' in st.session_state:
                st.subheader("Query Generada (Revisión Requerida)")
                sql_to_run = st.text_area("Revisa y ajusta la query si es necesario:", value=st.session_state['generated_sql'], height=200)
                
                target_table = st.text_input("Nombre de la tabla de resultados:", value="query_result_1")
                
                if st.button("[ EXEC ] Ejecutar y Guardar Resultados"):
                    with st.spinner("[ TRANSMITTING TO BIGQUERY ... ]"):
                        exec_resp = requests.post(
                            f"{BACKEND_URL}/queries/execute", 
                            params={"sql": sql_to_run, "target_table": target_table}
                        )
                        if exec_resp.status_code == 200:
                            res = exec_resp.json()
                            st.success(f"Éxito. Registros totales: {res['total_records']}")
                            st.table(res['first_5'])
                        else:
                            st.error(f"Error de ejecución: {exec_resp.text}")

# Table Management Module
elif "Tablas Registradas" in choice:
    st.header("[ LIST ] Gestión de Tablas Registradas")
    
    tables_resp = requests.get(f"{BACKEND_URL}/tables")
    if tables_resp.status_code == 200:
        available_tables = tables_resp.json()
        if not available_tables:
            st.info("No hay tablas registradas en el catálogo.")
        else:
            # Tag Filtering
            all_tags = set()
            for t in available_tables:
                for tag in (t.get('tags') or []):
                    all_tags.add(tag)
            
            selected_filter_tags = st.multiselect("🏷️ Filtrar por Tags", options=sorted(list(all_tags)))
            
            if selected_filter_tags:
                filtered_tables = [t for t in available_tables if any(tag in (t.get('tags') or []) for tag in selected_filter_tags)]
            else:
                filtered_tables = available_tables
            
            if not filtered_tables:
                st.info("No hay tablas que coincidan.")
            else:
                if 'selected_table_id' not in st.session_state:
                    st.session_state['selected_table_id'] = None
                
                # List View
                if st.session_state['selected_table_id'] is None:
                    # Deletion Confirmation logic
                    if st.session_state.get('delete_confirm_id'):
                        target_id = st.session_state['delete_confirm_id']
                        t_to_del = next((t for t in available_tables if t['id'] == target_id), None)
                        if t_to_del:
                            st.warning(f"¿Estás seguro de borrar la tabla '{t_to_del['short_name']}'? Se eliminarán los metadatos y la caché local.")
                            cd1, cd2 = st.columns([1,1])
                            if cd1.button("[ YES ] Confirmar Borrado", type="primary"):
                                del_resp = requests.delete(f"{BACKEND_URL}/tables/{target_id}")
                                if del_resp.status_code == 200:
                                    st.success("Tabla eliminada")
                                    st.session_state['delete_confirm_id'] = None
                                    st.rerun()
                                else:
                                    st.error(f"Error al borrar: {del_resp.text}")
                            if cd2.button("[ NO ] Cancelar"):
                                st.session_state['delete_confirm_id'] = None
                                st.rerun()
                        st.divider()

                    st.write("Seleccione una tabla:")
                    for t in filtered_tables:
                        col1, col2, col3, col4 = st.columns([3, 5, 1, 1])
                        col1.write(f"**{t['short_name']}**")
                        full_id = t.get('full_remote_id', f"{t['project_id']}.{t['dataset_id']}.{t['table_id']}")
                        col2.write(f"`{full_id}`")
                        if col3.button("Detalles", key=f"btn_{t['id']}"):
                            st.session_state['selected_table_id'] = t['id']
                            st.rerun()
                        if col4.button("🗑️", key=f"del_{t['id']}"):
                            st.session_state['delete_confirm_id'] = t['id']
                            st.rerun()
                # Detail View
                else:
                    if st.button("⬅️ Volver"):
                        st.session_state['selected_table_id'] = None
                        st.rerun()
                    
                    st.divider()
                    selected_table = next((t for t in available_tables if t['id'] == st.session_state['selected_table_id']), None)
                    if selected_table:
                        with st.form("edit_form"):
                            st.text_input("ID BigQuery", value=selected_table.get('full_remote_id', f"{selected_table['project_id']}.{selected_table['dataset_id']}.{selected_table['table_id']}"), disabled=True)
                            new_short = st.text_input("Nombre Corto", value=selected_table['short_name'])
                            new_desc = st.text_area("Descripción", value=selected_table.get('description', ''), height=150)
                            
                            if "schema_json" in selected_table and selected_table["schema_json"]:
                                st.subheader("🧬 Esquema Técnico")
                                st.write(pd.DataFrame(selected_table["schema_json"]))
                            
                            current_tags = selected_table.get('tags') or []
                            new_tags_str = st.text_input("Tags (comas)", value=", ".join(current_tags))
                            
                            if st.form_submit_button("Guardar"):
                                new_tags = [tx.strip() for tx in new_tags_str.split(',') if tx.strip()]
                                up_resp = requests.put(
                                    f"{BACKEND_URL}/tables/{selected_table['id']}",
                                    json={"short_name": new_short, "description": new_desc, "tags": new_tags}
                                )
                                if up_resp.status_code == 200:
                                    st.success("Actualizado")
                                    st.session_state['selected_table_id'] = None
                                    st.rerun()
                                else:
                                    st.error("Error")
    else:
        st.error("Error cargando tablas")
