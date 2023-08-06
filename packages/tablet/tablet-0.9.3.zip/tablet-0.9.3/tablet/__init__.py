#!/usr/bin/env python
#-------------------------------------------------------------------------------
# Author:      Cho-Yi Chen, ntu.joey@gmail.com
# Created:     2008/06/08
#-------------------------------------------------------------------------------
"""A tool for manipulating text spreadsheet and table data in Python.
"""
__author__ = "Cho-Yi Chen, ntu.joey@gmail.com"
__date__ = "2012-07-23"
__revision__ = "0.9.3"

class Table(object):
	"""Table is a data structure for storing tabular data.
	
	A text table can be easily read as a Table instance.
	
	>>> import tablet as T
	>>> t1 = T.read('demo.tsv', title='demo table 1')
	
	Now, t1 is a Table instance. For more details, see help page of read().
	
	We can see its content by method show().
	
	>>> t1.show()
	demo table 1
	H ['HA', 'HB', 'HC', 'HD', 'HE']
	0 ['A1', 'B1', 'C1', 'D1', 'E1']
	1 ['A2', 'B2', 'C2', 'D2', 'E2']
	2 ['A3', 'B3', 'C3', 'D3', 'E3']
	3 ['A4', 'B4', 'C4', 'D4', 'E4']
	4 ['A5', 'B5', 'C5', 'D5', 'E5']
	5 ['A6', 'B6', 'C6', 'D6', 'E6']
	6 ['A7', 'B7', 'C7', 'D7', 'E7']
	7 ['A8', 'B8', 'C8', 'D8', 'E8']
	8 ['A9', 'B9', 'C9', 'D9', 'E9']
	
	We can also get its source file path.
	
	>>> t1.path
	'demo.tsv'
	
	We can easily get a row by its row index.
	
	>>> t1.row[0]
	['A1', 'B1', 'C1', 'D1', 'E1']
	
	If we indicate the key column index, we can also get a row by key name.
	
	>>> t1.key_col = 0
	>>> t1.row_dict['A1']
	['A1', 'B1', 'C1', 'D1', 'E1']
	
	In terms of column, the key row is always the header.
	
	>>> t1.col[0]
	('A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9')
	>>> t1.col_dict['HA']
	('A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9')
	
	We may access the table header by member variable 'header'.
	Plz note that once the header changes, so does the col_dict.
	
	>>> t1.header
	['HA', 'HB', 'HC', 'HD', 'HE']
	>>> t1.header = ['Ha', 'Hb', 'Hc', 'Hd', 'He']
	>>> t1.header
	['Ha', 'Hb', 'Hc', 'Hd', 'He']
	>>> t1.col_dict['Ha']
	('A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9')
	
	"""
	
	def __init__(self, width=0, height=0, fill='', title=''):
		"""Initialize a Table object.
		
		width -- How many fields in a row
		height -- How many fields in a col
		fill -- What string to fill in the new fields
		title -- The title of this table
		"""
		# private variables
		self._data = []
		self._header = []
		self._key_col = None
		#self._factor_col = None
		# public constant (should not be directly modified by users)
		self.row = []
		self.col = []
		self.row_dict = None
		self.col_dict = None
		# public variables
		self.path = ''
		self.title = title
		# initialize
		self.expand(width, height, fill)
		self._sync()
		self._build_dict()
	
	def _sync(self):
		"""Synchronize internal _data to row & col."""
		if self._data:
			self.row = self._data
			self.col = zip(*self._data)
	
	def _build_dict(self):
		"""Build the row_dict & col_dict from key_col & header, repectively."""
		if self._key_col != None and self.col:
			self.row_dict = dict(zip(self.col[self._key_col], self.row))
		if self._header:
			self.col_dict = dict(zip(self._header, self.col))
	
	def __getitem__(self, key):
		"""Support [rows, cols] operators.
		
		key -- rows and cols can either be an int, str, or slice.
		
		>>> t = read('demo.tsv')
		>>> t[0,1]
		'B1'
		>>> t[0][1]
		'B1'
		>>> t.key_col = 0
		>>> t['A1',1]
		'B1'
		>>> t['A2',-1]
		'E2'
		>>> t[1]
		['A2', 'B2', 'C2', 'D2', 'E2']
		>>> t[1,:]
		['A2', 'B2', 'C2', 'D2', 'E2']
		>>> t['A2',:]
		['A2', 'B2', 'C2', 'D2', 'E2']
		>>> t['HB']
		('B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9')
		>>> t[:,'HB']
		['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9']
		>>> t[:,1]
		['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9']
		>>> t[:,-1]
		['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9']
		"""
		if isinstance(key, int) or isinstance(key, slice):
			# the key is a single row index/slice (compatible w/numpy)
			return self._data[key]
		if isinstance(key, str):
			# the key is a column name (compatible w/numpy)
			return self.col_dict[key]
		# from now on, the key should be a (x,y) tuple
		x,y = key
		# translate a string index into an int index
		if isinstance(x, str):
			x = self.get_row_index(x, self.key_col)
		if isinstance(y, str):
			y = self.get_col_index(y)
		# slices return 1-d or 2-d list
		if isinstance(x, slice) or isinstance(y, slice):
			return [row[y] for row in self.row[x]]
		# both row & col are single index -> return an element
		else:
			return self._data[x][y]
	
	def __str__(self):
		"""Return the header & data as python string format"""
		return self.text()
	
	def __iter__(self):
		"""Iterator over the rows in the table"""
		return iter(self._data)
	
	def _get_width(self):
		"""Get width of the table."""
		return len(self._data[0]) if self._data else 0
	
	def _get_height(self):
		"""Get height of the table."""
		return len(self._data)
	
	def _get_shape(self):
		"""Get the shape of the table."""
		return self.width, self.height
	
	def _get_header(self):
		"""Get the header of the table."""
		return self._header
	
	def _set_header(self, header):
		"""Set the header ot the table.
		
		header -- a list/tuple of column names.
		"""
		assert isinstance(header, (list, tuple)), "header must be a list/tuple."
		self._header = map(str, header)
		self._build_dict()
	
	def _get_key_col(self):
		"""Get current key column index."""
		return self._key_col
	
	def _set_key_col(self, name):
		"""Set current key column index/name.
		
		name -- a column index (int) or a column name (str).
		
		>>> t1 = read('demo.tsv', key_col=0)
		>>> t1.row_dict['A2']
		['A2', 'B2', 'C2', 'D2', 'E2']
		>>> t1.key_col = 1
		>>> t1.row_dict['B2']
		['A2', 'B2', 'C2', 'D2', 'E2']
		>>> t1.key_col = 'HC'
		>>> t1.row_dict['C2']
		['A2', 'B2', 'C2', 'D2', 'E2']
		"""
		if name == None:
			self._key_col = None
		else:
			self._key_col = self.get_col_index(name)
		self._build_dict()
	
