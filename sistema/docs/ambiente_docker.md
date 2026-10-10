> Registro da etapa anterior. O diretório e os comandos atuais estão no [README do sistema](../README.md). A nova pasta foi organizada com os serviços parados.

# Ambiente Docker local — DataMind 03

## Serviços

Estado verificado em 10/10/2026 às 12h21, horário de Cuiabá: os cinco serviços estão saudáveis, login autenticado testado e as execuções validacao_01 e validacao_02 concluídas com sucesso. audit.source_file permaneceu com cinco fontes. Evidência em outputs/ambiente/validacao.json. A idempotência demonstrada é do registro do manifesto, não do ETL analítico completo.

- Airflow 3.3.2 / Python 3.12, imagem oficial estendida com openpyxl 3.1.5.
- PostgreSQL 17.6 em dois contêineres: metadados do Airflow e banco analítico.
- LocalExecutor com paralelismo 2, adequado à execução local inicial.
- API/interface, scheduler e DAG processor em serviços separados.
- Volumes persistentes para bancos e logs. Fontes montadas como somente leitura.

O Docker Desktop foi consultado e apresentou backend Linux, 20 CPUs e cerca de 7,57 GiB de memória disponíveis ao motor. A porta 5433 foi recusada pelo Windows, por isso o banco analítico usa 15432. Os serviços estão limitados ao acesso pela máquina local.

## Acesso

- Airflow: http://localhost:8080
- Usuário: datamind
- Senha: arquivo local runtime/private/ACESSO_LOCAL.txt
- PostgreSQL analítico: host localhost, porta 15432, banco datamind, usuário datamind.
- Senha do banco: variável DATAMIND_DB_PASSWORD do arquivo .env.

Não enviar .env ou runtime/private ao GitHub/Drive. Há .env.example sem credenciais reais. O arquivo .gitignore já exclui esses caminhos.

## Primeira instalação

Na raiz do projeto:

```powershell
python src/setup_local.py
docker compose config --quiet
docker compose build
docker compose up -d postgres-meta postgres-data
docker compose run --rm airflow-init
docker compose up -d airflow-api airflow-scheduler airflow-dag-processor
docker compose ps
```

Executar uma etapa seguinte somente após sucesso da anterior. O setup preserva credenciais já existentes. Em outra máquina, copiar/baixar os cinco originais referenciados pelo manifesto para data/raw/ antes de executar a DAG. Os scripts de inicialização SQL só rodam quando o volume analítico está vazio.

## DAG de validação

Nome: datamind_validar_ambiente. Execução manual, sem agendamento automático.

1. validar_fontes: confere bytes e SHA-256 dos cinco arquivos contra o manifesto.
2. registrar_manifesto: grava/upserta cinco fontes em audit.source_file no banco analítico.
3. confirmar: confere conexão, nome do banco e quantidade de fontes.

Essa DAG verifica a infraestrutura e o registro idempotente do manifesto. A carga analítica inicial está em uma segunda DAG, `datamind_trajetoria_2015`, documentada em [primeira orquestração](primeira_orquestracao.md). Ela implementa staging, transformação SQL, conferência, quarentena e publicação versionada do recorte inicial da P1; os demais fluxos P2–P5 continuam pendentes.

```powershell
docker compose exec -T airflow-scheduler airflow dags unpause datamind_validar_ambiente
docker compose exec -T airflow-scheduler airflow dags trigger datamind_validar_ambiente
docker compose exec -T airflow-scheduler airflow dags list-runs datamind_validar_ambiente
```

Também é possível executar pela interface. Consultar logs pelo serviço e pela tarefa sem compartilhar credenciais.

## Parar e retomar

```powershell
docker compose stop
docker compose start
```

Esses comandos preservam volumes. Não usar down --volumes durante o evento, pois apagaria os bancos deste projeto. Os contêineres de outros projetos não foram alterados.

## Relação com Vercel

O site será um projeto separado, alimentado por JSON/CSV agregados e validados. Airflow e PostgreSQL rodam no Docker local. A implementação e a publicação da página web ainda não fazem parte deste ambiente inicial.

## Referências

- https://airflow.apache.org/docs/apache-airflow/3.3.2/howto/docker-compose/index.html
- https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/auth-manager/simple/index.html

SimpleAuthManager é usado para este ambiente de desenvolvimento local. O estado dos testes reais deve ser consultado em outputs/ambiente/validacao.json.
