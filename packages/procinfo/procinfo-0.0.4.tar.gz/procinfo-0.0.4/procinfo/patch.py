#! -*- coding: utf-8 -*-

import psutil

FACTOR = 1024.0  # This value is used for converting kB to MB , MB to GB
MEMORY_UNITS = ['B', 'KB', 'MB', 'GB', 'TB']


def return_human_readable(value, unit=0):
    if value < FACTOR:
        return {'value': round(value, 2), 'str': ' '.join([str(round(value, 2)), MEMORY_UNITS[unit]])}
    elif value == FACTOR:
        temp = round(value / FACTOR, 2)
        return {'value': temp, 'str': ' '.join([str(temp), MEMORY_UNITS[unit]])}
    elif value > FACTOR:
        return return_human_readable(value / FACTOR, unit + 1)


TOTAL_MEMORY = return_human_readable(psutil.TOTAL_PHYMEM)
