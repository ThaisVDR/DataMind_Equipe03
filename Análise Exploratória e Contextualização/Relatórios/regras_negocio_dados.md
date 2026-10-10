# Regras de negócio e rastreabilidade dos dados

DataMind Equipe 03 · DataHack UNIVAG · 10/10/2026

## Objetivo

Responder, com dados públicos e linguagem descritiva: **de cada 100 estudantes que entram numa graduação em Mato Grosso, quantos chegam ao diploma; em quais cursos, redes e modalidades a rota se perde; e o que aparece associado a essa trajetória?**

A unidade e a população variam por pergunta. Trajetória do INEP permite acompanhar uma coorte curso a curso; Censo Superior descreve estados agregados anuais de cursos/ofertas; CPC e Enade medem avaliações de ciclos e participantes próprios. Os denominadores não são intercambiáveis. Nenhum cruzamento abaixo identifica causa individual.

## Evidência exploratória e escopo

A EDA foi feita em duas etapas, que devem continuar claramente separadas nas apresentações:

1. **Perfil estrutural da Fase 1:** cinco recortes representativos, com todas as linhas de MT das edições escolhidas: Trajetória 2015 (5.150 registros), Censo 2021 (12.278 antes do filtro de nível), CPC 2021 (155), Enade Licenciaturas 2025 (97) e IBGE tabela 9514 em nível estadual N3 (2.412 observações longas). Foram verificados cabeçalhos, tipos de armazenamento, ausências, marcadores, chaves candidatas e junções diagnósticas. Isto não é amostra aleatória nem validação de todas as edições. Evidências reproduzíveis: `../../DataMin.03/outputs/fase1/resumo.json`, `perfil_colunas.csv`, `manifesto.json`, `juncoes_diagnosticas.json` e `reconciliacao_trajetoria.json`.
2. **Carga usada pelo protótipo:** 31 versões ativas (6 Trajetória, 4 Censo, 14 indicadores, 7 tabelas IBGE), total de 1.720.436 linhas nas granularidades próprias das fontes. São linhas de fatos/tabelas, não pessoas únicas. As estatísticas e resultados do painel vêm do snapshot exportado por `../../DataMin.03/src/export_dashboard.py` em transação PostgreSQL somente de leitura.

### Achados estruturais que viraram regras

- Trajetória: a chave curso + coorte + referência foi única no recorte de 2015; as dez linhas de referência de cada curso não são dez alunos distintos. Todos os registros testados eram modalidade presencial. Códigos numéricos lidos do Excel tornam-se texto no banco para preservar identificadores.
- Censo 2021: 12.275 de 12.278 linhas de MT são nível de graduação (1); três são nível 2 e ficam fora das métricas de graduação. `CO_CURSO` sozinho repete porque há oferta por município/modalidade/nível. A chave composta ano + curso + município + modalidade + nível foi única no recorte testado; repetição válida não deve ser removida com `DISTINCT`. Três graus acadêmicos ausentes permanecem ausentes.
- CPC 2021: seis CPC contínuos vazios e faixa SC; ambos significam conceito indisponível, nunca zero. Os cabeçalhos variam por edição e precisam de mapeamento explícito.
- Enade Licenciaturas 2025: seis proficiências vazias/SC e quatro contagens de participantes ausentes. A proficiência numérica observada está na escala 0–1 e só vira percentual na apresentação (×100). Participantes de 2025 não são a coorte de ingresso de 2015.
- IBGE 9514 perfilado é estadual (N3), não municipal (N6). Variável, unidade, localidade, período e combinação de categorias integram a identidade do registro. Totais não podem ser somados junto a subcategorias sobrepostas. O bônus municipal requer novo perfilamento.
- Junções diagnósticas da Fase 1 usam códigos únicos de MT contra a Trajetória presencial 2015: CPC 2021, 116/155 (74,84%); Enade Licenciaturas 2025, 68/97 (70,10%). São coberturas brutas estruturais, antes dos filtros finais, não equivalem às métricas de elegibilidade do snapshot P4/P5.

## Regras gerais de qualidade, agregação e publicação