#	def _get_factor_col(self):
#		"""Get current factor column index."""
#		return self._factor_col
	
#	def _set_factor_col(self, name):
#		"""Set current factor column index/name"""
#		self._factor_col = self.get_col_index(name)
	
	width = property(_get_width, doc="Width of the table. (Read only)")
	height = property(_get_height, doc="Height of the table. (Read only)")
	shape = property(_get_shape, doc="Shape of the table. (Read only)")
	header = property(_get_header, _set_header, doc="Header of the table")
	key_col = property(_get_key_col, _set_key_col, doc="Key column index")
	#factor_col = property(_get_factor_col, _set_factor_col, doc="Factor column index")

# End of private part
#-------------------------------------------------------------------------------
# Start of public part

	def add_col(self, col, colname='', fill=''):
		"""Add a column to current table.
		
		col -- a list of string as a column.
		colname -- add the colname to current header.
		fill -- what string to be filled when the col is too short.
		
		Change in place. Return self table.
		
		NOTE: If the col is longer than table height, it will be shrink
		to current height; if shorter, if will be extended with fill.
		
		NOTE: If there are many cols to add, consider use paste_right()
		
		>>> Table().add_col(['a', 'b'], '1st col').show()
		H ['1st col']
		0 ['a']
		1 ['b']
		
		>>> Table(3,3,'a').add_col(['b', 'b']).show()
		0 ['a', 'a', 'a', 'b']
		1 ['a', 'a', 'a', 'b']
		2 ['a', 'a', 'a', '']
		
		>>> Table(2,2,'a').add_col(range(3)).show()
		0 ['a', 'a', 0]
		1 ['a', 'a', 1]
		
		>>> read('demo.tsv').add_col(range(10), 'ADD').show()
		H ['HA', 'HB', 'HC', 'HD', 'HE', 'ADD']
		0 ['A1', 'B1', 'C1', 'D1', 'E1', 0]
		1 ['A2', 'B2', 'C2', 'D2', 'E2', 1]
		2 ['A3', 'B3', 'C3', 'D3', 'E3', 2]
		3 ['A4', 'B4', 'C4', 'D4', 'E4', 3]
		4 ['A5', 'B5', 'C5', 'D5', 'E5', 4]
		5 ['A6', 'B6', 'C6', 'D6', 'E6', 5]
		6 ['A7', 'B7', 'C7', 'D7', 'E7', 6]
		7 ['A8', 'B8', 'C8', 'D8', 'E8', 7]
		8 ['A9', 'B9', 'C9', 'D9', 'E9', 8]
		"""
		W = self.width
		H = self.height
		if H == 0:
			# current table is empty
			self._data = [[x] for x in col]
		else:
			# cut to hight when inserted col is longer, else extend it
			col = col[:H] if len(col) >= H else col + [fill] * (H - len(col))
			for i,row in enumerate(self._data):
				row.append(col[i])
		if self._header:
			self._header.append(colname)
		elif colname:
			self._header = [''] * W + [colname]
		self._sync()
		self._build_dict()
		return self
	
	def add_row(self, row, fill=''):
		"""Add a row to current table.
		
		row -- a list of string as a column.
		fill -- what string to be filled when the row is too short.
		
		Change in place. Return self table.
		
		NOTE: If the row is longer than table width, it will be shrink
		to current width; if shorter, if will be extended with fill.
		
		NOTE: If there are many rows to add, consider use paste_below()
		
		>>> Table(3,2,'a').add_row(['b', 'b']).show()
		0 ['a', 'a', 'a']
		1 ['a', 'a', 'a']
		2 ['b', 'b', '']
		
		>>> Table(2,2,'a').add_row(range(3)).show()
		0 ['a', 'a']
		1 ['a', 'a']
		2 [0, 1]
		
		>>> read('demo.tsv').add_row(map(str, range(10, 15))).show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A1', 'B1', 'C1', 'D1', 'E1']
		1 ['A2', 'B2', 'C2', 'D2', 'E2']
		2 ['A3', 'B3', 'C3', 'D3', 'E3']
		3 ['A4', 'B4', 'C4', 'D4', 'E4']
		4 ['A5', 'B5', 'C5', 'D5', 'E5']
		5 ['A6', 'B6', 'C6', 'D6', 'E6']
		6 ['A7', 'B7', 'C7', 'D7', 'E7']
		7 ['A8', 'B8', 'C8', 'D8', 'E8']
		8 ['A9', 'B9', 'C9', 'D9', 'E9']
		9 ['10', '11', '12', '13', '14']
		"""
		W = self.width
		row = row[:W] if len(row) >= W else row + [fill] * (W - len(row))
		self._data.append(row)
		self._sync()
		self._build_dict()
		return self
		
	def aggregate(self, factor_col):
		"""Aggregate the table into a dict of rows.
		
		Grouped by factor column.
		
		Return a dict (keys are factors).
		"""
		D = {}
		i = self.get_col_index(factor_col)
		for row in self._data:
			D.setdefault(row[i], []).append(row)
		return D
	
	def copy(self, title=''):
		"""Return a new copy from currrent table.
		
		title -- the title of new table.
		
		>>> t1 = read('demo.tsv')
		>>> t2 = t1.copy()
		>>> print str(t1) == str(t2)
		True
		"""
		from copy import deepcopy
		ncopy = Table(title=title)
		ncopy._header = list(self.header)
		ncopy._data = deepcopy(self._data)
		ncopy._key_col = self._key_col
		ncopy._sync()
		ncopy._build_dict()
		return ncopy
	
	def cut_cols(self, names, title=''):
		"""Extracts cols from table with name or index.
		
		names -- column indexs or column names.
		title -- title for new table.
		
		Return new table.
		
		>>> t3 = read('demo3.tsv')
		>>> t3.cut_cols([1, 2]).show()
		H ['p1', 'p2']
		0 ['1', '4']
		1 ['2', '5']
		2 ['3', '6']
		>>> t3.cut_cols(['p1', 'p2']).show()
		H ['p1', 'p2']
		0 ['1', '4']
		1 ['2', '5']
		2 ['3', '6']
		"""
		assert isinstance(names, (list, tuple, set)), 'invalid names type.'
		# get column indexes
		I = map(self.get_col_index, names)
		# deal with data
		data = [[row[i] for i in I] for row in self._data]
		# deal with header
		header = [self._header[i] for i in I] if self._header else []
		return new(data, header, title=title)
	
	def cut_rows(self, keys, key_col=None, title='', uniq=False):
		"""Extract rows from table at specific indexes and return them.
		
		keys -- the keys to search in key column field.
		key_col -- key column index/name for the keys to be searched.
		           If None, keys must be indexes.
		title -- title of new table.
		uniq -- if there are many rows with the same key,
		        only cut the first one when uniq is True.
		
		Return a new table composed of cut rows, old header, 
		and old key_col from the original table.
		NOTE: When uniq is False, all key-matched rows will be cutted.
		
		>>> t1 = read('demo.tsv')
		>>> t1.cut_rows([1, 2]).show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A2', 'B2', 'C2', 'D2', 'E2']
		1 ['A3', 'B3', 'C3', 'D3', 'E3']
		>>> t1.cut_rows(['A2', 'A3'], key_col=0).show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A2', 'B2', 'C2', 'D2', 'E2']
		1 ['A3', 'B3', 'C3', 'D3', 'E3']
		>>> t1.cut_rows(['A2', 'A3'], key_col='HA').show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A2', 'B2', 'C2', 'D2', 'E2']
		1 ['A3', 'B3', 'C3', 'D3', 'E3']
		"""
		assert isinstance(keys, (list, tuple, set)), 'invalid keys type.'
		if uniq:
			# Version 1. Only the 1st key matched row will be found.
			I = [self.get_row_index(k, key_col) for k in keys]
		else:
			# Version 2. All key matched row will be found.
			I = self.get_row_indexes(keys, key_col=key_col)
		data = [self.row[i] for i in I]
		return new(data, self.header, title=title)
	
	def del_col(self, name):
		"""Delete column with name in names.
		
		name -- an index or name
		
		Change in place. Return self table.
		
		>>> read('demo2.tsv').del_col('B1').del_col('B3').show()
		H ['B2']
		0 ['b']
		1 ['b']
		2 ['b']
		"""
		return self.del_cols((name,))
	
	def del_cols(self, names):
		"""Delete column with name in names.
		
		names -- a container of indexes/names
		
		Change in place. Return self table.
		
		>>> read('demo2.tsv').del_cols(['B1', 'B3']).show()
		H ['B2']
		0 ['b']
		1 ['b']
		2 ['b']
		"""
		assert isinstance(names, (list, tuple, set)), 'invalid name type.'
		# get column indexes (sort from large index to small index)
		I = sorted(map(self.get_col_index, names), reverse=True)
		# deal with data; delete from tail to head
		for row in self._data:
			for i in I:
				del row[i]
		# deal with header
		if self._header:
			for i in I:
				del self._header[i]
		self._sync()
		self._build_dict()
		return self
	
	def del_row(self, i, key_col=None):
		"""Delete row[i] in internal data of current table.
		
		i -- if i is index, delete row[i]. 
		     If i is key, delete the row with key in key column.
		key_col -- the column with keys. (useless when i is index)
		
		Change in place. Return self table.
		
		>>> read('demo.tsv').del_row(0).show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A2', 'B2', 'C2', 'D2', 'E2']
		1 ['A3', 'B3', 'C3', 'D3', 'E3']
		2 ['A4', 'B4', 'C4', 'D4', 'E4']
		3 ['A5', 'B5', 'C5', 'D5', 'E5']
		4 ['A6', 'B6', 'C6', 'D6', 'E6']
		5 ['A7', 'B7', 'C7', 'D7', 'E7']
		6 ['A8', 'B8', 'C8', 'D8', 'E8']
		7 ['A9', 'B9', 'C9', 'D9', 'E9']
		>>> read('demo.tsv').del_row('A1', 0).show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A2', 'B2', 'C2', 'D2', 'E2']
		1 ['A3', 'B3', 'C3', 'D3', 'E3']
		2 ['A4', 'B4', 'C4', 'D4', 'E4']
		3 ['A5', 'B5', 'C5', 'D5', 'E5']
		4 ['A6', 'B6', 'C6', 'D6', 'E6']
		5 ['A7', 'B7', 'C7', 'D7', 'E7']
		6 ['A8', 'B8', 'C8', 'D8', 'E8']
		7 ['A9', 'B9', 'C9', 'D9', 'E9']
		"""
		self.del_rows((i,), key_col=key_col)
		return self
	
	def del_rows(self, keys, key_col=None, uniq=False):
		"""Delete rows from table with keys in their key column.
		
		keys -- a container of key strings or row indexes.
		key_col -- the index of the column with keys.
		           If None, keys must be row indexes.
		uniq -- if there are many rows with a same key, 
		        delete the 1st row when uniq is True.
		
		Change in place. Return self table.
		NOTE: When uniq is False, all key-matched rows will be deleted.
		
		>>> read('demo.tsv').del_rows(['A1', 'A3', 'A5', 'A7'], 0).show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A2', 'B2', 'C2', 'D2', 'E2']
		1 ['A4', 'B4', 'C4', 'D4', 'E4']
		2 ['A6', 'B6', 'C6', 'D6', 'E6']
		3 ['A8', 'B8', 'C8', 'D8', 'E8']
		4 ['A9', 'B9', 'C9', 'D9', 'E9']
		"""
		assert isinstance(keys, (list, tuple, set)), "Invalid keys type"
		if uniq:
			# Version 1. Only the 1st key matched row will be found.
			I = [self.get_row_index(k, key_col) for k in keys]
		else:
			# Version 2. All key-matched row will be found.
			I = self.get_row_indexes(keys, key_col)
		# del row from tail to head
		for i in sorted(I, reverse=True):
			del self._data[i]
		self._sync()
		self._build_dict()
		return self
	
	def expand(self, width=None, height=None, fill=''):
		"""Expand the current table to rows x cols.
		
		width -- How many fields in a row
		height -- How many fields in a col
		fill -- What string to fill in the new fields
		
		Expand in place and self table is also returned.
		
		NOTE: When width and height are None, it will try to 
		maintance internal _data square to the longest row.
		
		>>> Table(2, 2, 'a').expand(3, 3, 'b').show()
		0 ['a', 'a', 'b']
		1 ['a', 'a', 'b']
		2 ['b', 'b', 'b']
		"""
		fill = str(fill)
		dirty = False
		if width == None and height == None:
			# square the _data
			width = max([len(row) for row in self._data])
			height = self.height
		for i in xrange(height):
			if i < self.height:
				diff = width - len(self._data[i])
				if diff > 0:
					self._data[i].extend([fill] * diff)
					dirty = True
			else:
				self._data.append([fill] * max(width, self.width))
				dirty = True
		if dirty:
			self._sync()
			self._build_dict()
		return self
	
	def fill(self, stuff):
		"""Fill the stuff to each empty string field.
		
		stuff -- a string to fill in each empty fields. e.g., '0', '-' or "Blank"
		
		Replace in place and return self table.
		
		>>> Table(2, 2).fill('b').show()
		0 ['b', 'b']
		1 ['b', 'b']
		"""
		return self.replace("", str(stuff))
	
	def get_col(self, name, type=None):
		"""Get column with specific type.
		
		name -- column index or name
		type -- python data type for that elements in that col
		
		Return the col in the type.
		
		>>> read('demo3.tsv').get_col(1, int)
		[1, 2, 3]
		>>> read('demo3.tsv').get_col('p2', float)
		[4.0, 5.0, 6.0]
		"""
		i = self.get_col_index(name)
		return map(type, self.col[i]) if type else self.col[i]
	
	def get_col_index(self, name):
		"""Get the column index from name.
		
		name -- can be index(int) or name(str).
		
		Return the corresponding column index.
		
		>>> t1 = read('demo.tsv')
		>>> t1.get_col_index(1)
		1
		>>> t1.get_col_index('HB')
		1
		"""
		if isinstance(name, int):
			assert name < self.width, 'column index out of range.'
			return name
		else:
			assert name != None, 'column name should not be None.'
			assert self._header, 'current table has no header.'
			assert name in self._header, 'column name not in header.'
			return self._header.index(name)
	
	def get_row(self, key, key_col=None, type=None):
		"""Get row with specific type.
		
		key -- row index or key string.
		key_col -- column index or name for key column.
		type -- python data type for that elements in that row.
		
		Return the row in the type.
		NOTE: Only the 1st key-matched row will be found.
		
		>>> t3 = read('demo3.tsv')
		>>> t3.cut_cols([1,2,3]).get_row(0)
		['1', '4', '7']
		>>> t3.cut_cols([1,2,3]).get_row(0, type=int)
		[1, 4, 7]
		"""
		i = self.get_row_index(key, key_col=key_col)
		return map(type, self.row[i]) if type else self.row[i]
	
	def get_row_index(self, key, key_col=None):
		"""Get the row index from key.
		
		key -- can be row index(int) or key name(str).
		       If the key is index, key_col is useless.
		key_col -- column index or name for key column.
		           If None, key must be index.
		
		NOTE: Only the 1st key-matched row index will be found.
		
		Return the corresponding row index (an integer).
		
		>>> t1 = read('demo.tsv')
		>>> t1.get_row_index(1)
		1
		>>> t1.get_row_index('A2', 0)
		1
		"""
		if isinstance(key, int):
			# key is an index
			assert key < self.height, 'key index out of range.'
			return key
		else:
			# key should be a string
			assert key_col != None, 'no key column assigned.'
			i = self.get_col_index(key_col)
			return self.col[i].index(key)
	
	def get_row_indexes(self, keys, key_col=None):
		"""Get the row indexes from keys.
		
		keys -- can be row indexes or key names.
		        If keys are indexes, key_col is useless.
		key_col -- column index or name for key column.
		           If None, keys must be indexes.
		
		NOTE: All key-matched row indexes will be found.
		
		Return the corresponding row indexes (an int list).
		
		>>> t1 = read('demo.tsv')
		>>> t1.get_row_indexes([1, 2])
		[1, 2]
		>>> t1.get_row_indexes(['A2', 'A3'], 0)
		[1, 2]
		>>> read('demo2.tsv').get_row_indexes(['b'], 0)
		[0, 1, 2]
		"""
		if not isinstance(keys, (list, tuple, set)):
			# It might be an int or string. Transform into an 1-element tuple.
			keys = (keys,)
		# divide the keys into int keys and str keys
		ints = set([k for k in keys if isinstance(k, int)])
		strs = set([k for k in keys if isinstance(k, str)])
		# for each int key, get its correponding index.
		indexes = set()
		for i in ints:
			assert i < self.height, 'key index %d out of range' % i
			indexes.add(i)
		# go through all rows, get correponding indexes for str keys.
		if strs:
			assert key_col != None, 'no key column assigned'
			ci = self.get_col_index(key_col)
			ids = set([i for i,row in enumerate(self._data) if row[ci] in strs])
			indexes.update(ids)
		return sorted(indexes)
	
	def insert_col(self, index, col, colname=None, fill=''):
		"""Insert the column at the index of current table.
		
		index -- the column index of the table.
		col -- insert column
		colname -- the name of the column
		fill -- what to fill when column length < self.height
		
		Change in place. Return self table.
		
		>>> read('demo1.tsv').insert_col(1, ['c', 'c'], 'HC').show()
		H ['A1', 'HC', 'A2']
		0 ['a', 'c', 'a']
		1 ['a', 'c', 'a']
		"""
		# deal with data
		if len(col) < self.height:
			col.extend([fill] * (self.height - len(col)))
		for i,row in enumerate(self._data):
			row.insert(index, col[i])
		# deal with header
		if self._header:
			if colname:
				self._header.insert(index, colname)
			else:
				self._header.insert(index, '')
		# sync
		self._sync()
		self._build_dict()
		return self
	
	def insert_row(self, index, row, fill=''):
		"""Insert the row at the index of current table.
		
		index -- the row index of the table.
		row -- insert row
		fill -- what to fill when column length < self.height
		
		Change in place. Return self table.
		
		>>> read('demo1.tsv').insert_row(1, ['c', 'c']).show()
		H ['A1', 'A2']
		0 ['a', 'a']
		1 ['c', 'c']
		2 ['a', 'a']
		"""
		# deal with row length
		if len(row) > self.width:
			row = row[:self.width]
		else:
			row.extend([fill] * (self.width - len(row)))
		# deal with data
		self._data.insert(index, row)
		self._sync()
		self._build_dict()
		return self
	
	def join(self, key_col, tableB):
		"""Join another table (tableB) to current table (tableA).
		
		key_col -- key column index/name in self table.
		           int for index, str for column name.
		tableB -- another table to lookup.
		
		For each key in key column of tableA, if the key is also in tableB.row_dict, 
		the corresponind row in tableB will be add after the row in tableA.
		
		Change in place and return self table back.
		
		>>> t1 = new([['A1', 'x', 'x'], ['A2', 'y', 'y']], ['1', '2', '3'])
		>>> t2 = read('demo.tsv', key_col=0)
		>>> t1.join(0, t2).show()
		H ['1', '2', '3', 'HB', 'HC', 'HD', 'HE']
		0 ['A1', 'x', 'x', 'B1', 'C1', 'D1', 'E1']
		1 ['A2', 'y', 'y', 'B2', 'C2', 'D2', 'E2']
		"""
		# make sure tableB has a row_dict
		assert tableB.row_dict, "tableB has no row_dict."
		Bkc = tableB.key_col
		# get self key column
		kcol = self.col[self.get_col_index(key_col)]
		# go through the key column, find each key in tableB
		for i,x in enumerate(kcol):
			row = tableB.row_dict.get(x, None)
			if row:
				self._data[i].extend(row[:Bkc] + row[Bkc+1:])
		# deal with header issue
		if tableB._header:
			if not self._header:
				self._header = [''] * self.width
			self._header.extend(tableB.header[:Bkc] + tableB.header[Bkc+1:])
		else:
			self._header.extend([''] * (tableB.width - 1))
		self.expand()
		self._sync()
		self._build_dict()
		return self
	
	def lookup(self, keys, key_col, value_col, type=None, uniq=False):
		"""Get all corresponding values in the key-matched rows.
		
		keys -- row indexes or row key names.
		key_col -- column index or name for key column.
		value_col -- the values in this column will be return.
		type -- set the type to return value list if not None.
		uniq -- if True, get only the first matched.
		
		Return the value list.
		NOTE: When uniq is False, all key-matched values will be found.
		
		>>> t3 = read('demo3.tsv')
		>>> t3.lookup(['g1', 'g3'], 0, 1)
		['1', '3']
		>>> t3.lookup(['g1', 'g3'], 'gene', 'p1', int)
		[1, 3]
		>>> read('demo2.tsv').lookup(['b'], 'B1', 'B2')
		['b', 'b', 'b']
		"""
		vc = self.get_col_index(value_col)
		if uniq:
			I = [self.get_row_index(k, key_col) for k in keys]
		else:
			I = self.get_row_indexes(keys, key_col)
		if type:
			return map(type, [self.row[i][vc] for i in I])
		else:
			return [self.row[i][vc] for i in I]
	
	def paste_below(self, T):
		"""Paste the table T to the bottom of current table.
		
		T -- a table instance.
		
		Change in place. Return self table.
		
		>>> t1 = read('demo1.tsv')
		>>> t2 = read('demo2.tsv')
		>>> t1.paste_below(t2).show()
		H ['A1', 'A2', 'B3']
		0 ['a', 'a', '']
		1 ['a', 'a', '']
		2 ['b', 'b', 'b']
		3 ['b', 'b', 'b']
		4 ['b', 'b', 'b']
		"""
		from copy import deepcopy
		# cope with header
		if len(self._header) < len(T._header):
			self._header.extend(T._header[len(self._header):])
		# cope with data
		self._data.extend(deepcopy(T._data))
		self.expand()
		# sync & rebuild dict
		self._sync()
		self._build_dict()
		return self
	
	def paste_right(self, T):
		"""Paste the table T to the right of current table.
		
		T -- a table instance.
		
		Change in place. Return self table.
		
		>>> t1 = read('demo1.tsv')
		>>> t2 = read('demo2.tsv')
		>>> t1.paste_right(t2).show()
		H ['A1', 'A2', 'B1', 'B2', 'B3']
		0 ['a', 'a', 'b', 'b', 'b']
		1 ['a', 'a', 'b', 'b', 'b']
		2 ['', '', 'b', 'b', 'b']
		"""
		# cope with header
		if self._header:
			if T._header:
				self._header.extend(T._header)
			else:
				self._header.extend([''] * T.width)
		# cope with data
		if T.height > self.height:
			self.expand(self.width, T.height)
		for i in xrange(self.height):
			if i < T.height:
				self._data[i].extend(T._data[i])
			else:
				self._data[i].extend([''] * T.width)
		self._sync()
		self._build_dict()
		return self
	
	def replace(self, old, new):
		"""Replace old string to new string in every field.
		
		old -- Old string to be replaced by a new one.
		new -- New string to replace the old one.
		
		Replace in place and self table is also returned.
		
		>>> Table(2, 2, 'a').replace('a', 'b').show()
		0 ['b', 'b']
		1 ['b', 'b']
		"""
		new = str(new)    # make sure 'new' is a string
		dirty = False
		for row in self._data:
			for i,x in enumerate(row):
				if x == old:
					row[i] = new
					dirty = True
		if dirty:
			self._sync()
			self._build_dict()
		return self
	
	def row_filter(self, fnct, title=''):
		"""Cut those rows passed the function (fnct).
		
		fnct -- A boolean function for input row.
		
		Return a table of cutted rows that passed the filter.
		
		>>> read('demo3.tsv').row_filter(lambda row: int(row[1]) < 3).show()
		H ['gene', 'p1', 'p2', 'p3']
		0 ['g1', '1', '4', '7']
		1 ['g2', '2', '5', '8']
		"""
		data = filter(fnct, self._data)
		return new(data, self.header, title=title)
	
	def show(self):
		"""Print every row in order. One row per line.
		Row indexes will be printed at the head of each line.
		Header will be marked 'H' at the start of line.
		
		>>> read('demo.tsv').show()
		H ['HA', 'HB', 'HC', 'HD', 'HE']
		0 ['A1', 'B1', 'C1', 'D1', 'E1']
		1 ['A2', 'B2', 'C2', 'D2', 'E2']
		2 ['A3', 'B3', 'C3', 'D3', 'E3']
		3 ['A4', 'B4', 'C4', 'D4', 'E4']
		4 ['A5', 'B5', 'C5', 'D5', 'E5']
		5 ['A6', 'B6', 'C6', 'D6', 'E6']
		6 ['A7', 'B7', 'C7', 'D7', 'E7']
		7 ['A8', 'B8', 'C8', 'D8', 'E8']
		8 ['A9', 'B9', 'C9', 'D9', 'E9']
		"""
		if self.title:
			print self.title
		if self.header:
			print 'H', self.header
		line_num_width = len(str(len(self._data))) - 1 #start from 0
		for i,row in enumerate(self._data):
			print str(i).rjust(line_num_width), row
	
	def sort(self, col=0, reverse=False):
		"""Sort table based on specific column.
		
		col -- sort by the col index(es) or name(s).
		reverse -- if True, sorted from large to small.
		
		Change in place. Return self.
		
		>>> read('demo3.tsv').sort(col=1, reverse=True).show()
		H ['gene', 'p1', 'p2', 'p3']
		0 ['g3', '3', '6', '9']
		1 ['g2', '2', '5', '8']
		2 ['g1', '1', '4', '7']
		"""
		if isinstance(col, int) or isinstance(col, str):
			# col is an index or col name
			from operator import itemgetter
			self._data.sort(key=itemgetter(self.get_col_index(col)), reverse=reverse)
		else:
			# col should be a container of indexes or col names
			indexes = [self.get_col_index(i) for i in col]
			self._data.sort(key=lambda x: [x[i] for i in indexes], reverse=reverse)
		self._sync()
		self._build_dict()
		return self
	
	def summary(self, cols=[], format='%.2f'):
		"""Return a summary table of selected columns.
		
		cols -- column indexes or names to print the summary.
		        If empty, use all columns.
		format -- output string format for mean/std/sum/max/min.
		
		Return the summary table.
		
		>>> read('demo3.tsv', title='demo3').summary((1,2,3)).show()
		Summary of demo3
		H ['class', 'number', 'mean', 'std', 'sum', 'max', 'min']
		0 ['p1', '3', '2.00', '0.82', '6.00', '3.00', '1.00']
		1 ['p2', '3', '5.00', '0.82', '15.00', '6.00', '4.00']
		2 ['p3', '3', '8.00', '0.82', '24.00', '9.00', '7.00']
		"""
		if not cols:
			data = self.col
			header = self.header
		else:
			I = map(self.get_col_index, cols)
			data = [self.col[i] for i in I]
			header = [self._header[i] for i in I]
		return summary(data, header, 'Summary of ' + self.title, format=format)
	
	def text(self, delim='\t', header=True, title=True):
		"""Return current table in raw text (str).
		
		delim -- delimiter of the table.
		header -- print table header or not.
		title -- print table title or not.
		"""
		out = []
		if title and self.title:
			out.append(self.title)
		if header and self._header:
			out.append(delim.join(map(str, self._header)))
		out.extend([delim.join(map(str, row)) for row in self._data])
		return '\n'.join(out)
	
	def to_array(self, type=str):
		from numpy import array
		return array(self._data, type)
	
	def to_html(self, path, header=True, border=0, cellpadding=3, cellspacing=3):
		out = ["<html><head>%s</head><body>" % self.title]
		out.append("<table border=%d cellpadding=%d cellspacing=%d>" % 
				(border, cellpadding, cellspacing))
		if header and self._header:
			out.append("<tr>")
			out.extend(["\t<th>%s</th>" % n for n in self._header])
			out.append("</tr>")
		for row in self._data:
			out.append("<tr>")
			out.extend(["\t<td>%s</td>" % n for n in row])
			out.append("</tr>")
		out.append("</table>")
		out.append("</body></html>")
		open(path, 'w').writelines('\n'.join(out))
	
	def to_wiki(self, path, header=True):
		out = []
		if header and self._header:
			out.append('^' + '^'.join(map(str, self._header)) + '^')
		out.extend(['|' + '|'.join(map(str, row)) + '|' for row in self._data])
		open(path, 'w').writelines('\n'.join(out))
	
	def write(self, path, mode='w', delim='\t', header=True, title=True):
		"""Write table to a text file.
		
		path -- File writing path
		mode -- File writing mode
		delim -- Delimiter of the table
		header -- Write header or not
		title -- Write title or not
		
		>>> data = [[1,2,3],[4,5,6]]
		>>> header = ['c1', 'c2', 'c3']
		>>> t1 = new(data, header)
		>>> t1.write("doctest.out.tsv")
		>>> t2 = read("doctest.out.tsv")
		>>> print str(t1) == str(t2)
		True
		"""
		# method 1: translate to text and write out
		out = self.text(delim=delim, header=header, title=title)
		open(path, mode).write(out)
		# method 2: write out line by line (for large table)
		#fp = open(path, mode)
		#if title and self.title:
		#	fp.write(self.title)
		#if header and self._header:
		#	fp.write(delim.join(map(str, self._header)) + '\n')
		#for row in self._data:
		#	fp.write(delim.join(map(str, row)) + '\n')
		#fp.close()

