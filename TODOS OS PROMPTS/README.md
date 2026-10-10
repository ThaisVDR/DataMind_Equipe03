# Registro dos prompts do Projeto DataMind — Rota do Diploma

Este arquivo reúne, em ordem cronológica, os pedidos feitos pela equipe nesta conversa sobre o DataHack UNIVAG 2026 e o Projeto Rota do Diploma. Foram registrados os pedidos, objetivos, links e materiais anexados que aparecem no histórico; mensagens de progresso sem uma nova solicitação foram incorporadas ao pedido correspondente. A análise do colega Pedro Renny foi mantida como parte do prompt que a apresentou.

## 1. Contexto do evento e pergunta central

> Bom dia! Nesta manhã, estou participando de um evento sobre Análise de Dados, aqui da minha faculdade (UNIVAG). Tenho meu grupo formado já e temos como um objetivo criar um Projeto de Dados, onde temos apresentou para nós um contexto e o que devemos fazer. Para que você saiba de todo este contexto do evento e do que deve ser feito, análise detalhadamente o github do nosso grupo que criamos para alocar nosso projeto deste evento. O link está logo abaixo: https://github.com/ThaisVDR/DataMind_Equipe03.git

> Em relação a pergunta central seria essa: “De cada 100 estudantes que entram numa graduação em Mato Grosso, quantos chegam ao diploma? Em quais cursos, redes e modalidades a rota se perde, e o que está associado a isso?” Eu coloquei aqui o HTML de guia que foi disponibilizado para todos do evento e além de um slide que foi colocado para a apresentação do evento. Faça análise novamente destes arquivos, pois que você saiba exatamente cada passo que devemos fazer para cada grupo.
>
> Materiais anexados: guia_participante.html e DataHack_Abertura_Rota_do_Diploma.pptx.

> Primeiramente, devemos realizar esta fase 1 no evento. Meu grupo já está cadastrado no Sistema e estamos começando aqui a trabalhar.

> Maravilha que você analisou completamente tudo sobre este evento. Destaquei uma anotação já do que devemos apresentar para a banca. Destaquei um anotação do que disse acima e mais um print da tela do que devemos entregar.
>
> Material anexado: imagem com os itens esperados pela banca técnica nas Fases 1, 2 e 3, incluindo planejamento de ELT, download e perfil das bases, escolha do banco, ingestão e protótipo, dashboard final, recomendações e documentação reproduzível.

## 2. Arquitetura, fontes e preparação da Fase 1

> Decidimos utilizar o Airflow como nossa plataforma de open-source, para nossa modelagem e orquestração de dados e alocar este nosso sistema do Airflow no Docker com Linux, e utilizando como banco de dados o PostgreSQL. Os dados que vamos buscar, a pergunta central do contexto e as perguntas priorizadas que já foram definidas pelos administradores do evento. Eu criei um pasta compartilhada no Drive com o meu grupo todo, onde definimos que seria nosso plano B e nosso GitHub como plano A. Eu coloquei aqui o link desta pasta do Drive para que você possa buscar os dados.
>
> Pasta compartilhada: https://drive.google.com/drive/folders/1rFUqfrsmLJumJsYJBRxIQIh9Od4TRLGA?usp=sharing

> Faça isso aqui primeiramente: transforme o inventário das fontes em evidência, verificando uma amostra de cada fonte e registrando cabeçalhos, tipos, nulos e chaves; documente as camadas e explique como a reexecução evitará duplicações. Reproduza os resultados descritos nos PDFs antes de apresentá-los como verificações desta execução.
>
> Pensamento do grupo: utilizar Airflow open-source, Docker/Linux e PostgreSQL; para visualização, montar uma página web interativa e hospedá-la na Vercel.

> Meu grupo elaborou um slide de apresentação para entregarmos essa primeira parte do evento. Avalie e veja como fizemos, para agregar nas suas informações. Temos que estudar primeiramente a base de dados disponibilizada e, depois desse estudo, elaborar o ambiente Docker para subir e rodar corretamente.
>
> Material anexado: Estrategia_Equipe_Rota_do_Diploma_Infografico.pptx.pdf.

## 3. Airflow, ETL e instruções de execução

> Pode continuar seu processo.

> Ok, quero começar a orquestrar os dados no airflow, por onde eu começo?

> Utilize essa apresentação como base.
>
> Material anexado: Estrategia_Equipe_Rota_do_Diploma_Infografico.pptx.pdf.

> Desenvolva todo o airflow aqui: C:\Users\THAIII\Documents\GitHub\DataMind_Equipe03, se for necessário modifique diretamente o airflow.

