# Fase 2 · respostas iniciais e plano do painel

Extração do PostgreSQL em 10/10/2026, a partir do catálogo ativo. O snapshot identifica o lote e as versões das 31 fontes. Os resultados abaixo são descritivos, sujeitos às limitações registradas no painel. Percentuais arredondados.

## Primeiras respostas

**P1 — a turma presencial de 2015.** Dos 41.918 ingressantes em 515 cursos de Mato Grosso, no fim do acompanhamento em 2024 a TCA foi 38,80%, a TDA 59,90% e a TAP 1,30%, usando o denominador efetivo de 41.889 depois de 29 falecimentos acumulados. O maior incremento anual de desistência ocorreu no segundo ano do curso: 16,67%, em 2016. Os indicadores TCA/TDA/TAP são ponderados pelo denominador efetivo, não pela média simples dos cursos.

**P2 — onde comparar.** Cursos e áreas podem ser ordenados pela desistência acumulada no quinto ano. A extração inclui todas as seis coortes, comparadas no mesmo tempo de acompanhamento. Rótulos CINE idênticos são necessários para contrapor uma coorte à referência de 2015. Grupos de base menor que dez ficam de fora.

**P3 — ano atípico a explicar.** Na rede pública presencial, a proxy é 4,35% em 2021, 5,28% em 2022, 19,18% em 2023 e 6,63% em 2024. A volta em 2024 reforça a necessidade de investigar o salto antes de interpretá-lo como mudança estrutural. Censo mede situação anual; não segue os mesmos indivíduos.

**P4 — CPC.** De 558 cursos listados no ciclo CPC 2021–2023, 398 (71,33%) têm código correspondente à trajetória da coorte presencial de 2015. Após exigir dados contínuos, notas presentes e base de trajetória de ao menos dez, 371 cursos são elegíveis. A correlação de Pearson entre CPC contínuo e desistência acumulada, uma observação por curso, é 0,045. O resultado não indica relação linear relevante nesta comparação simples; não controla rede, área, tamanho ou seleção de quem é avaliado.

**P5 — licenciaturas.** 68 de 97 cursos têm correspondência por código à trajetória presencial, e 38 permanecem após exigir grau de licenciatura, medidas válidas e bases mínimas de dez. O painel compara a TDA/TCA da turma de 2015 com a proficiência dos participantes do Enade Licenciaturas 2025, separados por área. O Enade não reavalia a mesma turma de 2015.

## Exploração que sustenta o protótipo

O inventário ativo tem 6 arquivos de trajetória, 4 anos de Censo, 14 arquivos de indicadores e 7 tabelas IBGE: 31 fontes, totalizando 1.720.436 linhas nas granularidades próprias de cada fonte. A trajetória reúne 26.513 registros de curso/coorte/ano; o Censo, 62.674 registros em municípios de oferta; indicadores INEP, 1.919 linhas; IBGE, 1.629.330 linhas por tabela, localidade, variável, período e categorias. Essas contagens não devem ser somadas para formar um total de pessoas.

Os códigos permanecem texto. No Censo, filtramos nível de graduação, preservamos modalidade/categoria, e somamos polos por curso e ano antes dos indicadores. Trajetórias são agrupadas por contagens e horizonte comum; médias simples de taxas não são usadas. CPC e trajetória se ligam por código do curso; Censo e IBGE, por código municipal, nas perguntas territoriais ainda não implementadas. `SC`, valores em falta e códigos IBGE de supressão ficam distintos de zero.

As consultas validam 31 fontes ativas, unicidade das chaves curso/coorte/referência, reconciliação TCA+TDA+TAP pelo denominador efetivo, consistência de modalidade e rede entre polos, CPC único por curso no ciclo e mínimo de dez na base publicada. Perfil resumido verifica ausências em CINE e município da trajetória e CINE/rede no Censo; o dicionário completo por campo ainda é trabalho para a etapa final.

## Regras de negócio e rastreabilidade

A matriz completa de população, granularidade, campos, fórmula, denominador, elegibilidade, validação SQL e interpretação de cada gráfico está em [regras_negocio_dados.md](regras_negocio_dados.md). A aba **Evidências e método** do protótipo traz o resumo visual desse contrato. A EDA distingue os cinco recortes estruturais perfilados na Fase 1 das 31 versões carregadas; não generaliza os perfis por coluna às edições ainda não perfiladas.

## Plano do dashboard

O painel atende gestores de IES, secretarias e equipes de políticas públicas. Cada aba abre pela pergunta do guia e informa fonte, medida, recorte, horizonte e limites. Os gráficos usam taxas agregadas por contagens, com tabela acessível e botão para baixar o snapshot; filtros não escondem a definição da métrica. Uma extração versionada do PostgreSQL permite acesso fora da máquina da equipe.

Na próxima fase, acrescentar o bônus de financiamento (B2) ou a oferta territorial (B1), investigar documentalmente o salto de 2023 e ampliar validações de junção. Antes da apresentação final, testar a publicação Vercel, gerar PDF de contingência, completar README e entregar as conversas reais de IA em `prompts/`; nenhum registro de conversa foi fabricado por este documento.
