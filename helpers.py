
NFL_teams = [
    ['ARI', 'Arizona', 'Cardinals', 'Arizona Cardinals'],
    ['ATL', 'Atlanta', 'Falcons', 'Atlanta Falcons'],
    ['BAL', 'Baltimore', 'Ravens', 'Baltimore Ravens'],
    ['BUF', 'Buffalo', 'Bills', 'Buffalo Bills'],
    ['CAR', 'Carolina', 'Panthers', 'Carolina Panthers'],
    ['CHI', 'Chicago', 'Bears', 'Chicago Bears'],
    ['CIN', 'Cincinnati', 'Bengals', 'Cincinnati Bengals'],
    ['CLE', 'Cleveland', 'Browns', 'Cleveland Browns'],
    ['DAL', 'Dallas', 'Cowboys', 'Dallas Cowboys'],
    ['DEN', 'Denver', 'Broncos', 'Denver Broncos'],
    ['DET', 'Detroit', 'Lions', 'Detroit Lions'],
    ['GB', 'Green Bay', 'Packers', 'Green Bay Packers', 'G.B.', 'GNB'],
    ['HOU', 'Houston', 'Texans', 'Houston Texans'],
    ['IND', 'Indianapolis', 'Colts', 'Indianapolis Colts'],
    ['JAC', 'Jacksonville', 'Jaguars', 'Jacksonville Jaguars', 'JAX'],
    ['KC', 'Kansas City', 'Chiefs', 'Kansas City Chiefs', 'K.C.', 'KAN'],
    ['LA', 'Los Angeles', 'Rams', 'Los Angeles Rams', 'L.A.'],
    ['MIA', 'Miami', 'Dolphins', 'Miami Dolphins'],
    ['MIN', 'Minnesota', 'Vikings', 'Minnesota Vikings'],
    ['NE', 'New England', 'Patriots', 'New England Patriots', 'N.E.', 'NWE'],
    ['NO', 'New Orleans', 'Saints', 'New Orleans Saints', 'N.O.', 'NOR'],
    ['NYG', 'Giants', 'New York Giants', 'N.Y.G.'],
    ['NYJ', 'Jets', 'New York Jets', 'N.Y.J.'],
    ['OAK', 'Oakland', 'Raiders', 'Oakland Raiders'],
    ['PHI', 'Philadelphia', 'Eagles', 'Philadelphia Eagles'],
    ['PIT', 'Pittsburgh', 'Steelers', 'Pittsburgh Steelers'],
    ['SD', 'San Diego', 'Chargers', 'San Diego Chargers', 'S.D.', 'SDG'],
    ['SEA', 'Seattle', 'Seahawks', 'Seattle Seahawks'],
    ['SF', 'San Francisco', '49ers', 'San Francisco 49ers', 'S.F.', 'SFO'],
    ['STL', 'St. Louis', 'Rams', 'St. Louis Rams', 'S.T.L.'],
    ['TB', 'Tampa Bay', 'Buccaneers', 'Tampa Bay Buccaneers', 'T.B.', 'TAM'],
    ['TEN', 'Tennessee', 'Titans', 'Tennessee Titans'],
    ['WAS', 'Washington', 'Redskins', 'Washington Redskins', 'WSH'],
    ]
    
def standard_team(team):
    """
    Returns a standard abbreviation when team corresponds to a team in
    nflgame.teams (case insensitive).  All known variants of a team name are
    searched. If no team is found, None is returned.
    """
    team = team.lower()
    for variants in NFL_teams:
        for variant in variants:
            if team == variant.lower():
                return variants[0]
    return None

