from ff_espn_api import League

league_id = 1889382
year = 2019
swid = '{DA15D2DF-39CF-493B-95D2-DF39CF993B46}'
espn_s2 = 'AEB%2BILmFxhqafm2YvjqdG7xw0hROHoIAr2lWmdy90SlgZeJrBPlGEclPKBphwVASEmDhEtI%2FD8Qc8mGda8PCMovvRHTCHP09cXgtwvlrf7a%2Bw2fTAcY7GEYOzMCzQ9L3XTDYBDCxMaNiBqNQhv1g8XNgmLXZ7GhAAa0lp5EcaqZQT4avngNfk2hyZNN9BRxY88OVxcAB5CNn1DvuEiMdDL9lOwhpV0Z5Ef4%2B4f7iqssT8tPbMFQXMvzPmx6gx0F4BWGNmUag4XFk2LFyosciIZnF'
team_num = 5



league = League(league_id, year, espn_s2, swid)
my_team = league.teams[team_num-1]
my_dudes = my_team.roster
my_pals = [dude.name for dude in my_dudes if not ('D/ST' in dude.eligibleSlots or 'K' in dude.eligibleSlots)]

teams = league.teams
rosters = [team.roster for team in teams]
rostered_pals = []
for roster in rosters:
	dudes = [dude.name for dude in roster if not ('D/ST' in dude.eligibleSlots or 'K' in dude.eligibleSlots)]
	rostered_pals.extend(dudes)



print(my_pals)
print(rostered_pals)
