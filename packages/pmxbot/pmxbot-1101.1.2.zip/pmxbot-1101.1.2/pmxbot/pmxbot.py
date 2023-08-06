# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:noexpandtab
# c-basic-indent: 4; tab-width: 4; indent-tabs-mode: true;
from __future__ import absolute_import, division

import time
import sys
import re
import urllib
import random
import csv
import logging
import functools
import traceback
from datetime import date, timedelta
from cStringIO import StringIO
try:
	import json
except ImportError:
	import simplejson as json
from xml.etree import ElementTree

import popquotes.pmxbot as pq

from .botbase import (command, contains, execdelay, execat,
	_handler_registry, NoLog)
from . import botbase
from .util import *
from . import util
from . import saysomething as saysomethinglib
from .cleanhtml import plaintext

log = logging.getLogger(__name__)

@command("google", aliases=('g',), doc="Look a phrase up on google")
def google(client, event, channel, nick, rest):
	BASE_URL = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&'
	url = BASE_URL + urllib.urlencode({'q' : rest.encode('utf-8').strip()})
	raw_res = urllib.urlopen(url).read()
	results = json.loads(raw_res)
	hit1 = results['responseData']['results'][0]
	return ' - '.join((urllib.unquote(hit1['url']), hit1['titleNoFormatting']))

@command("googlecalc", aliases=('gc',), doc="Calculate something using google")
def googlecalc(client, event, channel, nick, rest):
	query = rest
	html = get_html('http://www.google.com/search?%s' % urllib.urlencode({'q' : query.encode('utf-8')}))
	try:
		gcre = re.compile('<h2 class=r style="font-size:138%"><b>(.+?)</b>')
		res = gcre.search(html).group(1)
	except AttributeError:
		gcre = re.compile('<h3 class=r><b>(.+?)</b>')
		res = gcre.search(html).group(1)
	return plaintext(res.decode('utf-8'))

@command("time", doc="What time is it in.... Similar to !weather")
def googletime(client, event, channel, nick, rest):
	rest = rest.strip()
	if rest == 'all':
		places = config.places
	elif '|' in rest:
		places = [x.strip() for x in rest.split('|')]
	else:
		places = [rest]
	time_callables = (functools.partial(time_for, place) for place in places)
	return suppress_exceptions(time_callables, AttributeError)

def time_for(place):
	"""
	Retrieve the time for a specific place
	"""
	if not place.startswith('time'):
		query = 'time ' + place
	else:
		query = place
	timere = re.compile(r'<b>\s*(\d+:\d{2}([ap]m)?).*\s*</b>', re.I)
	query_string = urllib.urlencode({'q' : query.encode('utf-8')})
	html = get_html('http://www.google.com/search?%s' % query_string)
	return plaintext(timere.search(html).group(1))

def to_snowman(condition):
	"""
	Replace 'Snow' and 'Snow Showers' with a snowman (☃).
	"""
	return condition.replace('Snow Showers', u'☃').replace('Snow', u'☃')

def weather_for(place):
	"Retrieve the weather for a specific place using the iGoogle API"
	url = "http://www.google.com/ig/api?" + urllib.urlencode({'weather' : place.encode('utf-8')})
	parser = ElementTree.XMLParser()
	wdata = ElementTree.parse(urllib.urlopen(url), parser=parser)
	city = wdata.find('weather/forecast_information/city').get('data')
	tempf = wdata.find('weather/current_conditions/temp_f').get('data')
	tempc = wdata.find('weather/current_conditions/temp_c').get('data')
	conds = wdata.find('weather/current_conditions/condition').get('data')
	# sometimes, for no apparent reason, the current condition is blank,
	#  so put something else there to keep the tests from failing.
	unknown_conditions = ['spammy', 'unknown', 'mysterious']
	conds = conds or random.choice(unknown_conditions)
	conds = to_snowman(conds)
	future_day = wdata.find('weather/forecast_conditions/day_of_week').get('data')
	future_highf = wdata.find('weather/forecast_conditions/high').get('data')
	future_highc = int((int(future_highf) - 32) / 1.8)
	future_conds = wdata.find('weather/forecast_conditions/condition').get('data')
	future_conds = to_snowman(future_conds)
	fmt = '    '.join((
		u"%(city)s. Currently: %(tempf)sF/%(tempc)sC, %(conds)s.",
		u"%(future_day)s: %(future_highf)sF/%(future_highc)sC, %(future_conds)s",
	))
	weather = fmt % vars()
	return weather

def suppress_exceptions(callables, exceptions=Exception):
	"""
	Suppress supplied exceptions (tuple or single exception)
	encountered when a callable is invoked.
	>>> five_over_n = lambda n: 5//n
	>>> callables = (functools.partial(five_over_n, n) for n in xrange(-3,3))
	>>> safe_results = suppress_exceptions(callables, ZeroDivisionError)
	>>> tuple(safe_results)
	(-2, -3, -5, 5, 2)
	"""
	for callable in callables:
		try:
			yield callable()
		except exceptions:
			pass

