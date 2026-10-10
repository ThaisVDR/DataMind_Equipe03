# Micro-pitch Fase 1 — roteiro de três minutos

## 0:00–0:35 — Objetivo e escolhas

“Nosso projeto responde quantos estudantes chegam ao diploma em Mato Grosso, onde ocorrem as perdas e quais características estão associadas a elas. Escolhemos Airflow em Docker/Linux para coordenar as etapas e PostgreSQL para armazenar e transformar os dados. A visualização será uma página web interativa na Vercel.”

## 0:35–1:30 — O que já verificamos

“Baixamos e identificamos por hash cinco arquivos, cobrindo uma edição de cada família. No recorte MT, encontramos 5.150 registros da trajetória 2015, 12.278 do Censo 2021, 155 do CPC 2021 e 97 do Enade 2025. Também inspecionamos a estrutura da tabela 9514 do IBGE no nível estadual.

O Censo tem três registros sequenciais que devem ficar fora da graduação. O código de curso se repete por oferta, então usamos chave composta. Encontramos seis cursos sem conceito no CPC e seis no Enade; eles não receberão nota zero.”

## 1:30–2:20 — Como vamos tratar e relacionar

“Preservaremos os originais, padronizaremos os dados em staging e manteremos fatos separados por granularidade. A trajetória usa curso, coorte e ano; o Censo precisa preservar município de oferta. Nos testes por código, 116 dos 155 cursos do CPC e 68 dos 97 do Enade apareceram na trajetória de 2015. Vamos explicitar a cobertura e investigar as perdas antes das análises finais.

O PostgreSQL produzirá tabelas por pergunta. O site consumirá exportações agregadas validadas, para funcionar mesmo sem o banco do laboratório.”

## 2:20–3:00 — Reexecução e próximos passos

“A carga será identificada por arquivo, hash e versão do código. Prepararemos o recorte em uma área temporária, validaremos e substituiremos a versão vigente em transação. Na Fase 2 demonstraremos duas execuções com as mesmas contagens e totais.

Esta primeira exploração cobre arquivos selecionados. Ainda precisamos verificar as outras edições, executar a carga no banco e calcular as respostas. Já temos evidências da estrutura e uma estratégia documentada para avançar.”

## Preparação para perguntas

- Por que Airflow? Dependências, logs e reexecução coordenados. A lógica fica em adaptadores e SQL.
- Por que PostgreSQL? Relacionamentos, restrições e transações permitem controlar a integridade.
- O que já está executado? Download, hashes, perfilagem de cinco arquivos e cobertura diagnóstica de códigos.
- O que ainda é plano? Serviços, DAG, carga no PostgreSQL, idempotência no banco e publicação Vercel.
- Por que não juntar tudo por curso diretamente? A trajetória repete o curso a cada referência e o Censo repete por oferta. Isso pode multiplicar medidas.
- Já temos a taxa de evasão? Não nesta entrega de exploração. Os números apresentados aqui medem estrutura e cobertura.
