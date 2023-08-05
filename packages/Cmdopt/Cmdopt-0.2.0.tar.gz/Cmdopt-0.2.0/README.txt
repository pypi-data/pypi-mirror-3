================
Cmdopt.py README
================

Release: 0.2.0


About
-----

Cmdopt.py is command-line option parser for Python.

Cmdopt.py support Python 2.4 or later, including Python 3.


Install
-------

::

	$ easy_install cmdopt


Usage
-----

Example::

	## create parser
	import cmdopt
	parser = cmdopt.Parser()
	## define options
	parser.option("-h, --help",      "show help")
	parser.option("-f, --file=FILE", "read file")
	## parse args
	import sys
	args = sys.argv[1:]
	defaults = {'file': "config.json"}
	try:
	    opts = parser.parse(args, defaults)
	    print(opts)
	except cmdopt.ParseError as ex:
	    sys.stderr.write("%s\n" % ex)
	    sys.exit(1)

More example::

	## no argument
	parser.option("-h",         "show help")
	parser.option("    --help", "show help")
	parser.option("-h, --help", "show help")
	## required argument
	parser.option("-f FILE",         "read file")
	parser.option("    --file=FILE", "read file")
	parser.option("-f, --file=FILE", "read file")
	## optional argument
	parser.option("-i[N]",            "indent width")
	parser.option("    --indent[=N]", "indent width")
	parser.option("-i, --indent[=N]", "indent width")

Validation::

	parser.option("-m, --mode=MODE", "set mode")\
	      .validation(lambda val: val not in ['verbose', 'quiet']
	                              and "'verbose' or 'quiet' expected.")
	parser.option("-i, --indent[=N]", "indent width (default 2)")\
	      .validation(lambda val: val != True and not val.isdigit()
	                              and "integer required.")

Action::

	## change default handler
	parser.option("--verbose", "quiet mode")\
	      .action(lambda val, opts: setattr(opts, 'mode', "verbose"))
	parser.option("--quiet", "quiet mode")\
	      .action(lambda val, opts: setattr(opts, 'mode', "quiet"))
	
	## The following definitions...
	parser.option("-h, --help",      "show help")
	parser.option("-f, --file=FILE", "read file")
	## are equivarent to:
	parser.option("-h, --help",      "show help")\
	      .action(lambda val, opts: setattr(opts, 'help', val))
	parser.option("-f, --file=FILE", "read file")\
	      .action(lambda val, opts: setattr(opts, 'file', val))

Multiple option::

	## define custom handler to store values into list
	def add_path(val, opts):
	    arr = getattr(opts, 'paths', None)
	    if arr is None:
	        opts.paths = []
	    opts.paths.append(val)
	parser.option("-I path  #paths", "include path (multiple OK)")\
	      .action(add_path)
	##
	opts = parser.parse(["-Ipath1", "-Ipath2", "-Ipath3"])
	assert opts.paths == ["path1", "path2", "path3"]

Attribute name::

	## usually, long name or sort name is used as attribute name of opts.
	parser.option("-h, --help", "show help")
	opts = parser.parse(["-h"])
	assert opts.help == True    # attr name == long name
	parser.option("-h", "show help")
	opts = parser.parse(["-h"])
	assert opts.h == True       # attr name == short name
	## it is possible to specify attribute name by '#name'.
	## this is very helpful when you want not to use long name.
	parser.option("-h  #help", "show help")
	opts = parser.parse(["-h"])
	assert opts.help == True    # not opts.h

Help message::

	print("Usage: command [options] [file...]")
	print(parser.help())    # or parser.help(20, "  ")

Private option::

	parser.option("-D, --debug", None)   # private option: no description
	helpmsg = parser.help()
	assert '--debug' not in helpmsg      # not included in help message


History
-------

Release 0.2.0
~~~~~~~~~~~~~

* Public released


License
-------

$License: MIT License $


Copyright
---------

$Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $
