#!/usr/bin/env python
"""Script para testar se o app está pronto para deploy"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Verificando configuração do app...\n")

# 1. Verificar imports
try:
    from app import app, db
    print("✅ Flask app carrega corretamente")
except Exception as e:
    print(f"❌ Erro ao carregar app: {e}")
    sys.exit(1)

# 2. Verificar banco de dados
try:
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados configurado")
except Exception as e:
    print(f"❌ Erro ao configurar banco: {e}")
    sys.exit(1)

# 3. Verificar requirements.txt
try:
    with open('requirements.txt', 'r') as f:
        reqs = f.read()
        required = ['flask', 'flask_sqlalchemy', 'psycopg2', 'gunicorn', 'python-dotenv']
        for req in required:
            if req.lower() not in reqs.lower():
                print(f"⚠️ {req} não encontrado em requirements.txt")
        print("✅ requirements.txt contém dependências necessárias")
except Exception as e:
    print(f"❌ Erro ao verificar requirements.txt: {e}")

# 4. Verificar render.yaml
if os.path.exists('render.yaml'):
    print("✅ render.yaml encontrado")
else:
    print("⚠️ render.yaml não encontrado")

# 5. Verificar .gitignore
if os.path.exists('.gitignore'):
    print("✅ .gitignore encontrado")
else:
    print("⚠️ .gitignore não encontrado")

print("\n" + "="*50)
print("🚀 App está pronto para deploy no Render!")
print("="*50)
print("\nPróximas etapas:")
print("1. git add .")
print("2. git commit -m 'Preparar para deploy Render'")
print("3. git push origin main")
print("4. Deploy no Render seguindo DEPLOY_RENDER.md")
