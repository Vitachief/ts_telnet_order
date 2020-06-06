from telnetlib import Telnet
from collections import namedtuple
import re
import datetime
import os
import time
from merge_names_in_files import merge_files
from merge_names_in_files import EventType
import configparser


# Tools -> Options -> Addons -> ClientQuery -> Settings
#apikey=b'LKFS-098M-WMQO-N89U-MV2Z-LUUD'
# auth apikey=BB8V-9NWV-TD71-MJ19-AYBO-2DZN
# channelclientlist -groups cid=
# channelclientlist -groups cid=3137
# Мурровская тс - cid=9958
# channelclientlist -groups cid=9962

# channelclientlist -uid -groups cid=20087
# clid=4175 cid=20087 client_database_id=62097 client_nickname=Фырыпыры client_type=0 client_unique_identifier=j9z9kh1nB9JOkmQYtamWmzPeik8= client_servergroups=1703,1722,2107 client_channel_group_id=410

# serverconnectinfo
# ip=drakon.pw port=6000

# Рема: 505
# ТВ: 653
# МБГ, Садик: 3137

ChanInfo = namedtuple('ChanInfo', ['cid', 'pid', 'name', 'client_count'])
ClientInfo = namedtuple('ClientInfo', ['clid', 'client_db_id', 'nickname', 'client_servergroups', 'uid', 'cid'])

print('Reading config...')
def read_config():
    channels_section = 'Channels'
    general_section = 'General'
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Reading interested channels
    interested_chans = {}
    for key in config[channels_section]:
        interested_chans[config[channels_section][key]] = key
    return (config[general_section]['apikey'], config[general_section]['server_group'], config[general_section]['target_folder'], interested_chans)


(apikey_str, server_group, target_folder, interested_channels) = read_config()
apikey = apikey_str.encode()
print('Reading config done')

def create_folders(folders_list):
    for folder in folders_list:
        os.makedirs(folder, exist_ok=True)


#interested_channels = {'505': 'Ремесло', '653': 'ГвГ', '3137': 'МБГ_Садеман'}
# order_group = '85' # Order TS
# murr_group = '220' # Order TS
# order_group = '2107' # Murr TS
# interested_channels = {'9962': 'Садик'} #Murr ts
# interested_channels = {'9962': 'ремесло'} #Murr ts



def print_client_info(filename: str, info_list):
    with open(filename, 'a', encoding='utf8') as fout:
        for info in info_list:
            fout.write('clid: {}, client_db_id: {}, nick: {}, client_servergroups:{}\n'.format(info.clid,
                                                                                               info.client_db_id,
                                                                                               info.nickname,
                                                                                               info.client_servergroups))


def print_chan_info(filename, chan_info_list):
    with open(filename, 'w+', encoding='utf8') as fout:
        for chan_info in chan_info_list:
            fout.write('Name: {}, cid: {}, pid: {}\n'.format(chan_info.name, chan_info.cid, chan_info.pid))


def print_ts_list(filename: str, unformatted_str: str):
    info_list = unformatted_str.split('|')
    with open(filename, 'w+', encoding='utf8') as fout:
        for info_str in info_list:
            fout.write('{}\n'.format(info_str))


# clientlistid -uid: clid=15049 cid=15469 client_database_id=36516 client_nickname=Nyona client_type=0 client_unique_identifier=iGAJLCWKY\/TT+0UrhsvBJE329co=|
# clid=12869 cid=595 client_database_id=20757 client_nickname=Император client_type=0 client_servergroups=85,93,134 client_channel_group_id=42|
# clid=4175 cid=20087 client_database_id=62097 client_nickname=Фырыпыры client_type=0 client_unique_identifier=j9z9kh1nB9JOkmQYtamWmzPeik8= client_servergroups=1703,1722,2107 client_channel_group_id=410
def parse_client_info(info_str: str):
    clid = ''
    clid_match = re.findall('clid=([\d]*)', info_str)
    if len(clid_match) > 0:
        clid = clid_match[0]

    cl_db_id = ''
    cl_db_id_match = re.findall('client_database_id=([\d]*)', info_str)
    if len(cl_db_id_match) > 0:
        cl_db_id = cl_db_id_match[0]

    nickname = ''
    nickname_match = re.findall('client_nickname=(.*)\sclient_type', info_str)
    if len(nickname_match) > 0:
        nickname = nickname_match[0]

    serv_group_list = []
    serv_group_match = re.findall('client_servergroups=(.*)\sclient_channel_group_id', info_str)
    if len(serv_group_match) > 0:
        serv_group_list = serv_group_match[0].split(',')

    uid = ''
    uid_match = re.findall('client_unique_identifier=(.*)\sclient_servergroups', info_str)
    if len(uid_match) > 0:
        uid = uid_match[0]

    cid = ''
    cid_match = re.findall('cid=(.*)\sclient_database', info_str)
    if len(uid_match) > 0:
        cid = cid_match[0]

    return ClientInfo(clid, cl_db_id, nickname, serv_group_list, uid, cid)


