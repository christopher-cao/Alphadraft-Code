#!/usr/bin/env python3
# coding: utf-8

# In[1]:

import urllib.request
import json
import pymysql


# In[2]:

db = pymysql.connect(host="localhost", user="root", passwd="password", db="NA_LCS", autocommit="true")
cur = db.cursor()


# In[3]:

def create_team_table(table_name): 
    sql = "CREATE TABLE " + table_name + " (ID INTEGER PRIMARY KEY AUTO_INCREMENT, Date TEXT, Name TEXT, Opponent TEXT, Win TEXT, Length INT, KDA REAL, Kills INTEGER, Deaths INTEGER, Assists INTEGER, Gold INTEGER, GPM REAL, Towers INTEGER, FirstTower TEXT, Dragons INTEGER, FirstDrag TEXT, Barons INTEGER, FirstBaron TEXT, FirstBlood TEXT)"
    try:
        cur.execute(sql)
    except Exception:
        print(table_name + " already exists")


# In[25]:

def create_player_table(table_name):
    sql = "CREATE TABLE " + table_name + " (ID INTEGER PRIMARY KEY AUTO_INCREMENT, Date TEXT, Name TEXT, Team TEXT, Opponent TEXT, Win TEXT, Role TEXT, Length INTEGER, Champion TEXT, KDA REAL, Kills INTEGER, Deaths INTEGER, Assists INTEGER, CS INTEGER, CSPM REAL, Gold INTEGER, GPM REAL)"
    try: 
        cur.execute(sql)
    except Exception:
        print(table_name + " already exists")


# In[9]:

#Asking for all user input
date = input("Enter the date (YYYY-MM-DD): ")
game_code = input("enter a match ID ex. TRLH1/1001520070?gameHash=e5a089b1818d40b0: ")
game_url = 'https://acs.leagueoflegends.com/v1/stats/game/' + game_code


# In[26]:

team_table = input("Enter the name you'd like for the TEAM data table: ")


# In[27]:

player_table = input("Enter the name you'd like for the PLAYER data table: ")


# In[28]:

#Extracting game JSON
source = urllib.request.urlopen(game_url).read()
source = source.decode('utf-8')
json_page = json.loads(source)


# In[29]:

#Creating a dictionary to map champ keys to names
champ_ids = {}
champs_page = 'http://ddragon.leagueoflegends.com/cdn/6.1.1/data/en_US/champion.json'
champs_source = urllib.request.urlopen(champs_page).read().decode('utf-8') #need to decode the urlopen object
champs_json = json.loads(champs_source)
champs = champs_json['data']

for champ in champs:
    temp = champs[champ]
    key = int(temp['key'])
    name = temp['name']
    champ_ids[key] = temp['name']


# In[30]:

#Keeping track of player and team ids
participantIds = json_page['participantIdentities']

player_ids = {}
team_ids = {} 

for id in participantIds: 
    temp = id['player']['summonerName']
    player_ids[id['participantId']] = temp

team1 = player_ids[1][0:3]
team2 = player_ids[6][0:3]

team_ids[100] = team1
team_ids[200] = team2


# In[31]:

#Player Data
players = json_page['participants']
player_data = []
team1_kills = 0
team2_kills = 0
team1_deaths = 0
team2_deaths = 0
team1_assists = 0
team2_assists = 0
team1_gold = 0
team2_gold = 0

for player in players:
    temp = []
    stats = player['stats']
    timeline = player['timeline']
    
    playerId = player['participantId']
    kills = stats['kills']
    deaths = stats['deaths']
    assists = stats['assists']
    
    #kda calculation, depending on if they have 0 deaths
    if deaths > 0:
        kda = (kills + assists)/deaths
    else:
        kda = (kills + assists)/1

    cs = stats['neutralMinionsKilled'] + stats['totalMinionsKilled']
    length = json_page['gameDuration']
    
    #adding kda to team total 
    if playerId < 6:
        team1_kills += kills
        team1_deaths += deaths
        team1_assists += assists
        team1_gold += stats['goldEarned']
    else:
        team2_kills += kills
        team2_deaths += deaths
        team2_assists += assists
        team2_gold += stats['goldEarned']
    
    #date
    temp.append(date)
    #player name
    temp.append(playerId)
    #team
    temp.append(player['teamId'])
    #opponent and side 
    if player['teamId'] == 100:
        temp.append(200)
    else:
        temp.append(100)
    #win/loss
    temp.append(stats['win'])
    #role
    if playerId % 5 == 1:
        temp.append('TOP')
    elif playerId % 5 == 2:
        temp.append('JUNGLE')
    elif playerId % 5 == 3:
        temp.append('MIDDLE')
    elif playerId % 5 == 4:
        temp.append('ADC')
    else:
        temp.append('SUPPORT')
    #game length
    temp.append(json_page['gameDuration'])
    #champion
    temp.append(player['championId'])
    #kda
    temp.append(kda)
    temp.append(kills)
    temp.append(deaths)
    temp.append(assists)
    #cs
    temp.append(cs)
    #cs per minute
    temp.append(cs/length * 60)
    #gold
    temp.append(stats['goldEarned'])
    #gold per minute
    temp.append(stats['goldEarned']/length * 60)
    
    #adding the data to the list for all player data 
    player_data.append(temp)


