"""Python Backup
A python script to provide both full and incremental backups from a number of
sources to a destination. Full backups copy all files from the source location
to the backup location and increments copy the files to the new increment only if the
date modified is newer than it is in the previous increments or the full backup.

Copyright (C) 2015  James Benson - jmbensonn@gmail.com

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

>> Version: 0.4.0
>> Date: 20-01-2016
"""
import abc;
import sys;
import os;
import shutil;
import getopt;
import datetime;
import re;

class CLI:
    def main(self):
        # Required options
        backup_type = None;

		try:
			if len(sys.argv[1:]) == 0:
				self.print_help();
                self.terminate("", 1);

			options, args = getopt.getopt(sys.argv[1:], "fi", ["full", "increment"]);
			for o, v in options:
				if not backup_type and BackupType.is_backup(o):
					backup_type = BackupType.get_backup(o);

            if not backup_type:
                self.terminate("Required Option Missing: -f/--full OR -i/--increment");

			for i, a in enumerate(args):
				if i < len(args) - 1:
					if not backup.add_source(a):
						print("Source not found: %s" % a);
				else:
					if not backup.set_destination(a):
						print("Destination not found: %s" % a);

			# Check the options and args provided by the user.
			if not backup.has_sources() or not backup.has_destination():
				self.terminate("", 1);

			try:



			except TypeError as te:
				self.terminate("TypeError: %s" % te, 1);
			except IndexError as ie:
				self.terminate("IndexError: %s" % ie, 1);
			except NoFullBackupError as nf:
				self.terminate("Cannot Create Increment: No previous full backup found.", 1);
			except:
				self.terminate("Something Happened\nBackup Terminated", 1);

		except getopt.GetoptError:
			self.terminate("Invalid option found.", 1);

    def print_help(self):
        pass

	def terminate(message = "", code = 0):
        if message:
            print(message);
		sys.exit(code);

class Backup:
    def __init__(self):
        self.container = None;
        #Need to be given a destination location for the container.
        self.sources = []; #Local source

    def add_source(self, directory):
		"""Adds a source to the source list for the backup.
		Returns true if added, false if not. Sources will not be set if
		the directory does not exist."""
		if os.path.isdir(directory) and not directory in self.sources:
			self.sources.append(os.path.abspath(directory));
			return True;
		else:
			#Interface.println("Source Not Found: \n - %s" % directory);
			return False;
        #Should raise an exception

	def has_sources(self):
		"""Whether any sources were set.
		Returns true if has any sources, false if not."""
		return len(self.sources) > 0;

	def set_destination(self, directory):
		"""Sets the destination for the backup.
		Returns true if set, false if not. Destination will not be set if
		the directory does not exist."""
		if os.path.isdir(directory):
			self.destination = directory.rstrip('\\');
			return True;
		else:
			return False;
        #Should raise an exception

	def has_destination(self):
		"""Whether a destination was set.
		Returns true if has destination, false if not."""
		return self.destination != None;

    def get_progress_string(self):
        pass # add own info(eg source) and timings and get the progress from the type

    def start(self, backup_type):
        pass
    #Need some methods for enumerating the filesystem

# === BackupTypes ===
class BackupType:
    __metaclass__=abc.ABCMeta;
    def __init__(self):
        pass

    @staticmethod
    def is_backup(self, identifier):
        return identifier == "--full" or identifier == "-f"
            or identifier == "--inc" or identifier == "-i";

    @staticmethod
    def get_backup(identifier):
        if (identifier == "--full" or identifier == "-f"):
            return Full();
        if (identifier == "--inc" or identifier == "-i"):
            return Increment();
        raise TypeError("Type %s not recognised" % identifier);

    @abc.abstractmethod
    def backup_file(self, path):

    @abc.abstractmethod
    def get_progress_string(self):

class Full(BackupType):
    def __init__(self):
        self.count_new = 0;

    def backup_file(self, path):
        """Always backup when doing a full backup."""
        return True;

    def get_progress_string(self):
        return "New Files: %s" % self.count_new;

class Increment(BackupType):
    def __init__(self):
        self.count_new = 0;
        self.count_modified = 0;
        self.count_unmodified = 0;

    def backup_file(self):
        """Only backup a file if it is not in any previous backups or
        if it has been modified since any previous backups."""
        pass; # TODO: Increment backup_file choice. Needs location object

    def get_progress_string(self):
        return "New: %s | Modified: %s | Unmodified: %s" %
            (self.count_new, self.count_modified, self.count_unmodified);
# --- End BackupTypes ---

# === Filters === #
class Filter(BackupType):
    __metaclass__=abc.ABCMeta;
    def __init__(self, backup = None):
        self.backup = backup;

    @abc.abstractmethod
    def backup_file(self, path):
        """If the previous BackupType in backup returned false for backup_file
        this must be honored otherwise the current BackupType may do its own check."""

class ExcludeFileExtension(Filter):
    def __init__(self, extension, backup = None):
        super().__init__(backup);
        self.extension = extension;

    def backup_file(self, file):
        if not self.backup.backup_file(path):
            return false;

        return file.getExtension() != self.extension;

class ExcludeGTFileSize(Filter):
    def backup_file(self, path):
        if not self.backup.backup_file(path):
            return false;

        return true;

class ExcludeLTFileSize(Filter):
    def backup_file(self, path):
        if not self.backup.backup_file(path):
            return false;

        return true;
# --- End Filters ---