> Com base (C:\Users\THAIII\Documents\GitHub\DataMind_Equipe03\fonteDado) desenvolva o etl conectando no postgreSQL.

> Continue de onde parou.

> Tenho uma outra pasta local que estou organizando de fato a estrutura do meu diretório deste Projeto. Estruture a parte do sistema nesta pasta local e, a partir daqui, estou atualizando o repositório do GitHub do grupo. Pare de rodar o sistema, monte uma estrutura correta nesta pasta e me dê comandos para rodar manualmente. Depois disso, iremos revisar o servidor no Docker e o sistema do Airflow.
>
> Caminho da pasta: C:\Users\THAIII\DATAHCK_2026\DataMind.

> Depois de toda essa estruturação das pastas e padronização na hora de rodar e parar o sistema manualmente, quero subir agora o repositório do Projeto no GitHub para atualizar e que os administradores vejam as atualizações do grupo.
>
> Repositório: https://github.com/ThaisVDR/DataMind_Equipe03.git

> Diante desta última apresentação, faltamos falar da parte da análise exploratória das bases. O que estou dizendo seria um feedback passado a todos os grupos. Devemos ir para a próxima etapa do evento, definida no guia do participante, que seria a produção do protótipo.
>
> Material anexado: guia_participante.html.

> Continue os processos.

> Devemos olhar o que fizemos de análise exploratória das bases disponibilizadas. Nossa equipe faltou expor o que viu das bases. Vamos estudar as bases e gerar documentação para embasar as regras de negócio; depois estruturar o banco a partir das análises e gerar uma página HTML interativa como primeiro protótipo, para visualizar o que foi definido em cada gráfico.

> Tenho uma pasta chamada “Análise Exploratória e Contextualização” para guardar as documentações das análises. Coloque ali as documentações que você gerar e as que o grupo trouxer. Renomeie a pasta “sistema” para “DataMin.03”, organize as conexões dos bancos e use nomes padronizados para o grupo e o projeto. Separe como subir o Airflow e como abrir o protótipo, organize as consultas SQL e defina uma rota correta para a pasta de fontes de dados.

> Depois dessa organização e atualização do repositório do Projeto no GitHub, monte as orientações de como rodar cada coisa dentro de um README: banco de dados, Airflow e DAGs.

> Pare de rodar o Airflow para que eu faça tudo manualmente.

## 4. Protótipo e análises do grupo

> Ainda na parte do protótipo, meu grupo trouxe análises feitas a partir do que falamos sobre o protótipo que você criou. Analise o que meu grupo trouxe e veja como podemos melhorar a partir dessas análises.
>
> Análise do meu colega Pedro Renny:
>
> Visão 1: O Tamanho do Funil e a Queda (Foco na Pergunta P1). Objetivo: Mostrar o panorama geral da perda de alunos em Mato Grosso e identificar o momento crítico da jornada. Sugestões: gráfico de Sankey ou funil de conversão para mostrar ingressantes divididos entre concluintes, desistentes e matriculados após dez anos; barras da desistência ano a ano com destaque para o primeiro e segundo anos; aviso de que comparações entre coortes precisam de horizontes iguais e de que “matriculado” em coorte recente é pendência, não perda.
>
> Visão 2: O Mapa da Evasão por Cursos e Áreas (P2). Objetivo: identificar grupos com maiores e menores taxas de retenção. Sugestões: dispersão com evasão acumulada no eixo X, diplomação no eixo Y e tamanho da bolha representando ingressantes; tabelas de cinco maiores/menores; destaque a Engenharia (27,9% de diplomação), Computação (25,6%), Matemática (78,7% de desistência), Engenharia de Produção (80,4%) e Direito (15.772 desistentes); filtro de coortes preservando horizonte de cinco anos.
>
> Visão 3: Dinâmica de Mercado — Modalidades e Redes (P3). Objetivo: comparar rede pública/privada e EAD/presencial em anos recentes. Sugestões: séries anuais de matrículas e desvinculações de 2021 a 2024; barras empilhadas a 100%; ressalva de que a localização EAD usa a UF da sede da IES como aproximação e não identifica onde o estudante estuda.
>
> Visão 4: Relação entre Qualidade e Formação (P4 e P5). Sugestões: comparar faixas do CPC com desistência, sem presumir causalidade; um painel próprio para licenciaturas, mostrando trajetória e proficiência do Enade 2025, com ressalva de que os grupos e denominadores são diferentes.
>
> Visão 5: Desertos e Financiamento (bônus B1 e B2). Sugestões: mapa municipal de Mato Grosso com vagas por 100 jovens de 18–24 anos, usando dados do IBGE; comparar desistência de estudantes com e sem FIES/ProUni.
>
> Dicas para a entrega: transparência metodológica sobre limites e cobertura das fontes; botão ou seção de metodologia; KPIs e textos curtos de insights; cores consistentes para conclusão, desistência e matrícula.