# clid=12869 cid=595 client_database_id=20757 client_nickname=Император client_type=0 client_servergroups=85,93,134 client_channel_group_id=42|c
# 85 - order servergroup
def clients_by_group(unformat_str: str, client_group: str, debug_folder: str):
    # clid=14212 cid=665 client_database_id=2875 client_nickname=BendeR client_type=0 client_servergroups=85,97,134 client_channel_group_id=42|
    # client_nickname (.*) clienttype
    #client_servergroups=85,95,134 client_servergroups=85,102,134 client_channel_group_id
    info_list = unformat_str.split('|')
    # print("Getting clients from: {}".format(unformat_str))
    result_list = []
    skipped_list = []
    all_clients_info = []
    for info_str in info_list:
        if len(info_str) == 0:
            continue
        serv_group_match = re.findall('client_servergroups=(.*)\sclient_channel_group_id', info_str)
        if len(serv_group_match) > 0:
            all_clients_info.append(parse_client_info(info_str))
            serv_groups_list = serv_group_match[0].split(',')
            is_order = False
            for group in serv_groups_list:
                if group == client_group:
                    is_order = True
                    break
            if not is_order:
                print("not order's guy: {}".format(info_str))
                skipped_list.append(info_str)
                continue
        else:
            print('wtf with serv_groups? {}'.format(info_str))

        nickname_match = re.findall('client_nickname=(.*)\sclient_type', info_str)
        if len(nickname_match) > 0:
            result_list.append(nickname_match[0])
            print('Adding... {}'.format(nickname_match[0]))
        else:
            print('wtf with nickname? {}'.format(info_str))

    print_ts_list('{}\\{}_{}_skipped_clients.txt'.format(debug_folder, curr_date, datetime.datetime.now().strftime('%H-%M-%S')), '|'.join(skipped_list))
    print_client_info('{}\\{}_{}_all_clients_info.txt'.format(debug_folder, curr_date, datetime.datetime.now().strftime('%H-%M-%S')), all_clients_info)
    return result_list


def parse_chan_info(unformat_str: str):
    info_list = unformat_str.split('|')
    cid = None
    pid = None
    chan_name = None
    result_list = []
    for info_str in info_list:
        cid_match = re.findall('cid=([\d]*)', info_str)
        if len(cid_match) > 0:
            cid = cid_match[0]
        else:
            print('wtf with cid? {}'.format(info_str))

        pid_match = re.findall('pid=([\d]*)', info_str)
        if len(pid_match) > 0:
            pid = pid_match[0]
        else:
            print('wtf with pid? {}'.format(info_str))

        chan_match = re.findall('channel_name=(.*)\schannel_flag', info_str)
        if len(chan_match) > 0:
            chan_name = chan_match[0]
        else:
            print('wtf with channame? {}'.format(info_str))

        channel_info = ChanInfo(cid, pid, chan_name, 0)
        result_list.append(channel_info)
    return result_list


def get_children_list(chan_list, initial_channel):
    was_added = True
    result_list = [initial_channel]
    print(chan_list)
    while was_added:
        was_added = False
        for chan in chan_list:
            if chan.pid in result_list and not chan.cid in result_list:
                was_added = True
                print('adding ' + chan.name)
                result_list.append(chan.cid)
    return result_list


def parse_clientlist_req(unformat_str: str):
    result_list = []
    info_list = unformat_str.split('|')
    for info_str in info_list:
        result_list.append(parse_client_info(info_str))
    return result_list


def get_curr_folder_name():
    curr_date = datetime.datetime.now().strftime('%Y-%m-%d')
    return target_folder+curr_date


