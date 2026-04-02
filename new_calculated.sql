CREATE OR REPLACE TABLE `data-exp-contactcenter.100x100.new_calculated` AS

WITH 

basequ as
(
  SELECT
  qua.conversation_id,
  qua.conversation_date as call_date,
  qua.queue_name as skill_name,
  qua.factory_name AS factory_name,
  COALESCE(qua.talk_time_second, 0) + COALESCE(qua.held_time_second, 0) AS aht,
  qua.message_type,
  qua.agent_bp_number AS bp_executive_num
  FROM `cuscare-data-prod.contact_center_interaction.conversation_detail_unified` as qua
  WHERE conversation_date >= '2024-01-01' AND conversation_date < CURRENT_DATE()
  AND qua.factory_name IN ('AeC','Almacontact','KONECTA BR','Konecta')
  AND qua.originating_direction_type = 'inbound'
  AND qua.talk_time_second IS NOT NULL
  AND NOT REGEXP_CONTAINS(UPPER(qua.queue_name), 'CARGO')
  --AND NOT UPPER(qua.queue_name) LIKE '%CARGO%'
  GROUP BY ALL
),
basequ_enriched AS (
  SELECT distinct
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
    ON trim(sk.Nombre_de_Cola) = trim(b.skill_name)
),
ret AS (
  SELECT
    conversation_id,
    ANY_VALUE(market_code) AS market_code
  FROM `cuscare-data-prod.virtual_assistant_metrics.bot_retention`
  GROUP BY conversation_id
),
qu AS (
  SELECT
    b.conversation_id,
    ANY_VALUE(b.call_date) AS call_date,
    ANY_VALUE(b.message_type) AS message_type,
    ANY_VALUE(r.market_code) AS market_code,

    -- arrays ordenados por AHT desc (alineados entre sí)
    ARRAY_AGG(b.skill_name ORDER BY b.aht DESC, b.skill_name) AS skill_name,
    ARRAY_AGG(b.factory_name ORDER BY b.aht DESC, b.skill_name) AS factory_name,
    ARRAY_AGG(b.aht ORDER BY b.aht DESC, b.skill_name) AS aht_by_skill,

    ARRAY_AGG(
      STRUCT(
        b.skill_name AS skill_name,
        b.bp_executive_num,
        b.aht,
        b.Canal_de_Atencion,
        b.Departamento_SAG,
        b.Division,
        b.Fabrica_dic,
        b.ID_Cola,
        b.Cola_con_Demanda,
        b.Jefatura,
        b.SubGerente,
        b.Gerencia,
        b.Script,
        b.ID_Script
      )
      ORDER BY b.aht DESC, b.skill_name
    ) AS skill_lookup,

    -- bp list (no depende de skill, ordenado numérico)
    ARRAY_AGG(DISTINCT b.bp_executive_num IGNORE NULLS ORDER BY b.bp_executive_num) AS bp_executive_num

  FROM basequ_enriched as b
  LEFT JOIN ret as r
    ON b.conversation_id = r.conversation_id
  GROUP BY b.conversation_id
),



/* AS(
  SELECT
  qua.conversation_id,
  qua.conversation_date as call_date,
  ARRAY_AGG(DISTINCT qua.queue_name) AS skill_name,
  ARRAY_AGG(DISTINCT qua.factory_name) AS factory_name,
  r.market_code as market_code,
  qua.message_type,
  ARRAY_AGG(DISTINCT qua.agent_bp_number IGNORE NULLS ORDER BY qua.agent_bp_number) AS bp_executive_num
  FROM `cuscare-data-prod.contact_center_interaction.conversation_detail_unified` as qua
  left join `cuscare-data-prod.virtual_assistant_metrics.bot_retention` as r on qua.conversation_id=r.conversation_id
  WHERE conversation_date >= '2024-01-01' AND conversation_date < CURRENT_DATE()
  AND qua.factory_name IN ('AeC','Almacontact','KONECTA BR','Konecta')
  AND qua.originating_direction_type = 'inbound'
  AND qua.talk_time_second IS NOT NULL
  AND NOT UPPER(qua.queue_name) LIKE '%CARGO%'
  GROUP BY ALL
 

),*/
/******************************************************************************/
base AS (
  SELECT
    ticket_id,
    created_dt,
    agent_group_name,
    factory_name,
    case when language_name like "PT%" then "BR" else "SSC" end as language_name,
    contact_form_name,
    agent_name,
    subject_desc,
    tag_list,
    solved_dt,
    claim_ai_typification,
    claim_ai_subtypification
  FROM `sp-te-segdlak-prod-ky3g.dmt_customer_us.cus_claim`
  WHERE
    EXTRACT(YEAR FROM created_dt) in (2024,2025,2026)
    AND NOT REGEXP_CONTAINS(tag_list, r"monoquebrado|multiquebrado")
    AND tag_list NOT LIKE "%project_child%"
    AND UPPER(agent_name) != "LATAM AIRLINES"
    AND NOT REGEXP_CONTAINS(UPPER(subject_desc), r"TEST GOPE")
    AND NOT REGEXP_CONTAINS(agent_group_name, r"(?i)SOPORTE|SUPORTE")
    AND DATETIME_DIFF(solved_dt, created_dt, SECOND) > 10
    AND (
      -- Caso general: excluir HVC KON BR y excluir estos contact_form_name
      (
        agent_group_name != "HVC KON BR"
        AND UPPER(contact_form_name) NOT IN ("AGWS","WEB DEVOLUCIONES","URA","SPECIAL SERVICES")
      )
      OR
      -- Excepción: solo HVC KON BR con SPECIAL SERVICES
      (
        agent_group_name = "HVC KON BR"
        AND UPPER(contact_form_name) = "SPECIAL SERVICES"
      )
    )
)
/************************************************************/