> Ok, faça essas mudanças do nosso protótipo a partir do que você analisou acima.

> Eu conferi todo o protótipo e possui muitas palavras escritas erradas. Coloquei aqui um guia de estilos para dashboards; use-o para fazer as redefinições do nosso dashboard.
>
> Material anexado: UNIVAG_Guia_Estilos_Dashboards.md.

> Quero que você construa nosso dashboard de acordo com o que construímos antes.

> Tire toda a estilização no estilo da UNIVAG e quero do jeito que estava.

## 5. Organização dos pedidos neste repositório

> Gere um arquivo onde crie uma pasta dentro do nosso repositório chamada “TODOS OS PROMPTS”, com todos os prompts que fizemos nesta conversa sobre o Projeto como um todo. Depois disso, atualize o repositório no GitHub.

## Referências do projeto mencionadas na conversa

- GitHub: https://github.com/ThaisVDR/DataMind_Equipe03.git
- Drive do grupo: https://drive.google.com/drive/folders/1rFUqfrsmLJumJsYJBRxIQIh9Od4TRLGA?usp=sharing
- Diretório local principal: C:\Users\THAIII\DATAHCK_2026\DataMind
- Diretório inicial de trabalho do sistema: C:\Users\THAIII\Documents\GitHub\DataMind_Equipe03
- Guia do participante: guia_participante.html
- Slides do evento: DataHack_Abertura_Rota_do_Diploma.pptx; Estrategia_Equipe_Rota_do_Diploma_Infografico.pptx.pdf
- Guia visual compartilhado: UNIVAG_Guia_Estilos_Dashboards.md

> Observação: este registro consolida os pedidos e os detalhes identificáveis no histórico desta conversa. Trechos extensos de análise foram resumidos para facilitar consulta; links e materiais de origem foram preservados.

## Anexo A — Registro detalhado dos pedidos

A lista abaixo detalha os pedidos em sua ordem aproximada de envio. Os textos foram transcritos do histórico visível da conversa; a pontuação e quebras de linha foram ajustadas para leitura, sem mudar a intenção. As anotações sobre Fase 1 e os arquivos anexados estão associadas aos pedidos correspondentes.

### A1. Análise do repositório e do evento

> Bom dia! Nesta manhã, estou participando de um evento sobre Análise de Dados, aqui da minha faculdade (UNIVAG). Tenho meu grupo formado já e temos como um objetivo criar um Projeto de Dados, onde temos apresentou para nós um contexto e o que devemos fazer. Para que você saiba de todo este contexto do evento e do que deve ser feito, análise detalhadamente o github do nosso grupo que criamos para alocar nosso projeto deste evento. O link está logo abaixo: https://github.com/ThaisVDR/DataMind_Equipe03.git

> Em relação a pergunta central seria essa: “De cada 100 estudantes que entram numa graduação em Mato Grosso, quantos chegam ao diploma? Em quais cursos, redes e modalidades a rota se perde, e o que está associado a isso?” Eu coloquei aqui o HTML de guia que foi disponibilizado para todos do evento e além de um slide que foi colocado para a apresentação do evento. Faça análise novamente destes arquivos, pois que você saiba exatamente cada passo que devemos fazer para cada grupo.
>
> Arquivos: guia_participante.html e DataHack_Abertura_Rota_do_Diploma.pptx.

> Primeiramente, devemos realizar está fase 1 no evento. Meu grupo já está cadastrado no Sistema e estamos começando aqui a trabalhar.

> Maravilha que você analisou completamente tudo sobre este evento. Destaquei uma anotação já do que devemos apresentar para a banca. Destaquei um anotação do que disse acima e mais um print da tela do que devemos entregar.
>
> Anexo: imagem “O que a banca técnica espera em cada fase”.

### A2. Bases de dados, Fase 1 e arquitetura

