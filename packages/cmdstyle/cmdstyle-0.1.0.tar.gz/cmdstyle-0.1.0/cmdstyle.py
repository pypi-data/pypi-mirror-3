import collections
import os
import re
import sys


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class CommandError(Error):
    """Base class exceptions caused by errors in defining command classes."""
    pass


class DuplicateLongnameError(CommandError):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return "Long name '{}' can't be used by more than one option.".format(
                self._name)


class DuplicateShortnameError(CommandError):
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def __str__(self):
        return ("Short name '{}' can't be used by more than one option. "
               "(This might be caused by the InferShortnamesFromLongnames "
               "setting.)".format(self._name))


class ParseError(Error):
    """Base class for errors raised during argument parsing"""
    pass


class TooManyArgsError(ParseError):
    pass


class UnknownOptionError(ParseError):
    pass


class OptMissingArgError(ParseError):
    pass


class Param():
    # This class has a two step initialization:
    # First, __init__ is called when the Options are declared.
    # Next, _paramInit is called when the Command is created.

    def __init__(self, *, default=None, **kwargs):
        self._default = default
        self._attrname = None
        super().__init__(**kwargs)

    def _paramInit(self, commandClass, attrname, commandSettings):
        self._attrname = attrname

        getter = lambda self_: getattr(self_, '_' + attrname, self.default)
        setattr(commandClass, attrname, property(getter))

    @property
    def default(self):
        return self._default

    def setvalue(self, instance, value):
        setattr(instance, '_' + self._attrname,  value)


class Operand(Param):
    # These are Parameters that aren't options.
    # The terminology used is from
    # http://pubs.opengroup.org/onlinepubs/009695399/basedefs/xbd_chap12.html

    def __init__(self, *, name=None, **kwargs):
        self._name = name
        super().__init__(**kwargs)

    @property
    def name(self):
        return (self._name or self._attrname).upper()


