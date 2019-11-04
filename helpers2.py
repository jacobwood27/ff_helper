import pickle
import os.path
import sleeper_wrapper as SW
from fuzzywuzzy import fuzz,process
from nameparser import HumanName
import numpy as np
import string
import requests
import json
import ff_espn_api as espnfa
from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import praw as praw
import bs4 as bs4
from collections import defaultdict

database_file = 'player_database.pkl'
league_info_file = 'league_info.json'

ros_URL = 'https://5ahmbwl5qg.execute-api.us-east-1.amazonaws.com/dev/rankings'
def_expert = 'subvertadown'
kick_expert = 'subvertadown'
weekly_method = 'borischen'
yaml_config_temp = '_config_template.yml'

output_file = 'summary.txt'
yaml_config = '_config.yml'


def clean_name(dirty_name):
    name = HumanName(dirty_name.translate(str.maketrans('', '', string.punctuation)))
    if not name.first:
        name.first = name.title
    clean_name = name.first + ' ' + name.last
    return clean_name

if os.path.isfile(database_file):
    with open(database_file,'rb') as f:
        temp_obj = pickle.load(f)
        PLAYERLIST = temp_obj[0]
        REVERSE_LOOKUP = temp_obj[1]
        ESPN_LOOKUP= temp_obj[2]
        YAHOO_LOOKUP = temp_obj[3]
else:
    PLAYERLIST_full = SW.Players().get_all_players()
    PLAYERLIST = {}
    for key,val in PLAYERLIST_full.items():
        try:
            if val['search_rank'] < 19999990: #Remove people that are irrelevant to fantasy and names will bungle things up
                PLAYERLIST[key] = val 
        except KeyError: #If it is a defense
            PLAYERLIST[key] = val
    REVERSE_LOOKUP = {}
    ESPN_LOOKUP = {}
    YAHOO_LOOKUP = {}
    for k,p in PLAYERLIST.items():
        if 'full_name' in p.keys():
            REVERSE_LOOKUP[clean_name(p['full_name'])] = k
            ESPN_LOOKUP[str(p['espn_id'])] = k
            YAHOO_LOOKUP[str(p['yahoo_id'])] = k
        else:
            REVERSE_LOOKUP[k] = k
            ESPN_LOOKUP[p['player_id']] = k
            YAHOO_LOOKUP[p['player_id']] = k
    with open(database_file,'wb') as f:
        pickle.dump((PLAYERLIST,REVERSE_LOOKUP,ESPN_LOOKUP,YAHOO_LOOKUP),f)

NFL_TEAMS = [
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
    ['JAX', 'Jacksonville', 'Jaguars', 'Jacksonville Jaguars', 'JAC'],
    ['KC', 'Kansas City', 'Chiefs', 'Kansas City Chiefs', 'K.C.', 'KAN'],
    ['LAR', 'Rams', 'Los Angeles Rams', 'L.A.R.'],
    ['MIA', 'Miami', 'Dolphins', 'Miami Dolphins'],
    ['MIN', 'Minnesota', 'Vikings', 'Minnesota Vikings'],
    ['NE', 'New England', 'Patriots', 'New England Patriots', 'N.E.', 'NWE'],
    ['NO', 'New Orleans', 'Saints', 'New Orleans Saints', 'N.O.', 'NOR'],
    ['NYG', 'Giants', 'New York Giants', 'N.Y.G.'],
    ['NYJ', 'Jets', 'New York Jets', 'N.Y.J.'],
    ['OAK', 'Oakland', 'Raiders', 'Oakland Raiders'],
    ['PHI', 'Philadelphia', 'Eagles', 'Philadelphia Eagles'],
    ['PIT', 'Pittsburgh', 'Steelers', 'Pittsburgh Steelers'],
    ['LAC', 'Chargers', 'San Diego Chargers', 'L.A.C.'],
    ['SEA', 'Seattle', 'Seahawks', 'Seattle Seahawks'],
    ['SF', 'San Francisco', '49ers', 'San Francisco 49ers', 'S.F.', 'SFO'],
    ['STL', 'St. Louis', 'Rams', 'St. Louis Rams', 'S.T.L.'],
    ['TB', 'Tampa Bay', 'Buccaneers', 'Tampa Bay Buccaneers', 'T.B.', 'TAM'],
    ['TEN', 'Tennessee', 'Titans', 'Tennessee Titans'],
    ['WAS', 'Washington', 'Redskins', 'Washington Redskins', 'WSH'],
    ]
    
