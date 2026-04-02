CREATE OR REPLACE TABLE `data-exp-contactcenter.100x100.new_calculated_mejorada` AS

WITH 
-- 1. Base Interactions (Human)
basequ AS (
  SELECT
    qua.conversation_id,
    qua.conversation_date AS call_date,
    qua.queue_name AS skill_name,
    qua.factory_name AS factory_name,
    COALESCE(qua.talk_time_second, 0) + COALESCE(qua.held_time_second, 0) AS aht,
    qua.message_type,
    qua.agent_bp_number AS bp_executive_num
  FROM `cuscare-data-prod.contact_center_interaction.conversation_detail_unified` AS qua
  WHERE conversation_date >= '2024-01-01' 
    AND conversation_date < CURRENT_DATE()
    AND qua.factory_name IN ('AeC','Almacontact','KONECTA BR','Konecta')
    AND qua.originating_direction_type = 'inbound'
    AND qua.talk_time_second IS NOT NULL
    AND NOT REGEXP_CONTAINS(UPPER(qua.queue_name), 'CARGO')
  GROUP BY ALL
),

-- 2. Enrich with Skills
basequ_enriched AS (
  SELECT DISTINCT
    b.*,
    sk.Canal_de_Atencion,
    sk.Departamento_SAG,
    sk.Division,
    sk.Fabrica AS Fabrica_dic,
    sk.ID_Cola,
    sk.Cola_con_Demanda,
    sk.Jefatura,
    sk.SubGerente,
    sk.Gerencia,
    sk.Script,
    sk.ID_Script
  FROM basequ b
  LEFT JOIN `data-exp-contactcenter.100x100.asociacion_skill` sk
    ON TRIM(sk.Nombre_de_Cola) = TRIM(b.skill_name)
),

-- 3. Bot Retention Information
retention_all AS (
  SELECT
    conversation_id,
    DATE(conversation_start_datetime) AS call_date,
    ANY_VALUE(market_code) AS market_code,
    ANY_VALUE(channel_type) AS channel_type,
    ANY_VALUE(is_voicebot) AS is_voicebot,
    ANY_VALUE(is_has_queue) AS is_has_queue,
    ANY_VALUE(intent_type) AS intent_type,
    ANY_VALUE(category_voicebot_typification) AS category_voicebot_typification,
    ANY_VALUE(voicebot_category_process) AS voicebot_category_process
  FROM `cuscare-data-prod.virtual_assistant_metrics.bot_retention`
  WHERE DATE(conversation_start_datetime) >= '2024-01-01' 
    AND DATE(conversation_start_datetime) < CURRENT_DATE()
    AND originating_direction_type = 'inbound'
  GROUP BY ALL
),

-- 4. Human Interactions Aggregated
qu AS (
  SELECT
    b.conversation_id,
    ANY_VALUE(b.call_date) AS call_date,
    ANY_VALUE(b.message_type) AS message_type,
    ANY_VALUE(r.market_code) AS market_code,
    ARRAY_AGG(b.skill_name ORDER BY b.aht DESC, b.skill_name) AS skill_name,
    ARRAY_AGG(b.factory_name ORDER BY b.aht DESC, b.skill_name) AS factory_name,
    ARRAY_AGG(b.aht ORDER BY b.aht DESC, b.skill_name) AS aht_by_skill,
    ARRAY_AGG(
      STRUCT(
        CAST(b.skill_name AS STRING) AS skill_name,
        CAST(b.bp_executive_num AS STRING) AS bp_executive_num,
        CAST(b.aht AS FLOAT64) AS aht,
        CAST(b.Canal_de_Atencion AS STRING) AS Canal_de_Atencion,
        CAST(b.Departamento_SAG AS STRING) AS Departamento_SAG,
        CAST(b.Division AS STRING) AS Division,
        CAST(b.Fabrica_dic AS STRING) AS Fabrica_dic,
        CAST(b.ID_Cola AS STRING) AS ID_Cola,
        CAST(b.Cola_con_Demanda AS STRING) AS Cola_con_Demanda,
        CAST(b.Jefatura AS STRING) AS Jefatura,
        CAST(b.SubGerente AS STRING) AS SubGerente,
        CAST(b.Gerencia AS STRING) AS Gerencia,
        CAST(b.Script AS STRING) AS Script,
        CAST(b.ID_Script AS STRING) AS ID_Script
      )
      ORDER BY b.aht DESC, b.skill_name
    ) AS skill_lookup,
    ARRAY_AGG(DISTINCT b.bp_executive_num IGNORE NULLS ORDER BY b.bp_executive_num) AS bp_executive_num
  FROM basequ_enriched AS b
  LEFT JOIN retention_all AS r ON b.conversation_id = r.conversation_id
  GROUP BY b.conversation_id
),

