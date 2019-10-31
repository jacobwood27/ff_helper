from helpers import *
import shutil

league_info_file = 'league_info.json'

ros_URL = 'https://5ahmbwl5qg.execute-api.us-east-1.amazonaws.com/dev/rankings'
def_expert = 'subvertadown'
kick_expert = 'subvertadown'
weekly_method = 'borischen'
yaml_config_temp = '_config_template.yml'

output_file = 'summary.txt'
yaml_config = '_config.yml'


league_info = parse_league_info(league_info_file)
# ros_ranks,ros_ranked_dudes = parse_ros_ranks(ros_file)
ros_ranked_dudes,ros_ranks = get_ros_stuff(ros_URL)
# def_rank = parse_simple_file(def_file)
# kick_rank = parse_simple_file(kick_file)
def_rank = get_reddit_expert_rank(def_expert,'DEF')
kick_rank = get_reddit_expert_rank(kick_expert,'K')

summary = []
shutil.copy(yaml_config_temp,yaml_config)
for l in league_info:

    my_dudes,my_pos,rostered_dudes,my_def,rostered_def,my_kick,rostered_kick,starters = get_dudes(l)
    my_ros_dudes,my_ros_ranks,unowned_ros_dudes,unowned_ros_ranks = get_ranks(my_dudes, rostered_dudes, ros_ranked_dudes, ros_ranks)
    stream_def_advice = get_stream(my_def,rostered_def,def_rank)
    stream_kick_advice = get_stream(my_kick,rostered_kick,kick_rank)
    weekly_team,weekly_tiers,potential_stream_names,potential_stream_pos,potential_stream_tiers = get_weekly(my_dudes,rostered_dudes,weekly_method)

    txt = get_summary_text(l,my_ros_dudes,my_ros_ranks,unowned_ros_dudes,unowned_ros_ranks,stream_def_advice,stream_kick_advice,weekly_team,weekly_tiers,potential_stream_names,potential_stream_pos,potential_stream_tiers,starters)
    summary.extend(txt)

    md_file = write_league_md(l,my_ros_dudes,my_ros_ranks,unowned_ros_dudes,unowned_ros_ranks,stream_def_advice,stream_kick_advice,weekly_team,weekly_tiers,potential_stream_names,potential_stream_pos,potential_stream_tiers,starters)
    with open(yaml_config, 'a') as f:
        f.writelines(['  - title: ' + l['nickname'] + '\n','    url: ' + md_file + '\n'])

with open(output_file,'w') as f:
    f.writelines(summary)

print('Done')