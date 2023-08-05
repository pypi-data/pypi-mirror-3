# vim: set fileencoding=utf-8 :
# Todo.txt manager in Python
# Copyright (C) 2011 Ilkka Laukkanen <ilkka.s.laukkanen@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from argparse import ArgumentParser
import os.path
import sys
from configparser import ConfigParser
import re

class Options(object):
    """Combined command line args and config file parser.
    
    There are three types of args: flags, options and positional arguments.
    Flags have boolean values, options and positionals unicode values.

    >>> o = Options('description')
    >>> o.add_flag('my_flag', help='Help for my flag')
    >>> o.add_flag('other_flag', help='Help for my other flag')
    >>> o.add_flag('yet_another', help='Yet another flag')
    >>> o.add_option('thingy', group='other', help='Set thingy')
    >>> o.add_flag('flaggy', group='other')
    >>> o.add_argument('widget')

    Arguments also have optional counts: '*' for 0..n, '+' for 1..n or
    any integer. Specifying a count makes the argument's value always be
    a list. Not specifying the count makes the value be a plain value.

    You can pass the 'dest' keyword-only argument to add_argument for nicer,
    pluralized access to list-valued arguments.

    >>> o.add_argument('id', dest='ids', group='other', type=int, count='*')

    >>> o.parse(argv=['--my_flag', '-y', '--thingy', 'babar 1234', 'frobozz', '1', '2', '3'])
    >>> o.main.my_flag
    True
    >>> o.main.other_flag
    False
    >>> o.main.yet_another
    True
    >>> o.other.thingy
    u'babar 1234'
    >>> o.other.flaggy
    False
    >>> o.main.widget
    u'frobozz'
    >>> o.other.ids
    [1, 2, 3]
    """
    def __init__(self, description=None, **kwargs):
        self.parser = ArgumentParser(description=description)
        self.args = None
        self.config = ConfigParser()
        self.defaults = {}
        self.used_optdefs = []
        self.valuators = {}
        self.sub = None
        self.subparsers = {}
        self.command = None
        self.has_been_parsed = False

    @staticmethod
    def _booleanify(val):
        """Convert non-boolean option values to boolean.
        
        >>> Options._booleanify(u'yes')
        True
        >>> Options._booleanify('no')
        False
        >>> Options._booleanify('TrUE')
        True
        >>> Options._booleanify(False)
        False
        """
        if not (type(val) == str or type(val) == unicode):
            return bool(val)
        defs = {
                u'yes': True,
                u'true': True,
                u'no': False,
                u'false': False
                }
        val = unicode(val.lower())
        if val in defs:
            return defs[val]
        return None

    def __getattr__(self, attr):
        class Optgroup:
            def __init__(self, options, group):
                self.options = options
                self.group = group
            def __getattr__(self, attr):
                if getattr(self.options.args, attr) != None:
                    return self.options.valuators[self.group][attr](getattr(self.options.args, attr))
                elif self.group in self.options.config and attr in self.options.config[self.group]:
                    return self.options.valuators[self.group][attr](self.options.config[self.group][attr])
                else:
                    return self.options.defaults[self.group][attr]
        return Optgroup(self, attr)
    
    def _make_short_opt_for(self, option):
        """Make short one-character option for given option name.

        Remember what optchars have been used and don't return them again.
        Also try very hard not to return any reserved optchars (like '-h'
        for help and '-C' for config file).

        >>> o = Options()
        >>> o._make_short_opt_for('foobar')
        '-f'
        >>> o._make_short_opt_for('fuzzball')
        '-u'
        >>> o._make_short_opt_for('fun')
        '-n'
        >>> o._make_short_opt_for('fun')
        '-F'
        """
        for c in re.sub('r[hC]', '', option + option.upper() + "abcdefghijklmnopqrstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ"):
            if c == 'h':
                continue # try not to clobber help command
            opt = "-{}".format(c)
            if not opt in self.used_optdefs:
                self.used_optdefs.append(opt)
                return opt
        raise RuntimeError("Couldn't determine optchar for {}".format(option))

    def add_flag(self, flag, **kwargs):
        """Add a boolean flag.
        
        Command line options will be derived from flag name. Config file
        setting will have the same name as the flag, and the value will
        be accessible via an attribute with the same name also. If group
        keyword-only argument is not specified, the flag will be in the
        'main' group. If default keyword-only argument is not specified,
        the default is True. Help text is specified with the help keyword-
        only argument.
        """
        default = kwargs['default'] if 'default' in kwargs else False
        group = kwargs['group'] if 'group' in kwargs else 'main'
        help = kwargs['help'] if 'help' in kwargs else None
        parser = self.subparsers[group] if group in self.subparsers else self.parser
        parser.add_argument(self._make_short_opt_for(flag),
                "--{}".format(flag), dest=flag,
                action='store_const', const=not default,
                help=help)
        if group not in self.defaults:
            self.defaults[group] = {}
        if group not in self.valuators:
            self.valuators[group] = {}
        self.defaults[group][flag] = default
        self.valuators[group][flag] = self._booleanify

    def add_option(self, option, **kwargs):
        """Add an option taking a unicode argument.
        
        Command line options will be derived from option name. Config file
        setting will have the same name as the option, and the value will
        be accessible via an attribute with the same name also. If group
        keyword-only argument is not specified, the option will be in the
        'main' group. If default keyword-only argument is not specified,
        the default is None. Help text is specified with the help keyword-
        only argument.
        """
        default = kwargs['default'] if 'default' in kwargs else None
        group = kwargs['group'] if 'group' in kwargs else 'main'
        help = kwargs['help'] if 'help' in kwargs else None
        parser = self.subparsers[group] if group in self.subparsers else self.parser
        parser.add_argument(self._make_short_opt_for(option),
                "--{}".format(option), dest=option, metavar=option.upper(),
                type=unicode, help=help)
        if group not in self.defaults:
            self.defaults[group] = {}
        if group not in self.valuators:
            self.valuators[group] = {}
        self.defaults[group][option] = default
        self.valuators[group][option] = unicode

    def parse(self, **kwargs):
        """Parse command line and config file.
        
        By default parser sys.argv, but command line args can be passed
        as an array too. To parse a config file too, pass 'config_file'
        kwarg. Passing that argument will also enable the config file
        command line option, with the default set to whatever the value
        of the kwarg is.

        >>> import tempfile; import os
        >>> (handle, filename) = tempfile.mkstemp(); os.close(handle)
        >>> f = open(filename, 'w+')
        >>> f.write("[main]\\n")
        >>> f.write("my_flag = yes\\n")
        >>> f.write("[mygroup]\\n")
        >>> f.write("a_setting = blah blah raspberry 3.14159")
        >>> f.close()
        >>> o = Options()
        >>> o.add_flag('my_flag', default=False)
        >>> o.add_flag('other_flag', default=False)
        >>> o.add_option('a_setting', group='mygroup')
        >>> o.parse(argv=['-o'], config_file=filename)
        >>> o.main.my_flag
        True
        >>> o.main.other_flag
        True
        >>> o.mygroup.a_setting
        u'blah blah raspberry 3.14159'

        parse() can only be called once for a given Options instance.

        >>> o.parse(argv=['--my_flag'])
        Traceback (most recent call last):
        ...
        RuntimeError: parse can only be called once for any given Options instance.

        Config file overrides defaults, and command line overrides config file.

        >>> o = Options()
        >>> o.add_flag('my_flag', default=True)
        >>> o.add_option('a_setting', group='mygroup', default='asdf')
        >>> o.parse(argv=['--my_flag'], config_file=filename)
        >>> o.main.my_flag
        False
        >>> o.mygroup.a_setting
        u'blah blah raspberry 3.14159'
        """
        if self.has_been_parsed:
            raise RuntimeError("parse can only be called once for any given Options instance.")
        # Add config file arg here to not clobber any user stuff
        if 'config_file' in kwargs:
            self.parser.add_argument('-C', '--config_file', dest='config_file',
                    type=unicode, default=kwargs['config_file'])
        self.args = self.parser.parse_args(kwargs['argv']) if 'argv' in kwargs \
                else self.parser.parse_args()
        self.command = unicode(self.args.command) if hasattr(self.args, 'command') else None
        if 'config_file' in self.args:
            self.config.read(self.args.config_file)
        self.has_been_parsed = True
    
    def add_subcommand(self, command, **kwargs):
        """Add a subcommand.
        
        Subcommands create a new argument group. To add a subcommand-specific
        command-line argument and option, pass the subcommand's name as
        group.

        >>> o = Options()
        >>> o.add_subcommand('frob', help='frob the widget')
        >>> o.add_flag('foo')
        >>> o.add_flag('bar')
        >>> o.add_flag('baz', group='frob')
        >>> o.parse(argv=['-f', 'frob', '--baz'])

        After parsing, the subcommand used is available as the "command"
        attribute.

        >>> o.command
        u'frob'
        >>> o.frob.baz
        True
        """
        help = kwargs['help'] if 'help' in kwargs else None
        if not self.sub:
            self.sub = self.parser.add_subparsers(dest='command',
                    title='Subcommands')
        self.subparsers[command] = self.sub.add_parser(command, help=help)

    def add_argument(self, argument, **kwargs):
        """Add a positional argument.
        """
        group = kwargs['group'] if 'group' in kwargs else 'main'
        help = kwargs['help'] if 'help' in kwargs else None
        count = kwargs['count'] if 'count' in kwargs else None
        dest = kwargs['dest'] if 'dest' in kwargs else argument
        type = kwargs['type'] if 'type' in kwargs else unicode
        parser = self.subparsers[group] if group in self.subparsers else self.parser
        parser.add_argument(dest, metavar=argument.upper(),
                type=type, nargs=count, help=help)
        if group not in self.valuators:
            self.valuators[group] = {}
        self.valuators[group][dest] = lambda x: x

