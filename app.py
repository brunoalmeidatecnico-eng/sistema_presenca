from flask import Flask, render_template, request, redirect, send_file
from banco import db, Sala, Aluno, Presenca
from datetime import datetime
import pandas as pd
from reportlab.pdfgen import canvas
from licenca import *
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, instance_path=None)

# Usar PostgreSQL na produção, SQLite no desenvolvimento
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Render usa postgres://, converter para postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Desenvolvimento local com SQLite
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'banco.db'))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# =========================
# DASHBOARD
# =========================
@app.route('/')
def dashboard():

    total_alunos = Aluno.query.count()

    total_faltas = Presenca.query.filter_by(
        status='FALTA'
    ).count()

    total_presencas = Presenca.query.filter_by(
        status='PRESENTE'
    ).count()

    total_registros = total_faltas + total_presencas

    frequencia = 0

    if total_registros > 0:

        frequencia = round(
            (total_presencas / total_registros) * 100,
            2
        )

    ranking = db.session.query(
        Aluno.nome,
        db.func.count(Presenca.id).label('faltas')
    ).join(
        Presenca,
        Presenca.aluno_id == Aluno.id
    ).filter(
        Presenca.status == 'FALTA'
    ).group_by(
        Aluno.nome
    ).order_by(
        db.desc('faltas')
    ).limit(5).all()

    alertas = db.session.query(
        Aluno.nome,
        db.func.count(Presenca.id).label('faltas')
    ).join(
        Presenca,
        Presenca.aluno_id == Aluno.id
    ).filter(
        Presenca.status == 'FALTA'
    ).group_by(
        Aluno.nome
    ).having(
        db.func.count(Presenca.id) >= 3
    ).all()

    return render_template(
        'dashboard.html',
        total_alunos=total_alunos,
        total_faltas=total_faltas,
        frequencia=frequencia,
        ranking=ranking,
        alertas=alertas
    )


# =========================
# SALAS
# =========================
@app.route('/salas', methods=['GET', 'POST'])
def salas():

    if request.method == 'POST':

        nome = request.form['nome']

        nova = Sala(nome=nome)

        db.session.add(nova)
        db.session.commit()

        return redirect('/salas')

    salas = Sala.query.all()

    return render_template(
        'salas.html',
        salas=salas
    )


# =========================
# EDITAR SALA
# =========================
@app.route('/editar_sala/<int:id>', methods=['GET', 'POST'])
def editar_sala(id):

    sala = db.session.get(
        Sala,
        id
    )

    if request.method == 'POST':

        sala.nome = request.form['nome']

        db.session.commit()

        return redirect('/salas')

    return render_template(
        'editar_sala.html',
        sala=sala
    )


# =========================
# ALUNOS
# =========================
@app.route('/alunos', methods=['GET', 'POST'])
def alunos():

    salas = Sala.query.all()

    if request.method == 'POST':

        nome = request.form['nome']
        responsavel = request.form['responsavel']
        telefone = request.form['telefone']
        sala_id = request.form['sala_id']

        novo = Aluno(
            nome=nome,
            responsavel=responsavel,
            telefone=telefone,
            sala_id=sala_id
        )

        db.session.add(novo)
        db.session.commit()

        return redirect('/alunos')

    busca = request.args.get('busca')

    if busca:

        alunos = Aluno.query.filter(
            Aluno.nome.contains(busca)
        ).all()

    else:

        alunos = Aluno.query.all()

    return render_template(
        'alunos.html',
        alunos=alunos,
        salas=salas
    )


# =========================
# EDITAR ALUNO
# =========================
@app.route('/editar_aluno/<int:id>', methods=['GET', 'POST'])
def editar_aluno(id):

    aluno = db.session.get(
        Aluno,
        id
    )

    salas = Sala.query.all()

    if request.method == 'POST':

        aluno.nome = request.form['nome']

        aluno.responsavel = request.form['responsavel']

        aluno.telefone = request.form['telefone']

        aluno.sala_id = request.form['sala_id']

        db.session.commit()

        return redirect('/alunos')

    return render_template(
        'editar_aluno.html',
        aluno=aluno,
        salas=salas
    )


# =========================
# PRESENÇA
# =========================
@app.route('/presenca/<int:sala_id>', methods=['GET', 'POST'])
def presenca(sala_id):

    alunos = Aluno.query.filter_by(
        sala_id=sala_id
    ).all()

    if request.method == 'POST':

        data = datetime.now().strftime(
            '%d/%m/%Y'
        )

        for aluno in alunos:

            status = request.form.get(
                f'aluno_{aluno.id}'
            )

            nova = Presenca(
                aluno_id=aluno.id,
                data=data,
                status=status
            )

            db.session.add(nova)

        db.session.commit()

        return redirect('/')

    return render_template(
        'presenca.html',
        alunos=alunos
    )


# =========================
# FALTANTES
# =========================
@app.route('/faltantes')
def faltantes():

    busca = request.args.get('busca')

    if busca:

        faltas = Presenca.query.join(
            Aluno,
            Presenca.aluno_id == Aluno.id
        ).filter(
            Presenca.status == 'FALTA',
            Aluno.nome.contains(busca)
        ).all()

    else:

        faltas = Presenca.query.filter_by(
            status='FALTA'
        ).all()

    lista = []

    for falta in faltas:

        aluno = db.session.get(
            Aluno,
            falta.aluno_id
        )

        lista.append({

            'presenca_id': falta.id,

            'nome': aluno.nome,

            'responsavel': aluno.responsavel,

            'telefone': aluno.telefone,

            'data': falta.data,

            'whatsapp': falta.whatsapp_enviado,

            'data_envio': falta.data_envio

        })

    return render_template(
        'faltantes.html',
        lista=lista
    )


