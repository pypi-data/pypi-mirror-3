# $Id: vartypes.py,v 1.110 2012/03/06 05:38:22 irees Exp $
"""Vartypes (data types)

Classes:
	Vartype
	vt_*: A number of built-in data types

"""

import cgi
import operator
import collections
import urllib
import htmlentitydefs
import re

# Working with time is fun..
import time
import calendar
import datetime
# ... dateutil helps.
import dateutil
import dateutil.parser
import dateutil.tz
import dateutil.rrule


try:
	import markdown2 as markdown
except ImportError:
	try:
		import markdown
	except ImportError:
		markdown = None

# EMEN2 imports
import emen2.db.datatypes
import emen2.db.config
import emen2.db.exceptions
import emen2.util.listops
import emen2.db.exceptions

# Convenience
tzutc = dateutil.tz.tzutc()
ci = emen2.util.listops.check_iterable
ValidationError = emen2.db.exceptions.ValidationError
vtm = emen2.db.datatypes.VartypeManager



###########################
# Helper methods

def check_rectype(engine, value):
	key = engine.get_cache_key('paramdef', value)
	hit, paramdef = engine.check_cache(key)
	if not hit:
		paramdef = engine.db.getparamdef(value, filt=False)
		engine.store(key, paramdef)

	return paramdef


def check_rectypes(engine, values):
	key = engine.get_cache_key('recorddefnames')
	hit, rectypes = engine.check_cache(key)
	if not hit:
		rectypes = engine.db.getrecorddefnames()
		engine.store(key, rectypes)

	if set(values) - rectypes:
		raise ValidationError, "Unknown protocols: %s"%(", ".join(set(values)-rectypes))


def check_usernames(engine, values):
	key = engine.get_cache_key('usernames')
	hit, usernames = engine.check_cache(key)
	if not hit:
		usernames = engine.db.getusernames()
		engine.store(key, usernames)

	if set(values) - usernames:
		raise ValidationError, "Unknown users: %s"%(", ".join(set(values)-usernames))


def check_groupnames(engine, values):
	key = engine.get_cache_key('groupnames')
	hit, groupnames = engine.check_cache(key)
	if not hit:
		groupnames = engine.db.getgroupnames()
		engine.store(key, groupnames)

	if set(values) - groupnames:
		raise ValidationError, "Unknown groups: %s"%(", ".join(set(values)-groupnames))


def update_username_cache(engine, values, lnf=False):
	# Check cache
	to_cache = []
	for v in values:
		key = engine.get_cache_key('displayname', v)
		hit, dn = engine.check_cache(key)
		if not hit:
			to_cache.append(v)

	if to_cache:
		users = engine.db.getuser(to_cache)
		for user in users:
			user.getdisplayname(lnf=lnf)
			key = engine.get_cache_key('displayname', user.name)
			engine.store(key, user.displayname)



def iso8601duration(d):
	"""
	Parse ISO 8601 duration format.

	From Wikipedia, ISO 8601 duration format is:
		P[n]Y[n]M[n]DT[n]H[n]M[n]S

	P is the duration designator (historically called "period") placed at the start of the duration representation.
	Y is the year designator that follows the value for the number of years.
	M is the month designator that follows the value for the number of months.
	W is the week designator that follows the value for the number of weeks.
	D is the day designator that follows the value for the number of days.
	T is the time designator that precedes the time components of the representation.
	H is the hour designator that follows the value for the number of hours.
	M is the minute designator that follows the value for the number of minutes.
	S is the second designator that follows the value for the number of seconds.

	Examples:
	d = 'P1M2D' # 1 month, 2 days
	d = 'P1Y2M3DT4H5M6S' # 1 year, 2 months, 3 days, 4 hours, 5 minutes, 6 seconds
	d = 'P3W' # 3 weeks

	"""

	regex = re.compile("""
			(?P<type>.)
			((?P<weeks>[0-9,]+)W)?
			((?P<years>[0-9,]+)Y)?
			((?P<months>[0-9,]+)M)?
			((?P<days>[0-9,]+)D)?
			(T
				((?P<hours>[0-9,]+)H)?
				((?P<minutes>[0-9,]+)M)?
				((?P<seconds>[0-9,]+)S)?
			)?
			""", re.X)
	match = regex.search(d)
	rd = {} # return date

	# rdate['type'] = match.group('type')
	for key in ['weeks','years','months','days','hours','minutes','seconds']:
		if match.group(key):
			rd[key] = int(match.group(key))

	return rd




