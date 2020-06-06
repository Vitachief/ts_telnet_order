from helper_functions import connect_and_print_chan_list
from helper_functions import get_clients
import re

while True:
    print('Please enter a command, help for list of options')
    input_str = input()
    if 'exit' == input_str:
        break
    if 'help' == input_str:
        print('exit help channels users')
    elif 'channels' == input_str:
        connect_and_print_chan_list()
    elif 'users' in input_str:
        re.search('[0-9]+', input_str).group()
        chan_num = re.search('[0-9]+', input_str).group()
        print('Getting clients of chan {}'.format(chan_num))
        get_clients(chan_num)