# =========================
# PRESENTES
# =========================
@app.route('/presentes')
def presentes():

    presencas = Presenca.query.filter_by(
        status='PRESENTE'
    ).all()

    lista = []

    for presenca in presencas:

        aluno = db.session.get(
            Aluno,
            presenca.aluno_id
        )

        lista.append({

            'nome': aluno.nome,

            'responsavel': aluno.responsavel,

            'telefone': aluno.telefone,

            'data': presenca.data

        })

    return render_template(
        'presentes.html',
        lista=lista
    )


# =========================
# ENVIAR WHATSAPP
# =========================
@app.route('/enviar/<int:id>')
def enviar(id):

    import webbrowser
    import urllib.parse
    import time

    falta = db.session.get(
        Presenca,
        id
    )

    aluno = db.session.get(
        Aluno,
        falta.aluno_id
    )

    mensagem = f'''
Prezado(a),
Informamos que o aluno(a)
{aluno.nome}
faltou na aula de hoje.
Gostariamos de saber o motivo da falta.
A falta prejudica e acarreta problemas no andamentodo rendimento escolar.

Secretaria Escolar 

E.E. Prof. Pedro Silva
'''

    texto = urllib.parse.quote(
        mensagem
    )

    telefone = f"55{aluno.telefone}"

    link = f"https://wa.me/{telefone}?text={texto}"

    try:

        webbrowser.open(link)

        time.sleep(5)

        falta.whatsapp_enviado = 'SIM'

        falta.data_envio = datetime.now().strftime(
            '%d/%m/%Y %H:%M:%S'
        )

        db.session.commit()

    except Exception as erro:

        print(erro)

    return redirect('/faltantes')

# =========================
# EXPORTAR EXCEL
# =========================
@app.route('/exportar_excel')
def exportar_excel():
    try:
        registros = Presenca.query.all()

        if not registros:
            return "Nenhum registro de presença para exportar", 400

        dados = []

        for registro in registros:
            aluno = db.session.get(Aluno, registro.aluno_id)
            
            if aluno is None:
                continue

            dados.append({
                'Aluno': aluno.nome,
                'Responsável': aluno.responsavel,
                'Telefone': aluno.telefone,
                'Data': registro.data,
                'Status': registro.status,
                'WhatsApp': registro.whatsapp_enviado,
                'Data Envio': registro.data_envio
            })

        if not dados:
            return "Nenhum aluno associado aos registros", 400

        df = pd.DataFrame(dados)

        import tempfile
        arquivo = os.path.join(
            tempfile.gettempdir(),
            'relatorio_presenca.xlsx'
        )

        df.to_excel(
            arquivo,
            index=False,
            engine='openpyxl'
        )

        return send_file(
            arquivo,
            as_attachment=True,
            download_name='relatorio_presenca.xlsx'
        )

    except Exception as erro:
        print(f"Erro ao exportar Excel: {erro}")
        import traceback
        traceback.print_exc()
        return f"Erro ao exportar: {str(erro)}", 500


# =========================
# EXPORTAR PDF
# =========================
@app.route('/exportar_pdf')
def exportar_pdf():
    try:
        import tempfile

        registros = Presenca.query.all()

        if not registros:
            return "Nenhum registro de presença para exportar", 400

        arquivo_pdf = os.path.join(
            tempfile.gettempdir(),
            'relatorio_presenca.pdf'
        )

        pdf = canvas.Canvas(arquivo_pdf)

        pdf.setFont("Helvetica", 12)

        y = 800

        for registro in registros:
            aluno = db.session.get(Aluno, registro.aluno_id)

            if aluno is None:
                continue

            texto = f'Aluno: {aluno.nome} | Status: {registro.status} | Data: {registro.data}'

            pdf.drawString(50, y, texto)

            y -= 20

            if y < 50:
                pdf.showPage()
                y = 800

        pdf.save()

        return send_file(
            arquivo_pdf,
            as_attachment=True,
            download_name='relatorio_presenca.pdf'
        )

    except Exception as erro:
        print(f"Erro ao exportar PDF: {erro}")
        import traceback
        traceback.print_exc()
        return f"Erro ao exportar: {str(erro)}", 500

status, mensagem = verificar_licenca()

if status == False:

    print('\n===================================')
    print(' SISTEMA NÃO LICENCIADO ')
    print('===================================\n')

    print('Usuário mestre:')
    usuario = input()

    print('Senha mestre:')
    senha = input()

    if (
        usuario == USUARIO_MASTER
        and
        senha == SENHA_MASTER
    ):

        print('\nQuantos meses liberar?')
        meses = int(input())

        criar_licenca(meses)

        print('\nLICENÇA ATIVADA!\n')

    else:

        print('\nACESSO NEGADO\n')

        print(
            'Entre em contato:\n'
            'brunocaio33@gmail.com'
        )

        input('\nPressione ENTER')

        exit()

elif 'VENCENDO' in mensagem:

    dias = mensagem.split('_')[1]

    print('\n===================================')
    print(' ATENÇÃO ')
    print('===================================\n')

    print(
        f'Sua licença vence em '
        f'{dias} dias.\n'
    )

    print(
        'Entre em contato:\n'
        'brunocaio33@gmail.com\n'
    ) 
# =========================
# INICIAR SISTEMA
# =========================
if __name__ == '__main__':

    print('\n========================================')
    print('   SISTEMA ESCOLAR INICIADO')
    print('========================================\n')

    print('ACESSO LOCAL:')
    print('http://127.0.0.1:5000\n')

    print('ACESSO NA REDE:')
    print('http://192.168.1.7:5000\n')

    print('IMPORTANTE:')
    print('NÃO FECHE ESTA JANELA!')
    print('Ela mantém o sistema funcionando.\n')

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )