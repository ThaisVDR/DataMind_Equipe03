# DataMin.03 · sistema do projeto

Operação local do Airflow, PostgreSQL, ETL e dashboard. O stack usa o nome Compose datamind03 para preservar os volumes existentes.

## Comandos
Na pasta DataMin.03, execute:
- .\subir_airflow.ps1 — inicia os bancos e serviços Airflow; não dispara o ETL.
- .\parar_airflow.ps1 — para os contêineres preservando os volumes.
- .\abrir_prototipo.ps1 — abre http://127.0.0.1:4173, sem precisar do Docker.
- .\fechar_prototipo.ps1 — encerra somente o servidor local do dashboard.
- .\atualizar_prototipo.ps1 — exporta snapshot do PostgreSQL; requer o stack ligado.

## Acessos
- Airflow: http://localhost:8080; credenciais em runtime/private/ACESSO_LOCAL.txt.
- PostgreSQL analítico: localhost:15432, banco datamind03, usuário datamind; senha DATAMIND_DB_PASSWORD em .env.
- PostgreSQL metadados: somente na rede Docker, banco/usuário airflow; senha AIRFLOW_DB_PASSWORD em .env.
- Rode python src/setup_local.py numa instalação nova para gerar segredos aleatórios locais.

## Dados e SQL
Coloque os pacotes do evento em ../Fonte de Dados/, irmã desta pasta. O Compose monta os originais sem escrita em /opt/airflow/project/fonteDado, a rota lida pelo ETL. Não mude apenas um dos lados dessa montagem.
- sql/init/: esquemas e modelo inicial do PostgreSQL.
- sql/queries/: consultas analíticas somente leitura.
- dags/: orquestração Airflow.
- src/: ETL, exportação e verificadores.
- outputs/: evidências e snapshot exportado.
- runtime/: credenciais/intermediários locais, ignorados pelo Git.

Relatórios de EDA e regras estão em ../Análise Exploratória e Contextualização/Relatórios/.