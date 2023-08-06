# -*- coding: utf-8 -*-

"""
tests.py

Created by Michael Smith on 2012-06-21.
Copyright © 2012 True Action Network. All rights reserved.
"""

from tmpfile import NamedTemporaryFile, TemporaryFile
from unittest import TestCase
import csv
try:
	from . import MongoFile
except ImportError:
	from trueaction.mongofile import MongoFile

DATA = """Four score and seven years ago our fathers brought forth
upon this continent, a new nation, conceived in Liberty, and
dedicated to the proposition that all men are created equal."""
CSVDATA = [row.split() for row in DATA.split('\n')]

class MongoFileTest(TestCase):
	"""Test cases for Mongo File"""
	def test_can_write(self):
		with MongoFile('tmp', 'test', mode="w", db_name="test") as mfile:
			mfile.write(DATA)
		with MongoFile('tmp', 'test', mode='r', db_name="test") as mfile:
			got = mfile.read()
		self.assertEqual(DATA, got, got)
