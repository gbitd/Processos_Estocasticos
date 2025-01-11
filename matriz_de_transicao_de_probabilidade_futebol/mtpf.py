import sqlite3
from fractions import Fraction

import numpy as np
import pandas as pd

# Conectando ao banco de dados
conn = sqlite3.connect("database.sqlite")
cursor = conn.cursor()

# Lendo a tabela de partidas
matches = pd.read_sql_query("SELECT * FROM Match", conn)

# Filtrando as partidas de 2008/2009
matches_2008_2009 = matches[matches["season"] == "2008/2009"]


# Função que retorna as partidas em que um time específico jogou em 2008/2009
def get_matches_of_team(team_id):
    matches_of_team = matches_2008_2009[
        (matches_2008_2009["home_team_api_id"] == team_id)
        | (matches_2008_2009["away_team_api_id"] == team_id)
    ]
    return matches_of_team


teams = pd.read_sql_query("SELECT * FROM Team", conn)

# Encontrando o team_api_id do time Juventus. Alterar para o time de interesse
team_long_name = "Juventus"
team_api_id = teams[teams["team_long_name"] == team_long_name][
    "team_api_id"
].values[0]
print("Time: " + team_long_name + "\napi_id: " + str(team_api_id))

# Obtendo as partidas em que o Juventus jogou
matches_of_team = get_matches_of_team(team_api_id)
matches_of_team = matches_of_team.sort_values(by="date")

print("Número de partidas do Juventus: " + str(len(matches_of_team)))

matches_of_team["result"] = "Defeat"  # Inicializa toda a coluna como derrota
matches_of_team.loc[
    (matches_of_team["home_team_api_id"] == team_api_id)
    & (matches_of_team["home_team_goal"] > matches_of_team["away_team_goal"]),
    "result",
] = "Win"
matches_of_team.loc[
    (matches_of_team["away_team_api_id"] == team_api_id)
    & (matches_of_team["away_team_goal"] > matches_of_team["home_team_goal"]),
    "result",
] = "Win"

# Agora fazendo para os empates!
matches_of_team.loc[
    (matches_of_team["home_team_api_id"] == team_api_id)
    & (matches_of_team["home_team_goal"] == matches_of_team["away_team_goal"]),
    "result",
] = "Draw"
matches_of_team.loc[
    (matches_of_team["away_team_api_id"] == team_api_id)
    & (matches_of_team["away_team_goal"] == matches_of_team["home_team_goal"]),
    "result",
] = "Draw"


print(
    matches_of_team[
        ["id", "date", "home_team_goal", "away_team_goal", "result", "stage"]
    ]
)


# # Criando a matriz de transição de probabilidade

# Definindo os estados
estados = ["Win", "Draw", "Defeat"]
n = len(estados)

# Criando um dicionário para mapear os estados para índices
estado_to_idx = {estado: idx for idx, estado in enumerate(estados)}

# Inicializando a matriz de contagem
C = np.zeros((n, n))

# Obter a sequência de resultados
resultados = matches_of_team["result"].values

# Contando as transições entre estados
for i in range(len(resultados) - 1):
    estado_atual = resultados[i]
    estado_proximo = resultados[i + 1]
    C[estado_to_idx[estado_atual], estado_to_idx[estado_proximo]] += 1

# Normalizando para obter a matriz de probabilidades
P = C / C.sum(axis=1, keepdims=True)

# Substituindo NaNs (em caso de linhas com soma zero)
P = np.nan_to_num(P)

# Exibindo a matriz de probabilidade
print("\nMatriz de Probabilidade P:")
print(P)

# Exibindo de forma mais legível (frações)
P_df = pd.DataFrame(P, index=estados, columns=estados)
df_frac = P_df.map(lambda x: Fraction(x).limit_denominator())
print("\nMatriz de Probabilidade Legível:")
print(df_frac)
