
baklabel is designed for use in automated scripts to deliver a sensible
directory path fragment (or label) each day to construct a grandfathered
local backup destination. It can also be run as a stand-alone utility to
find the backup label produced for any given date and set of options.

Run  baklabel.py -h  to see command line usage options.

Call baklabel directly or import it and produce labels from your code.

Python 2.6, 2.7 and 3.x

In the docs directory after installing, see release_note.txt for more
detail on the package, instructions.txt for baklabel output examples and
backup_howto.txt for a complete example backup script for Windows.

Properly grandfathered, there needs to be a daily backup to one of 23
separate tapes, sets of media or local directories on a storage device.
This complement is made up of 6 weekday backups, 5 week backups and 12
month backups. 23 backups is quite economical for 12 months coverage.

This provides a stream of untouched backups for at least seven days plus
the ability to go back four or five Fridays plus having monthly snapshots
going back for twelve months. This represents real comfort when retrieving
data which has been compromised at some unknown point in the past.

Source:  Userid is 'public' with no password.
http://svn.pczen.com.au/repos/pysrc/gpl3/baklabel/distrib/

Mike Dewhirst
miked@dewhirst.com.au