@command('weather', aliases=('w'), doc='Get weather for a place. All '
	'offices with "all", or a list of places separated by pipes.')
def weather(client, event, channel, nick, rest):
	rest = rest.strip()
	if rest == 'all':
		places = config.places
	elif '|' in rest:
		places = [x.strip() for x in rest.split('|')]
	else:
		places = [rest]
	weather_callables = (functools.partial(weather_for, place) for place in places)
	suppressed_errors = (
		IOError,
		# sometimes, wdata.find returns None which has no .get
		AttributeError,
	)
	return suppress_exceptions(weather_callables, suppressed_errors)

@command("translate", aliases=('trans', 'googletrans', 'googletranslate'), doc="Translate a phrase using Google Translate. First argument should be the language[s]. It is a 2 letter abbreviation. It will auto detect the orig lang if you only give one; or two languages joined by a |, for example 'en|de' to trans from English to German. Follow this by the phrase you want to translate.")
def translate(client, event, channel, nick, rest):
	rest = rest.strip()
	langpair, meh, rest = rest.partition(' ')
	if '|' not in langpair:
		langpair = '|' + langpair
	BASE_URL = 'http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&format=text&'
	url = BASE_URL + urllib.urlencode({'q' : rest.encode('utf-8'), 'langpair' : langpair})
	raw_res = urllib.urlopen(url).read()
	results = json.loads(raw_res)
	response = results['responseData']
	if not response:
		return "I couldn't find a translation. Are you sure %(langpair)s is a valid language?" % vars()
	translation = response['translatedText']
	return translation


@command("boo", doc="Boo someone")
def boo(client, event, channel, nick, rest):
	slapee = rest
	util.karma.change(slapee, -1)
	return "/me BOOO %s!!! BOOO!!!" % slapee

@command("troutslap", aliases=("slap", "ts"), doc="Slap some(one|thing) with a fish")
def troutslap(client, event, channel, nick, rest):
	slapee = rest
	util.karma.change(slapee, -1)
	return "/me slaps %s around a bit with a large trout" % slapee

@command("keelhaul", aliases=("kh",), doc="Inflict great pain and embarassment on some(one|thing)")
def keelhaul(client, event, channel, nick, rest):
	keelee = rest
	util.karma.change(keelee, -1)
	return "/me straps %s to a dirty rope, tosses 'em overboard and pulls with great speed. Yarrr!" % keelee

@command("annoy", aliases=("a", "bother",), doc="Annoy everyone with meaningless banter")
def annoy(client, event, channel, nick, rest):
	def a1():
		yield 'OOOOOOOHHH, WHAT DO YOU DO WITH A DRUNKEN SAILOR'
		yield 'WHAT DO YOU DO WITH A DRUNKEN SAILOR'
		yield "WHAT DO YOU DO WITH A DRUNKEN SAILOR, EARLY IN THE MORNIN'?"
	def a2():
		yield "I'M HENRY THE EIGHTH I AM"
		yield "HENRY THE EIGHTH I AM I AM"
		yield "I GOT MARRIED TO THE GIRL NEXT DOOR; SHE'S BEEN MARRIED SEVEN TIMES BEFORE"
	def a3():
		yield "BOTHER!"
		yield "BOTHER BOTHER BOTHER!"
		yield "BOTHER BOTHER BOTHER BOTHER!"
	def a4():
		yield "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
		yield "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE"
		yield "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
	def a5():
		yield "YOUR MOTHER WAS A HAMSTER!"
		yield "AND YOUR FATHER SMELLED OF ELDERBERRIES!"
	def a6():
		yield "My Tallest! My Tallest! Hey! Hey My Tallest! My Tallest? My Tallest! Hey! Hey! Hey! My Taaaaaaallist! My Tallest? My Tallest! Hey! Hey My Tallest! My Tallest? It's me! My Tallest? My Tallest!"
	return random.choice([a1, a2, a3, a4, a5, a6])()

@command("dance", aliases=("d",), doc="Do a little dance")
def dance(client, event, channel, nick, rest):
	yield 'O-\-<'
	yield 'O-|-<'
	yield 'O-/-<'

@command("panic", aliases=("pc",), doc="Panic!")
def panic(client, event, channel, nick, rest):
	yield 'O-|-<'
	yield 'O-<-<'
	yield 'O->-<'
	yield 'AAAAAAAHHHH!!!  HEAD FOR THE HILLS!'

