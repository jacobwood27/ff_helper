from mdutils.mdutils import MdUtils

mdFile = MdUtils(file_name='League01',title='Grundle Me This')

mdFile.new_header(level=1, title='ROS Valuations')
mdFile.new_header(level=2, title='Your Roster')
mdFile.new_header(level=2, title='Available Free Agents')

mdFile.new_header(level=1, title='Weekly Tiers')
mdFile.new_header(level=2, title='Suggested Starting Lineup')
mdFile.new_header(level=2, title='Substitutions Necessary')
mdFile.new_header(level=2, title='Skill Streams Available')

mdFile.new_header(level=1, title='Weekly Streaming Advice')
mdFile.new_header(level=2, title='Defenses')
mdFile.new_header(level=2, title='Kickers')

mdFile.new_header(level=1, title='Data Sources')
mdFile.new_header(level=2, title='ROS Valuations')

mdFile.new_header(level=2, title='Weekly Tiers')
mdFile.new_header(level=3, title='QB')
mdFile.new_header(level=3, title='RB')
mdFile.new_header(level=3, title='WR')
mdFile.new_header(level=3, title='FLEX')

mdFile.new_header(level=2, title='Streaming Rankings')
mdFile.new_header(level=3, title='Defenses')
mdFile.new_header(level=3, title='Kickers')

mdFile.create_md_file()

