# 🎓 Sistema de Presença - GUIA DEPLOYMENT RENDER

## ✅ Pré-requisitos
- Conta GitHub (com o código já enviado)
- Conta Render (gratuita em render.com)

---

## 📋 PASSO A PASSO PARA DEPLOY ONLINE GRATUITO

### 1️⃣ PREPARAR GITHUB
```bash
# No seu computador, dentro da pasta do projeto:
git add .
git commit -m "Preparar para deploy online"
git push origin main
```

### 2️⃣ CRIAR CONTA RENDER (se não tiver)
- Acesse: https://render.com
- Faça signup com GitHub

### 3️⃣ CONECTAR REPOSITÓRIO NO RENDER
1. No Render, clique em **"New +"** → **"Web Service"**
2. Selecione **"Connect a repository"**
3. Escolha seu repositório do sistema_presenca
4. Clique em **"Connect"**

### 4️⃣ CONFIGURAR O DEPLOY
Na próxima tela, preencha:

| Campo | Valor |
|-------|-------|
| **Name** | sistema-presenca (ou seu nome) |
| **Region** | São Paulo ou sua região |
| **Branch** | main |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |

### 5️⃣ ADICIONAR BANCO DE DADOS (PostgreSQL Gratuito)
1. Clique em **"Create Database"** (no mesmo dashboard)
2. Nome: `sistema-presenca-db`
3. Região: São Paulo
4. **Gratuito** ✅ (até 90 dias com 400MB)
5. Clique em **"Create"**

### 6️⃣ CONECTAR DATABASE AO APP
1. Volte para o Web Service
2. Vá em **"Environment"**
3. A `DATABASE_URL` será adicionada automaticamente pelo Render ✅
4. Não precisa fazer nada!

### 7️⃣ DEPLOY
- Render fará o deploy automaticamente
- Aguarde 3-5 minutos
- Seu app estará online em: `https://sistema-presenca.onrender.com`

---

## 🌐 PRIMEIRA VEZ ONLINE?
- Suas tabelas do banco serão criadas automaticamente
- O código detecta se é produção (PostgreSQL) ou desenvolvimento (SQLite)

## 💾 DADOS PERSISTEM?
✅ **SIM!** PostgreSQL do Render persiste os dados mesmo com redeploy

## 🆓 É REALMENTE GRATUITO?
- ✅ Hospedagem: **Gratuito** (pode dormir após 15 min de inatividade)
- ✅ PostgreSQL: **Gratuito 90 dias** (400MB, depois R$ 15/mês se quiser)
- ✅ Sem cartão de crédito necessário para tier gratuito

---

## 🚀 COMANDOS ÚTEIS

### Testar localmente antes de enviar:
```bash
pip install -r requirements.txt
export FLASK_APP=app.py
flask run
```

### Ver logs do Render:
- Dashboard Render → Seu app → "Logs"

### Redeploy manual:
- Dashboard Render → "Manual Deploy" → "Deploy latest commit"

---

## ⚠️ LIMITAÇÕES GRATUITAS
- App dorme após 15 min inatividade (1ª requisição demora 30s para acordar)
- PostgreSQL: 90 dias gratuito depois R$ 15/mês
- Largura de banda: 100GB/mês

**Dica**: Se quiser evitar "dormir", use: uptime-robot.com (monitorar a cada 5 min)

---

## 🔒 SEGURANÇA
- Remova `licenca.py` públicas do GitHub se tiver dados sensíveis
- Não commit `.env` (já está em `.gitignore`)

---

## 📞 PRÓXIMOS PASSOS
1. Push para GitHub
2. Deploy no Render
3. Teste em `https://seu-app.onrender.com`
4. Pronto! ✨
