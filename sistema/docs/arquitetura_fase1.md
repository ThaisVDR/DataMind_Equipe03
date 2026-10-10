# Arquitetura proposta para a Fase 1

Equipe DataMind 03 · 10/10/2026

## Decisões confirmadas pelo grupo

- Apache Airflow para orquestração, em contêineres Docker/Linux.
- PostgreSQL para armazenamento, modelagem e transformações.
- Página web interativa hospedada na Vercel.
- GitHub como repositório principal e Drive como apoio e cópia de segurança.

Python foi usado nesta exploração para leitura de CSV/XLSX/JSON. Propõe-se reaproveitar esses adaptadores no pipeline. A versão do Airflow, PostgreSQL e do ambiente Docker deve ser registrada depois do teste no ambiente da equipe. Este documento não comprova instalação ou execução desses serviços.

## Fluxo e responsabilidades

1. Airflow coordena download ou reutilização dos arquivos versionados por hash.
2. Adaptadores Python abrem ZIP, XLSX, CSV e JSON, conferem estrutura e registram origem.
3. PostgreSQL recebe staging em lote e executa padronização, filtros e relacionamentos.
4. Consultas produzem tabelas analíticas por pergunta.
5. Verificações bloqueiam a publicação se houver erro de chave, escala, denominador ou duplicação.
6. Exportação gera JSON/CSV agregados e metadados em outputs/.
7. A página web usa uma cópia dessas saídas validada junto ao build na Vercel.

A publicação na Vercel será independente do PostgreSQL do laboratório. Filtros interativos podem operar nos dados agregados do próprio site. Uma atualização do banco só aparece no site após nova exportação e publicação. Airflow e PostgreSQL permanecem no ambiente Docker/Linux da equipe. GitHub Pages ou banco consultado pelo navegador não fazem parte desta proposta.

## Camadas

| Camada | Conteúdo | Regra |
|---|---|---|
| Arquivos originais em data/raw/ | ZIPs, XLSX e respostas JSON intactas | Fora do Git; origem e SHA-256 no manifesto |
| raw no PostgreSQL | Registros lidos, valores de origem e identificação da carga | Preservar valor original, arquivo, linha e versão |
| stg | Tipos, cabeçalhos e categorias padronizados | Registrar conversões inválidas; ausência não vira zero |
| core | Fatos por granularidade e dimensões comuns | Chaves únicas por versão, sem misturar curso, coorte e município |
| marts | Indicadores P1–P5 e bônus | Fórmula, período, denominador, cobertura e supressão explícitos |
| audit | Arquivos, execuções, validações e publicação vigente | Guardar falhas e rastrear quais versões produziram cada saída |

Para limitar volume, propõe-se preservar originais nacionais em arquivos e carregar recortes documentados no banco. Isso caracteriza uma abordagem híbrida: seleção territorial na extração e transformação analítica em SQL. A seleção EAD requer validação territorial específica; filtrar sede da IES não equivale a filtrar oferta em MT.

## Chaves e relações

| Fato | Chave candidata | Decisão |
|---|---|---|
| Trajetória | curso + coorte + ano de referência | Validada sem duplicação no recorte MT de 2015 |
| Censo de oferta | ano + curso + município + modalidade + nível | Validada em MT 2021; confirmar minimalidade e outras edições |
| CPC | curso + edição | Validada em MT 2021 |
| Enade licenciaturas | curso + edição | Validada em MT 2025 |
| IBGE | tabela + variável + nível territorial + localidade + período + categorias | Validada na resposta da UF da tabela 9514; município ainda pendente |

Identificadores são texto no modelo, ainda que o Excel os armazene como números. Uma conversão de número integral para texto deve preservar correspondência com o identificador, sem completar códigos por tentativa.

O Censo precisa de uma visão agregada de graduação por curso e ano antes de se ligar a outras tabelas por curso. Conferir a aditividade dos campos e os totais por município antes de somar. Trajetória deve ser reduzida à coorte e horizonte definidos antes de relacionar CPC/Enade. Medir contagens e totais antes/depois e manter os não correspondentes visíveis. Taxas de cobertura calculadas nesta exploração são diagnósticas, não uma amostra final de P4/P5.

