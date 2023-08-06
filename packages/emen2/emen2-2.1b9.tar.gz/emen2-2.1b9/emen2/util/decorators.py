# $Id: decorators.py,v 1.8 2011/03/07 09:45:30 irees Exp $
import itertools
import functools

class callonget(object):
	def __init__(self, cls):
		self._class = cls
	def __get__(self, instance, owner):
		try:
			result = object.__getattr__(instance, self._class.__name__)
		except AttributeError:
			result = self._class
		if instance != None and result is self._class:
			result = self._class()
			setattr(instance, self._class.__name__, result)
		return result
instonget = callonget


class _Null: pass
def cast_arguments(*postypes, **kwtypes):
	def _func(func):
		@functools.wraps(func)
		def _inner(*args, **kwargs):
			out = []
			for typ, arg in itertools.izip_longest(postypes, args, fillvalue=_Null):
				if arg != _Null:
					if typ != _Null and typ != None:
						arg = typ(arg)
					out.append(arg)
			for k,v in kwargs.iteritems():
				typ = kwtypes.get(k, _Null)
				if typ != _Null and typ != None:
					kwargs[k] = typ(kwargs[k])
			return func(*args, **kwargs)
		return _inner
	return _func



def make_decorator(func):
	def _inner1(_func):
		@functools.wraps(_func)
		def _inner(*a, **kw):
			return func(_func(*a, **kw))
		_inner.func = _func
		return _inner
	return _inner1

__version__ = "$Revision: 1.8 $".split(":")[1][:-1].strip()