# End of class definition
#-------------------------------------------------------------------------------
# Start of public functions

def new(data, header=None, key_col=None, title=''):
	"""Return a Table object from a 2 dimension list/tuple.
	
	data -- a 2 dimension list/tuple (list/tuple of lists/tuples)
	header -- a string list
	key_col -- the key column index/name
	title -- Title of the table
	
	Return a new Table object.
	
	>>> data = [[1,2,3],[4,5,6]]
	>>> header = ['c1', 'c2', 'c3']
	>>> new(data, header).show()
	H ['c1', 'c2', 'c3']
	0 ['1', '2', '3']
	1 ['4', '5', '6']
	"""
	T = Table(title=title)
	# deal with header
	if header:
		assert isinstance(header, (list, tuple)), "header should be a list or tuple."
		T.header = map(str, header)
	# deal with data
	assert isinstance(data, (list, tuple)), "data should be a list or tuple."
	T._data = [map(str, row) for row in data]
	width = max([len(row) for row in data])
	height = len(data)
	T.expand(width, height)
	T._sync()
	T.key_col = key_col
	return T

def read(path, delim='\t', header=True, comment='#', key_col=None, title='', skip=0):
	"""Read a file to a table (list of string lists).
	
	path -- Input file path (supports .gz or .zip files)
	        ('clipboard' for reading Windows clipboard)
	delim -- Delimiter of the table
	header -- If true, the header will be the 1st row after skipped lines, 
	          comment lines, and empty lines in the file
	comment -- Initial character indicating comment lines before the table
	key_col -- Which column to be used as key column
	title -- Title of the table
	skip -- Skip first n lines in the file
	
	Return a Table object.
	"""
	data = []
	hdr = []
	# table file open
	if path == 'clipboard':
		import win32clipboard, cStringIO
		win32clipboard.OpenClipboard()
		d = win32clipboard.GetClipboardData()
		fp = cStringIO.StringIO(d)
		win32clipboard.CloseClipboard()
	elif path.endswith('gz'):
		import gzip
		fp = gzip.open(path)
	elif path.endswith('.zip'):
		import zipfile
		from os.path import basename
		fp = zipfile.ZipFile(path).open(basename(path)[:-4])
	else:
		fp = open(path, 'r')
	# deal with skipped lines
	for i in xrange(skip):
		fp.next()
	# read table
	for line in fp:
		if not line.startswith(comment) and not line.startswith('\n'):
			cols = line.rstrip().split(delim)
			if header:
				hdr = cols
				header = False
			else:
				data.append(cols)
	t1 = new(data, hdr, key_col=key_col, title=title)
	t1.path = path
	return t1

