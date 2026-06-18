from enum import Enum

# Preços dos serviços em EUROS
class PrecosUnhas(Enum):
    REPARACAO_UNHA = -1 # contactar tiz
    REMOCAO_UNHA = 5
    VERNIZ_GEL_MAOS = 15
    VERNIZ_GEL_PES = 10
    PRIMEIRA_APLICACAO_UNHA_COM_EXTENSAO_MENOS_DE_2CM = 25
    PRIMEIRA_APLICACAO_UNHA_COM_EXTENSAO_MAIS_DE_2CM = -1   # contactar tiz
    PRIMEIRA_APLICACAO_SOBRE_UNHA_NATURAL = 20
    MANUTENCAO_DE_GEL = 17.5
    MANUTENCAO_DE_GEL_COM_NAIL_ART_SIMPLES = -1   # contactar tiz
    MANUTENCAO_DE_GEL_COM_NAIL_ART_COMPLEXA = -1  # contactar tiz

class PrecosEstetica(Enum):
    BUCO_A_LINHA = 4
    SOBRANCELHA_A_LINHA = 6
    SOBRANCELHA_E_BUCO_A_LINHA = 10
    LIMPEZA_DE_PELE = 30
    LIFTING_PESTANAS = 23
    BROW_LAMINATION = 18


# Tempos em minutos
class TemposUnhas(Enum):
    REPARACAO_UNHA = 15
    REMOCAO_UNHA = 30
    VERNIZ_GEL_PES = 30
    VERNIZ_GEL_MAOS = 75                            # 1h15
    PRIMEIRA_APLICACAO_UNHA_COM_EXTENSAO = 150      # 2h30m
    PRIMEIRA_APLICACAO_SOBRE_UNHA_NATURAL = 90      # 1h30m
    MANUTENCAO_DE_GEL = 90                          # 1h30m
    MANUTENCAO_DE_GEL_COM_NAIL_ART_SIMPLES = 15     # acrescenta 15m a cada serviço
    MANUTENCAO_DE_GEL_COM_NAIL_ART_COMPLEXA = 30    # acrescenta 30m a cada serviço

class TemposEstetica(Enum):
    BUCO_A_LINHA = 15                # 15m
    SOBRANCELHA_A_LINHA = 15         # 15m
    SOBRANCELHA_E_BUCO_A_LINHA = 15  # 15m
    LIMPEZA_DE_PELE = 75             # 1h15m
    LIFTING_PESTANAS = 90            # 1h30m
    BROW_LAMINATION = 60             # 1h