@vtm.register_vartype('none')
class Vartype(object):
	'''Base class for vartypes'''

	#: the index key type for this class
	keytype = None
	#: is this vartype iterable?
	iterable = True
	#: the CSS class to use when rendering as HTML
	elem_class = 'e2-edit'
	#: the element to use when rendering as HTML
	elem = 'span'

	def __init__(self, engine=None, pd=None):
		self.pd = pd
		self.engine = engine


	def process(self, value, *args, **kwargs):
		return [cgi.escape(unicode(i)) for i in ci(value)]


	# This is the default HTML renderer for single-value items. It is important to cgi.escape the values!!
	def render(self, value, name=0, edit=False, showlabel=False, markup=False, table=False, embedtype=None):
		'''Render a value as HTML'''
		# Store these for convenience
		self.name = name
		self.edit = edit
		self.showlabel = showlabel
		self.markup = markup
		self.table = table
		if self.pd.get('immutable'):
			self.edit = False

		value = self.process(value)
		return self._render(value, embedtype=embedtype)


	# After pre-processing values into markup
	def _render(self, value, embedtype=None):
		# Note: Value should already be escaped!
		webroot = emen2.db.config.get('network.EMEN2WEBROOT')
		label = ''
		if embedtype == '!':
			embedtype = 'data-required="True"'
		else:
			embedtype = ''
		editmarkup = 'data-name="%s" data-param="%s" %s'%(self.name, self.pd.name, embedtype)

		if value and self.pd.defaultunits:
			value = ['%s %s'%(i, self.pd.defaultunits) for i in value]

		# Plain text rendering
		if not self.markup:
			return ", ".join(value)

		# Empty value
		if not value:
			label = '<img src="%s/static/images/blank.png" class="e2l-label" alt="No value" />'%webroot
			if self.edit:
				return '<%s class="%s" %s>%s</%s>'%(self.elem, self.elem_class, editmarkup, label, self.elem)
			return '<%s></%s>'%(self.elem, self.elem)


		# Tables have links to the record
		if self.table:
			value = ['<a href="%s/record/%s">%s</a>'%(webroot, self.name, i) for i in value]

		# Iterable parameters
		if self.pd.iter:
			lis = ['<li>%s</li>'%(i) for i in value]
			if not self.edit:
				return '<ul>%s</ul>'%("\n".join(lis))
			# Editable..
			# Are we showing the edit label?
			# if self.showlabel:
			#	lis.append('<li><span class="e2-edit e2l-label"><img src="%s/static/images/edit.png" alt="Edit" /></span></li>'%webroot)
			# Put the editing widget together
			return '<ul class="%s" %s>%s</ul>'%(self.elem_class, editmarkup, "\n".join(lis))

		value = value.pop()

		# Non-iterable parameters
		if not self.edit:
			return value

		return '<%s class="%s" %s>%s%s</%s>'%(self.elem, self.elem_class, editmarkup, value, label, self.elem)


	def encode(self, value):
		return value


	def decode(self, pd, value):
		return value


	def validate(self, value):
		"""Validate a value"""
		raise ValidationError, "This is an organizational parameter, and is not intended to be used."


	def _rci(self, value):
		"""Validation methods generally work on iterables; if the parameter is non-iterable,
		return a single value."""
		if value and not self.pd.iter:
			return value.pop()
		return value or None


	# Replace these two methods.
	def getvartype(self):
		return self.vartype


	def getkeytype(self):
		return self.keytype


	def reindex(self, items):
		# print "reindex:", items
		# items format: [name, newval, oldval]
		addrefs = collections.defaultdict(set)
		delrefs = collections.defaultdict(set)
		for name, new, old in items:
			if new == old:
				continue

			if not self.pd.iter:
				new=[new]
				old=[old]

			new = set(new or [])
			old = set(old or [])
			for n in new-old:
				addrefs[n].add(name)
			for o in old-new:
				delrefs[o].add(name)

		if None in addrefs: del addrefs[None]
		if None in delrefs: del delrefs[None]

		return addrefs, delrefs




###################################
# Float vartypes
#	Indexed as 'f'
###################################

@vtm.register_vartype('float')
class vt_float(Vartype):
	"""Floating-point number"""
	#:
	keytype = 'f'

	def validate(self, value):
		return self._rci(map(float, ci(value)))

	def process(self, value):
		return ['%g'%i for i in ci(value)]


@vtm.register_vartype('percent')
class vt_percent(Vartype):
	"""Percentage. 0 <= x <= 1"""
	#:
	keytype = 'f'

	def validate(self, value):
		value = map(float, ci(value))
		for i in value:
			if not 0 <= i <= 1.0:
				raise ValidationError, "Range for percentage is 0 <= value <= 1.0; value was: %s"%i
		return self._rci(value)

	def process(self, value):
		return ['%0.0f'%(i*100.0) for i in ci(value)]



