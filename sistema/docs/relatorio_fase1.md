# Fase 1 — Exploração e estratégia

DataMind Equipe 03 · DataHack UNIVAG · 10/10/2026

## Pergunta central

De cada 100 estudantes que entram numa graduação em Mato Grosso, quantos chegam ao diploma? Em quais cursos, redes e modalidades a rota se perde, e o que está associado a isso?

## Escopo e método da verificação

Cinco arquivos foram baixados da pasta compartilhada do grupo, preservados localmente e identificados por tamanho e SHA-256 no manifesto. Esta execução examinou uma edição de cada família de dados. Para os quatro arquivos INEP, percorreu a aba/CSV selecionado e perfilou todas as linhas com UF MT/51. No IBGE, perfilou a resposta estadual completa da tabela 9514. Não se trata de amostra aleatória, nem de validação de todas as edições do projeto.

A perfilagem mede cabeçalhos, tipos de armazenamento, vazios, marcadores, chaves candidatas, duplicações e cobertura diagnóstica por código do curso. Não calcula respostas finais de evasão. Não executa cargas no PostgreSQL nem DAGs do Airflow.

## Evidências medidas

| Fonte | Recorte perfilado | Linhas | Colunas | Cabeçalho | Duplicações excedentes na chave testada |
|---|---|---:|---:|---|---:|
| Trajetória 2015–2024 | Todas as linhas CO_UF=51 | 5.150 | 31 | Linha 9, aba INDICADORES_TRAJETORIA | 0 |
| Censo Superior 2021 | Todas as linhas CO_UF=51, antes do filtro de nível | 12.278 | 200 | Linha 1, CSV com ponto e vírgula | 0 |
| CPC 2021 | Todas as linhas Sigla da UF=MT | 155 | 40 | Linha 1, aba CPC2021 | 0 |
| Enade Licenciaturas 2025 | Todas as linhas Sigla da UF=MT | 97 | 20 | Linha 1, aba Conceito Enade Licenciaturas | 0 |
| IBGE 9514 | Resposta estadual MT, nível N3 | 2.412 observações após expansão | 7 campos no formato longo criado | JSON hierárquico | 0 |

Os sete campos do IBGE foram criados pela expansão de variável, unidade, nível, localidade, período, categorias e valor. Não são sete colunas de uma planilha original. Não houve chave vazia nos cinco recortes testados. A ausência de duplicação nesses recortes não garante unicidade em outras edições.

O CSV nacional do Censo 2021 tem 444.786 registros, 257.896.224 bytes descompactados e foi lido como Windows-1252. As abas selecionadas de CPC e Enade contêm, respectivamente, 8.000 e 4.950 linhas não vazias após o cabeçalho. A trajetória contém 281.431 linhas não vazias após o cabeçalho, incluindo possíveis notas; esse número não deve ser apresentado como total nacional de registros válidos.

## Achados que mudam a implementação

### Censo: graduação e granularidade

Das 12.278 linhas de MT, 12.275 têm TP_NIVEL_ACADEMICO=1 e três têm valor 2. A análise de graduação deve usar o nível 1. TP_GRAU_ACADEMICO está vazio em três linhas; vazio não deve ser automaticamente preenchido com um grau.

O código CO_CURSO sozinho tem 9.541 repetições excedentes nas linhas MT. A chave composta testada foi ano, curso, município, modalidade e nível. Ela é única neste recorte, mas sua minimalidade ainda não foi determinada. Repetição do curso em diferentes ofertas não é motivo para apagar registros com DISTINCT.

Os campos QT_ING_FIES, QT_ING_PROUNII e QT_ING_PROUNIP existem no Censo 2021 consultado. Portanto, o bônus B2 pode manter o denominador de ingressantes exigido pelo guia nessa edição. Presença das colunas não comprova cobertura ou consistência nas edições 2022–2024.

### Trajetória: curso, coorte e referência

Foram encontrados 515 cursos por ano de referência, de 2015 a 2024, totalizando 5.150 registros. Todos os registros de MT desse arquivo têm modalidade 1, presencial. Não houve vazios em nenhuma das 31 colunas no recorte perfilado.

A chave curso + ano de ingresso + ano de referência não apresentou duplicação. A origem armazena códigos como valores numéricos no Excel; o modelo deve convertê-los para identificadores textuais de maneira controlada. Não extrapolar a cobertura presencial observada para todo o EAD de MT.

### CPC: cabeçalhos e ausência de conceito

Os cabeçalhos têm espaços e notas como Código do Curso** e Sigla da UF**. O script preserva os cabeçalhos originais no JSON e registra os nomes com espaços normalizados para inspeção. A implementação deve usar mapeamento explícito por edição.

Entre os 155 registros MT, seis têm CPC contínuo vazio e CPC Faixa=SC. São ausência de conceito, não nota zero. Há também nulos em componentes do indicador: por exemplo, 17 registros sem Nota Bruta - IDD e 13 sem sigla da IES. O perfil completo por coluna está no CSV de evidências.

### Enade: escala e população

Entre 97 registros MT, seis têm proficiência vazia e conceito SC. Quatro têm quantidade de participantes vazia. A faixa numérica observada da proporção de proficiência é 0–1, coerente com o dicionário do guia; para exibir porcentagem, multiplicar por 100.

A variável usa participantes da edição 2025. Ela não identifica individualmente os estudantes que ingressaram na coorte 2015. A comparação deve manter essa limitação visível.