-- 5. Cases / Claims
base_cases AS (
  SELECT
    ticket_id AS conversation_id,
    DATE(MIN(created_dt)) AS call_date,
    ARRAY_AGG(DISTINCT agent_group_name IGNORE NULLS) AS skill_name,
    ARRAY_AGG(DISTINCT COALESCE(factory_name,'NO_FACTORY') IGNORE NULLS) AS factory_name,
    ARRAY_AGG(CASE WHEN language_name LIKE "PT%" THEN "BR" ELSE "SSC" END IGNORE NULLS ORDER BY created_dt DESC LIMIT 1)[OFFSET(0)] AS market_code,
    'CASES' AS channel_type,
    ARRAY_AGG(claim_ai_typification IGNORE NULLS ORDER BY created_dt DESC LIMIT 1)[OFFSET(0)] AS cat_bot,
    'HUMAN' AS is_human,
    NULL AS skill_lookup,
    ARRAY_AGG(claim_ai_subtypification IGNORE NULLS ORDER BY created_dt DESC LIMIT 1)[OFFSET(0)] AS cat_pca
  FROM `sp-te-segdlak-prod-ky3g.dmt_customer_us.cus_claim`
  WHERE created_dt >= '2024-01-01'
    AND NOT REGEXP_CONTAINS(tag_list, r"monoquebrado|multiquebrado")
    AND tag_list NOT LIKE "%project_child%"
    AND UPPER(agent_name) != "LATAM AIRLINES"
    AND NOT REGEXP_CONTAINS(UPPER(subject_desc), r"TEST GOPE")
    AND NOT REGEXP_CONTAINS(agent_group_name, r"(?i)SOPORTE|SUPORTE")
    AND DATETIME_DIFF(solved_dt, created_dt, SECOND) > 10
    AND (
      (agent_group_name != "HVC KON BR" AND UPPER(contact_form_name) NOT IN ("AGWS","WEB DEVOLUCIONES","URA","SPECIAL SERVICES"))
      OR
      (agent_group_name = "HVC KON BR" AND UPPER(contact_form_name) = "SPECIAL SERVICES")
    )
  GROUP BY ticket_id
),

-- 6. PCA (Post Call Analytics)
pca AS (
  SELECT
    conversation_id,
    ARRAY_AGG(
      STRUCT(
        SPLIT(conversation_id_original, '_')[SAFE_OFFSET(1)] AS agent_id,
        first_category,
        second_category,
        third_category
      ) ORDER BY SPLIT(conversation_id_original, '_')[SAFE_OFFSET(1)] ASC
    ) AS all_agents,
    ARRAY_AGG(first_category ORDER BY SPLIT(conversation_id_original, '_')[SAFE_OFFSET(1)] ASC LIMIT 1)[OFFSET(0)] AS first_category,
    ARRAY_AGG(second_category ORDER BY SPLIT(conversation_id_original, '_')[SAFE_OFFSET(1)] ASC LIMIT 1)[OFFSET(0)] AS second_category,
    ARRAY_AGG(third_category ORDER BY SPLIT(conversation_id_original, '_')[SAFE_OFFSET(1)] ASC LIMIT 1)[OFFSET(0)] AS third_category
  FROM `cuscare-data-prod.post_call_analytics.pca_conversation_category`
  WHERE load_datetime >= '2024-01-01' AND load_datetime < CURRENT_DATE()
  GROUP BY conversation_id
),

