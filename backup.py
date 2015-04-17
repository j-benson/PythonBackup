import sys;
import getopt;
import os;
import shutil;
from datetime import datetime

# Full backup: copy every file from the source to the destination.
# Basically ctrl-c and ctrl-v the moment.

BackupFull = False;
BackupInc = False;
BackupSources = [];
BackupDestination = None;
BackupUsage = "Usage: backup.py [-f|-i] source [..] destination"

def main():
	global BackupFull;
	global BackupInc;
	global BackupSources;
	global BackupDestination;

	try:
		if len(sys.argv[1:]) == 0:
			terminate("No arguments found\n%s" % BackupUsage);

		options, args = getopt.getopt(sys.argv[1:], "fi", ["full", "inc"]);
		# options full or inc backup, args sources and last arg destination
		for o, v in options:
			if o == "-f" or o == "--full":
				BackupFull = True;
			if o == "-i" or o == "--inc":
				BackupInc = True;

		# Args will be a list of sources and the final arg will be the destination
		# build global vars and strip any trailing slashes.
		numArgs = len(args);
		for a in enumerate(args):
			if a[0] < numArgs - 1:
				BackupSources.append(a[1].rstrip('\\'));
			else:
				BackupDestination = a[1].rstrip('\\');

		# Temp Overrides #
		# BackupSources = ["D:\\python\\source"];
		# BackupDestination = "D:\\python\\backup";
		# BackupFull = True;
		##################

		# Check the options and args provided by the user.
		if (BackupFull == False and BackupInc == False) or (BackupFull == True and BackupInc == True):
			terminate("Either one of the options full (f) or inc (i) must be selected.", 1);

		## make sure paths don't end in \\
		if len(BackupSources) == 0 or BackupDestination == None:
			terminate("At least one source and a backup location is required.", 1);

		# Check source locations all exist, ignore those that don't.
		badSources = [];
		for s in BackupSources:
			if not os.path.exists(s):
				print("Source not found: %s" % s);
				badSources.append(s);
		## Remove the bad sources from the source list
		for bad in badSources:
			BackupSources.remove(bad);

		if len(BackupSources) == 0:
			terminate("No available source locations.", 1);

		# Check destination location exists, quit if it doesn't.
		if not os.path.exists(BackupDestination):
			terminate("Destination not found: %s" % BackupDestination);

	except getopt.GetoptError: #GetoptError
		terminate("Invalid option found.\n%s" % BackupUsage);

	if BackupFull:
		fullbackup();
	elif BackupInc:
		incbackup();

def fullbackup():
	# List contains an array of pairs (source filepath, array of files in source and its subdirectories)
	filepathList = [];
	for source in BackupSources:
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
				print("\r Found %i files" % numFiles, end="");

		filepathList.append((source, files));
	## use path to walk all the directories and get a list so can split the list into multiple threads.

	# Loop through the list of sources and source files
	# Copy the source to the backup location.
	permissionErrors = [];
	for source in filepathList:
		## Grab date and create new folder called Full yyyy-mm-dd put backup in there.
		newBackupDir = "%s_Full" % datetime.now().strftime("%Y-%m-%d_%H%M%S");
		# Backups go in the given backup destination, each source gets its own directory, 
		# then each backup for that source is put in a folder with the date time stamp.
		destDir = os.path.join(BackupDestination, os.path.basename(source[0]), newBackupDir);

		for fname in source[1]:		
			fnamedir = os.path.dirname(fname); # Remove the file from the path
			if len(fnamedir) == 0:
				destFileDir = destDir;
			else:
				destFileDir = os.path.join(destDir, fnamedir);

			if not os.path.exists(destFileDir):
				os.makedirs(destFileDir);
			try:
				shutil.copy2(os.path.join(source[0], fname), destFileDir); #overwrites any existing files
			except PermissionError:
				permissionErrors.append(fname);

	if len(permissionErrors) > 0:	
		print("Files not copied: Permission denied:");		
		for pErr in permissionErrors:
			print(" %s" % pErr);

def incbackup():
	pass;

def terminate(message, code = 0):
	print(message);
	#input("\nPress enter to exit...");
	sys.exit(code);


main();

## Maybe add an option to keep the command window open after option is complete.
#input("Press enter to exit");