> Decidimos utilizar o Airflow como nossa plataforma de open-source, para nossa modelagem e orquestração de dados e alocar este nosso sistema do Airflow no Docker com Linux, e utilizando como banco de dados o PostgreSQL. Os dados que vamos buscar, a pergunta central do contexto e as perguntas priorizadas que já foram definidas pelos administradores do evento.
>
> Eu criei um pasta compartilhada no Drive com o meu grupo todo, onde definimos que seria nosso plano B e nosso GitHub como plano A. Eu coloquei aqui o link desta pasta do Drive para que você possa buscar os dados.
>
> Link da pasta compartilhada: https://drive.google.com/drive/folders/1rFUqfrsmLJumJsYJBRxIQIh9Od4TRLGA?usp=sharing

> Faça isso aqui primeiramente que você já definiu: verificar uma amostra de cada fonte, registrar cabeçalhos, tipos, nulos e chaves, documentar camadas e explicar como a reexecução evitará duplicações. Reproduzir os resultados descritos nos PDFs antes de apresentá-los como verificações desta execução.
>
> Como pensamento do grupo: utilizar Airflow open-source em Docker/Linux, PostgreSQL e uma página web interativa hospedada na Vercel.

> Meu grupo elaborou um slide de apresentação para entregarmos essa primeira parte do evento. Quero que você avalie e veja como fizemos, para agregar nas suas informações. Temos que estudar primeiramente a base de dados disponibilizada para nós e, depois desse estudo, elaborar nosso ambiente Docker para subir e rodar tudo corretamente.
>
> Anexo: Estrategia_Equipe_Rota_do_Diploma_Infografico.pptx.pdf.

> Pode continuar seu processo.

> Ok, quero começar a orquestrar os dados no airflow, por onde eu começo?

> Utilize essa apresentação como base.
>
> Anexo: Estrategia_Equipe_Rota_do_Diploma_Infografico.pptx.pdf.

### A3. Desenvolvimento de Airflow, ETL e organização local

> Desenvolva todo o airflow aqui: C:\Users\THAIII\Documents\GitHub\DataMind_Equipe03, se for necessario modifique diretamente o airflow.

> Com base (C:\Users\THAIII\Documents\GitHub\DataMind_Equipe03\fonteDado) desenvolva o etl conectando no postgreSQL.

> Continue de onde parou.

> Ainda estou organizando uma outra pasta local para a estrutura do diretório do Projeto. Estruture a parte do sistema nesta pasta e, a partir daqui, estou atualizando o repositório do GitHub. Pare de rodar o sistema, monte a estrutura corretamente nessa pasta e me dê comandos para eu rodar manualmente. Depois disso, vamos revisar o servidor no Docker e o sistema do Airflow.
>
> Caminho: C:\Users\THAIII\DATAHCK_2026\DataMind.

> Depois dessa estruturação e padronização para rodar e parar o sistema manualmente, quero subir agora o repositório do Projeto no GitHub, para atualizar e que os administradores vejam as atualizações do grupo.
>
> Repositório: https://github.com/ThaisVDR/DataMind_Equipe03.git

> Diante desta última apresentação, faltamos falar da parte da análise exploratória das bases de dados. Isto seria um feedback do que foi passado para todos os grupos do evento. Agora devemos ir para a próxima etapa definida no guia do participante, que seria a produção do protótipo.
>
> Anexo: guia_participante.html.

> Continue os processos.

> Diante do que você já fez, devemos olhar o que fizemos de análise exploratória das bases de dados disponibilizadas. Nossa equipe faltou expor o que vimos das bases. Vamos estudar as bases, gerar documentação para embasar as regras de negócio, estruturar o banco a partir das análises e gerar uma página HTML interativa como primeiro protótipo, com os dados para vermos o que foi definido em cada gráfico.

> Diante dessas documentações, tenho uma pasta chamada “Análise Exploratória e Contextualização”, onde estou colocando documentações relacionadas às análises. Coloque ali as documentações das análises para não ficar bagunçado. Sobre o sistema, renomeie a pasta “sistema” para “DataMin.03”, organize melhor as conexões dos bancos, traga senhas (um exemplo poderia ser “datamin03”) e nomes padrões de acordo com o grupo e o Projeto. Organize a pasta do Sistema na hora de subir: quero separar quando subir Airflow e quando abrir o protótipo; organizar as pastas das consultas SQL; organizar a pasta de fontes de dados definindo uma rota certa para rodar sem erros. Vamos fazer toda essa organização do diretório!

> Depois dessa organização e atualização do repositório no GitHub, monte as orientações para rodar cada coisa dentro de um README. Quero saber como rodo o banco de dados e o Airflow com as DAGs.

> Quero que você pare de rodar o Airflow para que eu faça manualmente tudo.

### A4. Análise do Pedro e reconstrução do protótipo

