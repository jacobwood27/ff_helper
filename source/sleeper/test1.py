from sleeper_wrapper import League, Players
import pickle
import os.path

# Define Inputs
league_id = 470314205950504960
players_file = 'sleeper_players.pkl'
team_num = 8


# Access API
league = League(league_id)
rosters = league.get_rosters()

# Not supposed to call this all the time because it is a large file (5MB)
if os.path.isfile(players_file):
	with open(players_file,'rb') as f:
		players = pickle.load(f)
else:
	P = Players()
	players = P.get_all_players()
	with open(players_file,'wb') as f:
		pickle.dump(players,f)

my_team = rosters[team_num-1]
my_dudes = [players[id] for id in my_team['players']]
my_pals = [dude['full_name'] for dude in my_dudes if not (('DEF' in dude['fantasy_positions']) or ('K' in dude['fantasy_positions']))]

rostered_teams = [roster['players'] for roster in rosters]
rostered_players = sum(rostered_teams, [])
rostered_dudes = [players[id] for id in rostered_players]
rostered_pals = [dude['full_name'] for dude in rostered_dudes if not (('DEF' in dude['fantasy_positions']) or ('K' in dude['fantasy_positions']))]

print('Done')
print(my_pals)
print(rostered_pals)