
import datetime
import time
from merge_names_in_files import merge_files
from helper_functions import do_work
from helper_functions import how_much_to_sleep
from helper_functions import get_curr_folder_name
from helper_functions import get_needed_event_by_curr_date
from helper_functions import get_event_name_by_curr_date
from helper_functions import get_result_file_name

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



# Schedule: Thursday, 19:40 - 20:05, Saturday, 19:40 - 20:30, 21:30 - 22:30, Sunday, 19:40-20:30, 21:40 - 22:30
def main_loop():
    print("Let's start!")
    in_process = False
    while True:
        next_sleep = how_much_to_sleep()
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