> Ainda na parte do protótipo, meu grupo trouxe análises feitas a partir do que falamos sobre o protótipo que criou atualmente. Analise o que meu grupo trouxe e veja como podemos melhorar a partir das análises dele.
>
> Análise do meu colega Pedro Renny:
>
> Visão 1: O Tamanho do Funil e a Queda (Foco na Pergunta P1). Objetivo: Mostrar o panorama geral da perda de alunos em Mato Grosso e identificar o momento crítico da jornada. Como responder da melhor forma: Gráfico de Sankey ou Funil de Conversão para ilustrar o fluxo dos ingressantes (ex.: os 41.918 de 2015) se dividindo entre concluintes (38,8%), desistentes (59,9%) e matriculados (1,3%) após 10 anos. Gráfico de Barras (Decaimento por Ano): mostrar a evasão ano a ano e destacar “Ano 0” (16,77 desistências por 100) e “Ano 1” (15,05 por 100), evidenciando que a rota se perde no início. Nota de Contexto: comparar horizontes iguais (ex.: limite de 5 anos), pois coortes recentes ainda têm matriculados, o que é pendência e não perda.
>
> Visão 2: O Mapa da Evasão por Cursos e Áreas (Foco na Pergunta P2). Objetivo: identificar os “vilões” e os “heróis” da retenção. Como responder da melhor forma: dispersão (scatter plot) com evasão acumulada no eixo X, taxa de diplomação no eixo Y e volume de ingressantes no tamanho da bolha. Tabelas de Top/Bottom 5: áreas com menor diplomação, Engenharia (27,9%) e Computação (25,6%); cursos com maior perda percentual, Matemática (78,7% de desistência) e Engenharia de Produção (80,4%); maior perda absoluta, Direito (15.772 desistentes). Filtro interativo de coortes, mantendo horizonte de cinco anos para comparação justa.
>
> Visão 3: Dinâmica de Mercado — Modalidades e Redes (Foco na Pergunta P3). Objetivo: mostrar como o modelo de negócio (Pública x Privada, EAD x Presencial) afeta retenção nos anos recentes (2021–2024). Como responder: linhas para evolução de matrículas e desvinculações; barras 100% empilhadas para comparar Pública x Privada e Presencial x EAD. Limitação: trajetórias EAD não têm UF do curso; usa-se a UF da sede da IES como aproximação, o que não representa necessariamente onde o aluno estuda.
>
> Visão 4: A Relação entre Qualidade e Formação (Foco em P4 e P5). Objetivo: analisar se uma nota boa no MEC (CPC) e a proficiência no Enade se traduzem em conclusão. Para P4: dispersão ou boxplot com faixas CPC de 1 a 5 e taxa de desistência (TDA); se qualidade retém, a tendência seria decrescente. Para P5: dashboard das licenciaturas com funil de desistência e proficiência no Enade 2025 entre concluintes; evidenciar áreas com baixa formação e proficiência.
>
> Visão 5: Desertos e Financiamento (Bônus B1 e B2). Objetivo: explorar diferenciais territoriais e financeiros. Mapa coroplético de Mato Grosso (B1) com vagas por 100 jovens de 18–24 anos e identificação de desertos de ensino superior usando tabelas do IBGE. Análise FIES/ProUni (B2): comparar desistência entre alunos com e sem financiamento.
>
> Dicas de Ouro para a Entrega Final: botão “Info/Metodologia” com limitações, inclusive que comparações descritivas não indicam causalidade e há diferença de cobertura entre Censo e Trajetórias. Textos dinâmicos e KPIs no topo, por exemplo “A cada 100 alunos, quase 60 desistem, e a maior sangria ocorre nos 2 primeiros anos.” Consistência de cores: verde para concluintes/diploma, vermelho para desistência/TDA, cinza para matriculados.

> Ok, faça essas mudanças do nosso protótipo a partir do que você analisou acima.

> Eu conferi todo o protótipo e possui muitas erradas, escritas das palavras erradas. Eu coloquei aqui um guia para estilos de dashboards e use isso para fazer redefinições do nosso dashboard.
>
> Anexo: UNIVAG_Guia_Estilos_Dashboards.md.

> Quero que você construa nosso dashboard de acordo com o que construímos antes.

> Tire toda a estilização no estilo da UNIVAG e quero do jeito que estava.

### A5. Arquivamento e publicação solicitados agora

> Gere um arquivo onde crie uma pasta dentro do nosso repositório TODOS OS PROMPTS que fizemos aqui nesta conversa, do que fizemos do Projeto como um todo. Depois disso atualize para o nosso repositório no GitHub.