###################################
# Integer vartypes
#	Indexed as 'd'
###################################

@vtm.register_vartype('int')
class vt_int(Vartype):
	"""Integer"""
	#:
	keytype = 'd'

	def validate(self, value):
		return self._rci(map(int, ci(value)))


@vtm.register_vartype('coordinate')
class vt_coordinate(Vartype):
	"""Coordinates; tuples of floats."""

	def validate(self, value):
		return [[(float(x), float(y)) for x,y in coord] for coord in ci(value)]


@vtm.register_vartype('boolean')
class vt_boolean(Vartype):
	"""Boolean value. Accepts 0/1, True/False, T/F, Yes/No, Y/N, None."""
	#:
	keytype = 'd'

	def validate(self, value):
		t = ['t', 'y', 'yes', 'true', '1']
		f = ['f', 'n', 'no', 'false', 'none', '0']
		ret = []
		for i in ci(value):
			i = unicode(value).lower()
			if i in t:
				i = True
			elif i in f:
				i = False
			else:
				raise ValidationError, "Invalid boolean: %s"%unicode(value)
			ret.append(i)
		return self._rci(ret)


# ian: deprecated
@vtm.register_vartype('recid')
class vt_recid(Vartype):
	"""Record name"""

	def validate(self, value):
		value = map(int, ci(value))
		for i in value:
			if i < 0:
				raise ValidationError, "Invalid Record name: %s"%value
		return self._rci(value)


@vtm.register_vartype('name')
class vt_name(Vartype):
	"""DBO name"""

	def validate(self, value):
		ret = []
		for i in ci(value):
			try:
				i = int(value)
			except ValueError:
				i = unicode(value or '')
			ret.append(i)
		return self._rci(ret)



###################################
# String vartypes
#	Indexed as keytype 's'
###################################

@vtm.register_vartype('string')
class vt_string(Vartype):
	"""String"""
	#:
	keytype = 's'

	def validate(self, value):
		return self._rci([unicode(x).strip() for x in ci(value)])

	def process(self, value):
		value = ci(value)
		if self.markup:
			return [cgi.escape(i) for i in value]
		return value


@vtm.register_vartype('choice')
class vt_choice(vt_string):
	"""One value from a defined list of choices"""

	def validate(self, value):
		value = [unicode(i).strip() for i in ci(value)]
		for v in value:
			if v not in self.pd.choices:
				raise ValidationError, "Invalid choice: %s"%v
		return self._rci(value)



@vtm.register_vartype('rectype')
class vt_rectype(vt_string):
	"""RecordDef name"""

	def validate(self, value):
		value = [unicode(x).strip() for x in ci(value)]
		check_rectypes(self.engine, value)
		return self._rci(value)


@vtm.register_vartype('text')
class vt_text(vt_string):
	"""Freeform text, with word indexing."""
	#:
	elem = 'div'

	#:
	unindexed_words = set(["in", "of", "for", "this", "the", "at", "to", "from", "at", "for", "and", "it", "or"])

	def reindex(self, items):
		"""(Internal) calculate param index updates for vartype == text"""
		addrefs = collections.defaultdict(list)
		delrefs = collections.defaultdict(list)
		for item in items:
			if item[1]==item[2]:
				continue

			for i in self._reindex_getindexwords(item[1]):
				addrefs[i].append(item[0])

			for i in self._reindex_getindexwords(item[2]):
				delrefs[i].append(item[0])

		allwords = set(addrefs.keys() + delrefs.keys()) - set(self.unindexed_words)
		addrefs2 = {}
		delrefs2 = {}

		for i in allwords:
			# make set, remove unchanged items
			addrefs2[i] = set(addrefs.get(i,[]))
			delrefs2[i] = set(delrefs.get(i,[]))
			u = addrefs2[i] & delrefs2[i]
			addrefs2[i] -= u
			delrefs2[i] -= u

		return addrefs2, delrefs2


	_reindex_getindexwords_m = re.compile('([a-zA-Z]+)|([0-9][.0-9]+)')
	def _reindex_getindexwords(self, value, ctx=None, txn=None):
		"""(Internal) Split up a text param into components"""
		if value == None: return []
		value = unicode(value).lower()
		return set((x[0] or x[1]) for x in self._reindex_getindexwords_m.findall(value))


	def process(self, value):
		value = ci(value)
		if self.markup:
			value = [cgi.escape(i) for i in value]
			if markdown:
				value = [markdown.markdown(i) for i in value]
		return value




###################################
# Time vartypes (keytype is string)
#	Indexed as keytype 's'
###################################

