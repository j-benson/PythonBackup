# Python Backup Change Log
#### Version 0.3.0 - 05/08/2015
    Full backup and increment functionality added.

    Many sources can be added to be backed up to one location, the source
    directory name is used as the backup name. Inside each backup are the backup
    versions named by the date, the type of backup and the version number.

    Full backups copy all files from the source location to the backup location
    and increments copy the files to the new increment only if the
    date modified is newer than it is in the previous increments or the full backup.
