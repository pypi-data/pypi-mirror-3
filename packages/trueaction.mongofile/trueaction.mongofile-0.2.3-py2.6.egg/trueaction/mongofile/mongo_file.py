# -*- coding: utf-8 -*-

"""
file.py

Created by Michael Smith on 2012-06-21.
Copyright © 2012 True Action Network. All rights reserved.
"""

from contextlib import closing
from io import RawIOBase
from pymongo import Connection
from os import SEEK_CUR, SEEK_END, SEEK_SET

# TODO: Index on name

def valid_name(db_name="", connection_args=None):
	"""Validate database name argument."""
	try:
		return db_name or connection_args['host'].split('/')[3]
	except (IndexError, KeyError, TypeError):
		msg = "Cannot parse database name: Please specify a database name or a full mongodb URI."
		raise TypeError(msg)

def remove(name, collection_name, db_name="", connection_args=None):
	"""Remove a Mongo File from the database."""
	connection_args = dict(connection_args or {})
	db_name = valid_name(db_name, connection_args)
	with closing(Connection(**connection_args)) as conn:
		conn[db_name][collection_name].remove({"name": name}, multi=True)

def rename(old_name, new_name, collection_name, db_name="", connection_args=None):
	"""Move or rename a mongo file."""
	connection_args = dict(connection_args or {})
	db_name = valid_name(db_name, connection_args)
	with closing(Connection(**connection_args)) as conn:
		conn[db_name][collection_name].update(
			spec     = {"name": old_name},
			document = {"$set": {"name": new_name}},
			multi    = True,
		)

def exists(name, collection_name, db_name="", connection_args=None):
	"""Return True if the name exists in mongo."""
	connection_args = dict(connection_args or {})
	db_name = valid_name(db_name, connection_args)
	with closing(Connection(**connection_args)) as conn:
		return bool(conn[db_name][collection_name].find_one({"name": name}))

class MongoFile(RawIOBase):
	"""
	A file-like object that stores file data to mongodb.

	The data goes in a single collection and looks like:
	{
		"name": "/some/file/path",
		"data": "The data"
	}
	"""
	def __init__(self, name, collection_name, mode="r", db_name="", connection_args=None):
		"""Create a mongodb connection we can reuse."""
		super(MongoFile, self).__init__()
		self.name = name
		self._cursor = 0
		connection_args = dict(connection_args or {})
		self.connection = Connection(**connection_args)
		db_name = valid_name(db_name, connection_args)
		self.database = self.connection[db_name]
		self.collection = self.database[collection_name]
		if set(mode).intersection("rwa"):
			self.mode = mode
			self.readonly = mode == 'r'
			self.writeonly = mode == 'w'
			if 'r' == mode:
				if 0 == len(list(self.collection.find(self._spec))):
					raise IOError("No such mongo file: '%s'" % name)
			if 'w' == mode:
				self.truncate()
		else:
			raise ValueError("mode string must be one of 'r', 'w', 'a', not '%s'" % mode)
	def _collect(self):
		"""Return the unnormalized contents of the already stored/unbuffered data."""
		for doc in self.collection.find(self._spec):
			if "data" in doc:
				yield doc["data"]
	@property
	def _doc(self):
		"""Return concatenated data from documents with the same name."""
		return "".join(self._collect())
	def _normalize(self):
		"""
		Remove duplicate documents with the same filename and
		replace with a single joined document.
		Return the single joined document.
		"""
		buf = self._doc
		self.collection.remove(self._spec, multi=True)
		self.collection.insert({
			"name": self.name,
			"data": buf,
		}, safe=True)
		return buf
	@property
	def _spec(self):
		"""Convenience property for looking up file in MongoDB."""
		return {"name": self.name}
	@property
	def _stored_size(self):
		"""Return the size of data stored in MongoDB."""
		return sum(len(doc) for doc in self._collect())
	def close(self):
		"""
		Disconnect and release all resources. After calling close(),
		you cannot read or write any more files with this MongoFile.
		"""
		self.connection.close()
		del self.connection
		super(MongoFile, self).close()
	def flush(self):
		"""Normalize. Later on, maybe this will flush a buffer."""
		self._normalize()
	def read(self, limit=-1):
		"""
		Return the entire contents of this instance
		from the cursor position up to size bytes or the end.
		"""
		if self.readable():
			pos = self.tell()
			result = "".join(self._collect())
			if limit < 0:
				self.seek(1 + limit, SEEK_END)
			else:
				self.seek(limit, SEEK_CUR)
			newpos = self.tell()
			result = result[pos:newpos]
			try:
				return bytes(result)
			except UnicodeEncodeError:
				return result
		else:
			raise IOError("MongoFile '%s' is not readable." % self.name)
	def readable(self):
		"""Return True if this instance can be read from."""
		return set('r+').intersection(self.mode) and not self.closed
	def seek(self, offset, whence=SEEK_SET):
		"""Move the cursor to the given offset, relative to whence."""
		if whence == SEEK_SET:
			start = 0
		elif whence == SEEK_CUR:
			start = self._cursor
		elif whence == SEEK_END:
			start = self._stored_size
		self._cursor = start + offset
	def tell(self):
		"""Return the current cursor position."""
		return self._cursor
	def truncate(self, size=None):
		"""Resize the stream to the given size in bytes. Return the new size."""
		if self.writable():
			size = self._cursor if size is None else size
			buf = self._normalize()[:size]
			self.collection.remove(self._spec, multi=True)
			self.collection.insert({
				"name": self.name,
				"data": buf,
			}, safe=True)
		else:
			raise IOError("MongoFile '%s' is not writable." % self.name)
		return 0
	def write(self, data):
		"""
		Write the given bytes to the underlying raw stream.
		Return the number of bytes written.
		"""
		if self.writable():
			size = len(data)
			self.collection.insert({
				"name": self.name,
				"data": data,
			}, safe=True)
		else:
			raise IOError("MongoFile '%s' is not writable." % self.name)
		return size
	def writable(self):
		"""Return True if the stream is opened in a writable mode."""
		return set('aw+').intersection(self.mode) and not self.closed
