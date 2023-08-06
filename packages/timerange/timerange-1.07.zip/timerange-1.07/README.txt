Installing and using Timerange
==============================

**timerange** is a command line script to generate a range of date/times in 
various formats.
It is used to produce list of date/times that can then be passed to other
programs or used in shell/batch scripts where operations with date and times
are required. 

It can also be compiled for Windows (with py2exe_).


Installation instructions
--------------------------

Timerange is a single Python script with no external dependencies beyond
standard Python library. Installing from source is the usual::

    python setup.py install


Under Windows py2exe_ tool is used to generate singe exe binary::

    python setup.py py2exe


The resulting timerange.exe is in the dist/ folder.


Usage
=====

Getting help on the command line options::

    C:\> timerange --help
    usage: timerange [-h] [-d DEBUG_LEVEL] [-s START] [-e END] [-p PERIOD]
                     [-o OUTPUT_FORMAT] [-i INPUT_FORMAT] [-fh] [-v]
    
    timerange - generates a range of date/times in various formats
    
    optional arguments:
      -h, --help            show this help message and exit
      -d DEBUG_LEVEL, --debug DEBUG_LEVEL
                            Sets the debug level and adds debug messages to the
                            output
      -s START, --start START
                            Date to start from (format "YYYY-MM-DD", "today",
                            "+7days" or "-2hours")
      -e END, --end END     End date (format "YYYY-MM-DD", "today", "+7days" or
                            "-2days")
      -p PERIOD, --period PERIOD
                            Period term - examples: "1 hour", "-2 days", "3
                            months, 5 days"
      -o OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                            Output format string. Use --format-help option for
                            more details
      -i INPUT_FORMAT, --input-format INPUT_FORMAT
                            Input format string. Use --format-help option for more
                            details
      -fh, --format_help    Show the format strings available for date/time input
                            and output
      -v, --version         Show the version
    
    author: Todor Bukov <dev.todor@gmail.com> ver.1.06


Getting help on the input and output formats::

    
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
    

Showing today's date::

    C:\> timerange
    2012-01-29 00:00:00

    C:\> timerange.exe -s "now" -e "now, 1 sec"
    2012-01-29 11:21:10


Generating list of (relative) dates with specified period between them with
the command line option -p/--period::

    C:\> timerange -s "now" -e "tomorrow" -p "6 hours"
    2012-01-29 11:23:04
    2012-01-29 17:23:04
    2012-01-29 23:23:04
    2012-01-30 05:23:04
    2012-01-30 11:23:04


The relative dates can be combined with the tokens separated by comma::

    C:\> timerange -s "-3 days, -2 hours" -e "tomorrow, +1 day" -p "22 hours"
    2012-01-26 09:24:06
    2012-01-27 07:24:06
    2012-01-28 05:24:06
    2012-01-29 03:24:06
    2012-01-30 01:24:06
    2012-01-30 23:24:06


Generating a date range between two (absolute) dates::

    C:\> timerange -s  2012-01-01 -e 2013-01-01 -p "2 months, 2 days"
    ERROR: Could not convert the argument: '2012-01-01' using the format '%Y-%m-%d %H:%M:%S (time data '2012-01-01' does not match format '%Y-%m-%d %H:%M:%S')


The error is due to the dates being in format that is not expected by the
script. The input format may be changed using -i/--input-format option
(check the output from the -fh command option for the meaning of the format
letters)::

    C:\> timerange -s  2012-01-01 -i "%Y-%m-%d" -e 2013-01-01 -p "2 months, 2 days"
    2012-01-01 00:00:00
    2012-03-03 00:00:00
    2012-05-04 00:00:00
    2012-07-05 00:00:00
    2012-09-05 00:00:00
    2012-11-06 00:00:00


The output format can also be changed using the -o/--output-format option::

    C:\> timerange -s  2012-01-01 -i "%Y-%m-%d" -e 2013-01-01 -p "2 months, 2 days" -o "%b %d, %Y"
    Jan 01, 2012
    Mar 03, 2012
    May 04, 2012
    Jul 05, 2012
    Sep 05, 2012
    Nov 06, 2012


The dates can also be in descending order providing the period is negative::

    C:\> timerange.exe -s "tomorrow" -e "-3 days" -p "-12 hours, -5 minute, -30 secs"
    2012-01-30 11:26:10
    2012-01-29 23:20:40
    2012-01-29 11:15:10
    2012-01-28 23:09:40
    2012-01-28 11:04:10
    2012-01-27 22:58:40
    2012-01-27 10:53:10
    2012-01-26 22:47:40


If the start/end date and the period as such that it may cause infinite loop,
then an error will be thrown::

    C:\> timerange.exe -s "tomorrow" -e "yesterday" -p "12 hours"
    ERROR: The expression will never reach the final date with the given period


Making the period a negative value will make the above expression work as
expected::

    C:\> timerange.exe -s "tomorrow" -e "yesterday" -p "-12 hours"
    2012-01-30 11:29:04
    2012-01-29 23:29:04
    2012-01-29 11:29:04
    2012-01-28 23:29:04
    2012-01-28 11:29:04


Development and bug reports
===========================

The latest version of the script can be obtained from `timerange website`_.
Please report any bugs or recommendations for improvements to the author.


License
=======

The script is licensed under GNU General Public License version 3 or later
(GPLv3_).


.. _py2exe: http://www.py2exe.org/

.. _GPLv3: http://www.gnu.org/copyleft/gpl.html

.. _`timerange website`: https://bitbucket.org/todor/timerange