@vtm.register_vartype('datetime')
class vt_datetime(vt_string):
	"""ISO 8601 Date time"""
	#:
	keytype = 's'

	def validate(self, value):
		ret = []
		for i in ci(value):
			if i:
				t = dateutil.parser.parse(i)
				if not t.tzinfo:
					raise ValidationError, "No UTC offset: %s"%i
				# if any([t.hour, t.minute, t.second, t.microsecond, t.tzinfo]):
				# 	print "Datetime.."
				# else:
				# 	print "Date.."
				# print "dt:", t.isoformat()
				# print "d:", t.date().isoformat()
				# print "t:", t.time().isoformat()
				ret.append(t.isoformat())
		return self._rci(ret)

	def _render(self, value, embedtype=None):
		# if self.markup:
		value = ['<time class="e2-localize" datetime="%s">%s</time>'%(i,i) for i in value]
		return super(vt_datetime, self)._render(value, embedtype=embedtype)


@vtm.register_vartype('date')
class vt_date(vt_datetime):
	"""Date, yyyy/mm/dd"""

	def validate(self, value):
		ret = []
		for i in ci(value):
			i = parse_iso8601(i, result='date')
			if i:
				ret.append(i)
		return self._rci(ret)


@vtm.register_vartype('time')
class vt_time(vt_datetime):
	"""Time, HH:MM:SS"""

	def validate(self, value):
		ret = []
		for i in ci(value):
			i = parse_iso8601(i, result='time')
			if i:
				ret.append(i)
		return self._rci(ret)



### iCalendar-like date types
# 
# @vtm.register_vartype('duration')
# class vt_duration(Vartype):
# 	"""ISO 8601 Duration"""
# 	pass
# 
# 
# @vtm.register_vartype('recurrence')
# class vt_recurrence(Vartype):
# 	"""Date, yyyy/mm/dd"""
# 	pass


###################################
# Reference vartypes (uri, binary, hdf, etc.).
#	Indexed as keytype 's'
###################################

@vtm.register_vartype('uri')
class vt_uri(Vartype):
	"""URI"""
	#:
	keytype = 's'

	# ian: todo: parse with urlparse
	def validate(self, value):
		value = [unicode(i).strip() for i in ci(value)]
		for v in value:
			if not v.startswith("http://"):
				raise ValidationError, "Invalid URI: %s"%value
		return self._rci(value)


	def process(self, value):
		value = ci(value)
		if self.markup:
			value = [cgi.escape(i) for i in value]
			if not self.table:
				value = ['<a href="%s">%s</a>'%(i,i) for i in value]
		return value




###################################
# Mapping types
###################################


@vtm.register_vartype('dict')
class vt_dict(Vartype):
	"""Dictionary with valid param keys"""
	# ian: todo: parse with urlparse
	def validate(self, value):
		if not value:
			return None
		r = [(unicode(k), unicode(v)) for k,v in value.items() if k]
		return dict(r)

	def process(self, value):
		if not value:
			return 'Empty'
		r = [cgi.escape('%s: %s'%(k, v)) for k,v in value.items()]
		return '<br />'.join(r)


###################################
# Binary vartypes
#	Not indexed.
###################################

@vtm.register_vartype('binary')
class vt_binary(Vartype):
	"""File Attachment"""
	#:
	keytype = None
	#:
	elem_class = "e2-edit"

	def validate(self, value):
		return self._rci([i.name for i in self.engine.db.getbinary(ci(value), filt=False)])


	def process(self, value):
		webroot = emen2.db.config.get('network.EMEN2WEBROOT')
		value = ci(value)
		t = self.table
		if not self.markup:
			t = True
			# return value

		try:
			v = self.engine.db.getbinary(value)
			if t:
				value = ['%s'%(cgi.escape(i.filename)) for i in v]
			else:
				value = ['<a target="_blank" href="%s/download/%s/%s">%s</a>'%(webroot, i.name, urllib.quote(i.filename), cgi.escape(i.filename)) for i in v]

		except (ValueError, TypeError):
			value = ['Error getting binary %s'%i for i in value]

		return value


###################################
# md5 checksum
#	Indexed as keytype 's'
###################################

@vtm.register_vartype('md5')
class vt_md5(Vartype):
	"""String"""
	#:
	keytype = 's'


###################################
# Internal record-record linkes
#	Not indexed.
###################################

@vtm.register_vartype('links')
class vt_links(Vartype):
	"""References to other Records."""
	#:
	keytype = None

	def validate(self, value):
		return self._rci([int(x) for x in ci(value)])



###################################
# User, ACL, and Group vartypes
#	Indexed as keytype 's'
###################################