# 2107
def do_work():
    target_folder_curr = get_curr_folder_name()
    debug_folder = "{}\\script_logs".format(target_folder_curr)
    curr_time = datetime.datetime.now().strftime('%H-%M-%S')
    filename = '{}\\{}'.format(target_folder_curr, curr_time)
    create_folders({debug_folder, target_folder_curr})
    with Telnet('localhost', 25639) as ts:
        print("Authenticating...")
        ts.write(b'auth apikey=' + apikey + b'\n')
        auth_answ = ts.read_until(b'neverhappen', 1).decode('utf8')
        print("Done with answ {}".format(auth_answ))
        ts.write(b'channellist\n')
        chanlist_answ = ts.read_until(b'\n', 8).decode('utf-8').replace('\\s', ' ')
        # cid=341 pid=1099 channel_order=2109 channel_name=freestyle channel_flag_are_subscribed=1 total_clients=0|
        ts.read_very_eager()
        #print('chanlist_answ: {}'.format(chanlist_answ))

        chan_info_list = parse_chan_info(chanlist_answ)
        print_chan_info('{}\\channelslist_formatted.txt'.format(debug_folder), chan_info_list)
        print_ts_list('{}\\channelslist.txt'.format(debug_folder), chanlist_answ)

        # Get all clients list
        ts.write(b'clientlist -uid -groups\n')
        connected_clients_list = ts.read_until(b'\n', 8).decode('utf-8').replace('\\s', ' ')
        print_ts_list('{}\\clients_unformatted-all.txt'.format(debug_folder), connected_clients_list)
        connected_clients_struct = parse_clientlist_req(connected_clients_list)

        for first_chan in interested_channels.keys():
            parent_chanlists = get_children_list(chan_info_list, first_chan)
            print(parent_chanlists)
            with open('{} {}.txt'.format(filename, interested_channels[first_chan]) , "w+", encoding="utf8") as fout:
                for client in connected_clients_struct:
                    if client.cid in parent_chanlists:
                        if server_group in client.client_servergroups:
                            fout.write('{}\n'.format(client.nickname))
                            print(client)


def how_much_to_sleep():
    #return 0
    curr_time = datetime.datetime.now()
    if curr_time.weekday() in [3, 5, 6]:
        if curr_time.hour in [19, 21] and curr_time.minute >= 40 \
            or curr_time.hour in [20, 22] and curr_time.minute <= 30:
            return 0
    return 60


def get_event_name_by_curr_date():
    curr_time = datetime.datetime.now()
    if curr_time.weekday() == 3 and curr_time.hour == 20:
        return 'Ремесло'
    elif curr_time.weekday() == 3 and curr_time.hour == 22:
        return 'ГвГ'
    elif curr_time.weekday() == 5:
        return 'МБГ_Садеман'
    elif curr_time.weekday() == 6:
        return 'ГвГ'


def get_needed_event_by_curr_date():
    curr_time = datetime.datetime.now()
    if curr_time.hour == 20:
        return EventType.Near20
    elif curr_time.hour == 22:
        return EventType.Near22
    return EventType.Near22


def get_result_file_name():
    res_string = 'merged'
    curr_time = datetime.datetime.now()
    if curr_time.hour == 20:
        res_string += '_20'
    elif curr_time.hour == 22:
        res_string += '_22'
    res_string += '.txt'
    return res_string


# Schedule: Thursday, 19:40 - 20:05, Saturday, 19:40 - 20:30, 21:30 - 22:30, Sunday, 19:40-20:30, 21:40 - 22:30
def main_loop():
    print("Let's start!")
    in_process = False
    while True:
        next_sleep = 0#how_much_to_sleep()
        if next_sleep == 0:
            print('Start working')
            in_process = True
            do_work()
            print('{} Sleeping for 60'.format(datetime.datetime.now()))
            time.sleep(60)
        else:
            if in_process:
                in_process = False
                try:
                    merge_files(get_curr_folder_name(), get_needed_event_by_curr_date(), get_event_name_by_curr_date(), get_result_file_name())
                except:
                    print('Was exception while merging')
            print('{} Out of working hours, sleeping for {}'.format(datetime.datetime.now(), next_sleep))
            time.sleep(next_sleep)

print('Starting main loop...')
main_loop()