1. **Preservar origem:** arquivos têm hash/versão em `audit.fd_dataset`; payload de origem é mantido em `staging.fd_raw`. `audit.fd_active` define a versão ativa. Nunca selecionar uma edição revisada sem promover sua versão validada.
2. **Tipar sem apagar significado:** códigos de curso, IES e município são `text`; quantidades não negativas são inteiras; taxas/notas são numéricas; valor original e status de ausência/supressão ficam distinguíveis. Nulo, `SC`, `--` e zero têm significados diferentes. Ausência não se imputa como zero.
3. **Respeitar granularidade:** não unir trajetória curso-ano diretamente com oferta municipal do Censo sem agregar primeiro; não contar a mesma pessoa entre linhas/tabelas; não somar categorias IBGE sobrepostas. Para ligar avaliações à trajetória, fixar uma linha por curso, coorte e horizonte antes do join.
4. **Agregação de taxas:** somar numeradores e denominadores elegíveis e depois dividir. Não calcular média simples das taxas dos cursos. Denominador nulo/zero implica resultado indisponível.
5. **Supressão:** não publicar grupos com base efetiva menor que 10; para avaliação, também exigir pelo menos 10 participantes quando aplicável. Reaplicar a regra a tabelas, dados baixáveis e filtros. O snapshot do navegador contém apenas agregados do painel, sem linhas individuais.
6. **Unidade da linguagem:** “associado”/“comparado” é descritivo. Não afirmar que CPC, rede, município, modalidade ou proficiência causa evasão. Não identificar desistência do curso com abandono de todo o ensino superior.

## Contrato dos gráficos do protótipo

| Visual/pergunta | População, chave e campos de origem | Regra, numerador / denominador e recorte | Camada PostgreSQL e validação | Controle no protótipo e interpretação |
|---|---|---|---|---|
| **P1 · Desfecho da turma** | INEP Trajetória; modalidade 1, MT; curso × coorte × referência; ingressantes, permanência, concluintes_ano, desistentes_ano, falecidos_ano. | Acumular concluintes, desistentes e falecidos por curso/coorte até a referência. Base efetiva = ingressantes − falecidos acumulados. TCA = 100 × concluintes acumulados / base; TDA = 100 × desistentes acumulados / base; TAP = 100 × permanência / base; TADA = 100 × desistentes no ano / base. TCA+TDA+TAP = 100 quando reconciliado. | `core.fd_trajetoria` → `core.trajetoria_acumulada_mt` → `mart.trajetoria_coorte_mt`; o exportador agrega contagens e confere saldo e chave. Coorte 2015 reconcilia exatamente em `reconciliacao_trajetoria.json`. | Filtro de coorte; cartão 100 pontos usa taxas arredondadas; série usa acumuladas e destaque usa TADA anual (pico não é maior valor acumulado). Contagem bruta de ingressantes pode diferir da base efetiva por óbitos. Trajetória disponível neste lote é presencial. |
| **P2 · Cursos e áreas** | Mesma Trajetória, usando rótulo CINE ou área geral CINE por curso e coorte. | Selecionar referência = coorte + 4 (quinto ano); agrupar contagens nesse mesmo horizonte. TDA = desistentes acumulados / denominador efetivo. Base comparativa 2015 na mesma chave CINE; ordenar pela TDA e omitir denominadores <10. | `core.trajetoria_acumulada_mt`; agrupamento no exportador `trajectory_groups`, após selecionar horizonte. Validação de saldo e supressão. | Filtros de coorte, área/rótulo e direção. Ausência de barra para grupo sem correspondência não significa 0%; composição entre coortes pode mudar. |
| **P3 · Rede e modalidade** | Censo Superior; nível 1 graduação; ano × curso × município × modalidade × categoria administrativa. Campos de matrícula, desvinculado, transferência; município representa oferta/polo. | Primeiro somar ofertas/polos por curso/ano e verificar modalidade/rede consistentes; mapear categorias 1–3 como pública, 4 privada com fins lucrativos, 5 privada sem fins lucrativos; excluir categoria especial não mapeada. Proxy = 100 × Σ desvinculados / Σ(matrículas + desvinculados + transferências), para ano × modalidade × rede. Distribuição de matrículas usa Σ matrículas de cada rede / Σ das redes exibidas. Denominador zero é nulo. | `core.fd_censo` → `mart.censo_rede_modalidade_mt`; consolidação de polos e regras explícitas em `build_snapshot`. Ano/matrícula e proxy precisam de base ≥10. | Filtros de modalidade e ano; série mostra proxy anual, não uma coorte longitudinal. Município do polo EAD não localiza residência do estudante. Salto 2023 é sinal para investigação, sem causa confirmada. |
| **P4 · CPC e trajetória** | Indicador CPC por código de curso, ciclo 2021–23, associado a uma observação da coorte presencial 2015 em 2024. | Primeiro medir correspondência por código. Para análise, exigir CPC contínuo não nulo e base efetiva da trajetória ≥10; agrupar por faixa CPC e recalcular TDA/TCA pelas contagens da trajetória. Pearson é não ponderado, uma observação por curso elegível; não ajustar confundidores. SC/ausente excluídos, nunca zero. | `core.fd_indicador` + `core.trajetoria_acumulada_mt`; validação de unicidade do CPC por curso antes do join; elegibilidade aplicada pelo exportador. | Barras com TDA por faixa e cartão de cobertura/correlação. CPC é medido depois do ingresso de 2015; correlação exploratória não indica efeito nem causalidade. Cobertura elegível difere da cobertura bruta da Fase 1. |
| **P5 · Licenciaturas e Enade** | Indicador Enade Licenciaturas 2025 associado por curso a trajetória 2015–24; restringe grau acadêmico licenciatura (código 2). | Exigir proficiência, contagem de participantes e total de concluintes no padrão disponíveis; participantes ≥10 e denominador trajetória ≥10. Por área Enade: conclusão/desistência são ponderadas pela base efetiva da Trajetória; proficiência = 100 × soma de concluintes no padrão / soma de participantes. Populações e denominadores separados. | `core.fd_indicador` + `core.trajetoria_acumulada_mt` + payload para a contagem no padrão; checar unicidade e que concluintes no padrão ≤ participantes. | Filtros usam apenas cursos elegíveis; tabela exibe denominadores distintos. Não multiplicar ou combinar as taxas para inferir quantos ingressantes viraram professores proficientes. |

