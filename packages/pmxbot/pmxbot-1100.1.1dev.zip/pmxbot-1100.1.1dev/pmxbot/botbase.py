# vim:ts=4:sw=4:noexpandtab

import sys
import datetime
import os
import traceback
import time
import random
import StringIO
import collections

import ircbot

from . import util
from .logging import init_logger
from .rss import FeedparserSupport

LOGWARN_EVERY = 60 # seconds
LOGWARN_MESSAGE = \
'''PRIVACY INFORMATION: LOGGING IS ENABLED!!

The following channels are logged are being logged to provide a
convenient, searchable archive of conversation histories:
%s
'''
warn_history = {}
logger = None

class NoLog(object):
	@classmethod
	def secret_items(cls, items):
		"""
		Iterate over the items, and yield each item with an indicator of
		whether it should be secret or not.

		>>> tuple(NoLog.secret_items(['a', 'b', NoLog, 'c']))
		((False, 'a'), (False, 'b'), (True, 'c'))
		"""
		secret = False
		for item in items:
			if item is cls:
				secret = True
				continue
			yield secret, item

class LoggingCommandBot(FeedparserSupport, ircbot.SingleServerIRCBot):
	def __init__(self, db_uri, server, port, nickname, channels, nolog_channels=None, feed_interval=60, feeds=[], use_ssl=False, password=None):
		server_list = [(server, port, password)]
		ircbot.SingleServerIRCBot.__init__(self, server_list, nickname, nickname)
		FeedparserSupport.__init__(self, feed_interval, feeds)
		nolog_channels = nolog_channels or []
		self.nickname = nickname
		self._channels = channels + nolog_channels
		self._nolog = set(('#' + c if not c.startswith('#') else c) for c in nolog_channels)
		# for backward compatibility, allow db_uri to specify the folder where
		#  pmxbot.sqlite would reside
		if os.path.isfile(os.path.join(db_uri, "pmxbot.sqlite")):
			db_uri = os.path.join(db_uri, "pmxbot.sqlite")
		self.db_uri = db_uri
		globals().update(logger=init_logger(db_uri))
		util.init_karma(db_uri)
		util.init_quotes(db_uri)
		self._nickname = nickname
		self.__use_ssl = use_ssl

	def connect(self, *args, **kwargs):
		kwargs['ssl'] = self.__use_ssl
		return ircbot.SingleServerIRCBot.connect(self, *args, **kwargs)

	def out(self, channel, s, log=True):
		if s.startswith('/me '):
			self.c.action(channel, s.encode('utf-8').split(' ', 1)[-1].lstrip())
		else:
			self.c.privmsg(channel, s.encode('utf-8'))
			if channel in self._channels and channel not in self._nolog and log:
				logger.message(channel, self._nickname, s)

	def _schedule_at(self, name, channel, when, func, args, doc):
		if type(when) == datetime.datetime:
			difference = when - datetime.datetime.now()
			repeat=False
		elif type(when) == datetime.date:
			whendt = datetime.datetime.fromordinal(tomorrow.toordinal())
			difference = whendt - datetime.datetime.now()
			repeat=False
		elif type(when) == datetime.time:
			if when > datetime.datetime.now().time():
				nextday = datetime.date.today()
			else:
				nextday = datetime.date.today() + datetime.timedelta(days=1)
			whendt = datetime.datetime.combine(nextday, when)
			difference = whendt - datetime.datetime.now()
			repeat=True
		howlong = (difference.days * 86400) + difference.seconds
		if howlong > 0:
			self.c.execute_delayed(howlong, self.background_runner, arguments=(self.c, channel, func, args, None, when, repeat))

	def on_welcome(self, c, e):
		self.c = c
		for channel in self._channels:
			if not channel.startswith('#'):
				channel = '#' + channel
			c.join(channel)
		for name, channel, howlong, func, args, doc, repeat in _delay_registry:
			self.c.execute_delayed(howlong, self.background_runner, arguments=(self.c, channel, func, args, howlong, None, repeat))
		for action in _at_registry:
			self._schedule_at(*action)
		FeedparserSupport.on_welcome(self, c, e)

	def on_join(self, c, e):
		nick = e.source().split('!', 1)[0]
		channel = e.target()
		if channel in self._nolog or nick == self._nickname:
			return
		if time.time() - warn_history.get(nick, 0) > LOGWARN_EVERY:
			warn_history[nick] = time.time()
			msg = LOGWARN_MESSAGE % (', '.join([chan for chan in sorted(self._channels) if chan not in self._nolog]))
			for line in msg.splitlines():
				c.notice(nick, line)

	def on_pubmsg(self, c, e):
		msg = (''.join(e.arguments())).decode('utf8', 'ignore')
		nick = e.source().split('!', 1)[0]
		channel = e.target()
		if msg.strip() > '':
			if channel not in self._nolog:
				logger.message(channel, nick, msg)
			self.handle_action(c, e, channel, nick, msg)


	def on_privmsg(self, c, e):
		msg = (''.join(e.arguments())).decode('utf8', 'ignore')
		nick = e.source().split('!', 1)[0]
		channel = nick
		if msg.strip() > '':
			self.handle_action(c, e, channel, nick, msg)

	def on_invite(self, c, e):
		nick = e.source().split('!', 1)[0]
		channel = e.arguments()[0]
		if not channel.startswith('#'):
			channel = '#' + channel
		self._channels.append(channel)
		self._nolog.add(channel)
		time.sleep(1)
		c.join(channel)
		time.sleep(1)
		c.privmsg(channel, "You summoned me, master %s?" % nick)

	def _handle_output(self, channel, output):
		if not output:
			return

		if isinstance(output, basestring):
			# turn the string into an iterable of lines
			output = StringIO.StringIO(output)

		for secret, item in NoLog.secret_items(output):
			self.out(channel, item, not secret)

	def background_runner(self, c, channel, func, args, howlong, when, repeat):
		"""
		Wrapper to run scheduled type tasks cleanly.
		"""
		try:
			self._handle_output(channel, func(c, None, *args))
		except:
			print datetime.datetime.now(), "Error in bacakground runner for ", func
			traceback.print_exc()
		if repeat and howlong:
			self.c.execute_delayed(howlong, self.background_runner, arguments=(self.c, channel, func, args, howlong, None, repeat))
		elif repeat and when:
			self._schedule_at('rescheduled task', channel, when, func, args, '')


	def handle_action(self, c, e, channel, nick, msg):
		lc_msg = msg.lower()
		lc_cmd = msg.split()[0]
		res = None
		for typ, name, f, doc, channels, exclude, rate, priority in _handler_registry:
			if typ in ('command', 'alias') and lc_cmd == '!%s' % name:
				# grab everything after the command
				msg = msg.partition(' ')[2].lstrip()
				try:
					res = f(c, e, channel, nick, msg)
				except Exception, exc:
					explitives = ['Yikes!', 'Zoiks!', 'Ouch!']
					explitive = random.choice(explitives)
					res = ["{explitive} An error occurred: {exc}".format(**vars())]
					res.append('!{name} {doc}'.format(**vars()))
					print datetime.datetime.now(), "Error with command %s" % name
					traceback.print_exc()
				break
			elif typ in('contains', '#') and name in lc_msg:
				if (not channels and not exclude) \
				or channel in channels \
				or (exclude and channel not in exclude) \
				or (channels == 'logged' and channel in self._channels and channel not in self._nolog) \
				or (channels == "unlogged" and channel in self._nolog) \
				or (exclude == "logged" and channel in self._nolog) \
				or (exclude == "unlogged" and channel in self._channels and channel not in self._nolog):
					if random.random() <= rate:
						try:
							res = f(c, e, channel, nick, msg)
						except Exception, e:
							print datetime.datetime.now(), "Error with contains  %s" % name
							traceback.print_exc()
						break
		self._handle_output(channel, res)


