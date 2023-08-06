#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
timerange - generates a range of date/times in various formats

@author: Todor Bukov <todor.bukov@gmail.com>
@LICENSE: GPLv3

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import print_function
import argparse
import string
import sys
import datetime
import traceback

# some global variables
APPNAME = "timerange"
AUTHOR = "Todor Bukov"
AUTHOR_EMAIL = "Todor Bukov <dev.todor@gmail.com>"
VERSION = '1.07'
# Licensed under GPL v.3 or later
LICENSE = "GNU General Public License (GPL)"

DEBUG_LEVEL = 0
DEFAULT_FORMAT = '%Y-%m-%d %H:%M:%S'

# Let's define some constants that will be used later
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY
MONTH = 30 * DAY # I know this is cheating, but it on average 1 month = 30 days
YEAR = 365 * DAY
LEAP_YEAR = 366 * DAY

calendar_ranges = {
    'second'    :   SECOND,
    'minute'    :   MINUTE,
    'hour'      :   HOUR,
    'day'       :   DAY,
    'week'      :   WEEK,
    'month'     :   MONTH,
    'year'      :   YEAR,
    'leap_year' :   LEAP_YEAR,
    # and some abbreviations
    'sec'       :   SECOND,    
    'hr'        :   HOUR,
#    'w'         :   WEEK,
#    'd'         :   DAY
}


# now absolute datetimes
NOW         = datetime.datetime.now()
TODAY       = NOW.replace(hour=0, minute=0, second=0)

tdelta_abbr = {
    'now'       : datetime.timedelta(seconds=0),
    # NOW + "today" = TODAY (NOW is used as the base in the computations below)
    'today'     : -(NOW - TODAY),
    'yesterday' : datetime.timedelta(seconds=-DAY),
    'tomorrow'  : datetime.timedelta(seconds=DAY)
}

timeline_sign = {
    'ago': -1,
    'in the past' : -1,
    'from now': 1,
    'from today': 1
    }

# ----
datetime_format_help = """
Available arguments for the date/time format options (-i/-o)

%a 	Locale's abbreviated weekday name. 	 
%A 	Locale's full weekday name. 	 
%b 	Locale's abbreviated month name. 	 
%B 	Locale's full month name. 	 
%c 	Locale's appropriate date and time representation. 	 
%d 	Day of the month as a decimal number [01,31]. 	 
%H 	Hour (24-hour clock) as a decimal number [00,23]. 	 
%I 	Hour (12-hour clock) as a decimal number [01,12]. 	 
%j 	Day of the year as a decimal number [001,366]. 	 
%m 	Month as a decimal number [01,12]. 	 
%M 	Minute as a decimal number [00,59]. 	 
%p 	Locale's equivalent of either AM or PM. 	(1)
%S 	Second as a decimal number [00,61]. 	(2)
%U 	Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0. 	(3)
%w 	Weekday as a decimal number [0(Sunday),6]. 	 
%W 	Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0. 	(3)
%x 	Locale's appropriate date representation. 	 
%X 	Locale's appropriate time representation. 	 
%y 	Year without century as a decimal number [00,99]. 	 
%Y 	Year with century as a decimal number. 	 
%Z 	Time zone name (no characters if no time zone exists). 	 
%% 	A literal '%' character.

Notes:

(1) When used with the strptime() function, the %p directive only affects the output hour field if the %I directive is used to parse the hour.
(2) The range really is 0 to 61; this accounts for leap seconds and the (very rare) double leap seconds.
(3) When used with the strptime() function, %U and %W are only used in calculations when the day of the week and the year are specified.

Examples:
"%Y%-m-%d" results in something like "2012-01-01" (the actual date depends on the other parameters).

Dates can also be defined as relative to the current date/time using sign i.e. "+" and "-" or by using the keywords "from now" and "ago".

List of relative keywords:
- "now" - refers to the current time on the system
- "today" - same as "now", but with the time part zeroed (i.e. 00:00:00)
- "yesterday" - same as "now, -1 day"
- "tomorrow" - same as "now, +1 day"
- "ago" - refers to the period in the past e.g. "1 day ago" is the same as "-1 day"
- "from now" - refers to the period in the future (this is the default) e.g. "1 day", "+1 day", "1 day from now" are all the same.

Examples:
"1 day ago", "2 weeks from now", "-1 hour", "+2 minutes", "today", "tomorrow"

When using relative dates more than one keyword can be provided, seprated by comma.
Examples:
"1 day, 2 hours, 3 minutes" or "-3 days, -2 seconds"

NOTE: Combinations of keywords can sometimes lead to confusing results i.e. "+3days, -1 hour, 2 minutes ago". 
These combinations are additive and the final results is the sum of the results yelded by the individual keywords.
"""

