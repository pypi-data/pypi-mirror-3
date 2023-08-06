trac2google
===========

This is a simple script that will read a Trac timeline RSS feed,
look for tickets and put them on a timesheet calendar in Google.

Running it the first time will create a new file in your home,
called .gcalendar. You need to fill in your google account 
details, your trac id and the name of the calendar that contains
your timesheet.

IMPORTANT: this script only processes the current month, it will 
not record timesheet entries in other months, so it is best if 
you run this in cron, daily, at some convenient hour when you've
finished your work.
