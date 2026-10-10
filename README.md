# DataMind · Equipe 03

Repositório do projeto Rota do Diploma para o DataHack UNIVAG. Materiais recebidos, análises e sistema estão separados por finalidade.

## Estrutura
- Análise Exploratória e Contextualização/Materiais do grupo/ — apresentações e documentos recebidos.
- Análise Exploratória e Contextualização/Relatórios/ — EDA, regras de negócio, respostas iniciais e arquitetura.
- Análise Exploratória e Contextualização/Apresentações/ — roteiro de pitch.
- Fonte de Dados/ — arquivos oficiais, fora do Git.
- DataMin.03/ — Airflow, Docker, PostgreSQL, ETL, SQL e dashboard.
- docs/ — guia oficial do evento.

Índice: [Análise Exploratória e Contextualização/README.md](An%C3%A1lise%20Explorat%C3%B3ria%20e%20Contextualiza%C3%A7%C3%A3o/README.md).

## Comandos separados
No PowerShell: Set-Location -LiteralPath 'C:\Users\THAIII\DATAHCK_2026\DataMind\DataMin.03'

- Subir Airflow e PostgreSQL: .\subir_airflow.ps1
- Parar os contêineres sem remover volumes: .\parar_airflow.ps1
- Abrir o protótipo local, sem Docker: .\abrir_prototipo.ps1
- Fechar apenas o servidor do protótipo: .\fechar_prototipo.ps1
- Atualizar snapshot do banco (stack ligado): .\atualizar_prototipo.ps1

Airflow abre em http://localhost:8080; credenciais em runtime/private/ACESSO_LOCAL.txt. O início do stack não dispara a DAG. O dashboard abre em http://127.0.0.1:4173 e usa o snapshot já exportado.

## Bancos e fontes
- PostgreSQL analítico: localhost:15432, banco datamind03, usuário datamind.
- PostgreSQL de metadados Airflow: rede Docker, banco e usuário airflow.
- Senhas e segredos locais permanecem em .env e runtime/private/, ignorados pelo Git.
- Os arquivos originais ficam em Fonte de Dados/, irmã de DataMin.03/. O Compose monta essa pasta somente para leitura em /opt/airflow/project/fonteDado, rota usada pelo ETL.

O nome Compose datamind03 e os volumes existentes foram preservados. Inicie somente por DataMin.03/subir_airflow.ps1; não use uma cópia antiga com o mesmo nome de projeto Docker.

Consulte o [guia do evento](docs/guia_participante.html), os [documentos de análise](An%C3%A1lise%20Explorat%C3%B3ria%20e%20Contextualiza%C3%A7%C3%A3o/README.md) e o [repositório do grupo](https://github.com/ThaisVDR/DataMind_Equipe03).