def get_dudes(my_league):   

    starting_lineup = []

    if my_league['platform'] == 'ESPN':
        from ff_espn_api import League

        league_id = my_league['league_id']
        year = my_league['year']
        swid = my_league['swid']
        espn_s2 = my_league['espn_s2']
        team_num = my_league['team_num']

        league = League(league_id, year, espn_s2, swid)
        my_team = league.teams[team_num-1]
        my_dudes = my_team.roster
        my_pals = [dude.name for dude in my_dudes if not ('D/ST' in dude.eligibleSlots or 'K' in dude.eligibleSlots)]
        my_pos = [dude.position for dude in my_dudes if not ('D/ST' in dude.eligibleSlots or 'K' in dude.eligibleSlots)]
        my_def = [dude.proTeam for dude in my_dudes if 'D/ST' in dude.eligibleSlots]
        my_kick = [dude.name for dude in my_dudes if 'K' in dude.eligibleSlots]

        teams = league.teams
        rosters = [team.roster for team in teams]
        rostered_pals = []
        rostered_def = []
        rostered_kick = []
        for roster in rosters:
            dudes = [dude.name for dude in roster if not ('D/ST' in dude.eligibleSlots or 'K' in dude.eligibleSlots)]
            rostered_pals.extend(dudes)
            rostered_def.extend([dude.proTeam for dude in roster if 'D/ST' in dude.eligibleSlots])
            rostered_kick.extend([dude.name for dude in roster if 'K' in dude.eligibleSlots])


        team_name = my_team.team_name
        boxscores = league.box_scores()
        for boxscore in boxscores:
            if boxscore.away_team.team_name == team_name:
                my_guys = boxscore.away_lineup
            elif boxscore.home_team.team_name == team_name:
                my_guys = boxscore.home_lineup

        for guy in my_guys:
            if guy.slot_position not in ['D/ST','K','BE']:
                starting_lineup.append(guy.name)

    elif my_league['platform'] == 'YAHOO':
        from yahoo_oauth import OAuth2
        import yahoo_fantasy_api as yfa

        oauth_file = my_league['oauth_file']
        lg_number = my_league['lg_number']

        sc = OAuth2(None, None, from_file=oauth_file)
        gm = yfa.Game(sc, 'nfl')
        league = gm.to_league(lg_number)
        week = league.current_week()

        team_objs = league.teams()
        team_keys = [team['team_key'] for team in team_objs]
        teams = [league.to_team(key) for key in team_keys]
        rosters = [team.roster(week) for team in teams]
        rostered_pals = []
        rostered_def = []
        rostered_kick = []
        for roster in rosters:
            dudes = [dude['name'] for dude in roster if not ('K' in dude['eligible_positions'] or 'DEF' in dude['eligible_positions'])]
            rostered_pals.extend(dudes)
            rostered_def.extend([dude['name'] for dude in roster if 'DEF' in dude['eligible_positions']])
            rostered_kick.extend([dude['name'] for dude in roster if 'K' in dude['eligible_positions']])

        my_team = league.to_team(league.team_key())
        my_roster = my_team.roster(week)
        my_pals = [dude['name'] for dude in my_roster if not ('K' in dude['eligible_positions'] or 'DEF' in dude['eligible_positions'])]
        my_pos = [dude['eligible_positions'][0] for dude in my_roster if not ('K' in dude['eligible_positions'] or 'DEF' in dude['eligible_positions'])]
        my_def = [dude['name'] for dude in my_roster if 'DEF' in dude['eligible_positions']]
        my_kick = [dude['name'] for dude in my_roster if 'K' in dude['eligible_positions']]
        starting_lineup = [dude['name'] for dude in my_roster if not dude['selected_position'] in ['BN','K','DEF']]

        def_map  = { #This neglects the RAMS and the GIANTS because Yahoo is dumb and I don't want to figure out their player IDs.
            'New England':'NE',
            'Chicago':'CHI',
            'Tampa Bay':'TB',
            'Tennessee':'TEN',
            'San Francisco':'SF',
            'New York':'NYJ',
            'Green Bay':'GB',
            'New Orleans':'NO',
            'Pittsburgh':'PIT',
            'Carolina':'CAR',
            'Detroit':'DET',
            'Seattle':'SEA',
            'Cleveland':'CLE',
            'Los Angeles':'LAC',
            'Kansas City':'KC',
            'Minnesota':'MIN',
            'Buffalo':'BUF',
            'Dallas':'DAL',
            'Houston':'HOU',
            'Jacksonville':'JAX',
            'Indianapolis':'IND',
            'Oakland':'OAK',
            'Washington':'WAS',
            'Baltimore':'BAL',
            'Philadelphia':'PHI',
            'Arizona':'ARI',
            'Atlanta':'ATL',
            'Cincinnati':'CIN',
            'Denver':'DEN',
            'Miami':'MIA'}

        my_def = [def_map[d] for d in my_def]
        rostered_def = [def_map[d] for d in rostered_def]

    elif my_league['platform'] == 'SLEEPER':
        from sleeper_wrapper import League, Players
        import pickle
        import os.path

        league_id = my_league['league_id']
        players_file = my_league['players_file']
        team_num = my_league['team_num']

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
        starting_dudes = [players[id] for id in my_team['starters']]
        starting_lineup = [dude['full_name'] for dude in starting_dudes if not (('DEF' in dude['fantasy_positions']) or ('K' in dude['fantasy_positions']))]
        my_pos = [dude['position'] for dude in my_dudes if not (('DEF' in dude['fantasy_positions']) or ('K' in dude['fantasy_positions']))]
        my_def = [dude['player_id'] for dude in my_dudes if 'DEF' in dude['fantasy_positions']]
        my_kick = [dude['full_name'] for dude in my_dudes if 'K' in dude['fantasy_positions']]

        rostered_teams = [roster['players'] for roster in rosters]
        rostered_players = sum(rostered_teams, [])
        rostered_dudes = [players[id] for id in rostered_players]
        rostered_pals = [dude['full_name'] for dude in rostered_dudes if not (('DEF' in dude['fantasy_positions']) or ('K' in dude['fantasy_positions']))]
        rostered_def = [dude['player_id'] for dude in rostered_dudes if 'DEF' in dude['fantasy_positions']]
        rostered_kick = [dude['full_name'] for dude in rostered_dudes if 'K' in dude['fantasy_positions']]



    else:
        raise ValueError('League platform ' + league.platform + ' is not supported.')

    return my_pals,my_pos,rostered_pals,my_def,rostered_def,my_kick,rostered_kick,clean_names(starting_lineup)

