"""Python Backup Tests
Unit tests for the python backup script.

Copyright (C) 2015  James Benson (jmbensonn@gmail.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

import unittest;
import backup;
import os;
import shutil;
from datetime import datetime;

class BackupTestCase(unittest.TestCase):
	def rmdir(self, dir):
		parent = os.path.abspath("");
		if len(dir) > len(parent) and dir.startswith(parent):
			# failsafe: only delete if dir is child directory of the containing
			#           directory for this file. So not possible to delete anything
			#           else by accident.
			if os.path.isdir(dir):
				#print("Delete Suspended: %s" % dir);
				try:
					shutil.rmtree(dir);
				except OSError:
					print("On tearDown failed to remove %s"%dir); # for now

	def make_sample_file(self, path, contents):
		with open(path, "w") as f:
			f.write(contents);
		return path;

	def set_file_mtime(self, path, year, month, day, hour, min, sec):
		"""Set modified and access time to time."""
		timestamp = datetime(year, month, day, hour, min, sec).timestamp();
		os.utime(path, (timestamp, timestamp));

	def make_dirs(self, dirpath):
		if not os.path.exists(dirpath):
			os.makedirs(dirpath);

	def destroy_sources(self):
		self.rmdir(self.test_src_dir);

	def set_up_sources(self):
		self.test_src_dir = os.path.abspath("TestCase_Sources");
		# Create testing directories.
		# Valid sources
		self.src1 = os.path.join(self.test_src_dir, "source_one");
		self.src2 = os.path.join(self.test_src_dir, "source_two");
		self.make_dirs(self.src1); #also makes testdir
		self.make_dirs(self.src2);
		# Invalid sources
		self.src3 = os.path.join(self.test_src_dir, "source_three");
		self.src4 = "";
		self.src5 = os.path.join(self.test_src_dir, "source*five");

		# Sub directories
		self.src1_sub1 = os.path.join(self.src1, "sub1");
		self.src1_sub1_1 = os.path.join(self.src1_sub1, "sub1_1");
		self.src1_sub1_2 = os.path.join(self.src1_sub1, "sub1_2");
		self.make_dirs(self.src1_sub1_1);
		self.make_dirs(self.src1_sub1_2);
		# src1/sub1/sub1_1
		# src1/sub1/sub1_2

		self.src1_sub2 = os.path.join(self.src1, "sub2");
		self.make_dirs(self.src1_sub2);
		# src1/sub2

		# Sample Files
		self.file001 = self.make_sample_file(os.path.join(self.src1, "file001.txt"), "File 001");
		self.file002 = self.make_sample_file(os.path.join(self.src1, "file002.txt"), "File 002");
		self.file003 = self.make_sample_file(os.path.join(self.src1_sub1_1, "file003.txt"), "File 003");
		self.file004 = self.make_sample_file(os.path.join(self.src1_sub1_2, "file004.txt"), "File 004");
		self.file005 = self.make_sample_file(os.path.join(self.src1_sub1_2, "file005.txt"), "File 005");
		start = len(self.src1)+1;
		self.file001relpath = self.file001[start:];
		self.file002relpath = self.file002[start:];
		self.file003relpath = self.file003[start:];
		self.file004relpath = self.file004[start:];
		self.file005relpath = self.file005[start:];
		# src1/file001.txt
		# src1/file002.txt
		# src1/sub1/sub1_1/file003.txt
		# src1/sub1/sub1_2/file004.txt
		# src1/sub1/sub1_2/file005.txt

		# Set LastModified time and LastAccess time
		self.set_file_mtime(self.file001, 2015, 7, 1, 13, 15, 0);
		self.set_file_mtime(self.file002, 2015, 4, 24, 17, 30, 0);
		self.set_file_mtime(self.file003, 2015, 1, 16, 7, 45, 0);
		self.set_file_mtime(self.file004, 2014, 12, 12, 10, 0, 0);
		self.set_file_mtime(self.file005, 2014, 10, 9, 20, 20, 0);


	def destroy_backup_dest(self):
		self.rmdir(self.test_bup_dir);

	def set_up_backup_dest(self):
		self.test_bup_dir = os.path.abspath("TestCase_Backups");
		self.make_dirs(self.test_bup_dir);

	def set_up_local_backups(self):
		self.set_up_backup_dest();
		# Create testing directories.
		self.bup1 = os.path.join(self.test_bup_dir, "backup_one");
		self.bup2 = os.path.join(self.test_bup_dir, "backup_two");
		self.bup3 = os.path.join(self.test_bup_dir, "backup_three"); # doesn't exist
		self.make_dirs(self.bup1);
		self.bup1_f1 = os.path.join(self.bup1, "2015-07-01_2300__Full-1");
		self.bup1_f2 = os.path.join(self.bup1, "2015-07-02_2300__Full-2");
		self.bup1_f2_i1 = os.path.join(self.bup1, "2015-07-03_1330__Increment-2-1");
		self.bup1_f2_i2 = os.path.join(self.bup1, "2015-07-03_1830__Increment-2-2");
		self.bup1_f3 = os.path.join(self.bup1, "2015-07-03_2300__Full-3");
		self.bup1_f4 = os.path.join(self.bup1, "2015-07-04_2300__Full-4");
		self.make_dirs(self.bup1_f1);
		self.make_dirs(self.bup1_f2);
		self.make_dirs(self.bup1_f2_i1);
		self.make_dirs(self.bup1_f2_i2);
		self.make_dirs(self.bup1_f3);
		self.make_dirs(self.bup1_f4);

		# Sample backed up files
		# Full 1
		# self.f1file001 = self.make_sample_file(os.path.join(self.bup1_f2, self.file001relpath), "File 001");
		# self.f1file002 = self.make_sample_file(os.path.join(self.bup1_f2, self.file002relpath), "File 002");
		# self.f1file003 = self.make_sample_file(os.path.join(self.bup1_f2, self.file003relpath), "File 003");
		# self.f1file004 = self.make_sample_file(os.path.join(self.bup1_f2, self.file004relpath), "File 004");
		# self.f1file005 = self.make_sample_file(os.path.join(self.bup1_f2, self.file005relpath), "File 005");
		# self.set_file_mtime(self.file001, 2015, 7, 1, 13, 15, 0);
		# self.set_file_mtime(self.file002, 2015, 4, 24, 17, 30, 0);
		# self.set_file_mtime(self.file003, 2015, 1, 16, 7, 45, 0);
		# self.set_file_mtime(self.file004, 2014, 12, 12, 10, 0, 0);
		# self.set_file_mtime(self.file005, 2014, 10, 9, 20, 20, 0);

class SourcesTestCase(BackupTestCase):
	def setUp(self):
		self.set_up_sources();
		self.backup = backup.Full();

	def tearDown(self):
		self.destroy_sources();

	def test_addingSources(self):
		# Positive tests
		self.assertTrue(self.backup.add_source(self.src1));
		self.assertTrue(self.backup.add_source(self.src2));
		self.assertFalse(self.backup.add_source(self.src1));
		self.assertFalse(self.backup.add_source(self.src2));
		self.assertEqual(self.backup.sources, [self.src1, self.src2]);
		# Negative tests
		self.assertFalse(self.backup.add_source(self.src3)); # doesn't exist
		self.assertFalse(self.backup.add_source(self.src4)); # doesn't exist
		self.assertFalse(self.backup.add_source(self.src5)); # contains illegal char

	def test_hasSources(self):
		self.assertFalse(self.backup.has_sources());
		self.backup.add_source(self.src3); # doesn't exist, not added
		self.assertFalse(self.backup.has_sources());
		self.backup.add_source(self.src1); # added
		self.assertTrue(self.backup.has_sources());
		self.backup.add_source(self.src2)
		self.assertTrue(self.backup.has_sources());

class BackupsTestCase(BackupTestCase):
	"""Tests that don't require sample sources and backups."""
	def setUp(self):
		self.backup = backup.Full();

	# todo: write..
	# def test_setdestination(self):
	# def test_hasdestination(self):

	def test_fullVersion(self):
		# Valid
		self.assertEqual(self.backup.full_version("2015-02-22_1440__Full-1"), 1);
		self.assertEqual(self.backup.full_version("2015-05-11_1000__Full-2"), 2);
		self.assertEqual(self.backup.full_version("2026-12-11_1440__Full-0"), 0);
		self.assertEqual(self.backup.full_version("2015-10-11_1830__Full-001"), 1);
		self.assertEqual(self.backup.full_version("2010-02-11_1440__Full-012"), 12);
		self.assertEqual(self.backup.full_version("0000-00-00_0000__Full-12"), 12);
		self.assertEqual(self.backup.full_version("2003-07-03_0930__Full-55"), 55);
		self.assertEqual(self.backup.full_version("1990-05-03_1440__Full-425"), 425);
		# Invalid
		self.assertEqual(self.backup.full_version("2005-05-03_1440__full-one"), None);
		self.assertEqual(self.backup.full_version("1990-05-03_1440__Full-"), None);
		self.assertEqual(self.backup.full_version("1990-05-03_10__Full-9"), None);
		self.assertEqual(self.backup.full_version("1990-05-03_930__Full-9"), None);
		self.assertEqual(self.backup.full_version("1990-05-03_10304__Full-9"), None);
		self.assertEqual(self.backup.full_version("1990-05-03__Full-9"), None);
		self.assertEqual(self.backup.full_version("19934-05-03_1440__Full-3"), None);
		self.assertEqual(self.backup.full_version("15-05-03_1440__Full-4"), None);
		self.assertEqual(self.backup.full_version("2005-9-3_1440__Full-5"), None);
		self.assertEqual(self.backup.full_version("2015-02-11_1440__Ful-2"), None);
		self.assertEqual(self.backup.full_version("20050903_1440__Full-6"), None);
		self.assertEqual(self.backup.full_version("2003-05-03_1440_Full-23"), None);
		self.assertEqual(self.backup.full_version("Full-25"), None);
		self.assertEqual(self.backup.full_version("Random words"), None);
		self.assertEqual(self.backup.full_version("New Folder"), None);
		self.assertEqual(self.backup.full_version("2015-02-11_1440__Increment-9"), None);

	#@unittest.skip("No idea why errors") #TypeError: test_incrementversion() takes 0 positional arguments but 1 was given
	def test_incrementVersion(self):
		# Valid
		self.assertEqual(self.backup.increment_version("2015-02-22_1440__Increment-1-1"), (1,1));
		self.assertEqual(self.backup.increment_version("2015-05-11_1000__Increment-2-1"), (2,1));
		self.assertEqual(self.backup.increment_version("2026-12-11_1440__Increment-0-0"), (0,0));
		self.assertEqual(self.backup.increment_version("2015-10-11_1830__Increment-001-003"), (1,3));
		self.assertEqual(self.backup.increment_version("2010-02-11_1440__Increment-012-001"), (12,1));
		self.assertEqual(self.backup.increment_version("0000-00-00_0000__Increment-12-154"), (12,154));
		self.assertEqual(self.backup.increment_version("2003-07-03_0930__Increment-55-34"), (55,34));
		self.assertEqual(self.backup.increment_version("1990-05-03_1440__Increment-425-1024"), (425,1024));
		# Invalid
		self.assertEqual(self.backup.increment_version("2005-05-03_1440__Increment-14"), None);
		self.assertEqual(self.backup.increment_version("1990-505-03_1440__Increment-55-27"), None);
		self.assertEqual(self.backup.increment_version("1990-05-03_10__Increment-9-3"), None);
		self.assertEqual(self.backup.increment_version("1990-05-03_930__Increment-9-2"), None);
		self.assertEqual(self.backup.increment_version("1990-05-03_10304__Increment-9-9"), None);
		self.assertEqual(self.backup.increment_version("1990-05-03__Increment-9-4"), None);
		self.assertEqual(self.backup.increment_version("19934-05-03_1440__Increment-3-4"), None);
		self.assertEqual(self.backup.increment_version("15-05-03_1440__Increment-4-6"), None);
		self.assertEqual(self.backup.increment_version("2005-9-3_1440__Increment-5-3"), None);
		self.assertEqual(self.backup.increment_version("2015-02-11_1440__Inc-2-1"), None);
		self.assertEqual(self.backup.increment_version("20050903_1440__Increment-6-1"), None);
		self.assertEqual(self.backup.increment_version("2003-05-03_1440_Increment-23-12"), None);
		self.assertEqual(self.backup.increment_version("2003-05-03_1440__Increment-23-"), None);
		self.assertEqual(self.backup.increment_version("2003-05-03_1440__Increment-23"), None);
		self.assertEqual(self.backup.increment_version("increment-25-13"), None);
		self.assertEqual(self.backup.increment_version("Random words"), None);
		self.assertEqual(self.backup.increment_version("New Folder"), None);
		self.assertEqual(self.backup.increment_version("2015-02-11_1440__Full-9-2"), None);

	def test_getBackupName(self):
		self.assertEqual(self.backup.get_backup_name("D:\\Python\\Source"), "Source");
		self.assertEqual(self.backup.get_backup_name("D:\\Python"), "Python");
		self.assertEqual(self.backup.get_backup_name("D:\\Python\\"), "D"); # as ends in \
		self.assertEqual(self.backup.get_backup_name("D:\\"), "D");
		self.assertRaises(IndexError, self.backup.get_backup_name, "");
		self.assertRaises(TypeError, self.backup.get_backup_name, 9);


