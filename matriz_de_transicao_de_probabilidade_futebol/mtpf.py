import sqlite3

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

# Encontrando o team_api_id do time Juventus
team_api_id = teams[teams["team_long_name"] == "Juventus"][
    "team_api_id"
].values[0]
print("Time: Juventus\napi_id:" + str(team_api_id))

# Obtendo as partidas em que o Juventus jogou
matches_of_team = get_matches_of_team(team_api_id)
matches_of_team = matches_of_team.sort_values(by="date")

print("Número de partidas do Juventus: " + str(len(matches_of_team)))

matches_of_team["result"] = "Defeat" # Inicializa toda a coluna como derrota
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


print(matches_of_team[["id", "date", "home_team_goal", "away_team_goal", "result", "stage"]])


# # Criando a matriz de transição de probabilidade
# mtp = pd.DataFrame(
#     columns=["Win", "Draw", "Defeat"], index=["Win", "Draw", "Defeat"]
# )
#
# # Contando as transições de estado
# for i in range(len(matches_of_team) - 1):
#     mtp.loc[
#         matches_of_team.iloc[i]["result"], matches_of_team.iloc[i + 1]["result"]
#     ] += 1
#
# # Normalizando as transições
# mtp = mtp.div(mtp.sum(axis=1), axis=0)
#
# print(mtp)