def clean_names(dirty_names):
    from nameparser import HumanName
    import string

    names = []
    for dude in dirty_names:
        name = HumanName(dude.translate(str.maketrans('', '', string.punctuation)))
        if not name.first:
            name.first = name.title
        names.append(name.first + ' ' + name.last)

    return names

def get_ranks(my_dudes, rostered_dudes, ranked_dudes, ranks):
    from fuzzywuzzy import fuzz,process

    mds = clean_names(my_dudes)
    rsts = clean_names(rostered_dudes)
    rnks = clean_names(ranked_dudes)

    my_dudes_ranks = []
    my_good_dudes = []
    for dude in mds:
        fuzz_best = process.extractOne(dude,rnks)
        if fuzz_best[1] > 97:
            my_dudes_ranks.append(ranks[rnks.index(fuzz_best[0])])
            my_good_dudes.append(fuzz_best[0])
        else:
            my_dudes_ranks.append(0)
            my_good_dudes.append(dude)

    if len(my_good_dudes)>0:
        my_dudes_ranks, my_good_dudes = (list(t) for t in zip(*sorted(zip(my_dudes_ranks, my_good_dudes),reverse=True)))

    unowned_dudes = []
    unowned_dudes_ranks = []
    for player in rnks:
        fuzz_best = process.extractOne(player,rsts)
        if fuzz_best[1] < 97:
            unowned_dudes.append(player)
            unowned_dudes_ranks.append(ranks[rnks.index(player)])

    if len(unowned_dudes)>0:
        unowned_dudes_ranks, unowned_dudes = (list(t) for t in zip(*sorted(zip(unowned_dudes_ranks, unowned_dudes),reverse=True)))

    return my_good_dudes,my_dudes_ranks,unowned_dudes,unowned_dudes_ranks