-- 7. Unified Calls & Bots
bot_filtered AS (
  SELECT 
    conversation_id AS conversation_id,
    call_date,
    NULL AS skill_name,
    NULL AS factory_name,
    market_code,
    CASE WHEN channel_type = 'message' THEN 'bot_wsp' ELSE channel_type END AS channel_type,
    category_voicebot_typification AS cat_bot,
    'NOT_HUMAN' AS is_human,
    NULL AS skill_lookup
  FROM retention_all
  WHERE is_voicebot = 1 AND is_has_queue = 0
),

full_calls_unioned AS (
  SELECT 
    CAST(COALESCE(qu.conversation_id, bf.conversation_id) AS STRING) AS conversation_id,
    COALESCE(qu.call_date, bf.call_date) AS call_date,
    qu.skill_name,
    qu.factory_name,
    CAST(COALESCE(SAFE_CAST(qu.market_code AS STRING), bf.market_code) AS STRING) AS market_code,
    CAST(COALESCE(qu.message_type, bf.channel_type) AS STRING) AS channel_type,
    CAST(bf.cat_bot AS STRING) AS cat_bot,
    CASE
      WHEN qu.conversation_id IS NOT NULL AND bf.conversation_id IS NOT NULL THEN 'BOTH'
      WHEN qu.conversation_id IS NOT NULL THEN 'HUMAN'
      ELSE 'NOT_HUMAN'
    END AS is_human,
    CAST(qu.skill_lookup AS ARRAY<STRUCT<skill_name STRING, bp_executive_num STRING, aht FLOAT64, Canal_de_Atencion STRING, Departamento_SAG STRING, Division STRING, Fabrica_dic STRING, ID_Cola STRING, Cola_con_Demanda STRING, Jefatura STRING, SubGerente STRING, Gerencia STRING, Script STRING, ID_Script STRING>>) AS skill_lookup,
    CAST(NULL AS STRING) AS cat_pca -- Placeholder for cases
  FROM qu
  FULL JOIN bot_filtered bf ON qu.conversation_id = bf.conversation_id
  
  UNION ALL
  
  SELECT
    CAST(conversation_id AS STRING),
    call_date,
    skill_name,
    factory_name,
    CAST(market_code AS STRING),
    CAST(channel_type AS STRING),
    CAST(cat_bot AS STRING),
    CAST(is_human AS STRING),
    CAST(NULL AS ARRAY<STRUCT<skill_name STRING, bp_executive_num STRING, aht FLOAT64, Canal_de_Atencion STRING, Departamento_SAG STRING, Division STRING, Fabrica_dic STRING, ID_Cola STRING, Cola_con_Demanda STRING, Jefatura STRING, SubGerente STRING, Gerencia STRING, Script STRING, ID_Script STRING>>) AS skill_lookup,
    CAST(cat_pca AS STRING)
  FROM base_cases
),

-- 8. Final Join and Mercado Calculation
final_unioned AS (
  SELECT 
    fc.*,
    pca.first_category AS cat_pca_human,
    pca.second_category,
    pca.third_category,
    pca.all_agents
  FROM full_calls_unioned fc
  LEFT JOIN pca ON fc.conversation_id = pca.conversation_id
)

SELECT 
  f.* EXCEPT(cat_pca_human, cat_pca, market_code),
  COALESCE(f.cat_pca, f.cat_pca_human) AS cat_pca,
  -- Integrated Mercado Calculation
  CASE 
    WHEN f.market_code = "BR" THEN "BR"
    WHEN (f.market_code IS NULL OR f.market_code = "") AND s.country IS NOT NULL THEN UPPER(s.country)
    ELSE "SSC"
  END AS mercado,
  -- Resulting Market Code (replaces the original market_code)
  COALESCE(
    f.market_code, 
    CASE 
      WHEN (f.market_code IS NULL OR f.market_code = "") AND s.country IS NOT NULL THEN UPPER(s.country)
      ELSE "SSC"
    END
  ) AS market_code
FROM final_unioned f
LEFT JOIN `data-exp-contactcenter.ws_tpo_resp.novoz` AS s
  ON f.skill_name[SAFE_OFFSET(0)] = s.sagg
;
