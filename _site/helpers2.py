import pickle
import os.path
import sleeper_wrapper as SW
import fuzzywuzzy
from nameparser import HumanName

players_file = 'PLAYERLIST.pkl'

if os.path.isfile(players_file):
    with open(players_file,'rb') as f:
        PLAYERLIST = pickle.load(f)
else:
    PLAYERLIST_full = SW.Players().get_all_players()
    PLAYERLIST = {}
    for key,val in PLAYERLIST_full.items():
        try:
            if val['search_rank'] < 9999990:
                PLAYERLIST[key] = val 
        except KeyError: #If it is a defense
            PLAYERLIST[key] = val
    PLAYERLIST = [p for p in PLAYERLIST if p.search_rank is not 9999999] #remove all lame-Os
    with open(players_file,'wb') as f:
        pickle.dump(PLAYERLIST,f)

def get_id_from_name(name):
    
    return id

class player:
    def __init__(id):
        pass
