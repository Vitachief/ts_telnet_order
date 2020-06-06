import os
from enum import Enum
import datetime
import re
import shutil
from datetime import timedelta


def copy_to_folders(root_folder):
    for filename in os.listdir(root_folder):
        fullpath = '{}\\{}'.format(root_folder, filename)
        if os.path.isdir(fullpath):
            print('skipping folder {}'.format(filename))
            continue
        if os.stat(fullpath).st_size == 0:
            print('removed zero-sized file({})'.format(filename))
            os.remove(fullpath)
            continue
        event_date = re.search(r'\d\d\d\d-\d\d-\d\d', filename)
        if event_date:
            target_folder = '{}\\{}'.format(root_folder, event_date.group(0))
            os.makedirs(target_folder, exist_ok=True)
            new_filename = '{}\\{}'.format(target_folder, ''.join(filename.split(event_date.group(0)+' ')))
            shutil.move(fullpath, new_filename)
        else:
            print("not matched {}".format(filename))


class EventType(Enum):
    Near20 = 1
    Near22 = 2


def merge_files(path: str, needed_event, event_name: str, output_file_name='merged.txt'):
    nicknames_list = []

    # Read data
    needed_time_str = '20:00'
    if needed_event == EventType.Near22:
        needed_time_str = '22:00'
    needed_time = datetime.datetime.strptime(needed_time_str, '%H:%M')
    start_delta = needed_time - timedelta(minutes=30)
    end_delta = needed_time + timedelta(minutes=15)
    for filename in os.listdir(path):
        event_time_search = re.search(r'\d\d-\d\d', filename)
        fullpath = '{}\\{}'.format(path, filename)
        if event_time_search and event_name in filename:
            event_time_obj = datetime.datetime.strptime(event_time_search.group(0), '%H-%M')
            if event_time_obj >= start_delta and event_time_obj <= end_delta:
                with open(fullpath , "r", encoding="utf8") as fin:
                    for line in fin:
                        if line not in nicknames_list:
                            nicknames_list.append(line)
        else:
            print("Skipping {}, not containing {} ".format(fullpath, event_name))
    # generating new file
    result_file = '{}\\{}'.format(path, output_file_name)
    with open(result_file, "w+", encoding="utf8") as fout:
        for item in nicknames_list:
            fout.write('{}'.format(item))

#merge_files('D:\\order_activity\\2020-03-19', EventType.Near20, 'Ремесло', output_file_name='merged_Ремесло.txt')
# merge_files('D:\\order_activity\\2020-03-21', EventType.Near20, 'МБГ', output_file_name='merged_МБГ.txt')
# merge_files('D:\\order_activity\\2020-03-21', EventType.Near22, 'Садеман', output_file_name='merged_Садеман.txt')
# merge_files('D:\\order_activity\\2020-03-15', EventType.Near20, 'ГвГ', output_file_name='merged_ГвГ.txt')


