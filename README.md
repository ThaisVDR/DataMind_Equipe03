# DataMind · Equipe 03

Repositório do projeto Rota do Diploma para o DataHack UNIVAG. Materiais do evento, estudos e sistema estão organizados por finalidade.

## Estrutura

- `Análise Exploratória e Contextualização/Materiais do grupo/` — apresentações e documentos recebidos.
- `Análise Exploratória e Contextualização/Relatórios/` — EDA, regras de negócio, respostas iniciais e arquitetura.
- `Análise Exploratória e Contextualização/Apresentações/` — roteiro de pitch.
- `Fonte de Dados/` — arquivos oficiais locais, não versionados.
- `DataMin.03/` — Airflow, Docker, PostgreSQL, ETL, SQL e protótipo.
- `docs/` — guia oficial do evento.

## Executar o sistema

O guia completo de preparação, inicialização e parada do banco, Airflow e DAGs, validação da carga e protótipo está em [DataMin.03/README.md](DataMin.03/README.md).

Resumo: no PowerShell, entre em `DataMin.03/` e execute `.\subir_airflow.ps1` para iniciar PostgreSQL e Airflow. O início do stack não dispara a DAG: a carga principal `datamind_fonte_dado_etl` deve ser disparada separadamente pela interface do Airflow em http://localhost:8080 ou pela CLI descrita no guia. O dashboard local usa http://127.0.0.1:4173.

## Análises e materiais

Consulte o [índice dos documentos de análise](An%C3%A1lise%20Explorat%C3%B3ria%20e%20Contextualiza%C3%A7%C3%A3o/README.md), o [guia do evento](docs/guia_participante.html) e o [repositório do grupo](https://github.com/ThaisVDR/DataMind_Equipe03).
