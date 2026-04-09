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
menu = ["[ SYS ] Inicio", "[ DATA ] Catálogo e Ingesta", "[ REGS ] Tablas Registradas", "[ NEUR ] Consultas Inteligentes", "[ SAVE ] Consultas Guardadas"]
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
elif "NEUR" in choice:
    # Check if we came from a redirect
    if st.session_state.get('redirect_to_neur'):
        st.session_state['redirect_to_neur'] = False
        st.info("🔔 Consulta cargada desde 'Consultas Guardadas'. Puedes continuar refinándola aquí.")
    
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
                        generated_sql = gen_resp.json()['sql']
                        st.session_state['generated_sql'] = generated_sql
                        st.session_state['edited_sql'] = generated_sql
                        st.session_state['sql_needs_update'] = True  # Flag to force editor update
                    else:
                        st.error(f"Error: {gen_resp.text}")
            
            if 'generated_sql' in st.session_state:
                st.subheader("Query Generada (Revisión Requerida)")
                
                # Determine which SQL to show in editor
                sql_key = "sql_editor_content"
                
                # If we just refined/generated, use that value and clear the flag
                if st.session_state.get('sql_needs_update'):
                    current_sql = st.session_state.get('edited_sql') or st.session_state['generated_sql']
                    st.session_state[sql_key] = current_sql
                    st.session_state['sql_needs_update'] = False
                elif sql_key in st.session_state:
                    current_sql = st.session_state[sql_key]
                else:
                    current_sql = st.session_state.get('edited_sql') or st.session_state['generated_sql']
                    st.session_state[sql_key] = current_sql
                
                sql_to_run = st.text_area(
                    "Revisa y ajusta la query si es necesario:", 
                    value=current_sql,
                    height=200,
                    key=sql_key
                )
                
                # Save current value to edited_sql
                st.session_state['edited_sql'] = sql_to_run
                
                target_table = st.text_input("Nombre de la tabla de resultados:", value="query_result_1")
                
                # Refinement section
                st.divider()
                st.subheader("[ ✨ ] Mejorar Consulta con IA")
                refinement_instructions = st.text_area(
                    "¿Qué cambios o mejoras necesitas?",
                    placeholder="Ej: Agrega un filtro por fecha, ordena por total descendente, incluye solo registros activos...",
                    height=80
                )
                
                col_gen, col_exec = st.columns([1, 1])
                
                with col_gen:
                    if st.button("[ 🔁 ] Refinar con IA", disabled=not refinement_instructions.strip()):
                        with st.spinner("La IA está refinando la query..."):
                            # Use the current edited SQL as base
                            base_sql = st.session_state.get('edited_sql') or st.session_state['generated_sql']
                            refine_resp = requests.post(
                                f"{BACKEND_URL}/queries/refine",
                                json={
                                    "current_sql": base_sql,
                                    "additional_instructions": refinement_instructions
                                }
                            )
                            if refine_resp.status_code == 200:
                                refined_sql = refine_resp.json()['sql']
                                st.session_state['generated_sql'] = refined_sql
                                st.session_state['edited_sql'] = refined_sql
                                st.session_state['sql_needs_update'] = True  # Flag to update editor on next run
                                st.success("Consulta refinada. Revisa los cambios arriba.")
                                st.rerun()
                            else:
                                st.error(f"Error al refinar: {refine_resp.text}")
                
                with col_exec:
                    if st.button("[ EXEC ] Ejecutar y Guardar Resultados"):
                        # Use edited version if exists, otherwise use what's in the text area
                        final_sql = st.session_state.get('edited_sql') or sql_to_run
                        with st.spinner("[ TRANSMITTING TO BIGQUERY ... ]"):
                            exec_resp = requests.post(
                                f"{BACKEND_URL}/queries/execute", 
                                params={"sql": final_sql, "target_table": target_table}
                            )
                            if exec_resp.status_code == 200:
                                res = exec_resp.json()
                                st.success(f"Éxito. Registros totales: {res['total_records']}")
                                st.table(res['first_50'])
                            else:
                                st.error(f"Error de ejecución: {exec_resp.text}")
                
                # Option to save the query itself
                st.divider()
                st.subheader("[ SAVE ] Guardar Consulta")
                query_name = st.text_input("Nombre de la consulta:", value="mi_consulta")
                query_desc = st.text_input("Descripción:", value="Consulta generada automáticamente")
                query_tags = st.text_input("Tags (comas):", value="")
                
                if st.button("[ 💾 ] Guardar Consulta en Catálogo"):
                    tags_list = [t.strip() for t in query_tags.split(",") if t.strip()]
                    # Use edited version if exists
                    final_sql_to_save = st.session_state.get('edited_sql') or sql_to_run
                    save_q_resp = requests.post(
                        f"{BACKEND_URL}/queries/save",
                        json={
                            "name": query_name,
                            "description": query_desc,
                            "sql_query": final_sql_to_save,
                            "tags": tags_list
                        }
                    )
                    if save_q_resp.status_code == 200:
                        st.success(f"Consulta '{query_name}' guardada exitosamente")
                    else:
                        st.error(f"Error al guardar consulta: {save_q_resp.text}")

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