@command("duck", aliases=("ducky",), doc="Display a helpful duck")
def duck(client, event, channel, nick, rest):
	yield '__("<'
	yield '\__/'
	yield ' ^^'

@command("rubberstamp",  aliases=('approve',), doc="Approve something")
def rubberstamp(client, event, channel, nick, rest):
	parts = ["Bad credit? No credit? Slow credit?"]
	rest = rest.strip()
	if rest:
		parts.append("%s is" % rest)
		util.karma.change(rest, 1)
	parts.append("APPROVED!")
	return " ".join(parts)

@command("cheer", aliases=("c",), doc="Cheer for something")
def cheer(client, event, channel, nick, rest):
	if rest:
		util.karma.change(rest, 1)
		return "/me cheers for %s!" % rest
	util.karma.change('the day', 1)
	return "/me cheers!"

@command("golfclap", aliases=("clap",), doc="Clap for something")
def golfclap(client, event, channel, nick, rest):
	clapv = random.choice(clapvl)
	adv = random.choice(advl)
	adj = random.choice(adjl)
	if rest:
		clapee = rest.strip()
		util.karma.change(clapee, 1)
		return "/me claps %s for %s, %s %s." % (clapv, rest, adv, adj)
	return "/me claps %s, %s %s." % (clapv, adv, adj)

@command('featurecreep', aliases=('fc',), doc='Generate feature creep (P+C http://www.dack.com/web/bullshit.html)')
def featurecreep(client, event, channel, nick, rest):
	verb = random.choice(fcverbs).capitalize()
	adjective = random.choice(fcadjectives)
	noun = random.choice(fcnouns)
	return '%s %s %s!' % (verb, adjective, noun)

@command('job', aliases=('card',), doc='Generate a job title, http://www.cubefigures.com/job.html')
def job(client, event, channel, nick, rest):
	j1 = random.choice(jobs1)
	j2 = random.choice(jobs2)
	j3 = random.choice(jobs3)
	return '%s %s %s' % (j1, j2, j3)

@command('hire', doc="When all else fails, pmxbot delivers the perfect employee.")
def hire(client, event, channel, nick, rest):
	title = job(client, event, channel, nick, rest)
	task = featurecreep(client, event, channel, nick, rest)
	return "/me finds a new %s to %s" % (title, task.lower())

@command('strategy', doc='Social Media Strategy, courtsey of http://whatthefuckismysocialmediastrategy.com/')
def strategy(client, event, channel, nick, rest):
	return random.choice(socialstrategies)


@command('oregontrail', aliases=('otrail',), doc='It\'s edutainment!')
def oregontrail(client, event, channel, nick, rest):
	rest = rest.strip()
	if rest:
		who = rest.strip()
	else:
		who = random.choice([nick, channel, 'pmxbot'])
	action = random.choice(otrail_actions)
	if action in ('has', 'has died from'):
		issue = random.choice(otrail_issues)
		text = '%s %s %s.' % (who, action, issue)
	else:
		text = '%s %s' % (who, action)
	return text

#Added quotes
@command('quote', aliases=('q',), doc='If passed with nothing then get a random quote. If passed with some string then search for that. If prepended with "add:" then add it to the db, eg "!quote add: drivers: I only work here because of pmxbot!"')
def quote(client, event, channel, nick, rest):
	rest = rest.strip()
	if rest.startswith('add: ') or rest.startswith('add '):
		quoteToAdd = rest.split(' ', 1)[1]
		util.quotes.quoteAdd(quoteToAdd)
		qt = False
		return 'Quote added!'
	qt, i, n = util.quotes.quoteLookupWNum(rest)
	if not qt: return
	return '(%s/%s): %s' % (i, n, qt)

@command('zinger', aliases=('zing',), doc='ZING!')
def zinger(client, event, channel, nick, rest):
	name = 'you'
	if rest:
		name = rest.strip()
		util.karma.change(name, -1)
	return "OH MAN!!! %s TOTALLY GOT ZING'D!" % (name.upper())

@command("motivate", aliases=("m", "appreciate", "thanks", "thank"), doc="Motivate someone")
def motivate(client, event, channel, nick, rest):
	if rest:
		r = rest.strip()
	else:
		r = channel
	util.karma.change(r, 1)
	return "you're doing good work, %s!" % r

@command("imotivate", aliases=("im", 'ironicmotivate',), doc='''Ironically "Motivate" someone''')
def imotivate(client, event, channel, nick, rest):
	if rest:
		r = rest.strip()
		util.karma.change(r, -1)
	else:
		r = channel
	return '''you're "doing" "good" "work", %s!''' % r

@command("nailedit", aliases=("nail", "n"), doc="Nail that interview")
def nailedit(client, event, channel, nick, rest):
	random.shuffle(interview_excuses)
	yield "Sorry, but " + interview_excuses[0]
	yield("/me Nailed it!")