# ---
def print_debug(*args):
    global DEBUG_LEVEL
    
    if DEBUG_LEVEL > 0:
        print("%DEBUG%: ",*args)

# ---
def logerror(ex, exit_code=1):
    global DEBUG_LEVEL
    
    print("ERROR: " + str(ex))
    if DEBUG_LEVEL > 1:
        print("\nStack trace:")
        traceback.print_exc()
    sys.exit(exit_code)
    
# ---
def setup_args():
    parser = argparse.ArgumentParser(
    description=
        "timerange - generates a range of date/times in various formats",
    epilog='author: ' + AUTHOR + ' ver.' + VERSION
)
    parser.add_argument(
        '-d','--debug',
        action='store',
        dest='debug_level',
        type=int,
        default=0,
        help='Sets the debug level and adds debug messages to the output'
        )
    parser.add_argument(
        '-s','--start',
        action='store',
        default='today',
        help='Date to start from (format "YYYY-MM-DD", "today", "+7days" or "-2hours")'
        )
    parser.add_argument(
        '-e','--end',
        action='store',
        default='today, +1 second',
        help='End date (format "YYYY-MM-DD", "today", "+7days" or "-2days")'
        )
    parser.add_argument(
        '-p','--period',
        action='store',
        default='1 day',
        help='Period term - examples: "1 hour", "-2 days", "3 months, 5 days"'
        )
    parser.add_argument(
        '-o','--output-format',
        action='store',
        dest='output_format',
        default=DEFAULT_FORMAT,
        help='Output format string. Use --format-help option for more details'
        )
    parser.add_argument(
        '-i','--input-format',
        action='store',
        dest='input_format',
        default=DEFAULT_FORMAT,
        help='Input format string. Use --format-help option for more details'
        )
        
    parser.add_argument(
        '-fh','--format_help',
        action='store_true',
        help='Show the format strings available for date/time input and output'
    )
    parser.add_argument(
        '-v','--version',
        action='store_true',
        help='Show the version'
    )

    return parser

# ---
def parse_timedelta(args):
    """
    Convert argument like "+1 year, +2 months and -1 day" to valid 
    datetime.timedelta result (there can be multiple arguments, separated
    by comma).
    """
    print_debug("  parse_timedelta argument:", args)
    
    result = datetime.timedelta(seconds=0)
    
    dt = args.lower().strip()
    # remove "and" from the text and replace it with comma
    dt = dt.replace('and',',')
    for val in dt.split(','):
        val = val.strip()
        if val != '':
            result = result + parse_token(val)
    return result

# ---
def parse_token(arg):
    """
    Converts a single argument like "+2 days", "-3 months" or "5 years" into a
    valid datetime.timedelta (see Python library Reference for details) object.
    """
    
    result = None

    print_debug("    parse_token argument:", arg)

    dt_sign = 1
    dt_number = 0
    dt_range = 0
    
    # put the string into canonical form first
    dt = str(arg).lower().strip()

    # is the string a convenient abbreviation like "tomorrow"?
    if dt in tdelta_abbr:
        result = tdelta_abbr.get(dt)
        # short circuit the rest of the function
        return result
    
    # strip the leading sign if one exists
    if dt.startswith('-'):
        dt_sign = -1
        dt = dt[1:]
    elif dt.startswith('+'):
        dt = dt[1:]

    # check for the presense of the word "ago" and "from now" and change the
    # sign accordingly    
    for key in timeline_sign:
        if dt.find(key) >= 0:
            dt_sign = timeline_sign[key]
            dt = dt.replace(key,'').strip()
    
    # strip the final 's' in 'years', 'months', 'days', etc.
    if dt.endswith('s'):
        dt = dt[:-1]
    
    # now separate the numbers from the text
    dt_digits_list = []
    dt_digits_index = 0
    for symbol in dt:
        if symbol in string.digits:
            dt_digits_list.append(symbol)
            dt_digits_index += 1
        else:
            break # exit the loop on the first occurence of non-digit symbol

    # now attempt convert the string into a number
    dt_number_str = "".join(dt_digits_list)

    # some sanity checks    
    if dt_number_str == '':
        raise Exception("Missing number provided in token: "+ arg)

    try:
        dt_number = int(dt_number_str)
    except ValueError as ex:
        err_msg = 'Error while converting to number: ' + str(dt_number_str)
        raise Exception(err_msg + " (" + str(ex) + ")")

    # now attempt to decode the range - days, months, etc.
    dt_range_str = dt[dt_digits_index:]
    dt_range_str = dt_range_str.strip() # remove any extra _leading_ spaces
    dt_range = calendar_ranges.get(dt_range_str,None)
    if dt_range is None:
        err_msg = 'No valid range provided: ' + dt_range_str + "\n"
        err_msg += "Valid ranges: " + "(s),".join(calendar_ranges.keys() + [''])
        raise Exception(err_msg)
    
    result_seconds = dt_sign * dt_number * dt_range
    result = datetime.timedelta(seconds=result_seconds)
    return result

# ---
def parse_absolute_datetime(arg, fmt):
    """
    Parses the date in absolute format either as
    YYYY-MM-DD_HH:MM:SS (with the time) or as in ISO format 8601 like 
    YYYY-MM-DDTHH:MM:SS (with "T" separator between the date and the time)
    or as YYYY-MM-DD (just the date) and returns "datetime.dateime" object.
    """
    
    result = None
    arg = str(arg).strip().lower()

    try:
        result = datetime.datetime.strptime(arg, fmt)
    except ValueError as ex:
        err_msg = "Could not convert the argument: '" + arg + \
        "' using the format '" + fmt + " (" + str(ex) + ")"
        raise Exception(err_msg)
    return result 

# ---
def looks_like_timedelta(arg):
    """
    Attempt to guess if the provided argument is a free form text instead of
    a date in specific format.
    """
    result = False
    for symbol in arg.lower():
        # "T" is used as a separator in ISO 8601
        if (symbol in string.letters) and not (symbol == 't'):
            result = True
            break
    return result

# ---
def parse_arg(arg, input_format=DEFAULT_FORMAT):
    """
    Parses the input arguments, try to find out if it is "relative" (i.e. free
    text, plain english format) or "absolute" (i.e. provided in a specific 
    format)
    """
    result = NOW

    # some cleanups first
    dt = str(arg).lower().strip()
    
    # remove any leading/trailing quotes and other enclosures
    wrappers =['\'', '"',']','[','(',')']
    if dt[0] in wrappers:
        dt = dt[1:]
    if dt[-1] in wrappers:
        dt = dt[:-1]
    # remove any further leading/trailing spaces
    dt = dt.strip()

    if looks_like_timedelta(arg):
        result = NOW + parse_timedelta(arg)
        print_debug("  computing the timedelta: ",result)
    else:
        result = parse_absolute_datetime(arg, input_format)
        print_debug("  absolute date: ",result)
    return result

# ---
def gen_datetime_range(date_from, date_till, period, 
                       input_format, output_format):
    """
    Generates a range of dates/times in the specified format.
    - "date_from" and "date_till" are datetime.datetime objects
    - "period" is in datetime.timedelta object
    - "input_format" and "output_format" are text strings in 
       datetime.strftime() format
    """
    zero_timedelta = datetime.timedelta(0)
    
    if (date_from < date_till and period < zero_timedelta) or \
       (date_from > date_till and period > zero_timedelta):
        err_msg = "The expression will never reach the final date with the given period"
        raise Exception(err_msg)
    elif date_from == date_till:
        # if the start and the end are the same, then return an empty list
        return []
    
    result_dt = []
    current_date = date_from
    
    if date_from < date_till:
        # ascending date/time
        while current_date <= date_till:
            result_dt.append(current_date)
            current_date = current_date + period
    else:
        # descending date/time
        while current_date >= date_till:
            result_dt.append(current_date)
            current_date = current_date + period    
            
    # now convert the range of date/times into the specifieid text format
    try:
        result_str = [item.strftime(output_format) for item in result_dt]
    except ValueError as ex:
        err_msg = "Ivalid output format: '" + output_format + "'" + \
        " (" + str(ex) + ")"
        raise Exception(err_msg)
    return result_str

# ---
def main():
    global DEBUG_LEVEL
    
    parser = setup_args()
    arguments = parser.parse_args()
    
    DEBUG_LEVEL = arguments.debug_level
    print_debug("arguments", arguments)
    
    if arguments.format_help:
        print(datetime_format_help)
        sys.exit(0)
    
    if arguments.version:
        print(APPNAME + ' ver. ' + VERSION + '  author: ' + AUTHOR)
        sys.exit(0)
    
    start_dt = parse_arg(arguments.start, arguments.input_format)
    end_dt = parse_arg(arguments.end, arguments.input_format)
    period_dt = parse_timedelta(arguments.period)
    
    print_debug("start date:    ",start_dt, type(start_dt))
    print_debug("end date:      ",end_dt, type(end_dt))
    print_debug("period:        ",period_dt, type(period_dt))
    print_debug("input format:  ",arguments.input_format)
    print_debug("output format: ",arguments.output_format)
    
    results = gen_datetime_range(start_dt,
                                 end_dt,
                                 period_dt,
                                 arguments.input_format,
                                 arguments.output_format,)
    for res in results:
        print(res)

if __name__ == "__main__":
    # NOTE:   
    # datetime.datetime.strftime() generates ValueError for invalid format strings
    try:
        main()
    except Exception as ex:
        logerror(ex)