,
bot AS( 
  SELECT 
  conversation_id AS interaction_id,
  entity_id,
  customer_id,
  DATE(conversation_start_datetime) AS call_date,
  market_code,
  channel_type,
  is_voicebot,
  is_has_queue,
  intent_type,
  category_voicebot_typification,
  voicebot_category_process,

  FROM `cuscare-data-prod.virtual_assistant_metrics.bot_retention`
  
  WHERE date(conversation_start_datetime) >= '2024-01-01' AND date(conversation_start_datetime) < CURRENT_DATE()
  AND originating_direction_type = 'inbound'
  AND is_voicebot = 1
  AND is_has_queue = 0
  AND channel_type='voice'
),
/************************************************************/

bot_wsp AS( 
  SELECT 
  conversation_id AS interaction_id,
  entity_id,
  customer_id,
  DATE(conversation_start_datetime) AS call_date,
  market_code,
  channel_type,
  is_voicebot,
  is_has_queue,
  intent_type,
  category_voicebot_typification,
  voicebot_category_process,
  FROM `cuscare-data-prod.virtual_assistant_metrics.bot_retention`
  WHERE date(conversation_start_datetime) >= '2024-01-01' AND date(conversation_start_datetime) < CURRENT_DATE()
  AND originating_direction_type = 'inbound'
  AND is_voicebot = 1
  AND is_has_queue = 0
  AND channel_type='message'
),
/************************************************************/

/*pca AS(
  SELECT
  conversation_id as conversation_id,
  first_category,
  second_category,
  third_category
  FROM `cuscare-data-prod.post_call_analytics.pca_conversation_category`
  WHERE load_datetime  >= '2024-01-01' AND load_datetime < CURRENT_DATE()
  )
*/
 raw_data AS (
  SELECT
    conversation_id,
    -- Extraemos el agent_id usando el guion bajo como separador
    SPLIT(conversation_id_original, '_')[SAFE_OFFSET(1)] AS agent_id,
    first_category,
    second_category,
    third_category
  FROM `cuscare-data-prod.post_call_analytics.pca_conversation_category`
  WHERE load_datetime >= '2024-01-01' 
    AND load_datetime < CURRENT_DATE()
),
pca0 AS (
  SELECT
    conversation_id,
    -- 1. Creamos un ARRAY de STRUCTs con todos los agentes y sus categorías
    ARRAY_AGG(
      STRUCT(
        agent_id,
        first_category,
        second_category,
        third_category
      ) ORDER BY agent_id ASC
    ) AS all_agents,
    
    -- 2. Obtenemos las categorías del primer agente (el menor agent_id)
    -- Usamos LIMIT 1 dentro del ARRAY_AGG y luego accedemos al primer elemento [OFFSET(0)]
    ARRAY_AGG(
      STRUCT(first_category, second_category, third_category) 
      ORDER BY agent_id ASC LIMIT 1
    )[OFFSET(0)] AS first_agent_details
  FROM raw_data
  GROUP BY conversation_id
),
-- Consulta final para aplanar los campos del primer agente si los necesitas como columnas individuales
pca as(
SELECT 
  conversation_id,
  all_agents, -- Este es el struct/array con todo el historial
  first_agent_details.first_category AS first_category,
  first_agent_details.second_category AS second_category,
  first_agent_details.third_category AS third_category
FROM pca0
)
,
/************************************************************

zona as   
(
select distinct 
queue_name, 
CASE 
    WHEN queue_name LIKE 'AMC%' THEN 'AMC'
    WHEN queue_name LIKE 'KON_BR%' THEN 'KON_BR' 
    WHEN queue_name LIKE 'SUPORTE%' THEN 'SUPORTE'
    WHEN queue_name LIKE 'FS_CC%' THEN 'FS_CC'
    WHEN queue_name LIKE 'FS%' THEN 'FS'
    WHEN queue_name LIKE 'EST_SOPORTE%' THEN 'ESTADO'
    WHEN queue_name LIKE 'S02_EST%' THEN 'ESTADO'    
    WHEN queue_name LIKE 'KON%' THEN 'KON'
    WHEN queue_name LIKE 'AEC%' THEN 'AEC'
    WHEN queue_name LIKE 'LT%' THEN 'LT'
    WHEN queue_name LIKE 'HVC_BLACK%' THEN 'HVC_BLACK'
    WHEN queue_name LIKE 'LAE%' THEN 'LAE'
    ELSE 'S/I'
  END AS fabrica,
  factory_name,
  CASE 
    WHEN queue_name LIKE '%PT' THEN 'PT'
    WHEN queue_name LIKE '%ES' THEN 'ES'
    WHEN queue_name LIKE '%EN' THEN 'EN'
    WHEN queue_name LIKE '%EN' THEN 'EN'
    when queue_name LIKE 'KON_BR%' then "PT"
    WHEN queue_name LIKE 'SUPORTE%' then "PT"
    WHEN queue_name LIKE '%BR' THEN 'PT'
    WHEN queue_name LIKE '%SSC' THEN 'ES'
    WHEN queue_name LIKE 'LATAM_HELPCENTER' THEN 'PT'
    ELSE 'S/I'
  END AS idioma,
count(*) as n
from `cuscare-data-prod.contact_center_interaction.conversation_detail_unified`
where conversation_date>="2024-01-01"
and queue_name not like "%GSS%"
and queue_name not like "%CARGO%"
and originating_direction_type="inbound"
and queue_name not in ("EPA_TRIGGER","SCRIPT_FS_CONSULT","SCRIPT_CC_CONSULT","SCRIPT_BAGGAGE_PROBLEM_TRANSFER","AMC_SERVICIO_PAQUETES_FFP","AMC_SERVICIO_PAQUETES_NFFP")
group by all
),
zona1 as   
(
select *,
case when idioma="PT" then  "BR" else "SSC" end as zona
 from zona  
where 1=1
--and (fabrica="S/I" or idioma="S/I")
and n>99
order by 5 desc),





************************************************************/
full_calls AS(
  SELECT 
    COALESCE(qu.conversation_id, bot.interaction_id) AS conversation_id,
    COALESCE(qu.call_date, bot.call_date) AS call_date,
    qu.skill_name,
    qu.factory_name AS factory_name,
    COALESCE(safe_cast(qu.market_code as STRING), bot.market_code) AS market_code,
    COALESCE(qu.message_type, bot.channel_type) AS channel_type,
    category_voicebot_typification AS cat_bot,
    CASE
      WHEN qu.conversation_id IS NULL THEN 'NOT_HUMAN'
      WHEN bot.interaction_id IS NULL THEN 'HUMAN'
      WHEN qu.conversation_id = bot.interaction_id THEN 'BOTH'
    END AS is_human,
    qu.skill_lookup
  FROM qu
  FULL JOIN  bot
  ON qu.conversation_id = bot.interaction_id
  
  UNION ALL
  
  SELECT
    interaction_id AS conversation_id,
    call_date,
    null AS skill_name,
    null AS factory_name,
    market_code,
    'bot_wsp' AS channel_type,
    category_voicebot_typification AS cat_bot,
    'NOT_HUMAN' AS is_human,
    null as skill_lookup
  FROM bot_wsp
)
/*,*/

