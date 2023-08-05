###
### $Release: 0.2.0 $
### $Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, os, re


class Schema(object):

    def __init__(self):
        self.items = []
        self._option2item = {}

    def get(self, opt):   # ex. '-h' or '--help'
        return self._option2item.get(opt)

    def add(self, options, desc, validator=None, handler=None):
        attr = None
        m = re.search(r' *\#(\w+)$', options)
        if (m):
            attr = m.group(1)
            options = options[:-len(m.group(0))]
        short, long, arg, required = self._parse_options(options)
        attr = attr or long or short
        if not handler:
            handler = lambda val, opts, _attr=attr: setattr(opts, _attr, val)
        item = SchemaItem(short=short, long=long, arg=arg, required=required,
                          attr=attr, desc=desc, options=options,
                          validator=validator, handler=handler)
        self._register(item)
        return item

    _rexp1 = re.compile(r'^ *-(\w), *--(\w[-\w]*)(?:=(\S+)|\[=(\S+)\])?$')
    _rexp2 = re.compile(r'^ *-(\w)(?: +(\S+)|\[(\S+)\])?$')
    _rexp3 = re.compile(r'^ *--(\w[-\w]*)(?:=(\S+)|\[=(\S+)\])?$')

    def _parse_options(self, options):
        short = long = arg = arg2 = None
        while -1:
            m = self._rexp1.match(options)
            if (m):
                short, long, arg, arg2 = m.groups()
                break
            m = self._rexp2.match(options)
            if (m):
                short, arg, arg2 = m.groups()
                break
            m = self._rexp3.match(options)
            if (m):
                long, arg, arg2 = m.groups()
                break
            raise ValueError("add('%s'): invalid option definition." % (options,))
        return short, long, arg or arg2, bool(arg)

    def _register(self, item):
        self.items.append(item)
        if item.short: self._option2item["-" + item.short] = item
        if item.long:  self._option2item["--" + item.long] = item

    def help(self, width=None, indent="  "):
        if width is None:
            width = 0
            for item in self.items:
                if item.desc and len(item.options) > width:
                    width = len(item.options)
            width += 1
            max = 20
            if width > max: width = max
        buf = []; add = buf.append
        fmt = "%s%%-%ss: %%s\n" % (indent, width)
        for item in self.items:
            if item.desc:
                add(fmt % (item.options, item.desc))
        return "".join(buf)


class SchemaItem(object):

    def __init__(self, short=None, long=None, arg=None, required=None, attr=None,
                 desc=None, options=None, validator=None, handler=None):
        self.short     = short
        self.long      = long
        self.arg       = arg
        self.required  = required
        self.attr      = attr
        self.desc      = desc
        self.options   = options
        self.validator = validator
        self.handler   = handler


class Builder(object):

    def __init__(self, item):
        self._item = item

    def get_item(self):
        return self._item

    def validation(self, func):
        self._item.validator = func
        return self

    def action(self, func):
        self._item.handler = func
        return self


class Parser(object):

    def __init__(self):
        self.schema = Schema()

    def option(self, options, desc):
        item = self.schema.add(options, desc)
        return Builder(item)

    def help(self, width=None, indent="  "):
        return self.schema.help(width, indent)

    def parse(self, args, defaults=None):
        opts = self._new_opts(defaults)
        while args:
            arg = args.pop(0)
            if   arg == "--":          break
            elif arg.startswith("--"): self._parse_long(arg, opts)
            elif arg.startswith("-"):  self._parse_short(arg, args, opts)
            else:
                args.insert(0, arg)
                break
        return opts

    def _new_opts(self, defaults=None):
        d = dict( (item.attr, None) for item in self.schema.items )
        if defaults:
            d.update(defaults)
        return Options(**d)

    def _parse_long(self, arg, opts):
        m = re.match(r'^--(\w[-\w]*)(?:=(.*))?$', arg)
        if not m:
            raise ParseError("%s: invalid long option." % (arg,))
        name, val = m.groups()
        item = self.schema.get("--" + name)
        if not item:
            raise ParseError("%s: unknown option." % (arg,))
        if val is None:
            if item.required:
                raise ParseError("%s: argument required." % (arg,))
        else:
            if not item.arg:
                raise ParseError("%s: unexpected argument." % (arg,))
        if val is None: val = True
        self._call_validator(item.validator, val, arg)
        self._call_handler(item.handler, val, opts)

    def _parse_short(self, arg, args, opts):
        i, n = 1, len(arg)
        while i < n:
            ch = arg[i]
            item = self.schema.get("-" + ch)
            if not item:
                raise ParseError("-%s: unknown option." % ch)
            if not item.arg:
                val = True
            elif item.required:
                val = arg[i+1:]
                if not val:
                    if not args:
                        raise ParseError("-%s: argument required." % ch)
                    val = args.pop(0)
                i = n
            else:
                val = arg[i+1:] or True
                i = n
            if   val is True:   optarg = "-%s"    % (ch,)
            elif item.required: optarg = "-%s %s" % (ch, val)
            else:               optarg = "-%s%s"  % (ch, val)
            self._call_validator(item.validator, val, optarg)
            self._call_handler(item.handler, val, opts)
            i += 1

    def _call_validator(self, validator, val, arg):
        if validator:
            errmsg = validator(val)
            if errmsg:
                raise ParseError("%s: %s" % (arg, errmsg))

    def _call_handler(self, handler, val, opts):
        if handler:
            handler(val, opts)


class ParseError(Exception):
    pass


class Options(object):

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        d = self.__dict__
        s = ", ".join( "%s=%r" % (k, d[k]) for k in sorted(d.keys()) )
        return "<cmdopt.Options: %s>" % s
