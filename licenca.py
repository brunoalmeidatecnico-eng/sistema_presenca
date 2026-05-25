import os
import json
import socket
import uuid

from datetime import datetime
from dateutil.relativedelta import relativedelta

ARQUIVO_LICENCA = 'licenca.json'

USUARIO_MASTER = '@SamantaBenvindo'
SENHA_MASTER = '19202521'


def obter_ip():

    return socket.gethostbyname(
        socket.gethostname()
    )


def obter_mac():

    return str(uuid.getnode())


def criar_licenca(meses):

    data_expiracao = (
        datetime.now() +
        relativedelta(months=meses)
    )

    dados = {

        'ip': obter_ip(),

        'mac': obter_mac(),

        'expira': data_expiracao.strftime(
            '%Y-%m-%d'
        )
    }

    with open(
        ARQUIVO_LICENCA,
        'w'
    ) as arquivo:

        json.dump(
            dados,
            arquivo
        )


def verificar_licenca():

    if not os.path.exists(
        ARQUIVO_LICENCA
    ):

        return False, 'SEM_LICENCA'

    with open(
        ARQUIVO_LICENCA,
        'r'
    ) as arquivo:

        dados = json.load(
            arquivo
        )

    if dados['mac'] != obter_mac():

        return False, 'PC_INVALIDO'

    data_expira = datetime.strptime(
        dados['expira'],
        '%Y-%m-%d'
    )

    dias_restantes = (
        data_expira -
        datetime.now()
    ).days

    if dias_restantes <= 0:

        return False, 'LICENCA_EXPIRADA'

    if dias_restantes <= 30:

        return True, f'VENCENDO_{dias_restantes}'

    return True, 'OK'