# Evidências da Fase 1 — DataMind Equipe 03

Primeira carga analítica: [guia da orquestração baseada nos slides](docs/primeira_orquestracao.md). DAG `datamind_trajetoria_2015`, PostgreSQL e exportação JSON local para a P1 (MT presencial, coorte 2015).

Atualização: [ambiente Docker funcionando](docs/ambiente_docker.md), [avaliação dos slides do grupo](docs/avaliacao_slides_equipe.md) e [evidência dos testes](outputs/ambiente/validacao.json). As seções originais abaixo descrevem a perfilagem da Fase 1.

## Leitura

1. [Relatório de exploração](docs/relatorio_fase1.md)
2. [Arquitetura e idempotência propostas](docs/arquitetura_fase1.md)
3. [Roteiro de micro-pitch](docs/micro_pitch_fase1.md)
4. [Perfil por coluna](outputs/fase1/perfil_colunas.csv)

## Reprodução da perfilagem

Requer Python 3.11 ou superior e openpyxl 3.1.5. Nesta execução foi utilizado o Python fornecido pelo ambiente Codex e openpyxl 3.1.5.

Instalar dependências com `python -m pip install -r requirements-fase1.txt`.

Os arquivos originais estão em `data/raw/`, ignorada pelo Git. O manifesto em `outputs/fase1/manifesto.json` contém os links Drive exatos e os hashes. Para reproduzir em outra máquina, baixar desses links os cinco arquivos, preservar seus nomes e conferir os SHA-256. Os links do manifesto são estáveis; não contêm tokens temporários de download.

Executar na raiz: `python src/profile_phase1.py`.

O script lê arquivos locais, extrai somente o XLSX da trajetória, filtra MT nas fontes INEP e gera relatórios estruturais em `outputs/fase1/`. Não executa PostgreSQL, Airflow, Docker ou Vercel. As saídas substituem os relatórios anteriores. Nenhum indicador final de evasão é publicado.

`src/download_samples.py` foi o utilitário de transferência desta sessão. Ele recebe referências temporárias em `data/download_requests.private.json` e remove esse arquivo depois de uma transferência bem-sucedida. Esse arquivo temporário não integra a entrega. Para outra máquina, o caminho suportado nesta fase é obter os originais pelos links do manifesto e executar a perfilagem. A coleta automatizada oficial deve integrar a DAG da Fase 2.

## Cobertura

Trajetória 2015; Censo 2021; CPC 2021; Enade Licenciaturas 2025; IBGE 9514, resposta da UF MT. Outras edições e lotes municipais ainda pendentes.

## Publicação e colaboração

Arquivos preparados localmente. Não foram enviados ao GitHub ou Drive nesta etapa. Somente código, documentos e evidências agregadas devem ser versionados; os originais ficam fora do Git.

As conversas de IA usadas precisam ser exportadas integralmente em prompts/, conforme o guia do evento. Estes relatórios não substituem os registros de conversa.
