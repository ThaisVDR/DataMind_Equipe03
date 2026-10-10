# DataMind — diretório do projeto

Este é o diretório local organizado do projeto. Os materiais do grupo foram preservados. O sistema fica em `sistema/`, e os arquivos originais de dados ficam em `Fonte de Dados/`.

```text
DataMind/
├── README.md
├── .gitignore
├── Análise Exploratória e Contextualização/  # materiais da equipe
├── Fonte de Dados/                           # originais locais, fora do Git
├── DataMind.03/                              # pasta preexistente preservada
├── Analise_ETL_Rota_do_Diploma.pdf
├── Roadmap_Rota_do_Diploma_PostgreSQL.pdf
└── sistema/
    ├── README.md
    ├── compose.yaml
    ├── Dockerfile
    ├── .env.example
    ├── dags/          # orquestração Airflow
    ├── src/           # ETL e verificadores
    ├── sql/           # schemas, views e consultas
    ├── scripts/       # início, parada, status e validação
    ├── docs/          # operação, método e histórico
    ├── outputs/       # evidências e exportações
    ├── data/          # amostras do fluxo anterior, fora do Git
    └── runtime/       # credenciais e intermediários, fora do Git
```

## Operar manualmente

Os cinco serviços foram parados, preservando os volumes do PostgreSQL e os logs. A nova pasta foi preparada e conferida sem iniciar o sistema novamente.

No PowerShell:

```powershell
Set-Location -LiteralPath 'C:\Users\THAIII\DATAHCK_2026\DataMind\sistema'
.\scripts\verificar_configuracao.ps1
.\scripts\iniciar.ps1
.\scripts\status.ps1
```

Depois, abrir http://localhost:8080. Usuário `datamind`; senha em `sistema/runtime/private/ACESSO_LOCAL.txt`. O botão Trigger inicia a DAG `datamind_fonte_dado_etl`; iniciar o ambiente não dispara o ETL automaticamente.

Para parar:

```powershell
.\scripts\parar.ps1
```

Consulte [operação do sistema](sistema/README.md) e [ETL e PostgreSQL](sistema/docs/etl_fonte_dado.md).

## GitHub e arquivos locais

Versionar código, configuração sem segredos, documentação e evidências adequadas. `.gitignore` exclui fontes brutas, `.env`, credenciais e intermediários, inclusive o arquivo de acesso preexistente em `DataMind.03`.

Repositório do grupo: [ThaisVDR/DataMind_Equipe03](https://github.com/ThaisVDR/DataMind_Equipe03). Esta pasta está vinculada ao histórico existente, preservando as contribuições anteriores.

O nome do projeto Docker continua `datamind03`, para reaproveitar os bancos desta máquina. Executar os comandos somente a partir de `sistema/`; as cópias anteriores permanecem como histórico e não devem ser iniciadas em paralelo.


## Entrega técnica disponível

A DAG principal `datamind_fonte_dado_etl` carregou 31 conjuntos de Mato Grosso no PostgreSQL, totalizando 1.720.436 registros nas granularidades de cada fonte. Estão incluídas trajetórias 2015–2020, Censo 2021–2024, indicadores INEP e sete tabelas IBGE.

- [Modelo, regras e execução do ETL](sistema/docs/etl_fonte_dado.md)
- [Evidências de carga, idempotência e rejeição de lote](sistema/outputs/ambiente/validacao_fonte_dado.json)
- [Configuração Docker](sistema/compose.yaml)
- [DAG principal](sistema/dags/datamind_fonte_dado_etl.py)
- [Guia do evento](docs/guia_participante.html)

O site na Vercel e a interpretação final de todas as perguntas não integram esta entrega. Os registros completos de uso de IA exigidos pelo evento devem ser incluídos pela equipe em `prompts/`; relatórios técnicos não substituem as conversas.

## Reproduzir em outra máquina

Requer Git, Docker Desktop com contêineres Linux e Python 3.11+ para preparar as credenciais locais.

```powershell
git clone https://github.com/ThaisVDR/DataMind_Equipe03.git
Set-Location DataMind_Equipe03
New-Item -ItemType Directory -Force 'Fonte de Dados'
Set-Location sistema
python src/setup_local.py
```

Baixar os três pacotes disponibilizados pelo evento na [pasta de dados do grupo](https://drive.google.com/drive/folders/1rFUqfrsmLJumJsYJBRxIQIh9Od4TRLGA) e colocá-los em `Fonte de Dados/`, preservando os nomes dos ZIPs. O ETL principal reconhece também os arquivos já extraídos. A pasta precisa conter as 31 fontes relacionadas no guia do ETL; nenhum dado bruto foi incluído neste repositório.

```powershell
.\scripts\verificar_configuracao.ps1
.\scripts\iniciar.ps1
.\scripts\status.ps1
```

Os bancos de uma nova máquina começam vazios; execute manualmente `datamind_fonte_dado_etl` após a inicialização. As duas DAGs da etapa anterior usam cinco amostras adicionais em `sistema/data/raw/`, identificadas no [manifesto da Fase 1](sistema/outputs/fase1/manifesto.json). Elas não são necessárias para executar o ETL principal.
