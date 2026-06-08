from enum import Enum

# Preços dos serviços em EUROS
class PrecosDepilacaoLaser(Enum):
    # ROSTO
    ORELHAS = 5
    BUCO = 10
    QUEIXO = 10
    PATILHAS = 10
    MACAS_ROSTO = 5
    NARIZ = 5
    LINHA_NUCA = 15
    LINHA_PESCOCO = 15
    ENTRE_SOBRANCELHAS = 5
    BARBA = 25

    # CORPO
    MAOS = 8
    PES = 8
    OMBROS = 10
    AXILAS = 15
    ANTEBRACOS = 15
    BRACOS_COMPLETOS = 25
    SEIOS = 5
    LINHA_PEITO = 5
    LINHA_ALBA = 5
    ABDOMEN_TORAX = 15
    PEITO = 25
    COSTAS = 25
    LOMBAR = 10
    GLUTEOS = 10
    JOELHOS = 10
    VIRILHAS = 20
    PERNA_SEM_VIRILHA = 30
    MEIA_PERNA_SUPERIOR = 20
    MEIA_PERNA_INFERIOR = 15