@command("demotivate", aliases=("dm",), doc="Demotivate someone")
def demotivate(client, event, channel, nick, rest):
	if rest:
		r = rest.strip()
	else:
		r = channel
	util.karma.change(r, -1)
	return "you're doing horrible work, %s!" % r

@command("8ball", aliases=("8",), doc="Ask the magic 8ball a question")
def eball(client, event, channel, nick, rest):
	return wchoice(ball8_opts)

@command("klingon", aliases=('klingonism',), doc="Ask the magic klingon a question")
def klingon(client, event, channel, nick, rest):
	return random.choice(klingonisms)

@command("roll", aliases=(), doc="Roll a die, default = 100.")
def roll(client, event, channel, nick, rest):
	if rest:
		rest = rest.strip()
		die = int(rest)
	else:
		die = 100
	myroll = random.randint(1, die)
	return "%s rolls %s" % (nick, myroll)

@command("flip", aliases=(), doc="Flip a coin")
def flip(client, event, channel, nick, rest):
	myflip = random.choice(('Heads', 'Tails'))
	return "%s gets %s" % (nick, myflip)

@command("deal", aliases=(), doc="Deal or No Deal?")
def deal(client, event, channel, nick, rest):
	mydeal = random.choice(('Deal!', 'No Deal!'))
	return "%s gets %s" % (nick, mydeal)

@command("ticker", aliases=("t",), doc="Look up a ticker symbol's current trading value")
def ticker(client, event, channel, nick, rest):
	ticker = rest.upper()
	# let's use Yahoo's nifty csv facility, and pull last time/price both
	symbol = 's'
	last_trade = 'l'
	format = ''.join((symbol, last_trade))
	url = 'http://finance.yahoo.com/d/quotes.csv?s=%(ticker)s&f=%(format)s' % vars()
	stockInfo = csv.reader(urllib.urlopen(url))
	lastTrade = next(stockInfo)
	ticker_given, price, date, time, diff = lastTrade[:5]
	if date == 'N/A':
		return "d'oh... could not find information for symbol %s" % ticker
	change = str(round((float(diff) / (float(price) - float(diff))) * 100, 1))
	return '%(ticker)s at %(time)s (ET): %(price)s (%(change)s%%)' % vars()

@command("pick", aliases=("p", 'p:', "pick:"), doc="Pick between a few options")
def pick(client, event, channel, nick, rest):
	question = rest.strip()
	choices = splitem(question)
	if len(choices) == 1:
		return "I can't pick if you give me only one choice!"
	else:
		pick = random.choice(choices)
		certainty = random.sample(certainty_opts, 1)[0]
		return "%s... %s %s" % (pick, certainty, pick)

@command("lunch", aliases=("lunchpick", "lunchpicker"), doc="Pick where to go to lunch")
def lunch(client, event, channel, nick, rest):
	rs = rest.strip()
	if not rs:
		return "Give me an area and I'll pick a place: (%s)" % (', '.join(list(config.lunch_choices)))
	if rs not in config.lunch_choices:
		return "I didn't recognize that area; here's what i have: (%s)" % (', '.join(list(config.lunch_choices)))
	choices = config.lunch_choices[rs]
	return random.choice(choices)

@command("password", aliases=("pw", "passwd",), doc="Generate a random password, similar to http://www.pctools.com/guides/password")
def password(client, event, channel, nick, rest):
	chars = '32547698ACBEDGFHKJMNQPSRUTWVYXZacbedgfhkjmnqpsrutwvyxz'
	passwd = []
	for i in range(8):
		passwd.append(random.choice(chars))
	return ''.join(passwd)

@command("insult", aliases=(), doc="Generate a random insult from http://www.webinsult.com/index.php")
def insult(client, event, channel, nick, rest):
	instype = random.randrange(4)
	insurl = "http://www.webinsult.com/index.php?style=%s&r=0&sc=1" % instype
	insre = re.compile('<div class="insult" id="insult">(.*?)</div>')
	html = get_html(insurl)
	insult = insre.search(html).group(1)
	if insult:
		if rest:
			insultee = rest.strip()
			util.karma.change(insultee, -1)
			if instype in (0, 2):
				cinsre = re.compile(r'\b(your)\b', re.IGNORECASE)
				insult = cinsre.sub("%s's" % insultee, insult)
			elif instype in (1, 3):
				cinsre = re.compile(r'^([TY])')
				insult = cinsre.sub(lambda m: "%s, %s" % (insultee, m.group(1).lower()), insult)
		return insult

