# ETL de fonteDado para PostgreSQL

A DAG `datamind_fonte_dado_etl` lê os arquivos de `../Fonte de Dados`, montados internamente como `fonteDado` e publica um lote coerente de dados de Mato Grosso no banco `datamind`.

## Executar

1. Iniciar o Docker Desktop em modo Linux e executar `scripts/iniciar.ps1` na raiz do repositório.
2. Abrir http://localhost:8080. Usuário `datamind`; senha no arquivo local `runtime/private/ACESSO_LOCAL.txt`.
3. Abrir `datamind_fonte_dado_etl` e clicar em **Trigger**, sem parâmetros.
4. Acompanhar `inventariar`, as 31 instâncias de `extrair_transformar_carregar` e `publicar_lote`.
5. Consultar `audit.fd_cobertura` para confirmar quais fontes foram publicadas.

Pelo terminal:

```powershell
docker compose exec -T airflow-scheduler airflow dags unpause datamind_fonte_dado_etl
docker compose exec -T airflow-scheduler airflow dags trigger datamind_fonte_dado_etl
docker compose exec -T postgres-data psql -U datamind -d datamind -c "SELECT * FROM audit.fd_cobertura ORDER BY source_key"
```

O limite de duas tarefas simultâneas evita carregar todos os arquivos grandes na memória ao mesmo tempo. Não modificar as fontes ou o código durante uma execução.

## Conexão PostgreSQL

| Uso | Host | Porta | Banco / usuário |
| --- | --- | --- | --- |
| DBeaver, pgAdmin ou outra aplicação nesta máquina | `localhost` | `15432` | `datamind` / `datamind` |
| Tarefas Airflow dentro do Compose | `postgres-data` | `5432` | `datamind` / `datamind` |

A senha está em `DATAMIND_DB_PASSWORD`, no `.env` local. As tarefas usam a variável `DATAMIND_DB_DSN` já configurada no Compose. Credenciais não são gravadas no código nem nos relatórios.

## Fontes incluídas

| Família | Arquivos canônicos | Recorte |
| --- | --- | --- |
| Trajetórias | 6 ZIPs, coortes 2015–2020 | UF 51; todas as referências disponíveis até 2024 |
| Censo Superior | 4 ZIPs, 2021–2024 | Cadastro de cursos com localidade de oferta em MT |
| CPC | 3 XLSX, 2021–2023 | Sigla da UF = MT |
| Conceito Enade | 3 XLSX, 2021–2023 | Sigla da UF = MT |
| IDD | 3 XLSX, 2021–2023 | Sigla da UF = MT |
| IGC | 3 XLSX, 2021–2023 | IES com UF = MT |
| Enade 2025 | Licenciaturas e Medicina, 2 XLSX | Sigla da UF = MT; populações separadas |
| IBGE | 7 CSVs: 10056, 10059, 10061, 10296, 5938, 6579 e 9514 | Estado N3 e municípios N6 de MT |

Total: 31 conjuntos lógicos. A descoberta exige essa cobertura para evitar publicar silenciosamente um lote incompleto.

Arquivos já extraídos têm preferência sobre os pacotes externos. O Censo 2024 é recuperado de seu ZIP externo quando necessário. XLSX é a representação escolhida para indicadores que também têm ODS; CSV é a escolhida para IBGE que também tem respostas JSON. Esses arquivos equivalentes não são somados como fontes adicionais. Documentos, páginas HTML e catálogos são material de apoio, não fatos analíticos.

## Modelo e granularidade

| Consulta recomendada | Uma linha representa |
| --- | --- |
| `core.trajetoria_mt` | Curso, coorte e ano de referência |
| `core.trajetoria_acumulada_mt` | Mesma granularidade, com contagens acumuladas e denominador ajustado |
| `core.censo_mt` | Ano, curso, município de oferta, modalidade e nível acadêmico |
| `core.indicadores_mt` | Tipo de indicador, ano e curso; para IGC, a entidade é a IES |
| `core.ibge_mt` | Tabela, variável, unidade, nível, localidade, período e combinação de categorias |
| `mart.trajetoria_coorte_mt` | Coorte, referência, modalidade, categoria administrativa e área CINE |
| `mart.censo_rede_modalidade_mt` | Ano, modalidade, categoria administrativa e rede; somente graduação |
| `audit.fd_cobertura` | Fonte ativa, versão, hash, contagem e execução que publicou |

As tabelas físicas `core.fd_*` guardam versões. As views acima consultam somente o lote aprovado em `audit.fd_active`. Para análise corrente, usar as views, evitando somar versões históricas das tabelas físicas.

`staging.fd_raw` mantém o conteúdo selecionado de cada linha como JSONB, associado à versão e ao número da linha original. No caso de Excel, os nomes dos campos são normalizados. O arquivo original permanece intacto em `../Fonte de Dados`, e `audit.fd_dataset.source_path` registra sua origem, inclusive o membro interno do ZIP.

Identificadores são TEXT; anos são INTEGER; contagens são BIGINT; taxas e valores são NUMERIC. As demais contagens QT_ do Censo ficam no JSONB `medidas`, sem perder colunas entre edições. Unidades e categorias do IBGE são preservadas; totais e subtotais não devem ser somados indiscriminadamente.

## Transformações e qualidade

