# -*- coding: utf-8 -*-

"""
file.py

Created by Michael Smith on 2012-06-21.
Copyright © 2012 True Action Network. All rights reserved.
"""

from contextlib import closing
from io import BufferedIOBase
from os import SEEK_CUR, SEEK_END, SEEK_SET
from pymongo import Connection
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

class MongoFile(BufferedIOBase):
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
		connection_args = dict(connection_args or {})
		self.connection = Connection(**connection_args)
		try:
			db_name = db_name or connection_args['host'].split('/')[3]
		except (KeyError, IndexError):
			raise TypeError("Cannot parse database name: Please specify a database name or a full mongodb URI.")
		self.database = self.connection[db_name]
		self.collection = self.database[collection_name]
		if mode[0] in "rwaU":
			self.mode = mode
			self.readonly = mode[0] == 'r' and '+' not in mode
			self.writeonly = mode[0] == 'w' and '+' not in mode
			if 'w' == mode[0]:
				self.truncate()
		else:
			raise ValueError("mode string must begin with one of 'r', 'w', 'a' or 'U', not '%s'" % mode)
		self._buf = None
		self._cursor_location = 0
	@property
	def _buflen(self):
		"""The size of the current buffer."""
		return getattr(self.buf, 'len', len(self.buf.getvalue()))
	def _newbuf(self, tell=0):
		"""Generate and return a new buffer."""
		try:
			self._buf.close()
		except AttributeError:
			pass
		self._buf = None
		newbuf = self.buf
		newbuf.seek(tell)
		return newbuf
	def _normalize(self):
		"""
		Remove duplicate documents with the same filename and
		replace with a single joined document.
		"""
		buf = ''.join(fileinfo['data'] for fileinfo in self.collection.find(self._spec))
		self.collection.remove(self._spec)
		self.collection.insert({
			"name": self.name,
			"data": buf
		})
	@property
	def _spec(self):
		"""Convenience property for looking up file in MongoDB."""
		return {"name": self.name}
	@property
	def buf(self):
		"""Get the buffer if it exists, or initialize one."""
		if not getattr(self, '_buf', None):
			doc = self.collection.find_one(self._spec)
			if self.readonly and doc and "data" in doc:
				self._buf = StringIO(doc["data"])
			else:
				self._buf = StringIO()
		return self._buf
	@buf.deleter
	def buf(self):
		"""Close and delete the buffer."""
		if self._buf:
			self._buf.close()
		del self._buf
	def close(self):
		"""
		Disconnect and release all resources. After calling close(),
		you cannot read or write any more files with this MongoFile.
		"""
		self.flush()
		del self.buf
		self.connection.close()
		del self.connection
	def flush(self):
		"""Write the buffered data directly to the collection."""
		if self._buf and not (self._buf.closed or self.readonly):
			existing_size = self._normalize()
			if self._cursor_location < existing_size:
				doc = self.collection.find_one(self._spec)
				with closing(StringIO()) as innerbuf:
					if doc and "data" in doc:
						innerbuf.write(doc["data"])
					innerbuf.seek(self._cursor_location)
					val = self.buf.getvalue()
					self._cursor_location += len(val)
					innerbuf.write(val)
					self.collection.remove(self._spec)
					self.collection.insert({
						"name": self.name,
						"data": innerbuf.getvalue()
					})
			else:
				val = self.buf.getvalue()
				self._cursor_location += len(val)
				self.collection.insert({
					"name": self.name,
					"data": val
				})
			self._normalize()
			self._newbuf()
	def read(self, limit=-1):
		"""
		Return the entire contents of this instance
		from the cursor position up to size bytes or the end.
		"""
		if self.readable():
			return self.buf.read(limit)
		else:
			raise IOError("MongoFile '%s' is not readable." % self.name)
	def readable(self):
		"""Return True if this instance can be read from."""
		return set('r+').intersection(self.mode) and not self.closed
	def readline(self, limit=-1):
		"""Read and return one line from the stream."""
		if self.readable():
			return self.buf.readline(limit)
		else:
			raise IOError("MongoFile '%s' is not readable." % self.name)
	def readlines(self, limit=-1):
		"""read and return a list of lines from the stream."""
		if self.readable():
			return self.buf.readlines(limit)
		else:
			raise IOError("MongoFile '%s' is not readable." % self.name)
	def remove(self):
		"""Delete this file."""
		if self.writable():
			self.collection.remove(self._spec)
		self.buf.close()
	def rename(self, new_name):
		"""Move or rename a mongo file."""
		if self.writable():
			self.collection.update(self._spec, {"$set": {"name":new_name}}, multi=True)
			self.name = new_name
		else:
			raise IOError("MongoFile '%s' is not writable." % self.name)
	def reset(self):
		"""Reset the buffer and set the cursor at 0."""
		self.seek(0)
	def seek(self, offset, whence=None):
		"""Change the stream position to the given byte offset."""
		if whence is None:
			self.buf.seek(offset)
		else:
			self.buf.seek(offset, whence)
	def tell(self):
		"""Return the current stream position."""
		return self.buf.tell()
	def truncate(self):
		"""Resize the stream to the given size in bytes. Return the new size."""
		if self.writable():
			self._newbuf()
			self.collection.remove(self._spec)
		else:
			raise IOError("MongoFile '%s' is not writable." % self.name)
		return self._buflen
	def write(self, data):
		"""Write the given bytes to the underlying raw stream and return the number of bytes written."""
		if self.writable():
			size = self.buf.write(data)
			self.flush()
		else:
			raise IOError("MongoFile '%s' is not writable." % self.name)
		return size
	def writable(self):
		"""Return True if the stream is opened in a writable mode."""
		return set('aw+').intersection(self.mode) and not self.closed
	def writelines(self, lines):
		"""Write a list of lines to the stream. Line separators are not added."""
		if self.writable():
			self.buf.writelines(lines)
			self.flush()
		else:
			raise IOError("MongoFile '%s' is not writable." % self.name)