@command("compliment", aliases=('surreal',), doc="Generate a random compliment from http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG")
def compliment(client, event, channel, nick, rest):
	compurl = 'http://www.madsci.org/cgi-bin/cgiwrap/~lynn/jardin/SCG'
	comphtml = ''.join([i for i in urllib.urlopen(compurl)])
	compmark1 = '<h2>\n\n'
	compmark2 = '\n</h2>'
	compliment = comphtml[comphtml.find(compmark1) + len(compmark1):comphtml.find(compmark2)]
	if compliment:
		compliment = re.compile(r'\n').sub('%s' % ' ', compliment)
		compliment = re.compile(r'  ').sub('%s' % ' ', compliment)
		if rest:
			complimentee = rest.strip()
			util.karma.change(complimentee, 1)
			compliment = re.compile(r'\b(your)\b', re.IGNORECASE).sub('%s\'s' % complimentee, compliment)
			compliment = re.compile(r'\b(you are)\b', re.IGNORECASE).sub('%s is' % complimentee, compliment)
			compliment = re.compile(r'\b(you have)\b', re.IGNORECASE).sub('%s has' % complimentee, compliment)
		return compliment


@command("karma", aliases=("k",), doc="Return or change the karma value for some(one|thing)")
def karma(client, event, channel, nick, rest):
	karmee = rest.strip('++').strip('--').strip('~~')
	if '++' in rest:
		util.karma.change(karmee, 1)
	elif '--' in rest:
		util.karma.change(karmee, -1)
	elif '~~' in rest:
		change = random.choice([-1, 0, 1])
		util.karma.change(karmee, change)
		if change == 1:
			return "%s karma++" % karmee
		elif change == 0:
			return "%s karma shall remain the same" % karmee
		elif change == -1:
			return "%s karma--" % karmee
	elif '==' in rest:
		t1, t2 = rest.split('==')
		util.karma.link(t1, t2)
		score = util.karma.lookup(t1)
		return "%s and %s are now linked and have a score of %s" % (t1, t2, score)
	else:
		karmee = rest or nick
		score = util.karma.lookup(karmee)
		return "%s has %s karmas" % (karmee, score)

@command("top10", aliases=("top",), doc="Return the top n (default 10) highest entities by Karmic value. Use negative numbers for the bottom N.")
def top10(client, event, channel, nick, rest):
	if rest:
		topn = int(rest)
	else:
		topn = 10
	selection = util.karma.list(topn)
	res = ' '.join('(%s: %s)' % (', '.join(n), k) for n, k in selection)
	return res

@command("bottom10", aliases=("bottom",), doc="Return the bottom n (default 10) lowest entities by Karmic value. Use negative numbers for the bottom N.")
def bottom10(client, event, channel, nick, rest):
	if rest:
		topn = -int(rest)
	else:
		topn = -10
	selection = util.karma.list(topn)
	res = ' '.join('(%s: %s)' % (', '.join(n), k) for n, k in selection)
	return res

@command("gettowork", aliases=("gtw",), doc="You really ought to, ya know...")
def gettowork(client, event, channel, nick, rest):
	suggestions = [u"Um, might I suggest working now",
		u"Get to work",
		u"Between the coffee break, the smoking break, the lunch break, the tea break, the bagel break, and the water cooler break, may I suggest a work break.  It’s when you do some work",
		u"Work faster",
		u"I didn’t realize we paid people for doing that",
		u"You aren't being paid to believe in the power of your dreams",]
	suggestion = random.choice(suggestions)
	rest = rest.strip()
	if rest:
		util.karma.change(rest, -1)
		suggestion = suggestion + ', %s' % rest
	else:
		util.karma.change(channel, -1)
	util.karma.change(nick, -1)
	return suggestion

@command("bitchingisuseless", aliases=("qbiu",), doc="It really is, ya know...")
def bitchingisuseless(client, event, channel, nick, rest):
	rest = rest.strip()
	if rest:
		util.karma.change(rest, -1)
	else:
		util.karma.change(channel, -1)
		rest = "foo'"
	advice = 'Quiet bitching is useless, %s. Do something about it.' % rest
	return advice

@command("curse", doc="Curse the day!")
def curse(client, event, channel, nick, rest):
	if rest:
		cursee = rest
	else:
		cursee = 'the day'
	util.karma.change(cursee, -1)
	return "/me curses %s!" % cursee

@command("tinytear", aliases=('tt', 'tear', 'cry'), doc="I cry a tiny tear for you.")
def tinytear(client, event, channel, nick, rest):
	if rest:
		return "/me sheds a single tear for %s" % rest
	else:
		return "/me sits and cries as a single tear slowly trickles down its cheek"

