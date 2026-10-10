"""Gera credenciais locais sem sobrescrever configuracao existente."""
import base64
import json
import secrets
from pathlib import Path

root=Path(__file__).resolve().parents[1]
for folder in ['data/raw','runtime/etl','outputs/analytics','outputs/ambiente']:
    (root/folder).mkdir(parents=True,exist_ok=True)
env=root/'.env'
private=root/'runtime/private'
private.mkdir(parents=True,exist_ok=True)
if not env.exists():
    values={
        'AIRFLOW_DB_PASSWORD':secrets.token_hex(24),
        'DATAMIND_DB_PASSWORD':secrets.token_hex(24),
        'AIRFLOW_FERNET_KEY':base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(),
        'AIRFLOW_JWT_SECRET':secrets.token_hex(32),
    }
    env.write_text(''.join(f'{k}={v}\n' for k,v in values.items()),encoding='utf-8')
passwords=private/'passwords.json'
if not passwords.exists():
    password=secrets.token_urlsafe(18)
    passwords.write_text(json.dumps({'datamind':password}),encoding='utf-8')
    (private/'ACESSO_LOCAL.txt').write_text(
        'Airflow: http://localhost:8080\nUsuario: datamind\nSenha: '+password+
        '\nPostgreSQL analitico: localhost:15432 / banco datamind / usuario datamind\n'
        'Senha do PostgreSQL: DATAMIND_DB_PASSWORD em .env\n',encoding='utf-8')
print('Configuracao local pronta. Credenciais em runtime/private/ACESSO_LOCAL.txt; nao versionar.')
