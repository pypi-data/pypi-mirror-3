from setuptools import find_packages

setup_params = dict(
	name="pmxbot",
	use_hg_version=True,
	packages=find_packages(),
	include_package_data=True,
	entry_points=dict(
		console_scripts = [
			'pmxbot=pmxbot.pmxbot:run',
			'pmxbotweb=pmxbotweb.pmxbotweb:run',
		],
	),
	install_requires=[
		"pyyaml",
		"python-irclib>=0.4.8",
		"httplib2",
		"feedparser",
		"pytz",
		"wordnik==1.2dev-r2b12657",
		#for viewer
		"jinja2",
		"cherrypy",
	],
	dependency_links=[
		'https://bitbucket.org/jaraco/httplib2/downloads',
		'https://github.com/jaraco/wordnik-python/downloads',
	],
	description="IRC bot - full featured, yet extensible and customizable",
	license = 'MIT',
	author="You Gov, Plc. (jamwt, mrshoe, cperry, chmullig, and others)",
	author_email="open.source@yougov.com",
	maintainer = 'chmullig',
	maintainer_email = 'chmullig@gmail.com',
	url = 'http://bitbucket.org/yougov/pmxbot',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: MIT License',
		'Operating System :: POSIX',
		'Operating System :: Microsoft :: Windows',
		'Operating System :: MacOS :: MacOS X',
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		'Topic :: Communications :: Chat :: Internet Relay Chat',
		'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
	],
	long_description = open('README').read(),
	setup_requires=[
		'hgtools',
	],
)

if __name__ == '__main__':
	from setuptools import setup
	setup(**setup_params)
