# Local de desenvolvimento e caminhos

A pasta de operação é C:\Users\THAIII\DATAHCK_2026\DataMind\DataMin.03. As fontes originais permanecem em C:\Users\THAIII\DATAHCK_2026\DataMind\Fonte de Dados, sua pasta irmã.

O Compose fixa o projeto como datamind03, monta os dados em modo somente leitura em /opt/airflow/project/fonteDado e preserva os volumes postgres-data, postgres-meta e airflow-logs. Os comandos operacionais independentes estão em subir_airflow.ps1, parar_airflow.ps1, abrir_prototipo.ps1 e fechar_prototipo.ps1.

O PostgreSQL analítico chama-se datamind03 e conserva o usuário de aplicação datamind já usado pelos objetos carregados. As credenciais locais permanecem nos arquivos ignorados .env e runtime/private/ACESSO_LOCAL.txt.