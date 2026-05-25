from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Sala(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100))


class Aluno(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(200))

    responsavel = db.Column(db.String(200))

    telefone = db.Column(db.String(20))

    sala_id = db.Column(
        db.Integer,
        db.ForeignKey('sala.id')
    )


class Presenca(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    aluno_id = db.Column(db.Integer)

    data = db.Column(db.String(20))

    status = db.Column(db.String(20))

    whatsapp_enviado = db.Column(
        db.String(10),
        default='NÃO'
    )

    data_envio = db.Column(
        db.String(30)
    )