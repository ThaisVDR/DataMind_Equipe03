-- Consultas internas. Aplicar supressao de pequenos grupos antes de publicar.
SELECT source_key,family,rows_loaded,run_id FROM audit.fd_cobertura ORDER BY source_key;

-- P1: agregado da coorte 2015 presencial em 2024, calculado pelas contagens.
SELECT coorte,referencia,sum(ingressantes) ingressantes,
 100.0*sum(concluintes_acum)/nullif(sum(denominador),0) tca,
 100.0*sum(desistentes_acum)/nullif(sum(denominador),0) tda,
 100.0*sum(permanencia)/nullif(sum(denominador),0) tap
FROM core.trajetoria_acumulada_mt
WHERE coorte=2015 AND referencia=2024 AND modalidade='1'
GROUP BY coorte,referencia;

-- Proxy do Censo: comparar anos na mesma granularidade.
SELECT * FROM mart.censo_rede_modalidade_mt ORDER BY ano,modalidade,categoria;

-- Indicadores sem conceito: nulo nao significa nota zero.
SELECT tipo,ano,count(*) linhas,count(*) FILTER(WHERE continuo IS NULL) sem_continuo
FROM core.indicadores_mt GROUP BY tipo,ano ORDER BY tipo,ano;

-- IBGE: separar zeros, ausencia e demais simbolos, sem somar categorias.
SELECT tabela,status_valor,count(*) linhas FROM core.ibge_mt
GROUP BY tabela,status_valor ORDER BY tabela,status_valor;
