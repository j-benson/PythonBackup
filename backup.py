import os;
import shutil;
from datetime import datetime

# Full backup: copy every file from the source to the destination.
# Basically ctrl-c and ctrl-v the moment.

backupSources = ["D:\\python\\source"];
backupDestination = "D:\\python\\backup";
## make sure they don't end in \\

# List contains an array of pairs (source filepath, array of files in source and its subdirectories)
filepathList = [];
for source in backupSources:
	print("Scanning %s..." % source);
	files = [];
	numFiles = 0;
	# Build a list of all the filenames in the source and its subdirectories
	for (path, dirnames, filenames) in os.walk(source):
		relativePath = path[len(source):] # Remove the source filepath leaving only a relative path to the file.
		if relativePath.startswith(os.sep):
			relativePath = relativePath[1:]; # remove leading path sep \

		for fname in filenames:
			files.append(os.path.join(relativePath, fname));
			numFiles += 1;
			print("\rFound %i files" % numFiles, end="");

	filepathList.append((source, files));
## use path to walk all the directories and get a list so can split the list into multiple threads.

# Loop through the list of sources and source files
# Copy the source to the backup location.
for source in filepathList:
	## Grab date and create new folder called Full yyyy-mm-dd put backup in there.
	newBackupDir = "%s_Full" % datetime.now().strftime("%Y-%m-%d_%H%M%S");
	# Backups go in the given backup destination, each source gets its own directory, 
	# then each backup for that source is put in a folder with the date time stamp.
	destDir = os.path.join(backupDestination, os.path.basename(source[0]), newBackupDir);

	for fname in source[1]:		
		fnamedir = os.path.dirname(fname); # Remove the file from the path
		if len(fnamedir) == 0:
			destFileDir = destDir;
		else:
			destFileDir = os.path.join(destDir, fnamedir);

		if not os.path.exists(destFileDir):
			os.makedirs(destFileDir);
		shutil.copy2(os.path.join(source[0], fname), destFileDir); #overwrites any existing files