class ListOperand(Operand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Option(Param):
    _name_re = re.compile('^[a-zA-Z0-9_]*$')

    # For longname and shortname
    #   - None means that the command should infer it
    #   - '' means that command should not infer it and
    #     is only allowed when another name is provided
    def __init__(self, *,
        longname=None, shortname=None, argname='ARG',
        description='', **kwargs):

        if longname:
            if len(longname) == 1:
                raise TypeError('Longname must be more than one character '
                                'long.')

            if not Option._name_re.match(longname):
                raise TypeError('Longname includes illegal characters.')

        if shortname:
            if len(shortname) != 1:
                raise TypeError('Shortname must be one character long.')

            if not Option._name_re.match(shortname):
                raise TypeError('Shortname includes illegal characters.')

        if longname == '' and shortname == '':
            raise TypeError("Longname and shortname can't both be blank.")

        self._longname = longname
        self._shortname = shortname
        self._argname = argname
        self._description = description

        super().__init__(**kwargs)

    def _paramInit(self, commandClass, attrname, commandSettings):
        commandSettings = commandSettings or CommandSettings()

        if commandSettings.inferNamesFromAttrnames:
            if len(attrname) > 1 and self._longname is None:
                self._longname = attrname
            if len(attrname) == 1 and self._shortname is None:
                self._shortname = attrname

        if commandSettings.inferShortnamesFromLongnames:
            if self._longname and self._shortname is None:
                self._shortname = self._longname[0]

        self._shortname = self._shortname or ''
        self._longname = self._longname or ''

        super()._paramInit(commandClass, attrname, commandSettings)

    @property
    def shortname(self):
        return self._shortname

    @property
    def longname(self):
        return self._longname

    @property
    def argname(self):
        return self._argname

    @property
    def description(self):
        return self._description

    @property
    def helpspec(self):
        column2 = ''
        if self.longname:
            column2 += '--' + self.longname
        if type(self) == Option:
            column2 += ' ' + self.argname

        return (
            '-' + self.shortname if self.shortname else '',
            column2,
            self.description)


class Flag(Option):
    def __init__(self, **kwargs):
        kwargs.setdefault('default', False)
        super().__init__(**kwargs)


class CommandSettings():
    def __init__(self,
            inferNamesFromAttrnames=True,
            inferShortnamesFromLongnames=True):
        self._inferNamesFromAttrnames = inferNamesFromAttrnames
        self._inferShortnamesFromLongnames = inferShortnamesFromLongnames

    @property
    def inferNamesFromAttrnames(self):
        return self._inferNamesFromAttrnames

    @property
    def inferShortnamesFromLongnames(self):
        return self._inferShortnamesFromLongnames


class CommandMeta(type):

    @classmethod
    def __prepare__(mcs, name, bases):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, classdict):
        commandClass = type.__new__(mcs, name, bases, classdict)

        paramAttrs = []
        settings = None

        for attrname, attr in classdict.items():
            if attrname.startswith('_'):
                continue

            if commandClass.__module__ != __name__ and attrname == 'parse':
                raise TypeError("Command can't define `parse`.")
            if commandClass.__module__ != __name__ and attrname == 'help':
                raise TypeError("Command can't define `help`.")

            if isinstance(attr, CommandSettings):
                if not settings:
                    settings = attr
                else:
                    raise TypeError("Command can't have more than one "
                                    "CommandSettings.")

            if isinstance(attr, Param):
                paramAttrs.append((attrname, attr))

        operands = []
        listParam = None
        options = []
        optionsByShort = {}
        optionsByLong = {}

        for attrname, param in paramAttrs:
            param._paramInit(commandClass, attrname, settings)

            if isinstance(param, Operand):
                operands.append(param)

            if isinstance(param, ListOperand):
                if not listParam:
                    listParam = param
                else:
                    raise TypeError("Command can't have more than one "
                                    "ListOperand.")

            if isinstance(param, Option):
                options.append(param)
                if param.shortname:
                    if param.shortname in optionsByShort:
                        raise DuplicateShortnameError(param.shortname)
                    optionsByShort[param.shortname] = param
                if param.longname:
                    if param.longname in optionsByLong:
                        raise DuplicateLongnameError(param.longname)
                    optionsByLong[param.longname] = param

        def parse(self, args):

            args = args[2:]
            current = None

            def next():
                nonlocal current
                current = args.pop(0) if args else None
                return current

            operands_ = operands[:]
            operandArgs = []

            def isOption(arg):
                return arg not in (None, '-', '--') and arg.startswith('-')

            def parseLongOpt():
                optName = current[2:]
                option = optionsByLong.get(optName)
                if not option:
                    raise UnknownOptionError()

                if not isinstance(option, Flag):
                    value = next()
                    if value is None or isOption(value):
                        raise OptMissingArgError()
                else:
                    value = True

                option.setvalue(self, value)

            def parseShortOptGroup():
                shortOptGroup = current[1:]
                for index, optName in enumerate(shortOptGroup):
                    option = optionsByShort.get(optName)
                    if not option:
                        raise UnknownOptionError()

                    if not isinstance(option, Flag):
                        value = shortOptGroup[index + 1:]
                        if value == '':
                            value = next()
                        if value is None or isOption(value):
                            raise OptMissingArgError()

                        option.setvalue(self, value)
                        break
                    else:
                        option.setvalue(self, True)

            next()
            while current is not None:
                if current == '--':
                    operandArgs += args
                    break
                elif current.startswith('--'):
                    parseLongOpt()
                elif current.startswith('-'):
                    parseShortOptGroup()
                else:
                    operandArgs.append(current)

                next()

            while operands_ and operandArgs:
                operand = operands_.pop(0)
                if isinstance(operand, ListOperand):
                    listlen = len(operandArgs) - len(operands_)
                    operand.setvalue(self, operandArgs[:listlen])
                    operandArgs[:listlen] = []
                    continue

                operand.setvalue(self, operandArgs.pop(0))

            if operandArgs:
                raise TooManyArgsError()

        def help(self, name, print):

            def print_table(rows, margins):
                if not rows:
                    return

                left_margin = margins[0]
                margins = [0] + list(margins[1:])

                widths = []
                for i in range(len(rows[0])):
                    width = max(len(row[i]) for row in rows)
                    widths.append(width)

                for i, width in enumerate(widths):
                    if not width:
                        margins[i] = 0

                for i, width in enumerate(widths[:-1]):
                    if width:
                        break
                    margins[i + 1] = 0

                for row in rows:
                    output = ' ' * left_margin
                    for item, margin, width in zip(row, margins, widths):
                        output += ' ' * margin + item.ljust(width)
                    output = output.rstrip()
                    print(output)

            doc_lines = re.split(r'\r\n|\n|\r', self.__doc__ or '')
            summary, explanation = doc_lines[0], doc_lines[1:]

            print(name + (': ' + summary if summary else ''))

            usage = 'usage: ' + name
            if operands:
                usage += ' ' + ' '.join(operand.name for operand in operands)
            print(usage)

            if explanation:
                for line in explanation:
                    line = line.lstrip()
                    if line == '':
                        print('')
                        continue
                    print('  ' + line.lstrip())
                pass

            if options:
                print('Options:')
                print('')

                rows = [option.helpspec for option in options]
                print_table(rows, (0, 1, 2))

        commandClass.parse = parse
        commandClass.help = help

        return commandClass