class LocalBackupsTestCase(BackupTestCase):
	"""Test the methods that handle the backups."""
	def setUp(self):
		self.set_up_local_backups();
		self.backup = backup.Full();

	def tearDown(self):
		self.destroy_backup_dest();

	def test_getAllFullBackups(self):
		self.assertEqual(self.backup.get_all_full_backups(self.bup1),
			[(1, self.bup1_f1),
			(2, self.bup1_f2),
			(3, self.bup1_f3),
			(4, self.bup1_f4)],
			"Full backup list not as expected."
		);
		self.assertEqual(self.backup.get_all_full_backups(self.bup2), [],
			"No backups should be found.");
		self.assertEqual(self.backup.get_all_full_backups(self.bup3), [],
			"No backups should be found as the direcory does not exist.");

	def test_getLastFullBackup(self):
		self.assertEqual(self.backup.get_last_full_backup(self.bup1),
			(4, self.bup1_f4), "Last backup not found as expected."
		);
		self.assertEqual(self.backup.get_last_full_backup(self.bup2),
			None, "No last backup should be found.");
		self.assertEqual(self.backup.get_last_full_backup(self.bup3),
			None, "No last backup should be found as direcory does not exist.");

	def test_getFullBackup(self):
		self.assertEqual(self.backup.get_full_backup(self.bup1, 2),
			(2, self.bup1_f2), "Backup 2 not found.");
		self.assertEqual(self.backup.get_full_backup(self.bup1, 4),
			(4, self.bup1_f4), "Backup 4 not found.");
		self.assertEqual(self.backup.get_full_backup(self.bup1, 3),
			(3, self.bup1_f3), "Backup 3 not found.");
		self.assertEqual(self.backup.get_full_backup(self.bup1, 1),
			(1, self.bup1_f1), "Backup 1 not found.");
		self.assertEqual(self.backup.get_full_backup(self.bup1, 9),
			None, "Backup 9 should not exist.");
		self.assertEqual(self.backup.get_full_backup(self.bup1, 21),
			None, "Backup 21 should not exist.");
		self.assertEqual(self.backup.get_full_backup(self.bup2, 1),
			None, "Backup location should not have any backups.");
		self.assertEqual(self.backup.get_full_backup(self.bup2, 2),
			None, "Backup location should not have any backups.");
		self.assertEqual(self.backup.get_full_backup(self.bup3, 1),
			None, "Backup location should not exist.");
		self.assertEqual(self.backup.get_full_backup(self.bup3, 2),
			None, "Backup location should not exist.");

	def test_getIncrementsFor(self):
		self.assertEqual(self.backup.get_increments_for(self.bup1, 2),
			[(1, self.bup1_f2_i1),
			(2, self.bup1_f2_i2)],
			"Increments for 2 not found as expected.");
		self.assertEqual(self.backup.get_increments_for(self.bup1, 1),
		[], "Should not be any increments for 1");
		self.assertEqual(self.backup.get_increments_for(self.bup1, 6),
		[], "Should not be any increments for 6, 6 does not exist"); # should this error?
		self.assertEqual(self.backup.get_increments_for(self.bup2, 2),
		[], "Empty dir: Should not be any increments for 2, 2 does not exist"); # should this error?
		self.assertEqual(self.backup.get_increments_for(self.bup3, 1),
		[], "Dir does not exist: Should not be any increments for 1, 2 does not exist"); # should this error?

