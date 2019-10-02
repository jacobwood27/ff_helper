from helpers import *


league_info_file = 'league_info.json'

ros_file = 'all2.csv'
def_file = 'def.csv'
kick_file = 'kick.csv'
weekly_method = 'borischen'

output_file = 'summary.txt'



league_info = parse_league_info(league_info_file)
ros_ranks,ros_ranked_dudes = parse_ros_ranks(ros_file)
def_rank = parse_simple_file(def_file)
kick_rank = parse_simple_file(kick_file)


summary = []
for l in league_info:

    my_dudes,my_pos,rostered_dudes,my_def,rostered_def,my_kick,rostered_kick = get_dudes(l)
    my_ros_dudes,my_ros_ranks,unowned_ros_dudes,unowned_ros_ranks = get_ranks(my_dudes, rostered_dudes, ros_ranked_dudes, ros_ranks)
    stream_def_advice = get_stream(my_def,rostered_def,def_rank)
    stream_kick_advice = get_stream(my_kick,rostered_kick,kick_rank)
    weekly_team,weekly_tiers,potential_stream_names,potential_stream_pos,potential_stream_tiers = get_weekly(my_dudes,rostered_dudes,weekly_method)

    txt = get_summary_text(l,my_ros_dudes,my_ros_ranks,unowned_ros_dudes,unowned_ros_ranks,stream_def_advice,stream_kick_advice,weekly_team,weekly_tiers,potential_stream_names,potential_stream_pos,potential_stream_tiers)
    summary.extend(txt)

with open(output_file,'w') as f:
    f.writelines(summary)

print('Done')