def get_standard_team(team):
    """
    Returns a standard abbreviation when team corresponds to a team in
    nflgame.teams (case insensitive).  All known variants of a team name are
    searched. If no team is found, None is returned.
    """
    team = team.lower()
    for variants in NFL_TEAMS:
        for variant in variants:
            if team == variant.lower():
                return variants[0]
    return None


def get_id_from_name(name):
    #try defense first
    standard_team = get_standard_team(name)
    if standard_team is not None:
        return standard_team

    possible_matches = process.extract(clean_name(name),REVERSE_LOOKUP.keys(),limit=12)
    if possible_matches[0][1] > 60: #We probably have a player
        match_scores = [p[1] for p in possible_matches]
        search_scores = []
        for p in possible_matches:
            try:
                search_scores.append(PLAYERLIST[REVERSE_LOOKUP[p[0]]]['search_rank'])
            except:
                search_scores.append(9999999)
        likelihood_scores = [float(m)**3 / float(s) for m,s in zip(match_scores,search_scores)] 
        idx = np.argmax(likelihood_scores)
        return REVERSE_LOOKUP[possible_matches[idx][0]]

    return None


def get_ranks(playerlist,ranker):
    #Assume that the ranker is in order of best to worst
    r_list = [r[0] for r in ranker]
    o_list = []
    idx_list = []
    num_misses = 0
    for p in playerlist:
        try: 
            idx = r_list.index(p)
            o_list.append(ranker[idx])
        except ValueError:
            num_misses += 1
            idx = len(r_list) + num_misses
            try:
                o_list.append((p,PLAYERLIST[p]['full_name'],None))
            except:
                o_list.append((p,p,None))
        idx_list.append(idx)
    ranks = [x for _,x in sorted(zip(idx_list,o_list))]
    return ranks
    
class Ranks:
    def __init__(self):
        self.QB = None
        self.RB = None
        self.WR = None
        self.TE = None
        self.FLEX = None
        self.K = None
        self.DEF = None

class Team:
    def __init__(self,my_id,starting_id):
        self.positions = ['QB','RB','RB','WR','WR','TE','FLEX','K','DEF','B','B','B','B','B','B','B']
        self.players = my_id
        self.starters = starting_id
        # self.ROS_ranks = get_ranks(self.players)

class Rostered_players:
    def __init__(self,rostered_id):
        self.playerlist = rostered_id

