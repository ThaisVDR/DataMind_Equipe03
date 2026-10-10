CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE TABLE IF NOT EXISTS audit.fd_dataset (
 version text PRIMARY KEY, source_key text NOT NULL, family text NOT NULL,
 source_path text NOT NULL, sha256 text NOT NULL, state text NOT NULL,
 rows_loaded bigint, details jsonb NOT NULL DEFAULT '{}', updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS audit.fd_batch (
 run_id text PRIMARY KEY, state text NOT NULL, manifest jsonb NOT NULL,
 details jsonb NOT NULL DEFAULT '{}', updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS audit.fd_active (
 source_key text PRIMARY KEY, version text NOT NULL REFERENCES audit.fd_dataset(version), run_id text NOT NULL
);
CREATE TABLE IF NOT EXISTS staging.fd_raw (
 version text NOT NULL, row_number bigint NOT NULL, payload jsonb NOT NULL,
 PRIMARY KEY(version,row_number)
);
CREATE TABLE IF NOT EXISTS core.fd_trajetoria (
 version text NOT NULL, curso text NOT NULL, ies text NOT NULL, coorte int NOT NULL,
 referencia int NOT NULL, municipio text, modalidade text NOT NULL, categoria text NOT NULL,
 cine text, area_cine text, nome_curso text, ingressantes bigint NOT NULL CHECK(ingressantes>=0),
 permanencia bigint NOT NULL CHECK(permanencia>=0), concluintes_ano bigint NOT NULL CHECK(concluintes_ano>=0),
 desistentes_ano bigint NOT NULL CHECK(desistentes_ano>=0), falecidos_ano bigint NOT NULL CHECK(falecidos_ano>=0),
 tap numeric NOT NULL, tca numeric NOT NULL, tda numeric NOT NULL, tcan numeric NOT NULL, tada numeric NOT NULL,
 PRIMARY KEY(version,curso,coorte,referencia)
);
CREATE TABLE IF NOT EXISTS core.fd_censo (
 version text NOT NULL, ano int NOT NULL, curso text NOT NULL, ies text NOT NULL,
 municipio text NOT NULL, modalidade text NOT NULL, nivel text NOT NULL,
 categoria text NOT NULL, rede text, cine text, nome_curso text,
 matriculas bigint NOT NULL CHECK(matriculas>=0), ingressantes bigint NOT NULL CHECK(ingressantes>=0),
 concluintes bigint NOT NULL CHECK(concluintes>=0), desvinculados bigint NOT NULL CHECK(desvinculados>=0),
 transferidos bigint NOT NULL CHECK(transferidos>=0), vagas bigint NOT NULL CHECK(vagas>=0),
 ingressantes_financiados bigint CHECK(ingressantes_financiados>=0), medidas jsonb NOT NULL,
 PRIMARY KEY(version,ano,curso,municipio,modalidade,nivel)
);
CREATE TABLE IF NOT EXISTS core.fd_indicador (
 version text NOT NULL, tipo text NOT NULL, ano int NOT NULL, entidade text NOT NULL,
 curso text, ies text NOT NULL, municipio text, modalidade text, categoria text,
 continuo numeric, faixa text, inscritos bigint CHECK(inscritos>=0), participantes bigint CHECK(participantes>=0),
 proficiencia numeric CHECK(proficiencia BETWEEN 0 AND 1), motivo_ausencia text,
 PRIMARY KEY(version,tipo,ano,entidade)
);
CREATE TABLE IF NOT EXISTS core.fd_ibge (
 version text NOT NULL, chave text NOT NULL, tabela text NOT NULL, variavel text NOT NULL,
 variavel_nome text NOT NULL, unidade text NOT NULL, nivel text NOT NULL CHECK(nivel IN ('N3','N6')),
 localidade text NOT NULL, localidade_nome text, periodo text NOT NULL,
 valor numeric, valor_original text NOT NULL, status_valor text NOT NULL,
 categorias jsonb NOT NULL, rotulos_categorias jsonb NOT NULL,
 PRIMARY KEY(version,chave)
);
CREATE OR REPLACE VIEW core.trajetoria_mt AS
 SELECT c.* FROM core.fd_trajetoria c JOIN audit.fd_active a USING(version);
CREATE OR REPLACE VIEW core.censo_mt AS
 SELECT c.* FROM core.fd_censo c JOIN audit.fd_active a USING(version);
CREATE OR REPLACE VIEW core.indicadores_mt AS
 SELECT c.* FROM core.fd_indicador c JOIN audit.fd_active a USING(version);
CREATE OR REPLACE VIEW core.ibge_mt AS
 SELECT c.* FROM core.fd_ibge c JOIN audit.fd_active a USING(version);
CREATE OR REPLACE VIEW core.trajetoria_acumulada_mt AS
 SELECT *, ingressantes-falecidos_acum denominador FROM (
 SELECT *,sum(concluintes_ano) OVER w concluintes_acum,
 sum(desistentes_ano) OVER w desistentes_acum,sum(falecidos_ano) OVER w falecidos_acum
 FROM core.trajetoria_mt
 WINDOW w AS (PARTITION BY curso,coorte ORDER BY referencia ROWS UNBOUNDED PRECEDING)) q;
CREATE OR REPLACE VIEW mart.trajetoria_coorte_mt AS
 SELECT coorte,referencia,modalidade,categoria,area_cine,count(*) cursos,
 sum(ingressantes) ingressantes,sum(permanencia) permanencia,
 sum(concluintes_acum) concluintes,sum(desistentes_acum) desistentes,
 sum(falecidos_acum) falecidos,sum(denominador) denominador,
 100.0*sum(concluintes_acum)/nullif(sum(denominador),0) tca,
 100.0*sum(desistentes_acum)/nullif(sum(denominador),0) tda,
 100.0*sum(permanencia)/nullif(sum(denominador),0) tap,
 100.0*sum(desistentes_ano)/nullif(sum(denominador),0) tada
 FROM core.trajetoria_acumulada_mt GROUP BY coorte,referencia,modalidade,categoria,area_cine;
CREATE OR REPLACE VIEW mart.censo_rede_modalidade_mt AS
 SELECT ano,modalidade,categoria,rede,count(*) ofertas,count(DISTINCT curso) cursos,
 sum(matriculas) matriculas,sum(ingressantes) ingressantes,sum(concluintes) concluintes,
 sum(desvinculados) desvinculados,sum(transferidos) transferidos,sum(vagas) vagas,
 100.0*sum(desvinculados)/nullif(sum(matriculas+desvinculados+transferidos),0) proxy_evasao_anual
 FROM core.censo_mt WHERE nivel='1' GROUP BY ano,modalidade,categoria,rede;
CREATE OR REPLACE VIEW audit.fd_cobertura AS
 SELECT a.source_key,d.family,d.rows_loaded,d.sha256,a.run_id,d.version
 FROM audit.fd_active a JOIN audit.fd_dataset d USING(version);
