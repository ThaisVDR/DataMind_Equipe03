# Publicar o protótipo na Vercel

O site é estático e não precisa de build nem de credenciais do PostgreSQL. Na configuração do projeto Vercel, use:

- Repositório: `ThaisVDR/DataMind_Equipe03`
- Root Directory: `sistema/dashboard`
- Framework Preset: `Other`
- Build Command: vazio
- Output Directory: `.`

`index.html`, `styles.css`, `app.js` e `data.js` precisam estar no commit. Atualize primeiro `data.js` pelo procedimento local do [README do projeto](README.md) e envie os arquivos ao GitHub. A página contém agregados públicos, sem conexão ao banco, usuários ou senhas. Cada nova publicação atualiza o snapshot público; verifique as células e as observações antes de publicar.

Para testar sem publicar, siga `scripts/iniciar_prototipo.ps1` na pasta `sistema/`.