# In[32]:

#team kda calculations
if team1_deaths == 0: 
    team1_kda = (team1_kills + team1_assists)/1
else:
    team1_kda = (team1_kills + team1_assists)/team1_deaths
    
if team2_deaths == 0: 
    team2_kda = (team2_kills + team2_assists)/1
else:
    team2_kda = (team2_kills + team2_assists)/team2_deaths


# In[33]:

#Team Data
teams = json_page['teams']
team_data = []
for team in teams:
    temp = []
    teamId = team['teamId']
    length = json_page['gameDuration']
    
    #date
    temp.append(date)
    #name
    temp.append(teamId)
    #side and opponent
    if teamId == 100:
        temp.append(200)
    else:
        temp.append(100)
    
    #win/loss
    #temp.append(team['win'])
    if team['win'] == 'Fail':
        temp.append(0)
    else:
        temp.append(1)
    #length
    temp.append(length)
    #kda, gold, and gold per minute
    if teamId == 100:
        temp.append(team1_kda)
        temp.append(team1_kills)
        temp.append(team1_deaths)
        temp.append(team1_assists)
        temp.append(team1_gold)
        temp.append(team1_gold/length * 60)
    else:
        temp.append(team2_kda)
        temp.append(team2_kills)
        temp.append(team2_deaths)
        temp.append(team2_assists)
        temp.append(team2_gold)
        temp.append(team2_gold/length * 60)
    
    #towers
    temp.append(team['towerKills'])
    temp.append(team['firstTower'])
    #dragons
    temp.append(team['dragonKills'])
    temp.append(team['firstDragon'])
    #barons
    temp.append(team['baronKills'])
    temp.append(team['firstBaron'])
    #firstblood
    temp.append(team['firstBlood'])
    
    team_data.append(temp)


# In[34]:

#For each player, replacement of all the ids and insertion of champion name
for player in player_data:
    #player name
    swap = player[1]
    player[1] = player_ids[swap]
    #team name
    swap = player[2]
    player[2] = team_ids[swap]
    #opponent team
    swap = player[3]
    player[3] = team_ids[swap]
    #champion
    swap = player[7]
    player[7] = champ_ids[swap]


# In[35]:

# Replacement of team names in the team_data
for team in team_data:
    #Name
    swap = team[1]
    team[1] = team_ids[swap]
    #opponent
    swap = team[2]
    team[2] = team_ids[swap]


# In[36]:

#Uploading data to Database
#Converting the lists to Tuples
team_tuples = []
player_tuples = []

for team in team_data: 
    team_tuples.append(tuple(team))
for player in player_data:
    player_tuples.append(tuple(player))



# In[37]:

#Creating the tables
create_team_table(team_table)
create_player_table(player_table)


# In[38]:

#Inserting team data 
for i in team_tuples: 
    cur.execute("INSERT INTO " + team_table + "(Date, Name, Opponent, Win, Length, KDA, Kills, Deaths, Assists, Gold, GPM, Towers, FirstTower, Dragons, FirstDrag, Barons, FirstBaron, FirstBlood) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", i)


# In[39]:

#Inserting player data
for i in player_tuples:
    cur.execute("INSERT INTO " + player_table + "(Date, Name, Team, Opponent, Win, Role, Length, Champion, KDA, Kills, Deaths, Assists, CS, CSPM, Gold, GPM) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", i)


# In[25]:

print("SCRAPING FINISHED YAYYYY~~~~")


# In[ ]:



