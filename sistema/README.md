# Sistema DataMind

Diretório de operação: `C:\Users\THAIII\DATAHCK_2026\DataMind\sistema`.

O sistema foi organizado aqui e deixado **parado**, conforme solicitado. Os bancos, logs e histórico de execuções continuam nos volumes Docker existentes. As credenciais locais foram preservadas.

## Iniciar manualmente

Com o Docker Desktop aberto em modo Linux:

```powershell
Set-Location -LiteralPath 'C:\Users\THAIII\DATAHCK_2026\DataMind\sistema'
.\scripts\verificar_configuracao.ps1
.\scripts\iniciar.ps1
.\scripts\status.ps1
```

`verificar_configuracao.ps1` confere diretórios, credenciais presentes e sintaxe do Compose; não inicia contêineres. `iniciar.ps1` prepara credenciais somente se não existirem, constrói a imagem se necessário, inicia os bancos, aplica a inicialização e inicia os três serviços do Airflow. O script espera os serviços ficarem saudáveis.

Se o PowerShell bloquear scripts por política local, a alternativa restrita a esse processo é:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\iniciar.ps1
```

Isso não altera permanentemente a política do Windows.

## Acessar

| Componente | Acesso |
| --- | --- |
| Airflow | http://localhost:8080 |
| Usuário Airflow | `datamind` |
| Senha Airflow | `runtime/private/ACESSO_LOCAL.txt` |
| PostgreSQL analítico no Windows | `localhost:15432`, banco e usuário `datamind` |
| Senha PostgreSQL | variável `DATAMIND_DB_PASSWORD` em `.env` |
| PostgreSQL usado pelas tarefas | `postgres-data:5432`, configurado por `DATAMIND_DB_DSN` |

## Executar o ETL manualmente

Na interface, abrir `datamind_fonte_dado_etl` e clicar em **Trigger**, sem parâmetros. Alternativamente:

```powershell
docker compose exec -T airflow-scheduler airflow dags unpause datamind_fonte_dado_etl
docker compose exec -T airflow-scheduler airflow dags trigger datamind_fonte_dado_etl
docker compose exec -T airflow-scheduler airflow dags list-runs datamind_fonte_dado_etl
```

Todas as DAGs têm execução manual. O sistema contém:

- `datamind_fonte_dado_etl`: 31 conjuntos, incluindo trajetórias, Censo, indicadores INEP e IBGE.
- `datamind_trajetoria_2015`: fluxo anterior da coorte 2015.
- `datamind_validar_ambiente`: conferência das cinco amostras da primeira etapa.

A carga completa anterior publicou 1.720.436 registros e passou pelos testes de repetição e rejeição. Esses resultados são históricos do ambiente anterior, preservado nos mesmos volumes; não significam que a nova pasta já foi iniciada. Existe uma execução vermelha de teste negativo (`fonte_dado_reprovacao_1791654012895226000`); a publicação válida anterior foi preservada.

## Parar e retomar

```powershell
.\scripts\parar.ps1
.\scripts\iniciar.ps1
```

O comando de parada preserva os volumes. Não usar `docker compose down --volumes`, pois isso apagaria os bancos. Na primeira inicialização neste caminho, utilizar `iniciar.ps1` ou `docker compose up`, para aplicar as novas montagens; `docker compose start` apenas reiniciaria contêineres com a configuração antiga.

## Dados e estrutura

`../Fonte de Dados` é montada como somente leitura em `/opt/airflow/project/fonteDado`. O código mantém esse caminho interno, sem depender da pasta Windows antiga. Foram copiados e verificados por SHA-256 os 159 arquivos de origem, sem modificar os originais.

- `dags/`: sequência e dependências das tarefas.
- `src/`: leitores, transformações, carga e testes.
- `sql/init/`: estruturas PostgreSQL; `sql/consultas_etl.sql`: exemplos de consultas.
- `docs/`: documentação técnica e registros anteriores.
- `outputs/`: evidências e exportações; `outputs/ambiente/organizacao_diretorio.json`: conferência da cópia.
- `data/raw/`: cinco amostras locais usadas pelas DAGs anteriores.
- `runtime/private/`: credenciais; `runtime/etl/`: intermediários reconstruídos a cada carga necessária.

Os intermediários antigos não foram duplicados. Para limpar e reprocessar uma tarefa de uma execução antiga, iniciar desde a extração, ou criar uma nova execução. Os dados publicados no banco continuam preservados.

## Alterar o sistema

DAGs, código e SQL são montados desta pasta. Alterações no Python não exigem reconstruir a imagem. Alterações em dependências do Dockerfile:

```powershell
.\scripts\iniciar.ps1 -Build
```

O projeto Compose permanece `datamind03`, com os volumes `datamind03_postgres-data`, `datamind03_postgres-meta` e `datamind03_airflow-logs`. Não iniciar as cópias antigas do sistema em paralelo.

[Detalhamento do ETL e PostgreSQL](docs/etl_fonte_dado.md). [Evidência dos testes anteriores](outputs/ambiente/validacao_fonte_dado.json).

## Protótipo da Fase 2

Consulte o [plano e as primeiras respostas](docs/fase2_prototipo.md) e o [painel com instruções](dashboard/README.md). Para atualizar os dados a partir do PostgreSQL carregado, execute `./scripts/atualizar_prototipo.ps1`; para abrir o site localmente, execute `./scripts/iniciar_prototipo.ps1`. A página usa uma extração agregada independente do servidor de banco e pode ser hospedada na Vercel.