@vtm.register_vartype('user')
class vt_user(Vartype):
	"""Users"""
	#:
	keytype = 's'

	def validate(self, value):
		value = [unicode(x).strip() for x in ci(value)]
		check_usernames(self.engine, value)
		return self._rci(value)


	def process(self, value):
		webroot = emen2.db.config.get('network.EMEN2WEBROOT')
		value = ci(value)
		lnf = False
		if self.table:
			lnf = True
		update_username_cache(self.engine, value, lnf=lnf)

		lis = []
		for i in value:
			key = self.engine.get_cache_key('displayname', i)
			hit, dn = self.engine.check_cache(key)
			dn = cgi.escape(dn or '')
			if self.table or not self.markup:
				lis.append(dn)
			else:
				lis.append('<a href="%s/user/%s">%s</a>'%(webroot, i, dn))

		return lis




@vtm.register_vartype('acl')
class vt_acl(Vartype):
	"""Permissions access control list; nested lists of users"""
	#:
	keytype = 's'

	def validate(self, value):
		if not hasattr(value, '__iter__'):
			value = [[value],[],[],[]]

		for i in value:
			if not hasattr(i, '__iter__'):
				raise ValidationError, "Invalid permissions format: ", value

		value = [[unicode(y) for y in x] for x in value]
		if len(value) != 4:
			raise ValidationError, "Invalid permissions format: ", value

		users = reduce(lambda x,y:x+y, value)
		check_usernames(self.engine, users)
		return value


	def process(self, value):
		if not value:
			return []

		allusers = reduce(lambda x,y:x+y, value)
		unames = {}
		for user in self.engine.db.getuser(allusers):
			unames[user.name] = user.displayname

		levels = ["Read","Comment","Write","Owner"]
		ret = []
		for level, names in zip(levels, value):
			namesr = [unames.get(i,"(%s)"%i) for i in names]
			ret.append("%s: %s"%(level, ", ".join(namesr)))
		return ['<br />'.join(ret)]


	def reindex(self, items):
		"""(Internal) Calculate secrindex updates"""
		# Calculating security updates...
		addrefs = collections.defaultdict(list)
		delrefs = collections.defaultdict(list)
		for name, new, old in items:
			#nperms = set(reduce(operator.concat, new or [], []))
			#operms = set(reduce(operator.concat, old or [], []))
			nperms = set()
			for i in new or []:
				nperms |= set(i)
			operms = set()
			for i in old or []:
				operms |= set(i)

			for user in nperms - operms:
				addrefs[user].append(name)

			for user in operms - nperms:
				delrefs[user].append(name)

		return addrefs, delrefs



@vtm.register_vartype('groups')
class vt_groups(Vartype):
	"""Groups"""
	#:
	keytype = 's'

	def validate(self, value):
		value = set([unicode(i).strip() for i in ci(value)])
		check_groupnames(self.engine, value)
		return self._rci(value)

	def process(self, value):
		value = ci(value)
		return [unicode(i) for i in value]


###################################
# Comment and History vartypes
#	Not indexed
###################################

@vtm.register_vartype('comments')
class vt_comments(Vartype):
	"""Comments"""
	#:
	keytype = None

	# ian: todo... sort this out.
	def validate(self, value):
		return value

	def process(self, value):
		webroot = emen2.db.config.get('network.EMEN2WEBROOT')
		value = ci(value)
		users = [i[0] for i in value]
		update_username_cache(self.engine, users)

		lis = []
		for user, time, comment in value:
			key = self.engine.get_cache_key('displayname', user)
			hit, dn = self.engine.check_cache(key)
			dn = cgi.escape(dn)
			comment = cgi.escape(comment)
			if self.table or not self.markup:
				t = '%s @ %s: %s'%(user, time, comment)
			else:
				t = '<div><h4><a href="%s/user/%s">%s</a> @ <time class="e2-localize" datetime="%s">%s</time></h4><p>%s</p></div>'%(webroot, user, dn, time, time, comment)
			lis.append(t)

		return lis


@vtm.register_vartype('history')
class vt_history(Vartype):
	"""History"""
	#:
	keytype = None

	def validate(self, value):
		users = [i[0] for i in value]
		times = [i[1] for i in value]
		check_usernames(self.engine, users)
		return [(unicode(i[0]), unicode(i[1]), unicode(i[2]), i[3]) for i in value]


	def process(self, value):
		value = ci(value)
		return [unicode(i) for i in value]



if __name__ == "__main__":
	v = vt_datetime()
	v.validate(['2011-01-01'])


__version__ = "$Revision: 1.110 $".split(":")[1][:-1].strip()