def parse_league_info(league_info_file):
    import json
    with open(league_info_file) as f:
        league_info = json.load(f)
    return league_info

def parse_ros_ranks(ros_file):
    import csv
    with open(ros_file) as f:
        reader = csv.reader(f)
        ranked_dudes = [i[0] for i in reader]
        f.seek(0)
        ranks = [float(i[1]) for i in reader]
    return ranks,ranked_dudes


def get_summary_text(league,my_ros_dudes,my_ros_ranks,unowned_ros_dudes,unowned_ros_ranks,def_advice,kick_advice,weekly_team,weekly_tiers,potential_stream_names,potential_stream_pos,potential_stream_tiers,starters):
    
    spacing = 25 # Number of characters before ranking printed 

    txt = [league['nickname'] + ':\n']
    txt.append('\tYOUR TEAM:\n')
    for dude,rank in zip(my_ros_dudes,my_ros_ranks):
        txt.append('\t\t' + dude + (spacing-len(dude))*'.' + str(rank) + '\n')
    txt.append('\tAVAILABLE FREE AGENTS:\n')
    for dude,rank in zip(unowned_ros_dudes,unowned_ros_ranks):
        if rank>0:
            txt.append('\t\t' + dude + (spacing-len(dude))*'.' + str(rank) + '\n')
    txt.append('\tCONSIDER THESE MOVES:\n')

    idx = 0
    while idx<len(unowned_ros_ranks) and my_ros_ranks[-1-idx] < unowned_ros_ranks[idx]:
        txt.append('\t\t' + my_ros_dudes[-1-idx] + (spacing-len(my_ros_dudes[-1-idx]))*'.' + 'DROP' + '\n')
        txt.append('\t\t' + unowned_ros_dudes[idx] + (spacing-len(unowned_ros_dudes[idx]))*'.' + 'ADD' + '\n')
        idx+=1

    txt.append('\tCONSIDER THIS STARTING LINEUP:\n')
    for guy,tier in zip(weekly_team,weekly_tiers):
        txt.append('\t\t' + guy + (spacing-len(guy))*'.' + str(tier) + '\n')

    txt.append('\tBORIS CHEN SAYS TO MAKE THESE CHANGES TO LINEUP:\n')
    for starter in starters:
        if starter not in weekly_team:
            txt.append('\t\t' + starter + (spacing-len(starter))*'.' + 'BENCH' + '\n')
    
    for guy in weekly_team:
        if guy not in starters:
            txt.append('\t\t' + guy + (spacing-len(guy))*'.' + 'START' + '\n')
    
    txt.append('\tHOWEVER, CONSIDER THESE SKILL STREAMS:\n')
    for guy,tier,pos in zip(potential_stream_names,potential_stream_tiers,potential_stream_pos):
        txt.append('\t\t' + pos + ' - ' + guy + (spacing-len(guy) - len(pos) - 3)*'.' + str(tier) + '\n')

    txt.append('\tCONSIDER THIS DEFENSE STREAMING ADVICE:\n')
    txt.append('\t\t' + def_advice + '\n')

    txt.append('\tCONSIDER THIS KICKER STREAMING ADVICE:\n')
    txt.append('\t\t' + kick_advice + '\n')

    txt.append('\n')
    return txt
    
    
def parse_simple_file(file_in):
    import csv
    with open(file_in) as f:
        reader = csv.reader(f)
        dudes = [i[0] for i in reader]
    return dudes


