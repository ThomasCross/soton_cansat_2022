from datetime import datetime
import time


def update_time(unix_time_as_string):
    clk_id = time.CLOCK_REALTIME
    time.clock_settime(clk_id, float(unix_time_as_string))

def get_time():
    return time.time()

def diff_time():
    mission_time = 1591105781

    print(datetime.fromtimestamp(mission_time).strftime('%Y-%m-%d %H:%M:%S'))

    diff = time.time() - mission_time

    print(datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

    print(datetime.utcfromtimestamp(diff).strftime('%Y-%m-%d %H:%M:%S'))

    return datetime.utcfromtimestamp(diff).strftime('%H:%M:%S')


print(datetime.fromtimestamp(get_time()).strftime('%Y-%m-%d %H:%M:%S'))
update_time("1591109442")
#print(datetime.fromtimestamp(get_time()).strftime('%Y-%m-%d %H:%M:%S'))
#update_time("1591105781")
print(diff_time())