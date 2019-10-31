from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa

# Define Inputs
oauth_file = 'oauth2.json'
lg_number = '390.l.824038'


# Access API
sc = OAuth2(None, None, from_file=oauth_file)
gm = yfa.Game(sc, 'nfl')
league = gm.to_league(lg_number)
week = league.current_week()

team_objs = league.teams()
team_keys = [team['team_key'] for team in team_objs]
teams = [league.to_team(key) for key in team_keys]
rosters = [team.roster(week) for team in teams]
rostered_pals = []
for roster in rosters:
	dudes = [dude['name'] for dude in roster if not ('K' in dude['eligible_positions'] or 'DEF' in dude['eligible_positions'])]
	rostered_pals.extend(dudes)


my_team = league.to_team(league.team_key())
my_roster = my_team.roster(week)
my_pals = [dude['name'] for dude in my_roster if not ('K' in dude['eligible_positions'] or 'DEF' in dude['eligible_positions'])]


print('Done')
print(my_pals)
print(rostered_pals)