### IBGE: categorias e território

O arquivo mt_uf.json contém nível N3, Unidade da Federação. Contém as unidades Pessoas e Percentual. A chave precisa incluir variável e combinação de categorias, além de localidade e período. Somar totais junto às categorias de sexo, idade ou declaração duplica populações.

Esta verificação estadual é suficiente para inspecionar o formato, mas não valida o bônus municipal B1. Será necessário ler os lotes municipais, selecionar população em pessoas, sexo total, declaração total e idades 18–24 sem incluir faixas sobrepostas.

## Tipos e nulos

| Família de campo | Armazenamento observado | Tipo proposto no PostgreSQL |
|---|---|---|
| Código de curso, IES e município | Números em XLSX; texto em CSV/JSON | text |
| Ano e categorias codificadas | Número ou texto conforme formato | integer para ano; código categórico documentado |
| Quantidades | Números em XLSX; texto numérico em CSV | bigint, mantendo NULL quando ausente |
| Taxas e conceitos contínuos | Valores numéricos e ausências | numeric com escala documentada |
| SC, sinais e valores ausentes | Texto ou célula vazia | Coluna de status separada do valor numérico |
| IBGE categorias | Estrutura hierárquica | Identificadores de classificação/categoria e chave canônica |

O CSV de perfil registra tipos de armazenamento, não uma tipagem SQL já aplicada. As contagens QT_ do Censo passaram por teste lexical de inteiro não negativo, registrado no JSON. A tipagem final, limites e reconciliação entre totais continuam na transformação.

## Junções diagnósticas executadas

Os códigos numéricos integrais do Excel foram representados como texto. Foram comparados conjuntos de códigos únicos, evitando multiplicar as dez referências anuais da trajetória.

| Origem MT | Cursos na origem | Encontrados na trajetória 2015 MT | Não encontrados | Cobertura |
|---|---:|---:|---:|---:|
| CPC 2021 | 155 | 116 | 39 | 74,84% |
| Enade Licenciaturas 2025 | 97 | 68 | 29 | 70,10% |

Esses percentuais usam todos os códigos do recorte, inclusive SC. Não constituem a amostra final de P4/P5. Não houve investigação individual da razão dos não correspondentes. A seleção da coorte, horizonte, grau acadêmico e validade do conceito deve ocorrer antes da junção analítica final.

## Confronto com os documentos recebidos

A arquitetura agora incorpora Airflow/Docker/Linux, PostgreSQL e web na Vercel, conforme a decisão do grupo. As propostas de Streamlit nos PDFs não são a escolha vigente.

As medidas do evento permanecem: P3 com desvinculados / (matriculados + desvinculados + transferidos); B1 com vagas presenciais totais de 2024 e população jovem de 2022; B2 entre ingressantes. As alternativas dos PDFs não substituem essas definições.

Esta execução reproduziu a inspeção de estrutura e chaves para os cinco recortes listados e mediu junções próprias. Não reproduziu integralmente os resultados dos PDFs em todas as bases/anos, nem confirmou suas conclusões de taxas, população jovem ou anomalias de 2023.

## Próxima etapa e evidências pendentes

### Complemento posterior à revisão dos slides

O script src/check_trajectory_method.py confrontou o saldo e as cinco taxas nos 5.150 registros MT da coorte 2015. Para este arquivo, a soma acumulada de concluintes, desistentes e falecidos, adicionada à permanência, coincide exatamente com os ingressantes. O denominador QT_INGRESSANTE menos falecidos acumulados reproduz TAP, TCA, TDA, TCAN e TADA com erro máximo inferior a 0,000000005 ponto percentual. TCA e TDA usam contagens acumuladas; TCAN e TADA usam contagens do ano. A evidência está em outputs/fase1/reconciliacao_trajetoria.json. Essa verificação confirma o ajuste citado pelo grupo para esta coorte, sem generalizar a outras edições. Para uma agregação pelas contagens, usar o denominador elegível reconciliado e documentar diferenças em relação à ponderação simplificada por ingressantes sugerida no guia.

1. Estender perfilagem às coortes 2016–2020, Censo 2022–2024, CPC 2022–2023 e lotes municipais IBGE.
2. Validar dicionários, regras de acumulação e denominadores da trajetória antes de calcular taxas agregadas.
3. Implementar os adaptadores e SQL, conforme arquitetura_fase1.md.
4. Demonstrar conexão com PostgreSQL e serviços Airflow no ambiente da equipe.
5. Rodar duas cargas e comparar resultados para comprovar idempotência no banco.
6. Construir P1–P5 e preparar JSON agregado para a página web.

## Arquivos de evidência

- outputs/fase1/manifesto.json: origem Drive, bytes e SHA-256 dos cinco arquivos.
- outputs/fase1/perfil_colunas.csv: cabeçalhos normalizados, tipos, vazios e marcadores de todas as colunas perfiladas.
- outputs/fase1/resumo.json e perfis individuais: escopo, chaves, contagens e verificações.
- outputs/fase1/juncoes_diagnosticas.json: cobertura por código.
- src/profile_phase1.py: código executado.
- docs/arquitetura_fase1.md: camadas, modelo e estratégia de idempotência ainda a implementar.

Os relatórios não exportam contagens de alunos por curso nem resultados de grupos pequenos. As quantidades nesta página são registros, cursos e diagnósticos estruturais, não indicadores de estudantes.