# Saved Queries Module
elif "SAVE" in choice:
    st.header("[ SAVE ] Gestión de Consultas Guardadas")
    
    with st.expander("[ + ] Crear Nueva Consulta Manual"):
        with st.form("create_manual_query_form"):
            new_q_name = st.text_input("Nombre de la consulta", placeholder="Ej: my_custom_query")
            new_q_desc = st.text_input("Descripción", placeholder="Consulta ingresada manualmente")
            new_q_tags_str = st.text_input("Tags (comas)", placeholder="manual, custom")
            new_q_sql = st.text_area("SQL Query", placeholder="SELECT * FROM dataset.table LIMIT 50;", height=150)
            
            if st.form_submit_button("[ 💾 ] Guardar Consulta Manual"):
                if new_q_name and new_q_sql:
                    tags_list = [t.strip() for t in new_q_tags_str.split(",") if t.strip()]
                    save_q_resp = requests.post(
                        f"{BACKEND_URL}/queries/save",
                        json={
                            "name": new_q_name,
                            "description": new_q_desc,
                            "sql_query": new_q_sql,
                            "tags": tags_list
                        }
                    )
                    if save_q_resp.status_code == 200:
                        st.success(f"Consulta '{new_q_name}' guardada exitosamente")
                        st.rerun()
                    else:
                        st.error(f"Error al guardar consulta: {save_q_resp.text}")
                else:
                    st.warning("Por favor ingresa un nombre y la query SQL.")

    queries_resp = requests.get(f"{BACKEND_URL}/queries")
    if queries_resp.status_code == 200:
        saved_queries = queries_resp.json()
        if not saved_queries:
            st.info("No hay consultas guardadas en el catálogo.")
        else:
            # Tag Filtering
            all_tags = set()
            for q in saved_queries:
                for tag in (q.get('tags') or []):
                    all_tags.add(tag)
            
            selected_filter_tags = st.multiselect("🏷️ Filtrar por Tags", options=sorted(list(all_tags)))
            
            if selected_filter_tags:
                filtered_queries = [q for q in saved_queries if any(tag in (q.get('tags') or []) for tag in selected_filter_tags)]
            else:
                filtered_queries = saved_queries
            
            if not filtered_queries:
                st.info("No hay consultas que coincidan.")
            else:
                if 'selected_query_id' not in st.session_state:
                    st.session_state['selected_query_id'] = None
                
                # List View
                if st.session_state['selected_query_id'] is None:
                    # Deletion Confirmation logic
                    if st.session_state.get('delete_query_confirm_id'):
                        target_id = st.session_state['delete_query_confirm_id']
                        q_to_del = next((q for q in saved_queries if q['id'] == target_id), None)
                        if q_to_del:
                            st.warning(f"¿Estás seguro de borrar la consulta '{q_to_del['name']}'?")
                            cd1, cd2 = st.columns([1,1])
                            if cd1.button("[ YES ] Confirmar Borrado", type="primary"):
                                del_resp = requests.delete(f"{BACKEND_URL}/queries/{target_id}")
                                if del_resp.status_code == 200:
                                    st.success("Consulta eliminada")
                                    st.session_state['delete_query_confirm_id'] = None
                                    st.rerun()
                                else:
                                    st.error(f"Error al borrar: {del_resp.text}")
                            if cd2.button("[ NO ] Cancelar"):
                                st.session_state['delete_query_confirm_id'] = None
                                st.rerun()
                        st.divider()
                    
                    st.write("Seleccione una consulta:")
                    for q in filtered_queries:
                        col1, col2, col3, col4 = st.columns([3, 5, 1, 1])
                        col1.write(f"**{q['name']}**")
                        desc = q.get('description', '')[:50] + "..." if q.get('description') and len(q['description']) > 50 else q.get('description', '')
                        col2.write(f"_{desc}_")
                        if col3.button("Detalles", key=f"btn_q_{q['id']}"):
                            st.session_state['selected_query_id'] = q['id']
                            st.rerun()
                        if col4.button("🗑️", key=f"del_q_{q['id']}"):
                            st.session_state['delete_query_confirm_id'] = q['id']
                            st.rerun()
                
                # Detail View
                else:
                    if st.button("⬅️ Volver"):
                        st.session_state['selected_query_id'] = None
                        st.rerun()
                    
                    st.divider()
                    selected_query = next((q for q in saved_queries if q['id'] == st.session_state['selected_query_id']), None)
                    if selected_query:
                        with st.form("edit_query_form"):
                            new_name = st.text_input("Nombre", value=selected_query['name'])
                            new_desc = st.text_area("Descripción", value=selected_query.get('description', ''), height=100)
                            st.subheader("🧬 SQL Query")
                            st.code(selected_query['sql_query'], language='sql')
                            
                            current_tags = selected_query.get('tags') or []
                            new_tags_str = st.text_input("Tags (comas)", value=", ".join(current_tags))
                            
                            col_exec, col_save = st.columns(2)
                            with col_exec:
                                target_table = st.text_input("Tabla de resultados:", value=f"result_{selected_query['name']}")
                            
                            submitted = st.form_submit_button("Guardar Cambios")
                            if submitted:
                                new_tags = [tx.strip() for tx in new_tags_str.split(',') if tx.strip()]
                                up_resp = requests.put(
                                    f"{BACKEND_URL}/queries/{selected_query['id']}",
                                    json={"name": new_name, "description": new_desc, "tags": new_tags}
                                )
                                if up_resp.status_code == 200:
                                    st.success("Consulta actualizada")
                                    st.session_state['selected_query_id'] = None
                                    st.rerun()
                                else:
                                    st.error("Error al actualizar")
                        
                        # Load into Query Generator
                        st.divider()
                        if st.button("[ 🧠 ] Cargar en Generador de Consultas"):
                            st.session_state['generated_sql'] = selected_query['sql_query']
                            st.session_state['edited_sql'] = selected_query['sql_query']
                            st.session_state['sql_needs_update'] = True
                            st.session_state['selected_query_id'] = None
                            # Set a flag to redirect to NEUR page
                            st.session_state['redirect_to_neur'] = True
                            st.rerun()
                        
                        # Execute saved query
                        st.divider()
                        if st.button("[ ▶️ ] Ejecutar Consulta en BigQuery"):
                            with st.spinner("[ TRANSMITTING TO BIGQUERY ... ]"):
                                exec_resp = requests.post(
                                    f"{BACKEND_URL}/queries/execute",
                                    params={"sql": selected_query['sql_query'], "target_table": target_table}
                                )
                                if exec_resp.status_code == 200:
                                    res = exec_resp.json()
                                    st.success(f"Éxito. Registros totales: {res['total_records']}")
                                    st.table(res['first_50'])
                                else:
                                    st.error(f"Error de ejecución: {exec_resp.text}")
    else:
        st.error("Error cargando consultas guardadas")