_handler_registry = []
_delay_registry = []
_at_registry = []

class Handler(collections.namedtuple('HandlerTuple',
	'type_ name func doc channels exclude rate priority')):
	sort_order = dict(
		# command processed before alias before contains
		command = 1,
		alias = 2,
		contains = 4,
	)
	@property
	def sort_key(self):
		return self.sort_order[self.type_], -self.priority, -len(self.name)

	def __gt__(self, other):
		return self.sort_key > other.sort_key

def contains(name, channels=None, exclude=None, rate=1.0, priority=1, doc=None):
	def deco(func):
		try:
			priority
		except UnboundLocalError:
			priority=1
		if name == '#':
			priority += 1
		_handler_registry.append(Handler('contains', name.lower(), func,
			doc, channels, exclude, rate, priority))
		_handler_registry.sort()
		return func
	return deco

def command(name, aliases=[], doc=None):
	def deco(func):
		_handler_registry.append(Handler('command', name.lower(), func,
			doc, None, None, None, 5))
		for a in aliases:
			_handler_registry.append(Handler('alias', a, func, doc, None,
				None, None, 4))
		_handler_registry.sort()
		return func
	return deco

def execdelay(name, channel, howlong, args=[], doc=None, repeat=False):
	def deco(func):
		_delay_registry.append((name.lower(), channel, howlong, func, args, doc, repeat))
		return func
	return deco


def execat(name, channel, when, args=[], doc=None):
	def deco(func):
		if type(when) not in (datetime.date, datetime.datetime, datetime.time):
			raise TypeError
		_at_registry.append((name.lower(), channel, when, func, args, doc))
		return func
	return deco
