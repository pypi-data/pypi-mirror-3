# -*- coding: utf-8 -*-

"""
tests.py

Created by Michael Smith on 2012-06-21.
Copyright © 2012 True Action Network. All rights reserved.
"""

from . import exists, MongoFile, remove, rename
from contextlib import closing
from csv import writer
from mongo_file import valid_name
from os import chdir, getcwdu
from pymongo import Connection
from shutil import rmtree
from tempfile import mkdtemp
from unittest import TestCase

DATA = """Four score and seven years ago our fathers brought forth
upon this continent, a new nation, conceived in Liberty, and
dedicated to the proposition that all men are created equal."""
CSV_DATA = (
	(u'2012-07-02T04:02:48+00:00', '', '', u'cs_svanbrug', u'100000238', '53', u'1113', '', '', '', '', 'Webstore', '', u'1.0', u'599.99', u'6.66666666667', u'49.5', '599.99', '', '', ''),
	(u'2012-07-02T04:02:48+00:00', '', '', u'cs_svanbrug', u'100000238', '51', u'1111', '', '', '', '', 'Webstore', '', u'2.0', u'599.98', u'6.66666666667', u'49.5', '599.98', '', '', ''),
	(u'2012-07-02T04:02:48+00:00', '', '', u'cs_svanbrug', u'100000238', '52', u'1112', '', '', '', '', 'Webstore', '', u'1.0', u'129.99', u'6.66666666667', u'10.72', '129.99', '', '', ''),
)
DB_ARGS = {
	"collection_name": "test",
	"db_name": "test",
}

