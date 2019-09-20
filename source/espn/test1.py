from ff_espn_api import League
import csv

league_id = 1889382
year = 2019
swid = '{DA15D2DF-39CF-493B-95D2-DF39CF993B46}'
espn_s2 = 'AEB%2BILmFxhqafm2YvjqdG7xw0hROHoIAr2lWmdy90SlgZeJrBPlGEclPKBphwVASEmDhEtI%2FD8Qc8mGda8PCMovvRHTCHP09cXgtwvlrf7a%2Bw2fTAcY7GEYOzMCzQ9L3XTDYBDCxMaNiBqNQhv1g8XNgmLXZ7GhAAa0lp5EcaqZQT4avngNfk2hyZNN9BRxY88OVxcAB5CNn1DvuEiMdDL9lOwhpV0Z5Ef4%2B4f7iqssT8tPbMFQXMvzPmx6gx0F4BWGNmUag4XFk2LFyosciIZnF'
team_num = 5
league = League(league_id, year, espn_s2, swid)



value_file = 'player_vals.csv'

val_dict = {};
with open(value_file,newline='') as csvfile:
	reader = csv.reader(csvfile)
	reader.__next__()
	reader.__next__()
	reader.__next__()
	for row in reader:
		val = row[2]
		dudes = [row[ii] for ii  in [3,6,9,12] if row[ii] is not '']
		for dude in dudes:
			val_dict.update({dude : val})


my_team = league.teams[team_num-1]
my_dudes = my_team.roster
fa_dudes = league.free_agents(size=200)

my_vals = []
my_pals = []
for dude in my_dudes:

	if dude.position == 'K' or dude.position == 'D/ST':
		continue

	my_pals.append(dude.name)
	try:
		my_vals.append(val_dict[dude.name])
	except:
		my_vals.append(0)


fa_vals = []
fa_pals = []
for dude in fa_dudes:

	if dude.position == 'K' or dude.position == 'D/ST':
		continue

	fa_pals.append(dude.name)
	try:
		fa_vals.append(val_dict[dude.name])
	except:
		fa_vals.append(0)


print(my_pals)
print(my_vals)
print(fa_pals)
print(fa_vals)



print('Done')