- CSVs do Censo são lidos como cp1252, com separador `;`. Censos 2023 e 2024 podem conter colunas adicionais, conservadas no staging.
- No Censo, o filtro territorial é a UF da oferta. Um curso EAD pode aparecer em vários municípios; a chave inclui a localidade. Registros de cursos sequenciais permanecem no core; o mart filtra `nivel = '1'` para graduação.
- A aba de indicadores é reconhecida pelo cabeçalho, inclusive quando a primeira aba contém apenas atualizações. Espaços, acentos e notas de rodapé dos cabeçalhos são normalizados.
- `SC` não vira zero: o conceito fica nulo e o motivo é registrado. Enade 2025 conserva proficiência na escala 0–1 e não a confunde com conceito contínuo.
- No IBGE, `-` é zero absoluto, `...` é indisponível, `..` não se aplica e `X` é inibido. O valor original e o status são mantidos. [Referência oficial: símbolos especiais do SIDRA](https://sidra.ibge.gov.br/tabela/4709/).
- Na trajetória, contagens anuais de conclusão, desistência e falecimento são acumuladas por curso/coorte. O denominador é ingressantes menos falecimentos acumulados. O saldo e as cinco taxas são reconciliados com tolerância de 0,000001 ponto percentual. As séries devem cobrir da coorte até 2024, sem alteração do número inicial de ingressantes.
- Chaves primárias rejeitam duplicações; contagens negativas, códigos obrigatórios ausentes, leiautes incompatíveis e divergências de linhas bloqueiam a carga. Cada fonte precisa produzir registros.

O proxy anual do Censo é `100 × desvinculados / (matriculados + desvinculados + transferidos)`. É distinto da desistência acumulada da trajetória. As fontes têm populações e períodos distintos; carregar todas não autoriza uma junção somente por nome de curso nem uma interpretação causal.

## Transações, reexecução e quarentena

1. A descoberta calcula SHA-256 das fontes e uma versão que inclui código e contrato SQL.
2. Cada tarefa lê a fonte, gera CSVs de trabalho, carrega staging e core por COPY e confere o resultado dentro da transação PostgreSQL.
3. Uma versão já validada é reaproveitada após reconferência de contagens e regras. A repetição não insere novamente os mesmos fatos.
4. Somente quando as 31 fontes estão prontas, uma transação troca o catálogo ativo inteiro. Consultas veem o lote anterior ou o novo, sem combinação parcial.
5. Falhas de conteúdo são registradas em `audit.fd_dataset`/`audit.fd_batch` como quarentena; a publicação anterior permanece. A DAG fica vermelha quando uma falha impede a publicação.

Erros técnicos têm uma tentativa adicional. Erros de conteúdo conhecidos não são repetidos automaticamente. Se a fonte for corrigida, uma nova execução calcula outra versão. Dados de versões antigas e intermediários ficam preservados; não há limpeza automática de histórico.

Para testar o bloqueio deliberadamente, executar com `{"force_validation_failure": true}`. Esse parâmetro reprova a etapa final e produz uma DAG com estado `failed`, de forma esperada. Não usar em cargas normais.

## Testes reproduzíveis

```powershell
docker compose exec -T airflow-scheduler python /opt/airflow/project/src/test_fonte_dado.py
python src/verify_fonte_dado.py --start-first --first-run-id teste_fontes_01
```

Usar identificador novo a cada execução com `--start-first`. Sem essa opção, o verificador acompanha uma execução existente indicada por `--first-run-id`. Ele compara contagens, versões e impressões digitais do conteúdo após repetição; também reprova um lote e verifica que a publicação anterior permanece. Evidência em `outputs/ambiente/validacao_fonte_dado.json`.

## Limites de publicação

Este ETL disponibiliza dados no PostgreSQL local. As views core e mart são internas e contêm contagens pequenas; aplicar as regras de supressão antes de exportar recortes para o público. Não foi publicado um novo dashboard nem exportados automaticamente todos esses dados para a Vercel. O JSON da DAG anterior de trajetória 2015 é independente deste lote.

## Primeira carga executada antes desta reorganização

A execução `fonte_dado_carga_01` concluiu com sucesso e publicou os 31 conjuntos:

| Família | Conjuntos | Registros no core ativo |
| --- | ---: | ---: |
| Trajetória 2015–2020 | 6 | 26.513 |
| Censo 2021–2024 | 4 | 62.674 |
| Indicadores INEP | 14 | 1.919 |
| IBGE | 7 | 1.629.330 |
| **Total** | **31** | **1.720.436** |

As contagens representam observações nas granularidades descritas, não pessoas únicas. A coorte 2015 foi comparada com o fluxo anterior, com zero divergência nas contagens e nas cinco taxas por curso/ano. Os testes de repetição e rejeição têm seu resultado detalhado no arquivo de evidências gerado pelo verificador.

## Resultado dos testes de integração

Carga inicial e repetição concluídas com sucesso. A repetição preservou contagens, versões e as impressões digitais calculadas sobre todo o conteúdo das quatro tabelas core. O tratamento de zero absoluto e de valores ausentes do IBGE também passou na conferência.

A execução `fonte_dado_reprovacao_1791654012895226000` foi reprovada deliberadamente na publicação. Ela aparece com estado `failed` no Airflow por ser um teste negativo. Os 31 conjuntos da execução válida anterior permaneceram ativos, com os mesmos dados. A última publicação válida é `fonte_dado_repeticao_1791654012895226000`.

Evidência reproduzível: `outputs/ambiente/validacao_fonte_dado.json`. Três testes unitários de conversão também passaram. Os cinco serviços permaneceram saudáveis após a carga.