class MongoFileTest(TestCase):
	"""Test cases for Mongo File"""
	def setUp(self):
		"""Create test files and mongo files we can work with."""
		self.old_dir = getcwdu()
		self.tmp_dir = mkdtemp()
		chdir(self.tmp_dir)
		MongoFile("empty", mode="w", **DB_ARGS).close() # Empty Mongo File
		with MongoFile("full", mode="w", **DB_ARGS) as full:
			full.write(DATA) # Mongo File with data in it
		open("empty", mode="w").close() # Empty regular file
		with open("full", mode="w") as full:
			full.write(DATA) # Regular file with data in it
	def tearDown(self):
		"""Remove the test database."""
		chdir(self.old_dir)
		rmtree(self.tmp_dir)
		with closing(Connection()) as connection:
			connection.drop_database(DB_ARGS["db_name"])
	def test_append(self):
		"""Test that you can append to a mongo file."""
		with MongoFile("full", mode="a", **DB_ARGS) as full:
			full.write("And one more thing!")
		with MongoFile("full", mode="r", **DB_ARGS) as full:
			result = full.read()
		with open("full", mode="a") as full:
			full.write("And one more thing!")
		with open("full", mode="r") as full:
			file_result = full.read()
		self.assertEqual(file_result, result, {"got": result, "exp": file_result})
	def test_close(self):
		"""Test that closing a mongo file sets its "closed" attribute and makes it not read/writable."""
		mfile = MongoFile("full", mode="r", **DB_ARGS)
		mfile.close()
		self.assertTrue(mfile.closed, mfile.closed)
		self.assertRaises(IOError, mfile.read)
	def test_csv_writelines(self):
		"""Test that csv.writelines works the same with a mongofile and a file."""
		with open("empty", mode="w") as csvfile:
			csvwriter = writer(csvfile)
			csvwriter.writerows(CSV_DATA)
		with MongoFile("empty", mode="w", **DB_ARGS) as csvfile:
			csvwriter = writer(csvfile)
			csvwriter.writerows(CSV_DATA)
		self.assertEqual(open("empty").read(), MongoFile("empty", **DB_ARGS).read())
	def test_exists(self):
		"""
		Test that a mongo file exists when you know it exists
		and doesn't when you know it doesn't. ;)
		"""
		self.assertTrue(exists("full", **DB_ARGS), "'full' should exist, but doesn't!")
		self.assertFalse(exists("williwonka", **DB_ARGS), "'williwonka' shoudn't exist, but does!")
	def test_invalid_mode(self):
		"""Test that only supported modes a, r, and w are allowed."""
		args = dict(DB_ARGS)
		args.update({
			"name": "full",
			"mode": "Q",
		})
		self.assertRaises(ValueError, MongoFile, **args)
	def test_invalid_name(self):
		"""Test that you can't do things to mongo files without a valid db name or mongo uri."""
		self.assertRaises(TypeError, valid_name)
	def test_invalid_writes(self):
		"""Test that you can't truncate a file opened in a readonly mode."""
		with MongoFile("full", mode="r", **DB_ARGS) as full:
			self.assertRaises(IOError, full.truncate)
			self.assertRaises(IOError, full.write, "buzz")
	def test_read(self):
		"""Test that you can read from a mongo file."""
		with MongoFile("full", mode="r", **DB_ARGS) as full:
			result = full.read()
		with open("full", mode="r") as full:
			file_result = full.read()
		self.assertEqual(file_result, result, {"got": result, "exp": file_result})
	def test_read_part(self):
		"""Test that you can read part of a mongo file."""
		with MongoFile("full", mode="r", **DB_ARGS) as full:
			result = full.read(12)
		with open("full", mode="r") as full:
			file_result = full.read(12)
		self.assertEqual(file_result, result, {"got": result, "exp": file_result})
	def test_readlines(self):
		"""Test that you can readlines from a mongo file"""
		with MongoFile("full", mode="r", **DB_ARGS) as full:
			result = full.readlines()
		with open("full", mode="r") as full:
			file_result = full.readlines()
		self.assertEqual(file_result, result, {"got": result, "exp": file_result})
	def test_remove(self):
		"""Test that you can remove a mongo file."""
		remove("full", **DB_ARGS)
		args = dict(DB_ARGS)
		args.update({
			"name": "full",
			"mode": "r",
		})
		self.assertRaises(IOError, MongoFile, **args)
	def test_rename(self):
		"""Test that you can rename a mongo file."""
		args = dict(DB_ARGS)
		args.update({
			"name": "fun",
			"mode": "r",
		})
		self.assertRaises(IOError, MongoFile, **args)
		rename("full", "fun", **DB_ARGS)
		with MongoFile("fun", mode="r", **DB_ARGS) as fun:
			result = fun.read()
		self.assertEqual(DATA, result, result)
	def test_seek_tell(self):
		"""Test that you can change the cursor position of a mongo file."""
		with MongoFile("full", mode="r", **DB_ARGS) as full:
			full.seek(12)
			abs_tell = full.tell()
			full.seek(-12, 2)
			rear_tell = full.tell()
			full.seek(3, 1)
			rel_tell = full.tell()
		with open("full", mode="r") as full:
			full.seek(12)
			fabs_tell = full.tell()
			full.seek(-12, 2)
			frear_tell = full.tell()
			full.seek(3, 1)
			frel_tell = full.tell()
		self.assertEqual(abs_tell, fabs_tell, {"got": abs_tell, "exp": fabs_tell})
		self.assertEqual(rear_tell, frear_tell, {"got": rear_tell, "exp": frear_tell})
		self.assertEqual(rel_tell, frel_tell, {"got": rel_tell, "exp": frel_tell})
	def test_truncate(self):
		"""Test that opening a mongo file with mode w truncates the file."""
		MongoFile("full", mode="w", **DB_ARGS).close()
		with MongoFile("full", mode="r", **DB_ARGS) as full:
			result = full.read()
		open("full", mode="w").close()
		with open("full", mode="r") as full:
			file_result = full.read()
		self.assertEqual(file_result, result, {"got": result, "exp": file_result})
	def test_unicode(self):
		"""Test that we can write and read unicode to/from a mongo file."""
		uchr = u'\xae'
		with MongoFile("empty", mode="w", **DB_ARGS) as afile:
			afile.write(uchr)
		with MongoFile("empty", mode="r", **DB_ARGS) as afile:
			result = afile.read()
		self.assertEqual(uchr, result, {"got": result, "exp": uchr})
	def test_write(self):
		"""Test that you can write to a mongo file."""
		with MongoFile("empty", mode="w", **DB_ARGS) as empty:
			empty.write("12345")
		with open("empty", mode="w") as empty:
			empty.write("12345")
		with MongoFile("empty", mode="r", **DB_ARGS) as empty:
			result = empty.read()
		with open("empty", mode="r") as empty:
			file_result = empty.read()
		self.assertEqual(file_result, result, {"got": result, "exp": file_result})