def summary(rows, rownames, title='', format='%.2f'):
	"""Return a summary table of rows.
	
	rows -- a list of rows.
	rownames -- the names of rows.
	format -- output string format for mean/median/std/sum/max/min.
	
	Return the summary table.
	
	>>> t3 = read('demo3.tsv')
	>>> summary(t3.col[1:], t3.header[1:], 'Summary of demo3').show()
	Summary of demo3
	H ['cls', 'n', 'mean', 'median', 'std',  'sum',   'max',  'min']
	0 ['p1',  '3', '2.00', '2.00',   '0.82', '6.00',  '3.00', '1.00']
	1 ['p2',  '3', '5.00', '5.00',   '0.82', '15.00', '6.00', '4.00']
	2 ['p3',  '3', '8.00', '8.00',   '0.82', '24.00', '9.00', '7.00']
	"""
	import numpy as N
	header = ['cls', 'n', 'mean', 'std', 'sum', 'max', 'min']
	out = []
	for i,row in enumerate(rows):
		a = N.array(map(float, row))
		temp = [rownames[i], str(len(row))]
		temp.extend([format % i for i in \
				[N.mean(a), N.median(a), N.std(a), N.sum(a), N.max(a), N.min(a)]])
		out.append(temp)
	return new(out, header, title=title)

if __name__ == '__main__':
	import doctest
	doctest.testmod()
	#print 'Read "demo.tsv" into table "t" for demo'
	#t = read('demo.tsv')
	#t.show()

