# DataMin.03 — guia para executar o sistema

Este guia explica como iniciar e parar PostgreSQL e Airflow, executar as DAGs, conferir a carga e abrir o protótipo local. Os comandos são para Windows PowerShell com Docker Desktop em modo Linux.

## 1. Requisitos e primeira configuração

Instale e inicie o Docker Desktop. Para a configuração inicial, instale também Python 3.11 ou superior. Clone/abra o repositório e confirme que os arquivos oficiais estão na pasta irmã `Fonte de Dados/`, na raiz do repositório. Essa pasta é local e não é enviada ao GitHub.

No PowerShell, entre na pasta do sistema:

    Set-Location -LiteralPath 'C:\Users\THAIII\DATAHCK_2026\DataMind\DataMin.03'

Na primeira execução, o script cria segredos locais aleatórios se `.env` e as credenciais privadas ainda não existirem. Os segredos ficam em arquivos ignorados pelo Git. Não compartilhe nem publique `.env` ou `runtime/private/`.

    python src/setup_local.py
    .\scripts\verificar_configuracao.ps1

O próprio inicializador também prepara as credenciais se necessário. Se os arquivos locais já existem, não rode o setup para substituí-los: preserve o `.env` e `runtime/private/passwords.json`.

## 2. Iniciar PostgreSQL e Airflow

Com o Docker Desktop em modo Linux, execute:

    .\subir_airflow.ps1

O script inicia os bancos PostgreSQL, prepara o banco de metadados do Airflow e sobe API, scheduler e processador de DAGs. Na primeira execução, a imagem pode precisar ser construída e levar alguns minutos. PostgreSQL analítico e Airflow fazem parte do mesmo Compose; não é preciso subir o banco em um comando separado.

O comando **não executa a carga ETL**. Ele apenas deixa os serviços prontos.

- Airflow: http://localhost:8080. Use o usuário e a senha registrados em `runtime/private/ACESSO_LOCAL.txt`.
- PostgreSQL analítico, para DBeaver/pgAdmin: host `localhost`, porta `15432`, banco `datamind03`, usuário `datamind`. A senha está na variável `DATAMIND_DB_PASSWORD` do `.env` local.
- PostgreSQL de metadados do Airflow: serviço `postgres-meta`, porta interna `5432`, banco/usuário `airflow`. É um banco interno do Compose e não é o banco analítico do projeto.

Os serviços usam portas locais. Não exponha essas credenciais ou portas em redes públicas.

## 3. Conferir serviços e DAGs

Para verificar os contêineres, execute:

    docker compose ps

O script de status também lista DAGs e erros de importação:

    .\scripts\status.ps1

Se uma DAG não aparecer no Airflow, confira a saída de `list-import-errors` nesse status e os logs do processador de DAGs.

## 4. Executar a carga principal

A DAG principal, `datamind_fonte_dado_etl`, lê os arquivos locais em `../Fonte de Dados/` e publica o conjunto validado de fontes no PostgreSQL `datamind03`. No Airflow, abra a DAG e clique em **Trigger**. Ela não recebe parâmetros para uma execução normal.

Também é possível dispará-la pelo PowerShell, ainda dentro da pasta `DataMin.03`:

    docker compose exec -T airflow-scheduler airflow dags unpause datamind_fonte_dado_etl
    docker compose exec -T airflow-scheduler airflow dags trigger datamind_fonte_dado_etl

Acompanhe a execução na interface do Airflow. A carga tem tarefas para inventariar as fontes, processar cada conjunto e publicar o lote. A primeira carga pode demorar. Não altere arquivos de dados ou código enquanto ela estiver rodando.

As fontes precisam estar na pasta esperada. O Compose a monta somente para leitura dentro dos contêineres em `/opt/airflow/project/fonteDado`; não altere apenas um lado dessa rota.

## 5. Conferir a publicação no PostgreSQL

Consulte a cobertura publicada para confirmar fontes, contagens e versões:

    docker compose exec -T postgres-data psql -U datamind -d datamind03 -c "SELECT source_key, row_count, version_hash FROM audit.fd_cobertura ORDER BY source_key"

Para contar as linhas de cobertura:

    docker compose exec -T postgres-data psql -U datamind -d datamind03 -c "SELECT count(*) AS fontes_ativas, sum(row_count) AS registros FROM audit.fd_cobertura"

Uma carga documentada e validada anteriormente cobriu 31 conjuntos lógicos e 1.720.436 registros; esses números são referência daquela execução, não garantia para dados ou execuções futuras.

Use as views `core` e `mart` para análise corrente. As tabelas físicas `core.fd_*` mantêm versões históricas; somá-las diretamente pode duplicar observações. A cobertura ativa está em `audit.fd_cobertura`. Mais detalhes sobre granularidade, regras e validação estão em `docs/etl_fonte_dado.md`.

## 6. DAGs auxiliares

Além da carga principal, o repositório contém DAGs para validação de ambiente e para a trajetória 2015:

- `datamind_validar_ambiente` — verificações do ambiente.
- `datamind_trajetoria_2015` — fluxo anterior e independente da carga completa das fontes.

Para o conjunto integrado descrito neste guia, execute `datamind_fonte_dado_etl`. Consulte `docs/primeira_orquestracao.md` antes de rodar o fluxo auxiliar de trajetória.

## 7. Atualizar e abrir o protótipo

O protótipo é um dashboard local separado da interface do Airflow. Para exportar um novo snapshot das tabelas publicadas no banco, com PostgreSQL e scheduler ativos, execute:

    .\atualizar_prototipo.ps1

Para servir a página localmente:

    .\abrir_prototipo.ps1

Abra http://127.0.0.1:4173. O servidor do protótipo usa o snapshot exportado e pode ser aberto sem Docker; para atualizá-lo com dados recentes, faça primeiro a exportação com o stack ligado. Para encerrar apenas o servidor web do protótipo:

    .\fechar_prototipo.ps1

Esses comandos abrem a versão local. Publicação na Vercel não é feita por eles.

## 8. Parar e retomar

Para parar PostgreSQL e Airflow sem apagar os dados dos bancos:

    .\parar_airflow.ps1

Os volumes são preservados. Para voltar a trabalhar, execute novamente `\.\subir_airflow.ps1`. O protótipo, se estiver aberto, é encerrado separadamente com `\.\fechar_prototipo.ps1`.

Os scripts de parada usam `docker compose stop`, não removem volumes. Evite `docker compose down -v`, pois esse comando remove os volumes e os dados persistidos.

## Pastas importantes

- `dags/` — definições das DAGs Airflow.
- `src/` — ETL, exportador do protótipo e verificadores.
- `sql/init/` — criação de schemas e objetos-base do PostgreSQL.
- `sql/queries/` — consultas analíticas.
- `../Fonte de Dados/` — fontes originais fornecidas ao grupo; local, fora do Git.
- `outputs/` — evidências e arquivos exportados.
- `runtime/` — credenciais e arquivos locais; não versionar.

Relatórios de análise exploratória, contexto e regras de negócio estão em `../Análise Exploratória e Contextualização/Relatórios/`. Para arquitetura e detalhes técnicos, consulte `docs/ambiente_docker.md` e `docs/etl_fonte_dado.md`.