@command("stab", aliases=("shank", "shiv",),doc="Stab, shank or shiv some(one|thing)!")
def stab(client, event, channel, nick, rest):
	if rest:
		stabee = rest
	else:
		stabee = 'wildly at anything'
	if random.random() < 0.9:
		util.karma.change(stabee, -1)
		weapon = random.choice(weapon_opts)
		weaponadj = random.choice(weapon_adjs)
		violentact = random.choice(violent_acts)
		return "/me grabs a %s %s and %s %s!" % (weaponadj, weapon, violentact, stabee)
	elif random.random() < 0.6:
		util.karma.change(stabee, -1)
		return "/me is going to become rich and famous after i invent a device that allows you to stab people in the face over the internet"
	else:
		util.karma.change(nick, -1)
		return "/me turns on its master and shivs %s. This is reality man, and you never know what you're going to get!" % nick

@command("disembowel", aliases=("dis", "eviscerate"),doc="Disembowel some(one|thing)!")
def disembowel(client, event, channel, nick, rest):
	if rest:
		stabee = rest
		util.karma.change(stabee, -1)
	else:
		stabee = "someone nearby"
	return "/me takes %s, brings them down to the basement, ties them to a leaky pipe, and once bored of playing with them mercifully ritually disembowels them..." % stabee

@command("embowel", aliases=("reembowel",), doc="Embowel some(one|thing)!")
def embowel(client, event, channel, nick, rest):
	if rest:
		stabee = rest
		util.karma.change(stabee, 1)
	else:
		stabee = "someone nearby"
	return "/me (wearing a bright pink cape and yellow tights) swoops in through an open window, snatches %s, races out of the basement, takes them to the hospital with entrails on ice, and mercifully embowels them, saving the day..." % stabee

@command("chain", aliases=(),doc="Chain some(one|thing)down.")
def chain(client, event, channel, nick, rest):
	if rest:
		chainee = rest
	else:
		chainee = "someone nearby"
	if chainee == 'cperry':
		return "/me ties the chains extra tight around %s" % chainee
	elif random.randint(1,10) != 1:
		return "/me chains %s to the nearest desk.  you ain't going home, buddy." % chainee
	else:
		util.karma.change(nick, -1)
		return "/me spins violently around and chains %s to the nearest desk.  your days of chaining people down and stomping on their dreams are over!  get a life, you miserable beast." % nick

@command("bless", doc="Bless the day!")
def bless(client, event, channel, nick, rest):
	if rest:
		blesse = rest
	else:
		blesse = 'the day'
	util.karma.change(blesse, 1)
	return "/me blesses %s!" % blesse

@command("blame", doc="Pass the buck!")
def blame(client, event, channel, nick, rest):
	if rest:
		blamee = rest
	else:
		blamee = channel
	util.karma.change(nick, -1)
	if random.randint(1,10) == 1:
		yield "/me jumps atop the chair and points back at %s." % nick
		yield "stop blaming the world for your problems, you bitter, two-faced sissified monkey!"
	else:
		yield "I blame %s for everything!  it's your fault!  it's all your fault!!" % blamee
		yield "/me cries and weeps in despair"

@command("paste", aliases=(), doc="Drop a link to your latest paste")
def paste(client, event, channel, nick, rest):
	req = urllib.urlopen("%slast/%s" % (config.librarypaste, nick))
	if req.getcode() >= 200 and req.getcode() < 400:
		return req.geturl()
	else:
		return "hmm.. I didn't find a recent paste of yours, %s. Checkout %s" % (nick, config.librarypaste)

@contains('pmxbot', channels='unlogged', rate=.3)
def rand_bot(client, event, channel, nick, rest):
	normal_functions = [featurecreep, insult, motivate, compliment, cheer,
		golfclap, nastygram, curse, bless, job, hire, oregontrail,
		chain, tinytear, blame, panic, rubberstamp, dance, annoy, klingon,
		storytime, murphy]
	quote_functions = [quote, pq.zoidberg, pq.simpsons, pq.bender,
		pq.hal, pq.grail, pq.R, pq.anchorman, pq.hangover]
	func = random.choice(normal_functions + quote_functions)
	nick = nick if func in normal_functions else ''
	# save the func for troubleshooting
	rand_bot.last_func = func
	return func(client, event, channel, 'pmxbot', nick)

@contains("sqlonrails")
def yay_sor(client, event, channel, nick, rest):
	util.karma.change('sql on rails', 1)
	return "Only 76,417 lines..."

@contains("sql on rails")
def other_sor(*args):
	return yay_sor(*args)

calc_exp = re.compile("^[0-9 \*/\-\+\)\(\.]+$")
@command("calc", doc="Perform a basic calculation")
def calc(client, event, channel, nick, rest):
	mo = calc_exp.match(rest)
	if mo:
		try:
			return str(eval(rest))
		except:
			return "eval failed... check your syntax"
	else:
		return "misformatted arithmetic!"