def get_stream(my_dude,rostered_dude,dude_rank):

    my_dude_lastnames = []
    for dude in my_dude:
        my_dude_lastnames.append(dude.split()[-1])

    rost_dude_lastnames = []
    for dude in rostered_dude:
        rost_dude_lastnames.append(dude.split()[-1])
    
    rank_dude_lastnames = []
    for dude in dude_rank:
        rank_dude_lastnames.append(dude.split()[-1])

    for dude in rank_dude_lastnames:
        if dude in my_dude_lastnames:
            stream_advice = 'Looks like you already have a great option in rank ' + str(rank_dude_lastnames.index(dude) + 1) + ' - ' + dude
            break
        elif dude not in rost_dude_lastnames:
            my_ranks = []
            for guy in my_dude_lastnames:
                if guy in rank_dude_lastnames:
                    my_ranks.append(str(rank_dude_lastnames.index(guy) + 1))
                else:
                    my_ranks.append('>' + str(len(rank_dude_lastnames)))
            stream_advice = 'Looks like you should pickup rank ' + str(rank_dude_lastnames.index(dude) + 1) + ' - ' + dude + ' over your rank ' + str(my_ranks) + ' - ' + str(my_dude_lastnames)
            break

    return stream_advice

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_after( s, first):
    try:
        start = s.index( first ) + len( first )
        return s[start::]
    except ValueError:
        return ""

def get_boris_stuff(URL):
    import requests

    page = requests.get(URL)
    text = page.text
    tier_split = text.split('\n')
    dudes = []
    tiers = []
    for tier in tier_split:
        if len(tier) < 5:
            continue

        tier_no = int(find_between(tier,'Tier ',':'))
        str_players = find_after(tier,':')
        players = str_players.split(',')
        players = [player[1::] for player in players]
        players = clean_names(players)
        dudes.extend(players)
        tiers.extend([tier_no] * len(players))

    return dudes,tiers

def get_ros_stuff(URL):
    import requests
    import json

    page = requests.get(URL)
    text = page.text
    d = json.loads(text)

    recent_week = max([int(a[5::]) for a in list(d['rankings'])])
    recent_key = 'Week ' + str(recent_week)

    dudes = []
    ranks = []
    for row in d['rankings'][recent_key]['halfppr']:
        val = float(row[1])
        for player in row[2::]:
            if player['name'] is not '':
                dudes.append(player['name'])
                ranks.append(val)

    return dudes,ranks

def get_reddit_expert_rank(expert,pos):
    import praw
    import bs4
    reddit = praw.Reddit(user_agent='FF extract',client_id='KJg5EYhXS1AEuw', client_secret="BKVUw4m7KVzRGnnsf3jYAZ8sJks")
    submissions = [s for s in reddit.redditor(expert).submissions.new()]

    ranked_list = []
    if expert == 'subvertadown':
        if pos.lower() == 'def':
            for post in submissions:
                if 'defensive maneuvers' in post.title.lower():
                    post_html = post.selftext_html
                    break
            soup=bs4.BeautifulSoup(post_html,features="html.parser")
            table = soup.find("table")

            for row in table.find_all("tr")[1:]:
                dataset = [td.get_text() for td in row.find_all("td")]
                team = standard_team(dataset[0])
                ranked_list.append(team)

        if pos.lower() == 'k':
            for post in submissions:
                if "but here's the kicker" in post.title.lower():
                    post_html = post.selftext_html
                    break
            soup=bs4.BeautifulSoup(post_html,features="html.parser")
            table = soup.find("table")

            for row in table.find_all("tr")[1:]:
                dataset = [td.get_text() for td in row.find_all("td")]
                guy = dataset[0]
                ranked_list.append(guy)

    else:
        raise ValueError('I do not know how to interpret results from ' + expert + '.')

    return ranked_list