/************************************************************/
--base1 as   
--(
SELECT 
  full_calls.*,
  pca.first_category AS cat_pca,
  pca.second_category,
  pca.third_category,
  pca.all_agents
FROM full_calls
LEFT JOIN pca 
ON full_calls.conversation_id = pca.conversation_id

UNION ALL


SELECT
  ticket_id AS conversation_id,
  DATE(MIN(created_dt)) AS call_date,   -- fecha de creación (mínima) del ticket
  ARRAY_AGG(DISTINCT agent_group_name IGNORE NULLS) AS skill_name,
  ARRAY_AGG(DISTINCT COALESCE(factory_name,'NO_FACTORY') IGNORE NULLS) AS factory_name,
  -- último valor no nulo por created_dt
  ARRAY_AGG(language_name IGNORE NULLS ORDER BY created_dt DESC LIMIT 1)[OFFSET(0)] AS market_code,
  'CASES' AS channel_type,
  ARRAY_AGG(claim_ai_typification IGNORE NULLS ORDER BY created_dt DESC LIMIT 1)[OFFSET(0)] AS category,
  'HUMAN' AS is_human,
  null as skill_lookup,
  ARRAY_AGG(claim_ai_subtypification IGNORE NULLS ORDER BY created_dt DESC LIMIT 1)[OFFSET(0)] AS cat_pca,
  null,
  null,
  null as all_agents
FROM base
GROUP BY ticket_id
ORDER BY conversation_id
--)

--select * from base1
--`data-exp-contactcenter.ws_tpo_resp.novoz`

;
create or replace table `data-exp-contactcenter.100x100.new_calculated` as
select nc.* ,
case when market_code="BR" then "BR"
 when (market_code is null and s.country is not null)  then upper(s.country)
 when market_code is not null then "SSC"
 else "SSC"
 end as mercado
from `data-exp-contactcenter.100x100.new_calculated` nc
left join  `data-exp-contactcenter.ws_tpo_resp.novoz` AS s
on nc.skill_name[SAFE_OFFSET(0)] = s.sagg

;
update `data-exp-contactcenter.100x100.new_calculated`
set market_code=mercado
where 1=1
and market_code is null
and mercado is not null