class Command(object, metaclass=CommandMeta):
    # Included to show signature.
    # Will be overwritten by CommandMeta.
    def parse(self, args):
        pass

    # Included to show signature.
    # Will be overwritten by CommandMeta.
    def help(self, name, print):
        pass


class Program():

    def __init__(self, execname, title, description, siteurl,
                 stdout=sys.stdout, stderr=sys.stderr):
        self._execname = execname
        self._title = title
        self._description = description
        self._siteurl = siteurl
        self._stdout = stdout
        self._stderr = stderr

        self._commands = {}

    def run(self, args):
        if len(args) <= 1:
            self._printHelpNotice()
            return 0

        command_name = args[1]

        if command_name == 'help':
            if len(args) == 2:
                self._printHelp()
                return 0
            elif len(args) == 3:
                help_arg = args[2]
                command = self._commands.get(help_arg)
                if not command:
                    self._print(
                        'Unknown command: `{}`'.format(help_arg),
                        self._stderr)
                    return 1
                self._printHelpFor(command)
                return 0

        command = self._commands.get(command_name)
        if not command:
            self._print(
                'Unknown command: `{}`'.format(command_name),
                self._stderr)
            self._printHelpNotice(self._stderr)
            return 1

        try:
            command.parse(args)
            return command()
        except ParseError as error:
            errorTemplate = {
                TooManyArgsError: 'Too many arguments for `{}`.',
                UnknownOptionError: 'Unknown option for `{}`.',
                OptMissingArgError: 'No argument given for option `{}`.'
                }[type(error)]
            errorMessage = 'Error: ' + errorTemplate.format(command_name)

            self._print(errorMessage, self._stderr)
            self._printCommandHelpNotice(command_name, self._stderr)
            return 1

    def register(self, command, name=None):
        _name = self._getCommandName(command) if not name else name
        self._commands[_name] = command

    def _print(self, text='', stream=None):
        (stream or self._stdout).write(text + os.linesep)

    def _printHelpNotice(self, stream=None):
        self._print('Use `{} help` for usage.'.format(self._execname), stream)

    def _printCommandHelpNotice(self, command, stream=None):
        self._print(
            'Use `{} help {}` for command usage.'.format(
                self._execname, command),
            stream)

    def _printHelp(self):
        self._print(
            'usage: {} <command> [options] [args]'
            .format(self._execname))
        self._print()
        self._print(self._title)
        self._print(self._description)
        self._print()
        self._print('Available commands:')
        for command_name in self._commands.keys():
            self._print('  ' + command_name)
        self._print()
        self._print(
            'Use `{} help <command>` for help on a specific command.'
            .format(self._execname))
        self._print('See {} for additional information.'.format(self._siteurl))

    def _printHelpFor(self, command):
        name = self._getCommandName(command)
        command.help(name, self._print)

    def _getCommandName(self, command):
        name = command.__class__.__name__.lower()
        if name.endswith('command') and not name == 'command':
            return name[:-len('command')]
        return name
