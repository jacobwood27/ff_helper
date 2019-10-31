from mdutils.mdutils import MdUtils

mdFile = MdUtils(file_name='league01',title='Grundle Me This')
mdFile.new_header(level=2, title='ROS Valuations',add_table_of_contents='n')

list_of_strings = ["Rank", "Player", "Value"]
player = ["AB", "asdf", "asdfad"]
value = [60, 45, 12]
for x in range(3):
    list_of_strings.extend([str(x), player[x], str(value[x])])
mdFile.new_table(columns=3, rows=4, text=list_of_strings, text_align='center')

mdFile.new_header(level=3, title='Your Roster',add_table_of_contents='n')
mdFile.new_header(level=3, title='Available Free Agents',add_table_of_contents='n')

mdFile.new_header(level=2, title='Weekly Tiers',add_table_of_contents='n')
mdFile.new_header(level=3, title='Suggested Starting Lineup',add_table_of_contents='n')
mdFile.new_header(level=3, title='Substitutions Necessary',add_table_of_contents='n')
mdFile.new_header(level=3, title='Skill Streams Available',add_table_of_contents='n')

mdFile.new_header(level=2, title='Weekly Streaming Advice',add_table_of_contents='n')
mdFile.new_header(level=3, title='Defenses',add_table_of_contents='n')
mdFile.new_header(level=3, title='Kickers',add_table_of_contents='n')



mdFile.create_md_file()





mdFile = MdUtils(file_name='crawl_data',title='Data Sources and Crawled Data')
mdFile.new_header(level=2, title='ROS Valuations',add_table_of_contents='n')
mdFile.new_header(level=2, title='Weekly Tiers',add_table_of_contents='n')
mdFile.new_header(level=3, title='QB',add_table_of_contents='n')
mdFile.new_header(level=3, title='RB',add_table_of_contents='n')
mdFile.new_header(level=3, title='WR',add_table_of_contents='n')
mdFile.new_header(level=3, title='FLEX',add_table_of_contents='n')

mdFile.new_header(level=2, title='Streaming Rankings',add_table_of_contents='n')
mdFile.new_header(level=3, title='Defenses',add_table_of_contents='n')
mdFile.new_header(level=3, title='Kickers',add_table_of_contents='n')

mdFile.create_md_file()