@command("define", aliases=("def",), doc="Define a word")
def defit(client, event, channel, nick, rest):
	word = rest.strip()
	res = util.lookup(word)
	fmt = (u'{lookup.provider} says: {res}' if res else
		u"{lookup.provider} does not have a definition for that.")
	return fmt.format(**dict(vars(), lookup=util.lookup))

@command("urbandict", aliases=("urb", 'ud', 'urbandictionary', 'urbandefine', 'urbandef', 'urbdef'), doc="Define a word with Urban Dictionary")
def urbandefit(client, event, channel, nick, rest):
		word = rest.strip()
		newword, res = urbanlookup(word)
		if res is None:
			return "Arg!  I didn't find a definition for that."
		else:
			newword = plaintext(newword)
			res = plaintext(res)
			return 'Urban Dictionary says %s: %s' % (newword, res)


@command("acronym", aliases=("ac",), doc="Look up an acronym")
def acit(client, event, channel, nick, rest):
	word = rest.strip()
	res = lookup_acronym(word)
	if res is None:
		return "Arg!  I couldn't expand that..."
	else:
		return ' | '.join(res)

@command("fight", doc="Pit two sworn enemies against each other (separate with 'vs.')")
def fight(client, event, channel, nick, rest):
	if rest:
		vtype = random.choice(fight_victories)
		fdesc = random.choice(fight_descriptions)
		bad_protocol = False
		if 'vs.' not in rest:
			bad_protocol = True
		contenders = [c.strip() for c in rest.split('vs.')]
		if len(contenders) > 2:
			bad_protocol = True
		if bad_protocol:
			util.karma.change(nick.lower(), -1)
			args = (vtype, nick, fdesc)
			return "/me %s %s in %s for bad protocol." % args
		random.shuffle(contenders)
		winner,loser = contenders
		util.karma.change(winner, 1)
		util.karma.change(loser, -1)
		return "%s %s %s in %s." % (winner, vtype, loser, fdesc)

@command("progress", doc="Display the progress of something: start|end|percent")
def progress(client, event, channel, nick, rest):
	if rest:
		left, right, amount = [piece.strip() for piece in rest.split('|')]
		ticks = min(int(round(float(amount) / 10)), 10)
		bar = "=" * ticks
		return "%s [%-10s] %s" % (left, bar, right)

@command("nastygram", aliases=('nerf', 'passive', 'bcc'), doc="A random passive-agressive comment, optionally directed toward some(one|thing).")
def nastygram(client, event, channel, nick, rest):
	recipient = ""
	if rest:
		recipient = rest.strip()
		util.karma.change(recipient, -1)
	return passagg(recipient, nick.lower())

@command("therethere", aliases=('poor', 'comfort'), doc="Sympathy for you.")
def therethere(client, event, channel, nick, rest):
	if rest:
		util.karma.change(rest, 1)
		return "There there %s... There there." % rest
	else:
		return "/me shares its sympathy."

@command("saysomething", aliases=(), doc="Generate a Markov Chain response based on past logs. Seed it with a starting word by adding that to the end, eg '!saysomething dowski:'")
def saysomething(client, event, channel, nick, rest):
	word_factory = functools.partial(
		saysomethinglib.words_from_logger_and_quotes,
		botbase.logger,
		util.quotes,
	)
	sayer = saysomethinglib.FastSayer(word_factory)
	if rest:
		return sayer.saysomething(rest)
	else:
		return sayer.saysomething()

@command("tgif", doc="Thanks for the words of wisdow, Mike.")
def tgif(client, event, channel, nick, rest):
	return "Hey, it's Friday! Only two more days left in the work week!"

@command("fml", aliases=(), doc="A SFW version of fml.")
def fml(client, event, channel, nick, rest):
	return "indeed"

@command("storytime", aliases=('story',), doc="A story is about to be told.")
def storytime(client, event, channel, nick, rest):
	if rest:
		return "Come everyone, gather around the fire. %s is about to tell us a story!" % rest.strip()
	else:
		return "Come everyone, gather around the fire. A story is about to be told!"

@command("murphy", aliases=('law',), doc="Look up one of Murphy's laws")
def murphy(client, event, channel, nick, rest):
	return random.choice(murphys_laws)

@command("meaculpa", aliases=('apology', 'apologize',), doc="Sincerely apologize")
def meaculpa(client, event, channel, nick, rest):
	if rest:
		rest = rest.strip()

	if rest:
		return random.choice(direct_apologies) % dict(a=nick, b=rest)
	else:
		return random.choice(apologies) % dict(a=nick)