# === BackupInfo ===
class BackupInfo:
    __metaclass__ = abc.ABCMeta;
    def __init__(self, path):
        """Path to the backups"""
        self.path = path;
        self.formatter = None;

    @staticmethod # REVIEW: This doesn't really fit here either
    def get_name_from_source(self, source):
        name = os.path.basename(source);
        if name == "":
            # basename("C:\") would return ""
            if os.name == "nt":
                # Use drive letter in Windows
                name = source[0]; # What if no drive letter?
            elif os.name == "posix":
                name = "root";
            else:
                pass
            # TODO: Check if backup_name was set by user.
            # do that first though..
    return name;

    def list(self):
        backups = [];
		for item in os.listdir(self.path):
			if os.path.isdir(os.path.join(self.path, item)):
                version = self.formatter.get_version(item);
                if version: #(If valid version)
                    backups.append((version, item));
        return backups.sort();

    def next_version(self):
        next_version = 1;
		backups = self.list();
		c = len(backups);
		if c > 0:
			next_version = c+1;
		return next_version;

class FullBackupInfo(BackupInfo):
    def __init__(self, path):
        super().__init__(path);
        self.formatter = FullVersionFormatter();

class IncrementBackupInfo(BackupInfo):
    def __init__(self, path, full_version):
        super().__init__(path);
        self.formatter = IncrementVerisonFormatter(full_version);
# --- End BackupInfo ---
class BackupItem:
    pass # one of the BackupInfos ??maybe

# === BackupVersionFormatters ===
class BackupVersionFormatter:
    __metaclass__=abc.ABCMeta;
    def __init__(self):
        self.TYPE_FULL = "Full";
        self.TYPE_INCREMENT = "Increment";

    @abc.abstractmethod
    def format(date, version):
        """Create a formatted name to use for the backup version container."""
    @abc.abstractmethod
    def get_version(name):
        """Get the version of the backup from the name."""
    def valid_format(self, name):
        return self.get_version(name) != None;
    def format_datetime(self, date):
		"""Get the datetime in the format wanted for the backup version."""
		return date.strftime("%Y-%m-%d_%H%M");

class FullVersionFormatter(BackupVersionFormatter):
    def format(self, date, version):
        return "%s__%s-%s" % (self.format_datetime(date), TYPE_FULL, version);
    def get_version(self, name):
        """Get an integer for the full version or None."""
        version = None;
        regex = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}__' + TYPE_FULL + r'-([0-9]{1,})$');
		match = regex.search(name);
		if match:
			version = int(match.group(1));
		return version;

class IncrementVersionFormatter(BackupVersionFormatter):
    def __init__(self, full_version):
        self.full_version = full_version;
    def format(self, date, version):
        return "%s__%s-%s-%s" % (self.format_datetime(date), TYPE_INCREMENT, self.full_version, version);
    def get_version(self, name):
        """Get an integer for the increment version or None."""
        version = None;
        regex = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}__" + TYPE_INCREMENT + "-([0-9]{1,})-([0-9]{1,})$");
		match = regex.search(name);
		if match and match.group(1) == str(self.full_version):
			version = int(match.group(2));
		return version;
# --- End BackupVersionFormatters ---

# === Containers ===
class Container(object):
    __metaclass__ = abc.ABCMeta;
    def __init__(self, name, location):
        self.files = [];
        self.total_size = 0;
        self.name = name;
        self.location = location;

        self.start_time = None;
        self.copied_files = 0;
        self.copied_size = 0;

    @abstractmethod
    def copy_file(self):

    def file_count(self):
        """Number of files inside the container."""
        return len(self.files);

    def file_size(self):
        """Size in ___ of all the files together."""
        return self.total_size;

    def set_file_list(self, list):
        self.files = list;

    def add_file(self, path):
        self.files.append(path);
        self.total_size += 0; # TODO: Replace with files size.

    def copy_files(self):
        self.start_time = datetime.datetime.now();
        self.location.mkdir(path, self.name); #TODO: What is path?
        for f in self.files:
            self.copy_file(f);

class LocalContainer(Container):
    def copy_file(self, item):
        """Copy one file in the container to the Location."""
        location.copy_file(src, dest); # TODO: what is the src and dest (dest needs to include the container name)

class ZippedContainer(Container):
    pass
# TODO: If zipped location is remote then will have to create on local then upload.

# === Locations ===
class Location(object):
    __metaclass__ = abc.ABCMeta;
    def __init__(self):
        self.path = "";

    def copy_file(self, src, dest):
        """Copies the local file at src to the destination on this Location."""
        pass
    def list_dir(self, dir):
        """ Get two lists of directory names and filenames inside the directory
        at the path in the pair ([dirs], [files])."""
        pass
    def mkdir(self, path, name):
        pass

class LocalLocation(Location):
    def copy_file(self, src, dest):
        shutil.copy2(src, dest);
        # raises: PermissionError, FileNotFoundError, OSError, ?shutil.Error
    def list_dir(self, path):
        dirs = [];
        files = [];
        for item in os.listdir(path):
            if os.path.isdir(item):
                dirs.append(item);
            if os.path.isfile(item):
                files.append(item);

class FTPLocation(Location):
    pass

# === Errors ===
class BackupError(Exception):
	pass
class NoFullBackupError(BackupError):
	pass
class NoSourceError(BackupError):
	pass
class NoDestinationError(BackupError):
	pass
class NoFilesToBackupError(BackupError):
	pass
# --- End Errors ---

if __name__ == "__main__":
	CLI().main();