def get_weekly(my_dudes,rostered_dudes,weekly_method):
    from fuzzywuzzy import fuzz,process

    thresh = 97

    my_avail_dudes = clean_names(my_dudes)
    rstrd_dudes = clean_names(rostered_dudes)
    
    if weekly_method == 'borischen':
        QB_url = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_QB.txt'
        RB_url = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_RB-HALF.txt'
        WR_url = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_WR-HALF.txt'
        TE_url = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_TE-HALF.txt'
        FLEX_url = 'https://s3-us-west-1.amazonaws.com/fftiers/out/text_FLX-HALF.txt'

        QBs,QBt = get_boris_stuff(QB_url)
        RBs,RBt = get_boris_stuff(RB_url)
        WRs,WRt = get_boris_stuff(WR_url)
        TEs,TEt = get_boris_stuff(TE_url)
        FLEXs,FLEXt = get_boris_stuff(FLEX_url)

        potential_stream_names = []
        potential_stream_pos = []
        potential_stream_tiers = []
        start_QB = []
        start_QBt = []
        start_RB = []
        start_RBt = []
        start_WR = []
        start_WRt = []
        start_TE = []
        start_TEt = []
        start_FLEX = []
        start_FLEXt = []

        for QB,tier in zip(QBs,QBt):
            fuzz_myteam = process.extractOne(QB,my_avail_dudes)
            fuzz_rostered = process.extractOne(QB,rstrd_dudes)
            if fuzz_myteam[1] > thresh:
                start_QB.append(QB)
                start_QBt.append(tier)
                my_avail_dudes.remove(fuzz_myteam[0])
                break
            elif fuzz_rostered[1] < thresh:
                potential_stream_names.append(QB)
                potential_stream_pos.append('QB')
                potential_stream_tiers.append(tier)

        flag = 0
        for RB,tier in zip(RBs,RBt):
            fuzz_myteam = process.extractOne(RB,my_avail_dudes)
            fuzz_rostered = process.extractOne(RB,rstrd_dudes)
            if fuzz_myteam[1] > thresh:
                start_RB.append(RB)
                start_RBt.append(tier)
                my_avail_dudes.remove(fuzz_myteam[0])
                flag+=1
                if flag == 2:
                    break
            elif fuzz_rostered[1] < thresh:
                potential_stream_names.append(RB)
                potential_stream_pos.append('RB')
                potential_stream_tiers.append(tier)

        flag = 0
        for WR,tier in zip(WRs,WRt):
            fuzz_myteam = process.extractOne(WR,my_avail_dudes)
            fuzz_rostered = process.extractOne(WR,rstrd_dudes)
            if fuzz_myteam[1] > thresh:
                start_WR.append(WR)
                start_WRt.append(tier)
                my_avail_dudes.remove(fuzz_myteam[0])
                flag+=1
                if flag == 2:
                    break
            elif fuzz_rostered[1] < thresh:
                potential_stream_names.append(WR)
                potential_stream_pos.append('WR')
                potential_stream_tiers.append(tier)

        for TE,tier in zip(TEs,TEt):
            fuzz_myteam = process.extractOne(TE,my_avail_dudes)
            fuzz_rostered = process.extractOne(TE,rstrd_dudes)
            if fuzz_myteam[1] > thresh:
                start_TE.append(TE)
                start_TEt.append(tier)
                my_avail_dudes.remove(fuzz_myteam[0])
                break
            elif fuzz_rostered[1] < thresh:
                potential_stream_names.append(TE)
                potential_stream_pos.append('TE')
                potential_stream_tiers.append(tier)

        for FLEX,tier in zip(FLEXs,FLEXt):
            fuzz_myteam = process.extractOne(FLEX,my_avail_dudes)
            fuzz_rostered = process.extractOne(FLEX,rstrd_dudes)
            if fuzz_myteam[1] > thresh:
                start_FLEX.append(FLEX)
                start_FLEXt.append(tier)
                my_avail_dudes.remove(fuzz_myteam[0])
                break
            elif fuzz_rostered[1] < thresh:
                potential_stream_names.append(FLEX)
                potential_stream_pos.append('FLEX')
                potential_stream_tiers.append(tier)

    else:
        raise ValueError('Weekly ranking method ' + weekly_method + ' is not supported.')

    weekly_team = start_QB + start_RB + start_WR + start_TE + start_FLEX
    weekly_tiers = start_QBt + start_RBt + start_WRt + start_TEt + start_FLEXt

    return weekly_team,weekly_tiers,potential_stream_names,potential_stream_pos,potential_stream_tiers



