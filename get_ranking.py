#!/usr/bin/python3

import requests
import json
import csv
import praw
import OAuth2Util
from datetime import datetime

subreddit_url = r'https://www.reddit.com/r/{}'
traffic_url = r'https://www.reddit.com/r/{}/about/traffic/.json'
user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
current_month_number = datetime.now().month  # this is not zero indexed
current_month_name = datetime.now().strftime('%B')

# list of all the elite related subreddits
subreddits = [
    'EliteOne',
    'EliteTraders',
    'EliteExplorers',
    'EliteMiners',
    'EliteBountyHunters',
    'EliteCG',
    'EiteDagerous',
    'EliteRacers',
    'EliteWings',
    'UnknownArtefact',
    'ElitePirates',
    'FuelRats',
    'EliteAlliance',
    'EliteDangerousPics',
    'EliteOutfitters',
    'EliteCombatLoggers',
    'IridiumWing',
    'EliteCQC',
    'EliteStories',
    'Canonn',
    'EliteMahon',
    'AislingDuval',
    'EliteLavigny',
    'ElitePatreus',
    'EliteTorval',
    'EliteWinters',
    'EliteHudson',
    'kumocrew',
    'EliteSirius',
    'EliteAntal'
]

# list of the subreddits related to powerplay, to format in their own table
powerplay_subreddits = [
    'EliteMahon',
    'AislingDuval',
    'EliteLavigny',
    'ElitePatreus',
    'EliteTorval',
    'EliteWinters',
    'EliteHudson',
    'kumocrew',
    'EliteSirius',
    'EliteAntal'
]

# list of powerplay allegiances, in the same order as the powerplay subs above
powerplay_allegiances = [
    'Alliance',
    'Empire',
    'Empire',
    'Empire',
    'Empire',
    'Federation',
    'Federation',
    'Independent',
    'Independent',
    'Independent'
]

# descriptions of all the elite related subreddits, same order as the first list
subreddit_descriptions = [
    'A community for playing with other Xbox One CMDRs',
    'Everything related to Trading',
    'Share useful information, noteworthy discoveries and opportunities for collaboration',
    'Share tips, hints, guides, refinery locations, and good asteroid locations',
    'Everything related to Bounty Hunting',
    'Latest, most accurate, and professionally moderated information on Community Goals',
    'The grease trap of the Galaxy - game-related humour and shit-posting',
    'Player-organized racing community with regular weekend events and races',
    'Where you can find fellow CMDRs to fly with in the harsh galaxy',
    'Discussion, news, and theorizing for the Unknown Artefact and Large Barnacles mysteries',
    'Meet and congregate, to discuss tactics, news, trade routes, and outfits',
    'Anarchic collective dedicated to rescuing stranded CMDRs that have run out of fuel in-game',
    'Support the Alliance SuperPower',
    'Have you taken a nice picture in E:D? Post it here',
    'Suggestions and discussions on how to best outfit your ship',
    'Videos of logging out to avoid combat/death, and grounds for being put as KoS.	',
    'Escorting explorers in/out of the bubble, to protect their ships and data',
    'Everything related to CQC/Arena',
    'Stories and adventures from the Milky Way',
    'The home of science in the galaxy',
    'Edmund Mahon',
    'Aisling Duval',
    'Arissa Lavigny-Duval',
    'Denton Patreus',
    'Zemina Torval',
    'Felicia Winters',
    'Zachary Hudson',
    'Archon Delaine',
    'Li Yong-Rui',
    'Pranav Antal'
]

# list with the subreddits without a traffic link
subreddits_without_traffic = [
    'EliteDangerousPics'
]

monthly_sub_data = []
for sub_name, sub_desc in zip(subreddits, subreddit_descriptions):
    print('Getting data for: {}'.format(sub_name))
    sub_data = dict()
    sub_data['name'] = sub_name
    sub_data['url'] = subreddit_url.format(sub_name)
    sub_data['traffic_url'] = traffic_url.format(sub_name)
    sub_data['description'] = sub_desc
    if sub_name in subreddits_without_traffic:
        sub_data['uniques'] = 'N/A'
        sub_data['views'] = 'N/A'
        sub_data['bimonthly_uniques_average'] = 'N/A'
        sub_data['traffic_url'] = 'N/A'
        monthly_sub_data.append(sub_data)
        continue
    response = requests.get(url=sub_data['traffic_url'], headers={'User-agent': user_agent})
    # The response returns a list of lists
    # each sub-list is: [epoch, uniques, pageviews, subscriptions]
    data = ''
    try:
        data = response.json()
        month_data = data['month']
    except Exception as e:
        print(e)
        # Keep trying till we get the data if we get a decode error
        while data == '':
            try:
                data = response.json()
                month_data = data['month']
            except Exception as e:
                print(e)
                from time import sleep
                sleep(2)
    # sort by epoch time string, ie by month. Largest epoch is always the latest time, so it will be most frequent first
    sorted(month_data, key=lambda month: month[0])
    try:
        # access the SECOND in the list as it is now sorted by epoch time in descending order
        # the current month is always the latest epoch time
        # since we run this on the 1st of the month, to get the values fo the previous 60 days we have to get
        # the data for current month + 1 and current month + 2
        sub_data['uniques'] = month_data[0][1]
        sub_data['views'] = month_data[0][2]
        sub_data['bimonthly_uniques_average'] = (month_data[1][1] + month_data[2][1]) // 2
        monthly_sub_data.append(sub_data)
    except Exception as e:
        print(e)
        quit()

# write the csv file
csv_file_name = 'ED_subs_{}.csv'.format(current_month_name)
with open(csv_file_name, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile, quotechar='"')
    for i, sub in enumerate(monthly_sub_data):
        writer.writerow([i, sub['name'],  sub['traffic_url'], sub['uniques'], sub['views'], sub['bimonthly_uniques_average']])
    csvfile.flush()


# had to write my own sort, since sorted with passing the bimonthly average as the key was not working
def rank_by_average(given_list):
    # first separate the non-rankable subreddits
    nonrankable = [item for item in given_list if item['bimonthly_uniques_average'] == 'N/A']
    rankable = [item for item in given_list if item['bimonthly_uniques_average'] != 'N/A']
    return_list = []
    while len(rankable) > 0:
        # find the largest average
        largest_average = 0
        for item in rankable:
            if item['bimonthly_uniques_average'] > largest_average:
                largest_average = item['bimonthly_uniques_average']
        # find the dictionary with that average
        for item in rankable:
            if item['bimonthly_uniques_average'] == largest_average:
                # add it to the return list
                return_list.append(item)
                # remove it from the list
                rankable.remove(item)
                # break the loop
                break
    # add the nonrankables at the end
    return_list.extend(nonrankable)
    return return_list

# rank normal and pp separately
# rank normal by the average
normal_sub_data = [item for item in monthly_sub_data if item['name'] not in powerplay_subreddits]
normal_ranked = rank_by_average(normal_sub_data)
# rank PowerPlay subs alphabetically
pp_sub_data = [item for item in monthly_sub_data if item not in normal_sub_data]
# assign the allegiances to the powerplay ones
for sub, allegiance in zip(pp_sub_data, powerplay_allegiances):
    sub['allegiance'] = allegiance
sorted(pp_sub_data, key=lambda sub: sub['description'])

# write the markdown files separately due to different formats

# write the normal markdown file
markdown_file_name = 'ED_subs_md_{}.md'.format(current_month_name)
with open(markdown_file_name, mode='w') as mdfile:
    mdfile.write('Subreddit|Description|Popularity\n')
    mdfile.write(':-:|:-:|:-:\n')
    for sub in normal_ranked:
        sub_name_and_link = '[/r/{}]({})'.format(sub['name'], sub['url'])
        if sub['traffic_url'] != 'N/A':
            sub_visits_and_link = '[{}]({})'.format(sub['bimonthly_uniques_average'], sub['traffic_url'])
        else:
            sub_visits_and_link = 'N/A'
        mdfile.write('{}|{}|{}\n'.format(
            sub_name_and_link,
            sub['description'],
            sub_visits_and_link
        ))
    mdfile.write('\n')

# write the powerplay file
markdown_pp_file_name = 'ED_pp_subs_md_{}.md'.format(current_month_name)
with open(markdown_pp_file_name, mode='w') as mdfile:
    mdfile.write('SuperPower|Power|Subreddit|Popularity\n')
    mdfile.write(':-:|:-:|:-:|:-:\n')
    for sub in pp_sub_data:
        sub_name_and_link = '[/r/{}]({})'.format(sub['name'], sub['url'])
        sub_traffic_and_link = '[{}]({})'.format(sub['bimonthly_uniques_average'], sub['traffic_url'])
        mdfile.write('{}|{}|{}|{}\n'.format(
            sub['allegiance'],
            sub['description'],
            sub_name_and_link,
            sub_traffic_and_link
        ))
    mdfile.write('\n')

# initialise a connection to Reddit
r = praw.Reddit('bimonthly-average-traffic-script-raspberry-pi-v1-by-Always_SFW')
o = OAuth2Util.OAuth2Util(r)

# put all the values of the markdown files into a string to send as a PM
markdown_string = ''
print('Sending message')
with open(markdown_file_name, mode='r') as mdfile:
    for line in mdfile.readlines():
        markdown_string += line
markdown_string += '\n\n____\n\n'
with open(markdown_pp_file_name, mode='r') as mdfile:
    for line in mdfile.readlines():
        markdown_string += line

# send the messages
r.send_message('Always_SFW', 'Automated Elite subreddit traffic report generated on {} 1st'.format(current_month_name), markdown_string)
r.send_message('StuartGT', 'Automated Elite subreddit traffic report generated on {} 1st'.format(current_month_name), markdown_string)
