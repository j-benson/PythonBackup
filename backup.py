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

>> Version: 0.3.3
>> Date: 26-08-2015
"""

import sys;
import getopt;
import os;
import shutil;
import re;
from datetime import datetime;
from abc import ABCMeta, abstractmethod;

# Full backup: copy every file from the source to the destination.
# Incremental backup: only copy files into new increment if they changed from any previous increment or the full backup.

BACKUP_USAGE = "Usage: backup.py [-f|-i] source+ destination"

TYPE_FULL = "Full"
TYPE_INCREMENT = "Increment";

class Interface(object):
	"""Provides a command line interface for creating backups."""

	def main(self):
		mode = 0;
		FULL = 1;
		INC = 2;

		try:
			if len(sys.argv[1:]) == 0:
				terminate(BACKUP_USAGE);

			options, args = getopt.getopt(sys.argv[1:], "fi", ["full", "increment"]);
			# options full or inc backup, args sources and last arg destination
			for o, v in options:
				if o == "-f" or o == "--full":
					if mode == 0:
						mode = FULL;
					else:
						terminate("Must select either -f/--full or i/--increment.");
				if o == "-i" or o == "--increment":
					if mode == 0:
						mode = INC;
					else:
						terminate("Must select either -f/--full or i/--increment.");

			# For the modes full and increment the args will be a list of sources followed by the destination.
			# Any trailing slashes will be removed.
			if mode == FULL or mode == INC:
				backup = None;
				if mode == FULL:
					backup = Full();
				elif mode == INC:
					backup = Increment();

				for i, a in enumerate(args):
					if i < len(args) - 1:
						if not backup.add_source(a):
							Interface.println("Source not found: %s" % a);
					else:
						if not backup.set_destination(a):
							Interface.println("Destination not found: %s" % a);

			# Check the options and args provided by the user.
			if not backup.has_sources() or not backup.has_destination():
				terminate("No valid sources or destination.", 1);

			try:
				backup.backup();
			except TypeError as te:
				Interface.println("TypeError: %s" % te);
			except IndexError as ie:
				Interface.println("IndexError: %s" % ie);
			except NoFullBackupError as nf:
				Interface.println("Cannot Create Increment: No previous full backup found.");
			except:
				Interface.println("Something Happened\nBackup Terminated");

		except getopt.GetoptError:
			terminate("Invalid option found.\n%s" % BACKUP_USAGE);

	@staticmethod
	def println(line, end="\n"):
		"""Controls printing to the terminal."""
		if __name__ == "__main__": # and if verbose mode on. TODO
			print(line, end=end);

	@staticmethod
	def printerr(line, end="\n"):
		"""Controls printing to the terminal."""
		if __name__ == "__main__":
			print(line, end=end);

	@staticmethod
	def terminate(message, code = 0):
		Interface.println(message);
		sys.exit(code);

class Backup(metaclass=ABCMeta):
	"""Abstract class for the different types of backups. Provides
	methods needed to create a new backup, the rest is done by the subclasses
	by overriding the backup abstract method.

	Attributes
	----------
	sources : [string]
		A list of directory filepaths to backup.
	destination : string
		The directory filepath to save the backup to.
	"""

	def __init__(self):
		self.sources = [];
		self.destination = None;

		self.copy = None
		self.current_source = -1;
		self.backup_name = None;
		self.backup_version = None;
		self.backup_path = None;
		self.last_full = None;

	def add_source(self, directory):
		"""Adds a source to the source list for the backup.
		Returns true if added, false if not. Sources will not be set if
		the directory does not exist."""
		if os.path.isdir(directory) and not directory in self.sources:
			self.sources.append(os.path.abspath(directory));
			return True;
		else:
			Interface.println("Source Not Found: \n - %s" % directory);
			return False;

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

	def has_destination(self):
		"""Whether a destination was set.
		Returns true if has destination, false if not."""
		return self.destination != None;

	def backup(self):
		"""This one does the backup."""
		for i, src in enumerate(self.sources):
			self.backup_source(i);

	def backup_source(self, src_num):
		"""Backs up a source in the sources list.
		src_num : int
			The index of the source from the sources list.
		Raises
			IndexError if src_num is not valid number.
			NoFullBackupError if no last backup when required (increment only)"""
		self.backup_init(src_num);
		for path, dirnames, filenames in os.walk(self.sources[src_num]):
			relpath = path[len(self.sources[src_num]):]  # Remove the dir filepath leaving only a relative path to the file.
			relpath = relpath.lstrip(os.sep);  # remove any leading path seperators
			for fname in filenames:
				self.backup_file(os.path.join(relpath, fname));
		Interface.println(""); # print a new line char \n after backup_file called for all files
		self.copy.start();
		self.copy.show_errors();

	def backup_init(self, src_num):
		"""Sets up the source for backup.
		src_num : int
			The index of the source from the sources list.
		Raises
			IndexError if src_num is not valid number.
			NoFullBackupError if no last backup when required (increment only)"""
		self.current_source = src_num;
		try:
			self.backup_name = self.get_backup_name(self.sources[src_num]);
		except IndexError:
			raise NoSourceError();
		Interface.println("Starting Backup %s of %s: %s" % (src_num + 1, len(self.sources), self.backup_name));
		if self.destination == None:
			raise NoDestinationError();
		self.backup_version = self.new_backup_version(self.destination, self.backup_name);
		self.backup_path = os.path.join(self.destination, self.backup_name, self.backup_version);
		self.copy = Copying();

	@abstractmethod
	def backup_file(self, rel_filepath):
		"""How the different backups backup each file.
		rel_filepath : str
			The filepath relative to the source filepath."""

	@staticmethod
	def full_version(name):
		"""Extracts the full backup version number from the name of the container.
		Full backups are named YYYY-MM-DD_HHMM__Full-n where n is the version.
		Can also be used to test if the directory is a full backup.

		Returns the version number of the full backup or None if the direcory name
		is not a full backup."""
		if not isinstance(name, str):
			raise TypeError("full_version - The container name must be a string.");

		regex = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}__' + TYPE_FULL + r'-([0-9]{1,})$');
		match = regex.search(name);
		if match:
			return int(match.group(1));
		else:
			return None;

	@staticmethod
	def increment_version(name):
		"""Extracts the increment version number from the name of the container.
		Increments are named YYYY-MM-DD_HHMM__Increment-n-m where n is the
		full backup version and m is the increment version.
		Also used to test if the directory is an increment.
		name : string
			The name of the container of the full backup.
		Returns : (int, int) or None
			A pair containing the full backup version number and the increment
			version number or None if the direcory name is not an increment.
			Example:
				(full_version, increment_version)"""
		if not isinstance(name, str):
			raise TypeError("increment_version - The container name must be a string.");

		regex = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{4}__" + TYPE_INCREMENT + "-([0-9]{1,})-([0-9]{1,})$");
		match = regex.search(name);
		if match:
			return (int(match.group(1)), int(match.group(2)));
		else:
			return None;

	@staticmethod
	def get_all_full_backups(directory):
		"""Get a list of the full backups in the directory.
		directory : string
			The filepath to the directory containing the backups.

		Returns : [(int, string)]
			A list of pairs containing the version number of the backup and the full filepath
			to the backup.
			The list is in ascending order of version number.
			An empty list is returned when there are no backups in the directory
			or the directory does not exist."""

		if not isinstance(directory, str):
			raise TypeError("The directory must be a string.");

		backups = [];
		if os.path.isdir(directory):
			for c in os.listdir(directory): #does this raise FileNotFoundError if not dir?
				fullpath = os.path.join(directory, c);
				if os.path.isdir(fullpath):
					version = Backup.full_version(c);
					if version:
						backups.append((version, fullpath));
			backups.sort();
		#else
		#TODO: raise error? yes
		return backups;

	@staticmethod
	def get_full_backup(directory, version):
		"""Get the filepath to a full backup by version number.
		directory : str
			The filepath to the directory containing all the backups.
		version : int
			The version number of the backup to return.
		Returns : (int, str)
			A pair containing the version number and the file path of the
			backup: (version, path)"""
		if not isinstance(version, int):
			raise TypeError("The version must be an integer.");

		result = None;
		backups = Backup.get_all_full_backups(directory);
		for v, p in backups:
			if v == version:
				result = (v, p);
				break;
		return result;

	@staticmethod
	def get_last_full_backup(directory):
		"""Gets the last full backup in the directory.
		directory : str
			The filepath to the directory containing the backups.
		Returns : (int, str) or None
			A pair with the version number and the filepath, or None if there are no
			previous backups."""

		lastfull = None;
		full_backups = Backup.get_all_full_backups(directory);
		c = len(full_backups);
		if c > 0:
			lastfull = full_backups[c-1];
		return lastfull;

	@staticmethod
	def get_increments_for(directory, version):
		"""Get the list of increments for a full backup in the given directory.
		directory : str
			The filepath to the directory containing the backup versions.
		version : int
			The version number of the full backup.
		Returns : [(int, string)]
			A list of pairs with the increment number and the filepath to the increment."""
		if not isinstance(directory, str):
			raise TypeError("The directory must be a string.");
		if not isinstance(version, int):
			raise TypeError("The version must be an integer.");

		increments = [];
		if os.path.isdir(directory):
			for c in os.listdir(directory):
				fullpath = os.path.join(directory, c);
				if os.path.isdir(fullpath):
					inc = Backup.increment_version(c);
					# inc = (full, increment) or None
					if inc and inc[0] == version:
						increments.append((inc[1], fullpath));
						# (increment_version, filepath)
			increments.sort();
			### REVIEW: This is VERY similar code to get full backups
			### only change is what regex is used and what to append. maybe can simplify
		else:
			# REVIEW: Raise error dir does not exit?
			pass;
		return increments;

	def dir_datetime(self):
		"""Get the datetime in the format wanted for the backup version."""
		return datetime.now().strftime("%Y-%m-%d_%H%M");

	def get_backup_name(self, source):
		# desintation - the destination filepath of the backup
		# source - the source filepath
		name = "";
		try:
			name = os.path.basename(source);
			if name == "":
				# C:\ would return ""
				if os.name == "nt": #and len(source) > 0;
					# Use drive letter in Windows
					name = source[0]; # What if no drive letter?
				elif os.name == "posix":
					name = "root";
				else:
					pass
				# TODO: Check if backup_name was set by user.
				# do that first though..
		except TypeError:
			# thrown by path.basename when len() fails
			raise TypeError("Source must be a string.");
		except IndexError:
			raise IndexError("Source cannot be an empty string.");
		return name;

	@abstractmethod
	def new_backup_version(self, destination, backup_name):
		"""Creates the directory name for a new backup."""

class Full(Backup):
	"""Provides full backup functionality.
	A full backup copies all files from the given sources to the given destination."""

	def __init__(self):
		super().__init__();
		self.C_files = 0;

	def backup_init(self, src_num):
		super().backup_init(src_num);
		self.c_files = 0;

	def backup_file(self, rel_filepath):
		self.copy.add(os.path.join(self.sources[self.current_source], rel_filepath),
			os.path.join(self.backup_path, os.path.dirname(rel_filepath)));
		self.c_files += 1;
		Interface.println("\rFound %s files" % self.c_files, "");

	def new_backup_version(self, destination, backup_name):
		"""Creates the version name for a new full backup.
		Also sets the last_full property.
		destination : str
			The filepath to the destination.
		backup_name : str
			The name for the backup.
		Returns : str
			The name for the new backup version."""
		# Naming Conventions for Full Backups
		# --------------------------------
		# Full backups are named "yyyy-mm-dd_hhmm__Full-n" where n is the full version number.
		self.last_full = self.get_last_full_backup(os.path.join(destination, backup_name));
		if not self.last_full:
			version = 0;
		else:
			version, path = self.last_full;
		return "%s__%s-%s" % (self.dir_datetime(), TYPE_FULL, version + 1);


class Increment(Backup):
	"""Provides incremental backup functionality.
	An increment compares previous increments and the full backup it relates to
	only copies files that have been modified to the new increment."""

	def __init__(self):
		super().__init__();
		self.backup_name_path = None;
		self.all_backups = None;
		self.c_new = 0;
		self.c_modified = 0;
		self.c_unmodified = 0;

	def backup_init(self, src_num):
		super().backup_init(src_num);
		self.backup_name_path = os.path.join(self.destination, self.backup_name);
		self.all_backups = Increment.get_increments_for(self.backup_name_path, self.last_full[0]);
		self.all_backups.reverse();
		self.all_backups.append(self.last_full);
		self.c_new = 0;
		self.c_modified = 0;
		self.c_unmodified = 0;

	def backup_file(self, rel_filepath):
		"""Performs an incremental backup of the given sources to the given destination by
		comparing the source to previous increments and the previous full backup."""
		found = False;
		for b_no, b_path in self.all_backups:
			b_filepath = os.path.join(b_path, rel_filepath);
			if os.path.isfile(b_filepath):
				found = True;
				src_filepath = os.path.join(self.sources[self.current_source], rel_filepath);
				if self.needs_backup(src_filepath, b_filepath):
					self.copy.add(src_filepath, os.path.join(self.backup_path,
						os.path.dirname(rel_filepath)));
					self.show_progress(2); # modified file
				else:
					self.show_progress(3); # unmodified file
				break;
		if not found:
			self.copy.add(os.path.join(self.sources[self.current_source], rel_filepath), 
				os.path.join(self.backup_path, os.path.dirname(rel_filepath)));
			self.show_progress(1); # new file

	def needs_backup(self, s, b):
		"""Return true if the file s needs backing up to the new increment
		compared to the already backed up file b."""
		return os.path.getmtime(s) > os.path.getmtime(b);

	def show_progress(self, increase = 0):
		"""Shows the progress of the increment and adds to the new, modified and
		unmodified counters if increase is specified.
			When increase is 1: +1 to new
			     increase is 2: +1 to modified
				 increase is 3: +1 to unmodified"""
		if increase == 1:
			self.c_new += 1;
		elif increase == 2:
			self.c_modified += 1;
		elif increase == 3:
			self.c_unmodified += 1;
		Interface.println("\rNew: %d / Modified: %d / Unmodified: %d" % (self.c_new, self.c_modified, self.c_unmodified), "");

	def new_backup_version(self, destination, backup_name):
		"""Creates the version name for a new increment.
		Also sets the last_full property.
		Raises
			NoFullBackupError if cannot create new version as there is no
			previous full backup."""
		# Naming Conventions for Increments
		# --------------------------------
		# Incremental backups are named "yyyy-mm-dd_hhmm__Increment-n-m"
		# where n is the full version number and m is the increment version number.
		backup_path = os.path.join(destination, backup_name);
		self.last_full = self.get_last_full_backup(backup_path);
		if self.last_full == None:
			raise NoFullBackupError();
		else:
			version, path = self.last_full;
			increments = Increment.get_increments_for(backup_path, version)
		return "%s__%s-%s-%s" % (self.dir_datetime(), TYPE_INCREMENT, version, len(increments) + 1);

class Copying(object):
	"""Handles sequential copying.
	Attributes
	----------
	copylist : [str]
		A list if files to be copied.
	errors [(str, str)]
		A list of failed copies with a reason.
	"""
	def __init__(self):
		self.copylist = [];
		self.errors = [];

	def add(self, source_file, destination_file):
		self.copylist.append((source_file, destination_file));

	def add_error(self, msg, src):
		self.errors.append("%s: %s" % (msg, src));

	def show_errors(self):
		for e in self.errors:
			Interface.printerr(e);

	def start(self):
		c = 0;
		for s, d in self.copylist:
			self.copy_file(s, d);
			c += 1;
			Interface.println("\rCopied %d of %d" % (c, len(self.copylist)), "");
		if c > 0:
			Interface.println("\nCopying Complete");
		else:
			Interface.println("No Files To Copy");

	def copy_file(self, source_file, destination_directory):
		"""Copies a source file to the destination directory.
		Also copies file stats such as date modified.
		If it cannot be copied it will be added to the errors list."""
		# REVIEW: Does copy2 overwrite existing files.
		if not os.path.exists(destination_directory):
			os.makedirs(destination_directory);
			# raises OSError if directory cannot be created.
		try:
			shutil.copy2(source_file, destination_directory);
		except PermissionError:
			self.add_error("Permission Denied", source_file);
		except FileNotFoundError:
			self.add_error("Not Found", source_file);
		except (shutil.Error, OSError) as e:
			self.add_error("Copy Failed", source_file);

# --- Custom Errors ---
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


# --- END CLASS DEFINITIONS ---


if __name__ == "__main__":
	Interface().main();