#Below is system junk
@command("help", aliases=('h',), doc="Help (this command)")
def help(client, event, channel, nick, rest):
	rs = rest.strip()
	if rs:
		for typ, name, f, doc, junk1, junk2, junk3, priority in _handler_registry:
			if name == rs:
				yield '!%s: %s' % (name, doc)
				break
		else:
			yield "command not found"
	else:
		def mk_entries():
			for typ, name, f, doc, junk1, junk2, junk3, priority in sorted(_handler_registry, key=lambda x: x[1]):
				if typ == 'command':
					aliases = sorted([x[1] for x in _handler_registry if x[0] == 'alias' and x[2] == f])
					res =  "!%s" % name
					if aliases:
						res += " (%s)" % ', '.join(aliases)
					yield res
		o = StringIO(" ".join(mk_entries()))
		more = o.read(160)
		while more:
			yield more
			time.sleep(0.3)
			more = o.read(160)

@command("ctlaltdel", aliases=('controlaltdelete', 'controlaltdelete', 'cad', 'restart', 'quit',), doc="Quits pmxbot. Daemontools should automatically restart it.")
def ctlaltdel(client, event, channel, nick, rest):
	if 'real' in rest.lower():
		sys.exit()
	else:
		return "Really?"

@command("hgup", aliases=('hg', 'update', 'hgpull'), doc="Update with the latest from mercurial")
def svnup(client, event, channel, nick, rest):
	svnres = os.popen('hg pull -u')
	svnres = svnres.read()
	svnres = svnres.splitlines()
	return svnres

@command("strike", aliases=(), doc="Strike last <n> statements from the record")
def strike(client, event, channel, nick, rest):
	yield NoLog
	rest = rest.strip()
	if not rest:
		count = 1
	else:
		if not rest.isdigit():
			yield "Strike how many?  Argument must be a positive integer."
			raise StopIteration
		count = int(rest)
	try:
		struck = botbase.logger.strike(channel, nick, count)
		yield ("Isn't undo great?  Last %d statement%s by %s were stricken from the record." %
		(struck, 's' if struck > 1 else '', nick))
	except Exception, e:
		traceback.print_exc()
		yield "Hmm.. I didn't find anything of yours to strike!"

@command("where", aliases=('last', 'seen', 'lastseen'), doc="When did pmxbot last see <nick> speak?")
def where(client, event, channel, nick, rest):
	onick = rest.strip()
	last = botbase.logger.last_seen(onick)
	if last:
		tm, chan = last
		return "I last saw %s speak at %s in channel #%s" % (
		onick, tm, chan)
	else:
		return "Sorry!  I don't have any record of %s speaking" % onick


global config

def run(configFile=None, configDict=None, configInput=None, start=True):
	global config
	import sys, yaml
	class O(object):
		def __init__(self, d):
			for k, v in d.iteritems():
				setattr(self, k, v)

	_setup_logging()

	if configInput:
		config = configInput
	elif configDict:
		config = O(configDict)
	else:
		if configFile:
			config_file = configFile
		else:
			if len(sys.argv) < 2:
				sys.stderr.write("error: need config file as first argument")
				raise SystemExit(1)
			config_file = sys.argv[1]
		config = O(yaml.load(open(config_file)))
	try:
		config.librarypaste
	except AttributeError:
		config.librarypaste = "http://a.libpa.st/"
	if config.librarypaste[-1] != '/':
		config.librarypaste = '%s/' % config.librarypaste

	if config.bot_nickname != 'pmxbot':
		@contains(config.bot_nickname, channels='unlogged', rate=.3)
		def rand_bot2(*args):
			return rand_bot(*args)

	_load_library_extensions()

	use_ssl = getattr(config, 'use_ssl', False)
	password = getattr(config, 'password', None)

	silent_bot = getattr(config, 'silent', False)

	class_ = botbase.LoggingCommandBot if not silent_bot else botbase.SilentCommandBot

	bot = class_(config.database, config.server_host, config.server_port,
		config.bot_nickname, config.log_channels, config.other_channels,
		config.feed_interval*60, config.feeds, use_ssl=use_ssl,
		password=password)
	if start:
		bot.start()

def _setup_logging():
	logging.basicConfig(level=logging.INFO, format="%(message)s")

def _load_library_extensions():
	"""
	Locate all setuptools entry points by the name 'pmxbot_handlers'
	and initialize them.
	Any third-party library may register an entry point by adding the
	following to their setup.py::

		entry_points = {
			'pmxbot_handlers': [
				'plugin_name = mylib.mymodule:initialize_func',
			],
		},

	`plugin_name` can be anything, and is only used to display the name
	of the plugin at initialization time.
	"""

	try:
		import pkg_resources
	except ImportError:
		log.warning('setuptools not available - entry points cannot be '
			'loaded')
		return

	group = 'pmxbot_handlers'
	entry_points = pkg_resources.iter_entry_points(group=group)
	for ep in entry_points:
		try:
			log.info('Loading %s', ep.name)
			init_func = ep.load()
			init_func()
		except Exception:
			log.exception("Error initializing plugin %s." % ep)
