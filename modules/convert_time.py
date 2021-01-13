import datetime
import time

def ms_to_struct(ms):
    """Converts Unix time (milliseconds since epoch) to the time.struct_time.

    ms (number): milliseconds since epoch,can be in string form since int() is used on it first
    """
    ms = int(ms)
    return time.gmtime(ms/1000.)

def struct_to_ms(struct):
    """Converts time.struct_time to Unix time (milliseconds since epoch)

    struct (time.struct_time object): the time.struct_time object to be converted
    """
    # copied from several stackoverflow - comments are just what I assume happens

    # convert struct to datetime since apparently you can't convert it directly? or at least no one ever asked on stackoverflow about it
    dt = datetime.datetime.fromtimestamp(time.mktime(struct))
    # get epoch in datetime format
    epoch = datetime.datetime.utcfromtimestamp(0)
    # subtract epoch from our converted datetime so we get the time since epoch, then get seconds and multiply by 1000 to convert to milliseconds
    return (dt - epoch).total_seconds() * 1000.0

def get_current_time():
    current = datetime.datetime.now()
    return current.timetuple()