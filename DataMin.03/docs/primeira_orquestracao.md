> Registro da primeira DAG de trajetória. Para a ingestão atual das 31 fontes, use o manual em [ETL fonteDado](etl_fonte_dado.md) e o lançador da pasta DataMin.03.

> Registro da etapa anterior. O diretório e os comandos atuais estão no [README do sistema](../README.md). A nova pasta foi organizada com os serviços parados.

# Primeira orquestração baseada na apresentação

Base: `Estrategia_Equipe_Rota_do_Diploma_Infografico.pptx.pdf`, recebido da pasta Downloads. As páginas 3–5 orientam a arquitetura, a sequência e as regras do fluxo. O PDF permanece inalterado.

## Começar pela interface

1. Abrir http://localhost:8080 e entrar com usuário `datamind03`. A senha está somente no arquivo local `runtime/private/ACESSO_LOCAL.txt`.
2. Abrir a DAG `datamind_trajetoria_2015` e clicar em **Trigger** para uma execução manual, sem parâmetros.
3. Acompanhar o gráfico: `extrair → carregar → transformar → conferir → decidir → publicar` ou `quarentena`.
4. Consultar o log da tarefa quando houver erro. Uma tarefa cinza `skipped` no ramo não escolhido é esperada.
5. Após publicação, consultar `mart.p1_trajectory_active` no PostgreSQL e `outputs/analytics/current.json` para localizar o JSON aprovado.

A DAG está sem agendamento automático: cada execução é iniciada pela equipe. A DAG anterior, `datamind_validar_ambiente`, continua disponível para conferir manifesto e conectividade.

Alternativa no terminal, a partir da raiz do projeto:

```powershell
docker compose exec -T airflow-scheduler airflow dags trigger datamind_trajetoria_2015
docker compose exec -T airflow-scheduler airflow dags list-runs datamind_trajetoria_2015
docker compose exec -T postgres-data psql -U datamind -d datamind03 -c "SELECT * FROM mart.p1_trajectory_active ORDER BY referencia"
```

## Correspondência com os slides

| Proposta da apresentação | Implementação deste primeiro fluxo |
| --- | --- |
| Docker/Linux, Airflow e PostgreSQL | Compose com metadados separados do banco analítico |
| Extração e conferência de arquivos | ZIP local conferido por tamanho e SHA-256; leiaute e campos obrigatórios verificados |
| Python e carga COPY | Leitura sequencial do XLSX; recorte MT presencial; CSV de trabalho e COPY em staging |
| Transformação SQL | Identificadores TEXT, contagens BIGINT, taxas NUMERIC e acumulados por curso/coorte |
| Conferências antes da publicação | Contagem, chave primária, dez referências por curso, escopo, saldo e reconciliação de cinco taxas |
| Quarentena | Validação reprovada deixa a execução registrada em audit e não avança a publicação |
| Publicação versionada | Core/mart por hash de fonte e código; views para versão ativa; JSON agregado para o futuro site |

## Recorte e método

Esta entrega cobre o fluxo inicial da P1: Mato Grosso, presencial, coorte de ingresso 2015 e referências 2015–2024. São 5.150 observações curso/coorte/ano, 515 cursos e dez linhas agregadas no mart. A soma de ingressantes representa vínculos da base; não houve deduplicação de pessoas entre cursos.

Conclusões, desistências e falecimentos anuais são acumulados por curso antes da agregação. O denominador efetivo é ingressantes menos falecimentos acumulados. TAP, TCA, TDA, TCAN e TADA publicados são preservados no core e reconciliados com as contagens, com tolerância de 0,000001 ponto percentual. As taxas do mart são calculadas a partir das somas das contagens e dos denominadores, sem média simples das taxas dos cursos.

O JSON contém apenas o agregado estadual. Por precaução, as quatro medidas de uma referência são omitidas quando alguma contagem subjacente positiva é inferior a dez; o campo `suprimido` sinaliza essa situação. O mart interno mantém os valores para auditoria. Futuros recortes por curso exigem aplicação própria da regra de supressão e análise de identificação por diferenças.

## Reexecução e evidências

`staging` separa dados por execução e substitui o mesmo lote dentro de uma transação. A versão analítica deriva do hash da fonte, do contrato e do código de transformação. As chaves de core e mart impedem duplicação da mesma versão. Uma alteração de fonte ou código gera outra versão, mantendo a anterior.

O teste `python src/verify_trajectory.py` confere a primeira execução `trajetoria_validacao_01`, inicia uma repetição e depois uma execução com `force_validation_failure: true`. Esse parâmetro serve exclusivamente para testar o ramo de quarentena. Evidências em `outputs/ambiente/validacao_trajetoria.json`, incluindo estados das tarefas, contagens, versões e hashes. Não utilizar esse parâmetro numa carga normal.

Quando uma reprovação segue corretamente até `quarentena`, a DAG termina com estado `success`: isso indica que o fluxo de tratamento funcionou, não que os dados foram aprovados. Consultar o ramo executado e `audit.trajectory_run.state` para distinguir `published` de `quarantined`.

## Limites desta entrega

- A extração usa o original já baixado e fixado no manifesto. Ainda não automatiza novos downloads do Drive/INEP.
- Outras coortes, recortes CINE/rede, Censo, CPC, Enade, IBGE e junções P2–P5 permanecem para os próximos fluxos.
- O JSON está preparado localmente. O site interativo e sua hospedagem na Vercel ainda não foram implementados.
- Há uma tentativa adicional após falha técnica. Falhas de validação seguem diretamente para quarentena.
- Banco e filesystem não compartilham transação: o JSON versionado é gravado antes do commit, e `current.json` depois. Uma falha nessa última gravação pode deixar o ponteiro do site atrasado; repetir a tarefa `publicar` repara a exportação. O teste cobre reprovação de qualidade, não interrupção de disco/rede durante publicação.
- Staging e arquivos de trabalho são conservados para auditoria; uma política de retenção ainda precisa ser definida se o fluxo passar a rodar periodicamente.

## Próximo passo da equipe

Executar a DAG pela interface e conferir juntos os registros de validação. Depois, ampliar o modelo com as dimensões de curso e rede necessárias às perguntas priorizadas, mantendo as mesmas regras de aprovação antes de alimentar o site.
