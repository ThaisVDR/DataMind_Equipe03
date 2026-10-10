# Avaliação da apresentação da equipe

Arquivo revisado: ../Materiais do grupo/Estrategia_Equipe_Rota_do_Diploma_Infografico.pptx.pdf, cinco páginas. Revisão textual e visual, com todas as páginas renderizadas e inspecionadas. Original preservado.

## Leitura geral

O material apresenta uma estratégia consistente para a Fase 1. O fluxo, os contrastes, a tipografia e as tabelas estão legíveis nas páginas renderizadas. A página 3 separa metadados do Airflow e banco analítico, distinção incorporada ao Docker Compose deste projeto. A página 4 explica bloqueio de publicação por validação e preservação da última versão válida. P2 mantém o mesmo horizonte e P5 separa períodos e populações, ambos cuidados metodológicos apropriados.

## Ajustes recomendados antes da entrega

1. Página 1: usar a pergunta central completa do guia, incluindo redes, modalidades e fatores associados. A unidade curso/coorte vale para trajetória; Censo e IBGE têm unidades diferentes.
2. Página 2, P3: incluir explicitamente evasão anual, além de matrículas e situações, distinguir privada com/sem fins lucrativos e mencionar investigação do ano atípico. A fórmula do evento é desvinculados / (matriculados + desvinculados + transferidos).
3. Página 3: substituir a saída genérica por “CSV/JSON validados → página web interativa na Vercel”, conforme a decisão atual. Os bancos continuarão em Docker/Linux.
4. Página 4: “mantém as mesmas chaves” não basta para idempotência. Acrescentar identificação por hash/versão, substituição transacional do recorte e conferência de contagens/totais na segunda execução.
5. Página 5: preservar as taxas publicadas da trajetória. Calcular acumulados das contagens anuais, não acumular novamente TCA/TDA. Ajuste por falecimentos precisa ser reconciliado com a fonte. A chave do Censo inclui curso, além de ano e localidade.
6. Acrescentar evidências reais de exploração: 5.150 linhas MT da trajetória 2015, 12.278 do Censo 2021 antes de excluir três registros sequenciais, seis SC no CPC e seis SC no Enade. Indicar edições examinadas e limitações. O deck atual explica principalmente o plano.
7. Corrigir os rodapés: há cinco páginas, mas todas mostram total de seis. O arquivo não permite saber se a sexta página foi omitida na exportação ou se a numeração ficou desatualizada.

O guia pede 3–4 slides ou uma página para a Fase 1. Este PDF tem cinco páginas. Para atender ao formato e aos três minutos, sugerimos consolidar capa/plano de perguntas e reunir regras de tratamento com evidências de exploração, ficando com quatro páginas. Não é preciso adicionar mais páginas.

## Decisões incorporadas

- Docker Compose para serviços Linux.
- Airflow com tarefas Python/SQL e execução manual inicial.
- PostgreSQL separado para metadados e dados analíticos.
- Volumes persistentes para bancos e logs.
- Camadas staging, core e mart, complementadas por raw e audit.
- Publicação condicionada a validações, com exportações para o site.

Estas decisões orientam a implementação. A DAG inicial registra manifesto e verifica conectividade. Uma segunda DAG, `datamind_trajetoria_2015`, implementa agora o recorte inicial da P1 conforme o fluxo da apresentação; consulte [primeira orquestração](../../DataMin.03/docs/primeira_orquestracao.md) para uso, evidências e limites. O fluxo completo P1–P5 permanece em desenvolvimento.

## Verificação adicional da página 5

Após a revisão, foi executado ../../DataMin.03/src/check_trajectory_method.py. O ajuste por falecimentos foi reconciliado em todos os 5.150 registros MT da coorte 2015: saldo exato e cinco taxas com erro máximo menor que 0,000000005 ponto percentual. Assim, esse item tem evidência para a coorte examinada. Preservar as taxas publicadas e a documentação da fórmula continua necessário.