### Perguntas bônus ainda fora dos gráficos

- **B1 — oferta territorial:** guia define vagas presenciais totais de 2024 em relação à população de 18–24 anos do Censo 2022. Antes de calcular: validar população/unidade, categorias totais sem sobreposição, nível municipal N6, municípios sem oferta, códigos IBGE e cobertura; exibir como vagas por 100 jovens, sem interpretar como matrícula ou acesso realizado. O snapshot atual não implementa essa medida.
- **B2 — financiamento:** guia define ingressantes FIES/ProUni. Censo 2021 contém esses campos, mas presença de coluna não prova cobertura nas edições 2022–24; não somar programas como beneficiários únicos sem verificar sobreposição. O protótipo atual não implementa esta medida.

## Estrutura do banco alinhada à EDA

| Esquema | Papel nesta solução | Relação com os achados |
|---|---|---|
| `audit` | Versões, lote, fonte ativa, hash e cobertura. | Sustenta proveniência; permite saber que os 31 conjuntos vêm de versões ativas. |
| `staging` | Payload original em JSONB por linha/versão. | Preserva rótulos e cabeçalhos enquanto contratos de edições evoluem. |
| `core` | Fatos tipados: trajetória, Censo, indicadores e IBGE, com chaves por granularidade. | Impede joins prematuros e codifica não negatividade/escalas; ids ficam texto. |
| `mart` | Visões agregadas reutilizáveis por coorte e por Censo/rede/modalidade. | Concentra fórmulas estáveis e deixa as perguntas analíticas reproduzíveis. |
| Snapshot estático | JSON agregado exportado por consulta somente leitura e transação consistente. | Separa publicação Vercel do banco local; atualiza somente após nova exportação e publicação do site. |

O DDL está em `../../DataMin.03/sql/init/002_fonte_dado.sql`; a extração e montagem do contrato estão em `../../DataMin.03/src/export_dashboard.py`. A regra no documento deve ser alterada junto da SQL/exportação e da definição exibida na interface quando a equipe mudar uma métrica.

## Próximas verificações antes da banca

O perfil por campo disponível cobre apenas as cinco edições da Fase 1. Generalizar para demais anos requer rodar perfil equivalente sobre todas as edições carregadas, reconciliar nomes/escala por versão, validar cobertura municipal IBGE, executar novamente a carga para evidenciar idempotência e explicar documentalmente o salto de 2023. Regras de supressão sob filtros também devem ser reavaliadas se forem criados novos cortes. A página atual apresenta P1–P5; B1/B2 permanecem explicitamente pendentes.
