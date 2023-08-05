###
### $Release: 0.2.0 $
### $Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

from __future__ import with_statement

import re

import picotest
test = picotest.new()

import cmdopt

##
## option definitions
##
parser_ = cmdopt.Parser()
# short and long options
parser_.option("-h, --help", "show help")
# short option only, but specify attribute name
parser_.option("-v #version", "print version")
# validation example
parser_.option("-m, --mode=MODE", "set mode ('verbose' or 'quiet')")\
       .validation(lambda val: (val != "verbose" and val != "quiet")
                               and "'verbose' or 'quiet' expected." or None)
# action example
parser_.option("--quiet", "quiet mode")\
       .action(lambda val, opts: setattr(opts, 'mode', "quiet"))
# optional argument
parser_.option("-i, --indent[=N]", "indent (default 2)")\
       .validation(lambda val: (val != True and not val.isdigit())
                               and "integer expected." or None)
# multiple option
def fn(val, opts):
    arr = getattr(opts, 'paths', None)
    if arr is None:
        opts.paths = []
    opts.paths.append(val)
parser_.option("-I PATH  #paths", "include path (multiple OK)").action(fn)
# private option (not displayed in help message)
parser_.option("-D", None)


with test("cmdopt.Schema"):


    with test("#add()"):

        @test.before
        def _(self):
            self.schema = cmdopt.Schema()
            self.item = self.schema.add("-m, --mode=MODE", "set mode")

        @test("returns item object.")
        def _(self):
            item = self.item
            self.assertTrue(isinstance(item, cmdopt.SchemaItem))

        @test("parses command-option definition.")
        def _(self):
            item = self.item
            self.assertEqual("m",        item.short)
            self.assertEqual("mode",     item.long)
            self.assertEqual("MODE",     item.arg)
            self.assertEqual(True,       item.required)
            self.assertEqual("mode",     item.attr)
            self.assertEqual("set mode", item.desc)
            self.assertEqual(None, item.validator)

        @test("sets default handler function.")
        def _(self):
            item = self.item
            self.assertTrue(isinstance(item.handler, type(lambda: None)))
            opts = cmdopt.Options()
            item.handler("verbose", opts)
            self.assertEqual("verbose", opts.mode)

        @test("register item object.")
        def _(self):
            schema = self.schema
            item = self.item
            self.assertTrue(schema.get("-m") is item)
            self.assertTrue(schema.get("--mode") is item)

        @test("throws error when option definition is invalid.")
        def _(self):
            schema = self.schema
            def fn():
                schema.add("-m MODE, --mode", "set mode", lambda val: 0)
            self.assertException(fn, ValueError, "add('-m MODE, --mode'): invalid option definition.")
        @test("recognizes '#name' as attribute name.")
        def _(self):
            schema = self.schema
            item = schema.add("-q #quiet", None)
            self.assertEqual("quiet", item.attr)
            self.assertEqual("q",     item.short)
            self.assertEqual(None,    item.long)
            #
            item = schema.add("-q value #quiet", None)
            self.assertEqual("quiet", item.attr)
            self.assertEqual("q",     item.short)
            self.assertEqual(None,    item.long)
            #
            item = schema.add("--silent #quiet", None)
            self.assertEqual("quiet",  item.attr)
            self.assertEqual(None,     item.short)
            self.assertEqual("silent", item.long)


    with test("#help()"):

        @test.fixture
        def parser(): yield parser_

        @test("returns help message of command-line options.")
        def _(self, parser):
            expected = (
                "  -h, --help          : show help\n"
                "  -v                  : print version\n"
                "  -m, --mode=MODE     : set mode ('verbose' or 'quiet')\n"
                "  --quiet             : quiet mode\n"
                "  -i, --indent[=N]    : indent (default 2)\n"
                "  -I PATH             : include path (multiple OK)\n"
                #"  -D                  : enable debug mode\n"
            )
            self.assertTextEqual(expected, parser.schema.help(20))
            self.assertTextEqual(expected, parser.help(20))

        @test("takes width and indent arguments.")
        def _(self, parser):
            expected = (
                "    -h, --help: show help\n"
                "    -v        : print version\n"
                "    -m, --mode=MODE: set mode ('verbose' or 'quiet')\n"
                "    --quiet   : quiet mode\n"
                "    -i, --indent[=N]: indent (default 2)\n"
                "    -I PATH   : include path (multiple OK)\n"
                #"    -D        : enable debug mode\n"
            )
            self.assertTextEqual(expected, parser.schema.help(10, "    "))
            self.assertTextEqual(expected, parser.help(10, "    "))

        @test("calculates width when not specified.")
        def _(self, parser):
            expected = (
                "  -h, --help       : show help\n"
                "  -v               : print version\n"
                "  -m, --mode=MODE  : set mode ('verbose' or 'quiet')\n"
                "  --quiet          : quiet mode\n"
                "  -i, --indent[=N] : indent (default 2)\n"
                "  -I PATH          : include path (multiple OK)\n"
                #"  -D               : enable debug mode\n"
            )
            self.assertTextEqual(expected, parser.schema.help())
            self.assertTextEqual(expected, parser.help())