class League:
    def __init__(self, league_info, ROS_ranks, weekly_ranks, d_stream_ranks, k_stream_ranks):

        self.my_team = None
        self.rostered_players = None
        self.league_info = league_info
        self.nickname = league_info['nickname']
        self.scoring = league_info['scoring']
        self.platform = league_info['platform']
        
        self.d_stream_ranks = d_stream_ranks
        self.k_stream_ranks = k_stream_ranks
        self.ROS_ranks = ROS_ranks
        self.weekly_ranks = weekly_ranks

        self.free_agents = None

        self.my_QB = None
        self.my_RB = None
        self.my_WR = None
        self.my_TE = None
        self.my_FLEX = None
        self.my_K = None
        self.my_DEF = None

        self.fa_QB = None
        self.fa_RB = None
        self.fa_WR = None
        self.fa_TE = None
        self.fa_FLEX = None
        self.fa_K = None
        self.fa_DEF = None


        self.my_QB_weekly_ranks = None
        self.my_RB_weekly_ranks = None
        self.my_WR_weekly_ranks = None
        self.my_TE_weekly_ranks = None
        self.my_FLEX_weekly_ranks = None
        self.my_K_weekly_ranks = None
        self.my_DEF_weekly_ranks = None
        self.my_QB_ROS_ranks = None
        self.my_RB_ROS_ranks = None
        self.my_WR_ROS_ranks = None
        self.my_TE_ROS_ranks = None
        self.my_FLEX_ROS_ranks = None

        self.fa_QB_weekly_ranks = None
        self.fa_RB_weekly_ranks = None
        self.fa_WR_weekly_ranks = None
        self.fa_TE_weekly_ranks = None
        self.fa_FLEX_weekly_ranks = None
        self.fa_K_weekly_ranks = None
        self.fa_DEF_weekly_ranks = None
        self.fa_QB_ROS_ranks = None
        self.fa_RB_ROS_ranks = None
        self.fa_WR_ROS_ranks = None
        self.fa_TE_ROS_ranks = None
        self.fa_FLEX_ROS_ranks = None

        self.get_dudes()
        self.get_fa()
        self.disseminate_players()

        self.apply_ranks()

    def disseminate_players(self):
        self.my_QB = [p for p in self.my_team if 'QB' in PLAYERLIST[p]['fantasy_positions']]
        self.my_RB = [p for p in self.my_team if 'RB' in PLAYERLIST[p]['fantasy_positions']]
        self.my_WR = [p for p in self.my_team if 'WR' in PLAYERLIST[p]['fantasy_positions']]
        self.my_TE = [p for p in self.my_team if 'TE' in PLAYERLIST[p]['fantasy_positions']]
        self.my_FLEX = [p for p in self.my_team if any(pos in PLAYERLIST[p]['fantasy_positions'] for pos in ['RB','WR','TE']]
        self.my_K = [p for p in self.my_team if 'K' in PLAYERLIST[p]['fantasy_positions']]
        self.my_DEF = [p for p in self.my_team if 'DEF' in PLAYERLIST[p]['fantasy_positions']]

        self.fa_QB = [p for p in self.free_agents if 'QB' in PLAYERLIST[p]['fantasy_positions']]
        self.fa_RB = [p for p in self.free_agents if 'RB' in PLAYERLIST[p]['fantasy_positions']]
        self.fa_WR = [p for p in self.free_agents if 'WR' in PLAYERLIST[p]['fantasy_positions']]
        self.fa_TE = [p for p in self.free_agents if 'TE' in PLAYERLIST[p]['fantasy_positions']]
        self.fa_FLEX = [p for p in self.free_agents if any(pos in PLAYERLIST[p]['fantasy_positions'] for pos in ['RB','WR','TE']]
        self.fa_K = [p for p in self.free_agents if 'K' in PLAYERLIST[p]['fantasy_positions']]
        self.fa_DEF = [p for p in self.free_agents if 'DEF' in PLAYERLIST[p]['fantasy_positions']]

    def apply_ranks(self):

        self.my_QB_weekly_ranks = get_ranks([p for p in self.my_team if PLAYERLIST[p]],self.weekly_ranks)
        self.my_RB_weekly_ranks = None
        self.my_WR_weekly_ranks = None
        self.my_TE_weekly_ranks = None
        self.my_FLEX_weekly_ranks = None
        self.my_K_weekly_ranks = None
        self.my_DEF_weekly_ranks = None
        self.my_QB_ROS_ranks = None
        self.my_RB_ROS_ranks = None
        self.my_WR_ROS_ranks = None
        self.my_TE_ROS_ranks = None
        self.my_FLEX_ROS_ranks = None

        self.fa_QB_weekly_ranks = None
        self.fa_RB_weekly_ranks = None
        self.fa_WR_weekly_ranks = None
        self.fa_TE_weekly_ranks = None
        self.fa_FLEX_weekly_ranks = None
        self.fa_K_weekly_ranks = None
        self.fa_DEF_weekly_ranks = None
        self.fa_QB_ROS_ranks = None
        self.fa_RB_ROS_ranks = None
        self.fa_WR_ROS_ranks = None
        self.fa_TE_ROS_ranks = None
        self.fa_FLEX_ROS_ranks = None

    def get_fa(self):
        all_good_players = [p[0] for p in self.ROS_ranks.ranks] + [p[0] for p in self.weekly_ranks.ranks] + [p[0] for p in self.d_stream_ranks.ranks] + [p[0] for p in self.k_stream_ranks.ranks]
        good_fa = []
        for p in all_good_players:
            if p not in self.rostered_players:
                good_fa.append(p)
        self.free_agents = good_fa

    def get_dudes(self):

        if self.platform == 'ESPN':
            league_id = self.league_info['league_id']
            year = self.league_info['year']
            swid = self.league_info['swid']
            espn_s2 = self.league_info['espn_s2']
            team_num = self.league_info['team_num']

            league = espnfa.League(league_id, year, espn_s2, swid)
            my_team = league.teams[team_num-1]
            my_dudes = my_team.roster
            my_espn_ids = [str(d.playerId) for d in my_dudes if not ('D/ST' in d.eligibleSlots)] + [d.proTeam for d in my_dudes if ('D/ST' in d.eligibleSlots)]
            my_ids = [ESPN_LOOKUP[p] for p in my_espn_ids]

            teams = league.teams
            rosters = [team.roster for team in teams]
            rostered_pals = []
            for roster in rosters:
                dudes = [str(d.playerId) for d in roster if not ('D/ST' in d.eligibleSlots)] + [d.proTeam for d in roster if ('D/ST' in d.eligibleSlots)]
                rostered_pals.extend(dudes)
            rostered_ids = [ESPN_LOOKUP[p] for p in rostered_pals[0:25]]


            team_name = my_team.team_name
            boxscores = league.box_scores()
            for boxscore in boxscores:
                if boxscore.away_team.team_name == team_name:
                    my_guys = boxscore.away_lineup
                elif boxscore.home_team.team_name == team_name:
                    my_guys = boxscore.home_lineup

            starting_pals = []
            for guy in my_guys:
                if guy.slot_position not in ['BE']:
                    if guy.slot_position not in ['D/ST']:
                        starting_pals.append(str(guy.playerId))
                    else:
                        starting_pals.append(guy.proTeam)
            starting_ids = [ESPN_LOOKUP[p] for p in starting_pals]

        elif self.platform  == 'YAHOO':

            oauth_file = self.league_info['oauth_file']
            lg_number = self.league_info['lg_number']

            sc = OAuth2(None, None, from_file=oauth_file)
            gm = yfa.Game(sc, 'nfl')
            league = gm.to_league(lg_number)
            week = league.current_week()

            team_objs = league.teams()
            team_keys = [team['team_key'] for team in team_objs]
            teams = [league.to_team(key) for key in team_keys]
            rosters = [team.roster(week) for team in teams]
            rostered_ids = []
            for roster in rosters:
                for dude in roster:
                    if not 'DEF' in dude['eligible_positions']:
                        rostered_ids.append(YAHOO_LOOKUP[str(dude['player_id'])])
                    elif get_standard_team(dude['name']) is not None:
                        rostered_ids.append(get_standard_team(dude['name']))
                    elif dude['player_id']==100014:
                        rostered_ids.append('LAR')
                    else:
                        rostered_ids.append('LAC')

            my_team = league.to_team(league.team_key())
            my_roster = my_team.roster(week)
            my_ids = []
            starting_ids = []
            for dude in my_roster:
                if not 'DEF' in dude['eligible_positions']:
                    my_ids.append(YAHOO_LOOKUP[str(dude['player_id'])])
                elif get_standard_team(dude['name']) is not None:
                    my_ids.append(get_standard_team(dude['name']))
                elif dude['player_id']==100014:
                    my_ids.append('LAR')
                else:
                    my_ids.append('LAC')
                
                if not 'BN' in dude['selected_position']:
                    if not 'DEF' in dude['eligible_positions']:
                        starting_ids.append(YAHOO_LOOKUP[str(dude['player_id'])])
                    elif get_standard_team(dude['name']) is not None:
                        starting_ids.append(get_standard_team(dude['name']))
                    elif dude['player_id']==100014:
                        starting_ids.append('LAR')
                    else:
                        starting_ids.append('LAC')


        elif self.platform == 'SLEEPER':

            league_id = self.league_info['league_id']
            team_num = self.league_info['team_num']

            league = SW.League(league_id)
            rosters = league.get_rosters()

            my_team = rosters[team_num-1]
            my_ids = my_team['players']
            starting_ids = my_team['starters']
            rostered_teams = [roster['players'] for roster in rosters]
            rostered_ids = sum(rostered_teams, [])

        else:
            raise ValueError('League platform ' + league.platform + ' is not supported.')

        self.my_team = Team(my_ids,starting_ids)
        self.rostered_players = Rostered_players(rostered_ids)




class League_collection:
    def __init__(self, league_info_file, ROS_ranks, weekly_ranks, d_stream_ranks, k_stream_ranks):
        self.my_league_infos = self.parse_league_info(league_info_file)
        self.ROS_ranks = ROS_ranks
        self.weekly_ranks = weekly_ranks
        self.d_stream_ranks = d_stream_ranks
        self.k_stream_ranks = k_stream_ranks
        self.my_leagues = [League(l, ROS_ranks, weekly_ranks, d_stream_ranks, k_stream_ranks) for l in self.my_league_infos]

    def parse_league_info(self,league_info_file):
        with open(league_info_file) as f:
            league_info = json.load(f)
        return league_info

    def make_summary_text(self):
        #TODO
        pass

    def make_summary_webpage(self):
        #TODO
        pass

class ROS_ranks:
    def __init__(self, ros_URL):
        self.method = None
        self.rank_dict = None
        self.ranks = None
        
        self.get_ranks(ros_URL, 'HALF')
        

    def get_ranks(self, URL, scoring_method):
        self.method = URL

        sm = {'NONE':'none','HALF':'halfppr','PPR':'ppr'}

        page = requests.get(URL)
        text = page.text
        d = json.loads(text)

        recent_week = max([int(a[5::]) for a in list(d['rankings'])])
        recent_key = 'Week ' + str(recent_week)

        dudes = []
        names = []
        ranks = []
        for row in d['rankings'][recent_key][sm[scoring_method]]:
            val = float(row[1])
            for player in row[2::]:
                if player['name'] is not '':
                    dudes.append(get_id_from_name(clean_name(player['name'])))
                    names.append(clean_name(player['name']))
                    ranks.append(val)

        self.rank_dict = dict(zip(dudes,ranks))
        self.ranks = zip(dudes,names,ranks)


class Week_ranks:
    def __init__(self, week_method):
        self.method = None
        self.ranks = None
        self.rank_dict = None


        self.get_ranks(week_method)
    
    def get_ranks(self,method):
        self.method = method

class D_stream_ranks:
    def __init__(self, def_method):
        self.method = None
        self.ranks = None
        self.rank_dict = None
        self.html_table = None

        self.get_def_streams(def_method)

    def get_def_streams(self,expert):
        self.method = expert
        reddit = praw.Reddit(user_agent='FF extract',client_id='KJg5EYhXS1AEuw', client_secret="BKVUw4m7KVzRGnnsf3jYAZ8sJks")
        submissions = [s for s in reddit.redditor(expert).submissions.new()]

        ranked_list = []
        rank_pts = []
        if expert == 'subvertadown':
            for post in submissions:
                if 'defensive maneuvers' in post.title.lower():
                    post_html = post.selftext_html
                    break
            soup=bs4.BeautifulSoup(post_html,features="html.parser")
            table = soup.find("table")
            self.html_table = table

            for row in table.find_all("tr")[1:]:
                dataset = [td.get_text() for td in row.find_all("td")]
                team = get_standard_team(dataset[0])
                ranked_list.append(team)
                rank_pts.append(dataset[1])

        else:
            raise ValueError('I do not know how to interpret results from ' + expert + '.')

        d = defaultdict(lambda: 32)
        for ii,v in enumerate(ranked_list):
            d[v] = ii+1
        
        self.ranks = zip(ranked_list,ranked_list,rank_pts)
        self.rank_dict = d


class K_stream_ranks:
    def __init__(self, kicker_method):
        self.method = None
        self.ranks = None
        self.rank_dict = None
        self.html_table = None

        self.get_kicker_streams(kicker_method)
        
    def get_kicker_streams(self,expert):
        self.method = expert

        reddit = praw.Reddit(user_agent='FF extract',client_id='KJg5EYhXS1AEuw', client_secret="BKVUw4m7KVzRGnnsf3jYAZ8sJks")
        submissions = [s for s in reddit.redditor(expert).submissions.new()]

        ranked_list = []
        ranked_pts = []
        ranked_names = []
        if expert == 'subvertadown':
            for post in submissions:
                if "but here's the kicker" in post.title.lower():
                    post_html = post.selftext_html
                    break
            soup=bs4.BeautifulSoup(post_html,features="html.parser")
            table = soup.find("table")
            self.html_table = table

            for row in table.find_all("tr")[1:]:
                dataset = [td.get_text() for td in row.find_all("td")]
                guy = dataset[0]
                pts = dataset[1]
                ranked_list.append(get_id_from_name(clean_name(guy)))
                ranked_names.append(clean_name(guy))
                ranked_pts.append(pts)

        else:
            raise ValueError('I do not know how to interpret results from ' + expert + '.')

        d = defaultdict(lambda: 32)
        for ii,v in enumerate(ranked_list):
            d[v] = ii+1
        
        self.ranks = zip(ranked_list,ranked_names,ranked_pts)
        self.rank_dict = d


RR = ROS_ranks(ros_URL)
WR = Week_ranks(weekly_method)
DSR = D_stream_ranks(kick_expert)
KSR = K_stream_ranks(kick_expert)
LC = League_collection(league_info_file,RR,WR,DSR,KSR)

print('END')




#TO FIX
#Kickers are listed with last names only on rankings, so when looked up they will grab a more popular player with same last name (Elliott is going to grab Zeke, not Jake)
#Twitter Sentiment for players
#Show in/Q/out
#Right now everything is halfppr