## Idempotência: plano de implementação

Unidade de processamento: fonte, competência/coorte, SHA-256 do arquivo, versão do contrato e versão do código. O ano sozinho não detecta arquivos oficiais revisados.

1. Registrar arquivo e hash em audit. Uma restrição única identifica a mesma unidade de processamento.
2. Obter bloqueio por fonte e competência para impedir duas publicações concorrentes. Reexecução concluída com a mesma combinação pode ser ignorada com registro explícito.
3. Carregar uma área temporária por execução. Usar COPY FROM STDIN com colunas declaradas para CSV e lotes convertidos de XLSX/JSON.
4. Validar chaves, nulos obrigatórios, categorias, escalas e contagens antes de alterar o conjunto vigente.
5. Em transação, substituir somente a partição lógica da fonte/competência escolhida, inserir os registros validados e marcar a carga concluída. Falha causa rollback; nenhuma tabela parcialmente carregada deve ficar vigente.
6. Reconstruir os marts afetados de maneira determinística. A versão anterior permanece disponível até todas as dependências estarem validadas.
7. Escrever exportações em diretório temporário e promover o conjunto completo, acompanhado de manifesto de hashes. A publicação web referencia uma única versão consistente.

Não usar INSERT cumulativo em toda reexecução. Um UPSERT pode ser alternativa, mas exige tratar também registros removidos em revisões da fonte. Para este evento, substituir o recorte validado em transação é a proposta mais simples de explicar.

### Demonstração exigida na Fase 2

- Executar a mesma carga duas vezes.
- Comparar quantidade de linhas, quantidade de chaves distintas e totais de medidas por tabela.
- Comparar hashes de saídas ordenadas, excluindo timestamps operacionais.
- Simular falha antes da promoção: publicação anterior deve permanecer íntegra.
- Registrar evidências em audit e outputs/.

O teste de idempotência no PostgreSQL ainda não foi executado. Reproduzir a perfilagem de arquivos não substitui esse teste.

## Regras das perguntas

- P1: coorte 2015, presencial, MT, referência 2024. Comparar ano relativo para identificar perda anual, sem tratar o maior acumulado como pico anual.
- P2: comparar coortes no mesmo tempo de acompanhamento. A coorte mais recente ainda precisa ser perfilada.
- P3: 100 × desvinculados / (matriculados + desvinculados + transferidos). Agregar quantidades antes de dividir; denominador zero produz indisponível.
- P4: fixar coorte/horizonte e selecionar CPC com regra temporal explícita. SC não equivale a zero. Associação não comprova causalidade.
- P5: proficiência é proporção 0–1, apresentada em %. Participantes de 2025 e coortes antigas são populações diferentes.
- B1: vagas presenciais totais de 2024 / jovens de 18–24 anos do Censo 2022 × 100. Validar categorias IBGE e incluir municípios sem oferta.
- B2: ingressantes FIES/ProUni, não matrículas. Não somar programas como beneficiários únicos sem verificar sobreposição.
- Suprimir células com menos de dez alunos em gráficos, tabelas, downloads e JSON entregue ao navegador. Reavaliar supressão sob filtros para evitar exposição indireta.

## Fontes técnicas consultadas

- Airflow, boas práticas para tarefas e reexecução: https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html
- PostgreSQL, restrições e ON CONFLICT: https://www.postgresql.org/docs/current/sql-insert.html
- Vercel, implantação de aplicação e ativos estáticos: https://vercel.com/docs/deployments/overview

## Limites desta entrega

Atualização após a Fase 1: ambiente local implementado e testado conforme docs/ambiente_docker.md. Dois PostgreSQL separados, serviços Airflow saudáveis e duas execuções de validação do manifesto concluídas. O parágrafo abaixo descreve o estado original da proposta, antes dessa implementação.

Arquitetura planejada. Sem contêineres iniciados, banco carregado, DAG executada ou página publicada nesta etapa. As verificações concluídas estão no relatório de exploração e nos JSONs gerados pelo script.