with test("cmdopt.Builder"):

    @test.before
    def _(self):
        self.item = cmdopt.SchemaItem()
        self.builder = cmdopt.Builder(self.item)


    with test("#get_item()"):

        @test("returns item object.")
        def _(self):
            self.assertTrue(self.builder.get_item() is self.item)


    with test("#validation()"):

        @test("sets validator function.")
        def _(self):
            fn = lambda val: "OK"
            self.builder.validation(fn)
            self.assertTrue(self.builder.get_item().validator is fn)

        @test("returns self.")
        def _(self):
            ret = self.builder.validation(lambda val: "OK")
            self.assertTrue(ret is self.builder)


    with test("#action()"):

        @test("sets handler function.")
        def _(self):
            fn = lambda val, opts: setattr(opt, 'val', val)
            self.builder.action(fn)
            self.assertTrue(self.builder.get_item().handler is fn)

        @test("returns self.")
        def _(self):
            ret = self.builder.action(lambda val: "OK")
            self.assertTrue(ret is self.builder)


with test("cmdopt.Parser"):


    with test("#option()"):

        @test("registers option definition.")
        def _(self):
            parser = cmdopt.Parser()
            parser.option("-h, --help", "show help")
            item = parser.schema.get("-h")
            self.assertTrue(isinstance(item, cmdopt.SchemaItem))
            self.assertEqual("h", item.short)
            self.assertEqual("help", item.long)
            self.assertEqual("show help", item.desc)

        @test("returns builder object.")
        def _(self):
            parser = cmdopt.Parser()
            ret = parser.option("-h, --help", "show help")
            self.assertTrue(isinstance(ret, cmdopt.Builder))


    with test("#help()"):

        @test("calls #schema.help().")
        def _(self):
            called = []
            def help(*args, **kwargs):
                called.append((args, kwargs))
                return "RET"
            parser = cmdopt.Parser()
            parser.schema.help = help
            ret = parser.help(19, "   ")
            self.assertEqual("RET", ret)
            self.assertEqual(((19, "   "), {}), called[0])


    with test("#parse()"):

        @test.fixture
        def parser(): yield parser_

        @test("parses args.")
        def _(self, parser):
            args = ["-vmquiet", "--help", "foo", "bar"]
            defaults = {'mode': "verbose", 'file': "config.json"}
            opts = parser.parse(args, defaults)
            self.assertTrue(opts is not defaults)
            self.assertEqual(True, opts.help)
            self.assertEqual(True, opts.version)
            self.assertEqual("quiet",      opts.mode)    # overrided
            self.assertEqual("config.json", opts.file)   # not overrided
            self.assertEqual(["foo", "bar"], args)

        @test("parses long options.")
        def _(self, parser):
            # no argument
            args = ["--quiet", "foo", "bar"]
            opts = parser.parse(args)
            self.assertEqual("quiet", opts.mode)
            self.assertEqual(["foo", "bar"], args)
            # required argument
            args = ["--mode=verbose", "foo", "bar"]
            opts = parser.parse(args)
            self.assertEqual("verbose", opts.mode)
            self.assertEqual(["foo", "bar"], args)

        @test("parses short options.")
        def _(self, parser):
            args = ["-h", "-m", "quiet", "foo", "bar"]
            opts = parser.parse(args);
            self.assertEqual(True,    opts.help)     # no argument
            self.assertEqual("quiet", opts.mode)     # required argument
            self.assertEqual(["foo", "bar"], args)

        @test("short options can be conbined.")
        def _(self, parser):
            args = ["-hmquiet", "foo", "bar"]
            opts = parser.parse(args)
            self.assertEqual(True, opts.help)
            self.assertEqual("quiet", opts.mode)
            self.assertEqual(["foo", "bar"], args)

        @test("optional argument is available for short option.")
        def _(self, parser):
            ## when optional argument is not passed
            args = ["-i", "foo", "bar"];
            opts = parser.parse(args);
            self.assertEqual(True, opts.indent)
            self.assertEqual(["foo", "bar"], args)
            ## when optional argument is passed
            args = ["-i3", "foo", "bar"];
            opts = parser.parse(args);
            self.assertEqual('3', opts.indent)
            self.assertEqual(["foo", "bar"], args)

        @test("optional argument is available for long option.")
        def _(self, parser):
            ## when optional argument is not passed
            args = ["--indent", "foo", "bar"]
            opts = parser.parse(args)
            self.assertEqual(True, opts.indent)
            self.assertEqual(["foo", "bar"], args)
            ## when optional argument is passed
            args = ["--indent=3", "foo", "bar"]
            opts = parser.parse(args)
            self.assertEqual('3', opts.indent)
            self.assertEqual(["foo", "bar"], args)

        @test("throws error when unknown short option specified.")
        def _(self, parser):
            args = ["-xD", "foo", "bar"]
            def fn(): parser.parse(args, {})
            self.assertException(fn, cmdopt.ParseError, "-x: unknown option.")

        @test("throws error when unknown long option specified.")
        def _(self, parser):
            ## when argument not passed
            args = ["--SOS"];
            def fn(): parser.parse(args)
            self.assertException(fn, cmdopt.ParseError, "--SOS: unknown option.")
            ## with argument passed
            args = ["--sos=SOS"];
            def fn(): parser.parse(args, {})
            self.assertException(fn, cmdopt.ParseError, "--sos=SOS: unknown option.")

        @test("calls handler function.")
        def _(self, parser):
            args = ["--quiet", "foo", "bar"];
            opts = parser.parse(args)
            self.assertEqual(None, opts.quiet)
            self.assertEqual("quiet", opts.mode)
            ## multiple option
            args = ["-Ipath1", "-Ipath2", "-Ipath3"]
            opts = parser.parse(args)
            self.assertEqual(["path1", "path2", "path3"], opts.paths)

        @test("throws error when validator returns error message.")
        def _(self, parser):
            ## when short option
            args = ["-msilent", "foo", "bar"]
            def fn(): parser.parse(args)
            self.assertException(fn, cmdopt.ParseError, "-m silent: 'verbose' or 'quiet' expected.")
            ## when short option (optional)
            args = ["-i9.99", "foo", "bar"]
            def fn(): parser.parse(args)
            self.assertException(fn, cmdopt.ParseError, "-i9.99: integer expected.")
            ## when long option
            args = ["--indent=zero", "foo", "bar"]
            def fn(): parser.parse(args)
            self.assertException(fn, cmdopt.ParseError, "--indent=zero: integer expected.")

        @test("stop parsing when '--' found.")
        def _(self, parser):
            args = ["-h", "--", "-m", "verbose"]
            opts = parser.parse(args)
            self.assertEqual(["-m", "verbose"], args)
            self.assertEqual(True, opts.help)
            self.assertEqual(None, opts.mode)

        @test("returns different object from defaults.")
        def _(self, parser):
            args = ["-Dm", "verbose", "foo", "bar"];
            defaults = {};
            opts = parser.parse(args, defaults)
            self.assertTrue(opts is not defaults)
            self.assertNotEqual(defaults, opts)
            self.assertEqual(0, len(defaults))


with test("cmdopt.ParseError"):

    @test.fixture
    def err(): yield cmdopt.ParseError("SOS")

    @test("subclass of Error")
    def _(self, err):
        self.assertTrue(isinstance(err, Exception))

    @test("#message is set.")
    def _(self, err):
        self.assertEqual("SOS", str(err))


with test("cmdopt.Options"):

    @test.fixture
    def bunch():
        yield cmdopt.Options(indent=2, paths=['path1'], help=True, mode="verbose")

    with test("#__init__()"):

        @test("takes keyword arguments.")
        def _(self, bunch):
            self.assertEqual(2,         bunch.indent)
            self.assertEqual(['path1'], bunch.paths)
            self.assertEqual(True,      bunch.help)
            self.assertEqual("verbose", bunch.mode)

    with test("#__repr__()"):

        @test("prints key and values in order of key.")
        def _(self, bunch):
            expected = "<cmdopt.Options: help=True, indent=2, mode='verbose', paths=['path1']>"
            self.assertEqual(expected, repr(bunch))


if __name__ == '__main__':
    picotest.main()