class BackupExecutionTestCase(BackupTestCase):
	def setUp(self):
		self.set_up_sources();
		self.set_up_backup_dest();
		self.full = backup.Full();
		self.increment = backup.Increment();
	def tearDown(self):
		self.destroy_sources();
		self.destroy_backup_dest();

	def test_backupInit(self):
		self.assertRaises(backup.NoSourceError, self.full.backup_init, 0);
		self.full.add_source(self.src1);
		self.assertRaises(backup.NoSourceError, self.full.backup_init, 1);
		self.assertRaises(backup.NoDestinationError, self.full.backup_init, 0);
		self.full.set_destination(self.test_bup_dir);

		self.full.backup_init(0);
		self.assertEqual(self.full.current_source, 0);
		self.assertEqual(self.full.backup_name, "source_one");
		# fails as ends in __Full-2
		# as previous fail doesn't clean up after it's self.
		self.assertTrue(self.full.backup_version.endswith("__Full-1"),
			"Backup version expected to be [date]__Full-1");
		self.assertEqual(self.full.backup_path,
			os.path.join(self.test_bup_dir, self.full.backup_name, self.full.backup_version),
			"Backup path not as expected.");
		self.assertEqual(self.full.last_full, None);
		self.assertEqual(self.full.c_files, 0);

	def test_backup(self):
		# Set up Full and Increment
		self.full.add_source(self.src1);
		self.full.set_destination(self.test_bup_dir);
		self.increment.add_source(self.src1);
		self.increment.set_destination(self.test_bup_dir);

		# Try an increment when there is no previous full backup.
		self.assertRaises(backup.NoFullBackupError, self.increment.backup_source, 0);
		# Do full backup
		self.full.backup_source(0);
		self.assertEqual(len(self.full.copy.copylist), 5,
		"All 5 files should be in the copylist.");
		# Check all files are in the backed up location.
		self.assertTrue(os.path.isfile(os.path.join(self.full.backup_path, self.file001relpath)),
		"File001 should have been backed up.");
		self.assertTrue(os.path.isfile(os.path.join(self.full.backup_path, self.file002relpath)),
		"File002 should have been backed up.");
		self.assertTrue(os.path.isfile(os.path.join(self.full.backup_path, self.file003relpath)),
		"File003 should have been backed up.");
		self.assertTrue(os.path.isfile(os.path.join(self.full.backup_path, self.file004relpath)),
		"File004 should have been backed up.");
		self.assertTrue(os.path.isfile(os.path.join(self.full.backup_path, self.file005relpath)),
		"File005 should have been backed up.");

		# TODO: Check modified times are the same.
		# TODO: Check source files aren't deleted.

		# Try create an increment with no modified files
		# Should create an empty increment.
		self.increment.backup_source(0);
		self.assertEqual(len(self.increment.copy.copylist), 0,
		"No files should have been copied.");
		## Should there? no files copied should the inc e created
		# self.assertEqual(len(backup.Increment.get_increments_for(os.path.dirname(self.increment.backup_path), 1)), 1,
		# "There should be one increment for Full-1");

		# Modify files
		self.set_file_mtime(self.file001, 2015, 7, 2, 9, 30, 0); # new by 1 day
		self.set_file_mtime(self.file003, 2015, 1, 16, 7, 50, 0); # new by 5 mins
		self.set_file_mtime(self.file005, 2014, 10, 9, 20, 20, 1); # new by one second
		# Try another increment
		# 3 files should be in increment.
		self.increment.backup_source(0);
		self.assertEqual(len(self.increment.copy.copylist), 3,
		"3 files should have been copied.");
		self.assertTrue(os.path.isfile(os.path.join(self.increment.backup_path, self.file001relpath)),
		"File001 should have been backed up.");
		self.assertTrue(os.path.isfile(os.path.join(self.increment.backup_path, self.file003relpath)),
		"File003 should have been backed up.");
		self.assertTrue(os.path.isfile(os.path.join(self.increment.backup_path, self.file005relpath)),
		"File005 should have been backed up.");
		self.assertFalse(os.path.isfile(os.path.join(self.increment.backup_path, self.file002relpath)),
		"File002 should not have been backed up.");
		self.assertFalse(os.path.isfile(os.path.join(self.increment.backup_path, self.file002relpath)),
		"File004 should not have been backed up.");

		# Modify files for second time
		self.set_file_mtime(self.file002, 2015, 5, 24, 17, 30, 0); # new by 1 month
		self.set_file_mtime(self.file003, 2015, 1, 16, 8, 50, 0); # new by 1 hour
		# Try another increment
		# 2 files should be in the increment.
		self.increment.backup_source(0);
		self.assertEqual(len(self.increment.copy.copylist), 2,
		"3 files should have been copied.");
		self.assertTrue(os.path.isfile(os.path.join(self.increment.backup_path, self.file002relpath)),
		"File002 should have been backed up.");
		self.assertTrue(os.path.isfile(os.path.join(self.increment.backup_path, self.file003relpath)),
		"File003 should have been backed up.");
		self.assertFalse(os.path.isfile(os.path.join(self.increment.backup_path, self.file001relpath)),
		"File001 should have been backed up.");
		self.assertFalse(os.path.isfile(os.path.join(self.increment.backup_path, self.file004relpath)),
		"File004 should not have been backed up.");
		self.assertFalse(os.path.isfile(os.path.join(self.increment.backup_path, self.file005relpath)),
		"File005 should not have been backed up.");

if __name__ == "__main__":
	unittest.main();
