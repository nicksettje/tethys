import os
import json
from re import findall

YAHOO_DATA_RAW_DIR = '/data/yahoo/raw'

YAHOO_FIELDS = {
    'ascii_first' : 'first',
    'ascii_last' : 'last',
    'editorial_team_abbr' : 'team',
    'week' : 'byes',
    'uniform_number' : 'number',
    'position' : 'positions',
    'position_type' : 'position_types'
}

PLAYER_FILES = ['%s/%s' % (YAHOO_DATA_RAW_DIR, player_id)
                for player_id in os.listdir(YAHOO_DATA_RAW_DIR)]

def clean_yahoo(outfile='/data/yahoo/inter/players.json', overwrite=True):
    players_list = []

    for player_file in PLAYER_FILES[:100]:
        with open(player_file, 'r') as pf:
            player_dict = {val : None for val in YAHOO_FIELDS.values()}
            player_dict['yahoo_id'] = player_file.split('/')[-1]
            for line in pf:
                for field in YAHOO_FIELDS:
                    if '<%s>' % field in line:
                        if player_dict[YAHOO_FIELDS[field]] is not None:
                            if not isinstance(player_dict[YAHOO_FIELDS[field]], list):
                                player_dict[YAHOO_FIELDS[field]] = [player_dict[YAHOO_FIELDS[field]]]
                            player_dict[YAHOO_FIELDS[field]].append(findall(r'>(.+?)<', line)[0])
                        else:
                            player_dict[YAHOO_FIELDS[field]] = findall(r'>(.+?)<', line)[0]
            assert len(player_dict.keys()) == len(YAHOO_FIELDS.keys())+1
            players_list.append(player_dict)

    if overwrite or not os.path.isfile(outfile):
        with open(outfile, 'w') as df:
            json.dump(players_list, df)

if __name__ == '__main__':
    clean_yahoo()
