# Painel Rota do Diploma · protótipo Fase 2

Site estático de exploração das cinco perguntas obrigatórias do DataHack UNIVAG. O painel usa um snapshot agregado extraído do catálogo ativo do PostgreSQL e funciona em qualquer computador com navegador, inclusive hospedado na Vercel. Ele não abre conexão de navegador com o banco.

## Atualizar os dados

No PowerShell, com o Docker em execução e o ETL já carregado:

```powershell
Set-Location -LiteralPath 'C:\Users\THAIII\DATAHCK_2026\DataMind\DataMin.03'
.\scripts\atualizar_prototipo.ps1
```

A exportação consulta as versões ativas das 31 fontes em transação somente de leitura. O JSON é publicado por substituição atômica em `outputs/analytics/prototipo/snapshot.json`; `dashboard/data.js` recebe o mesmo snapshot incorporado para servir o site localmente e em Vercel. Um erro mantém o snapshot anterior disponível.

## Abrir e parar o protótipo

```powershell
.\scripts\iniciar_prototipo.ps1
```

Abra `http://127.0.0.1:4173/`. A hospedagem local não inicia nem para Airflow ou PostgreSQL. Para encerrar apenas esse servidor:

```powershell
.\scripts\parar_prototipo.ps1
```

O painel também pode ser aberto sem rede pelo `index.html` se os arquivos estiverem na mesma pasta, mas o servidor local é o modo recomendado. Os comandos da [Vercel](vercel.md) usam a pasta `DataMin.03/dashboard` como raiz.

## Perguntas e cautelas

- P1: resultado da coorte presencial escolhida até 2024 e perfil anual da perda.
- P2: ranking no quinto ano, com horizonte igual entre coortes.
- P3: proxy anual do Censo, separada da desistência de uma coorte; modalidade e rede pública ou privada (com ou sem fins lucrativos).
- P4: CPC versus desistência acumulada entre cursos que casaram pelo código do curso.
- P5: trajetória presencial da coorte 2015 junto ao indicador do Enade Licenciaturas 2025, com denominadores separados.
- Grupos com base efetiva menor que 10 são omitidos; ausências e SC não viram zero.
- O dado municipal de polo EAD não localiza o aluno. Descrições não identificam causalidade.

O relatório da EDA, cobertura de junções, data da extração, manifesto e limitações aparecem na aba **Evidências e método**.

## Regras e evidências

A matriz de regras de negócio e a ligação entre EDA, PostgreSQL, fórmulas e visuais está em [docs/regras_negocio_dados.md](../../An%C3%A1lise%20Explorat%C3%B3ria%20e%20Contextualiza%C3%A7%C3%A3o/Relat%C3%B3rios/regras_negocio_dados.md). O painel resume o contrato na aba **Evidências e método**.
