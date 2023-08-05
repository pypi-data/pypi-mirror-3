#! /usr/bin/env python3.2

import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cmdstyle

# Naming Conventions:
# Operand           - arg (args1, args2, ... if multiple)
# Operand Values    - a, b, c, d, ...
# ListOperand       - args (args1, args2, ... if multiple)
# Options           - opt (opt1, opt2, ... if multiple)
# Option shortnames - o, p, q, ...
# Flags             - flag (flag1, flag2, ... if multiple)
# Flag shortnames   - f, g, h, ...

eol = os.linesep


class OptionTests(unittest.TestCase):

    def test_init_longnameAndShortnameBlank_raisesTypeError(self):
        with self.assertRaisesRegex(
                TypeError, "Longname and shortname can't both be blank."):
            cmdstyle.Option(longname='', shortname='')

    def test_init_longnameCantIncludeSpace(self):
        with self.assertRaisesRegex(
                TypeError, "Longname includes illegal character."):
            cmdstyle.Option(longname='opt ')

    def test_init_longnameCantIncludeDash(self):
        with self.assertRaisesRegex(
                TypeError, "Longname includes illegal character."):
            cmdstyle.Option(longname='opt-')

    def test_init_shortnameCantIncludeSpace(self):
        with self.assertRaisesRegex(
                TypeError, "Shortname includes illegal character."):
            cmdstyle.Option(shortname=' ')

    def test_init_shortnameCantIncludeDash(self):
        with self.assertRaisesRegex(
                TypeError, "Shortname includes illegal character."):
            cmdstyle.Option(shortname='-')

    def test_init_shortnameMustBeOneCharLong(self):
        with self.assertRaisesRegex(
                TypeError, 'Shortname must be one character long.'):
            cmdstyle.Option(shortname='oo')

    def test_init_longnameMustBeMoreThanOneCharLong(self):
        with self.assertRaisesRegex(
                TypeError, 'Longname must be more than one character long.'):
            cmdstyle.Option(longname='o')

    def test_names_withLongAttrnameAndNoOtherNames_usesAttrname(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option()

        command = TestCommand()

        command.parse('prog cmd --opt val'.split())

        self.assertEqual(command.opt, 'val')

    def test_namesFlag_withLongAttrnameAndNoOtherNames_usesAttrname(self):
        class TestCommand(cmdstyle.Command):
            flag = cmdstyle.Flag()

        command = TestCommand()

        command.parse('prog cmd --flag'.split())

        self.assertEqual(command.flag, True)

    def test_names_withShortAttrnameAndNoOtherNames_usesAttrname(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option()

        command = TestCommand()

        command.parse('prog cmd -o val'.split())

        self.assertEqual(command.o, 'val')

    def test_namesFlag_withShortAttrnameAndNoOtherNames_usesAttrname(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag()

        command = TestCommand()

        command.parse('prog cmd -f'.split())

        self.assertEqual(command.f, True)

    def test_names_withLongAttrnameAndLongname_usesLongname(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option(longname='opt_')

        command = TestCommand()

        command.parse('prog cmd --opt_ val'.split())

        self.assertEqual(command.opt, 'val')

    def test_namesFlag_withLongAttrnameAndLongname_usesLongname(self):
        class TestCommand(cmdstyle.Command):
            flag = cmdstyle.Flag(longname='flag_')

        command = TestCommand()

        command.parse('prog cmd --flag_'.split())

        self.assertEqual(command.flag, True)

    def test_names_withShortAttrnameAndShortname_usesShortname(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option(shortname='p')

        command = TestCommand()

        command.parse('prog cmd -p val'.split())

        self.assertEqual(command.o, 'val')

    def test_namesFlag_withShortAttrnameAndShortname_usesShortname(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag(shortname='g')

        command = TestCommand()

        command.parse('prog cmd -g'.split())

        self.assertEqual(command.f, True)

    def test_names_withLongAttrnameAndShortname_usesBoth(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option(shortname='o')

        longCommand = TestCommand()
        longCommand.parse('prog cmd --opt long'.split())

        shortCommand = TestCommand()
        shortCommand.parse('prog cmd -o short'.split())

        self.assertEqual(
            (longCommand.opt, shortCommand.opt),
            ('long', 'short'))

    def test_namesFlag_withLongAttrnameAndShortname_usesBoth(self):
        class TestCommand(cmdstyle.Command):
            flag = cmdstyle.Flag(shortname='f')

        longCommand = TestCommand()
        longCommand.parse('prog cmd --flag'.split())

        shortCommand = TestCommand()
        shortCommand.parse('prog cmd -f'.split())

        self.assertEqual(
            (longCommand.flag, shortCommand.flag),
            (True, True))

    def test_names_withShortAttrnameAndLongname_usesBoth(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option(longname='opt')

        shortCommand = TestCommand()
        shortCommand.parse('prog cmd -o short'.split())

        longCommand = TestCommand()
        longCommand.parse('prog cmd --opt long'.split())

        self.assertEqual(
            (shortCommand.o, longCommand.o),
            ('short', 'long'))

    def test_namesFlag_withShortAttrnameAndLongname_usesBoth(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag(longname='flag')

        shortCommand = TestCommand()
        shortCommand.parse('prog cmd -f'.split())

        longCommand = TestCommand()
        longCommand.parse('prog cmd --flag'.split())

        self.assertEqual(
            (shortCommand.f, longCommand.f),
            (True, True))

    def test_names_withLongAttrnameAndBlankLongname_doesntUseAttrname(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option(longname='', shortname='o')

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd --opt val'.split())

    def test_namesFlag_withLongAttrnameAndBlankParam_doesntUseAttrname(self):
        class TestCommand(cmdstyle.Command):
            flag = cmdstyle.Flag(longname='', shortname='f')

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd --flag'.split())

    def test_names_withShortAttrnameAndBlankShortname_doesntUseAttrname(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option(longname='opt', shortname='')

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd -o val'.split())

    def test_namesFlag_withShortAttrnameAndBlankParam_doesntUseAttrname(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag(longname='flag', shortname='')

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd -f'.split())

    def test_shortnameInferredFromLongname(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd -o x'.split())

        self.assertEqual(command.opt, 'x')

    def test_shortnameInferrenceCanBeDisabled(self):
        class TestCommand(cmdstyle.Command):
            settings = cmdstyle.CommandSettings(
                    inferShortnamesFromLongnames=False)
            opt = cmdstyle.Option()

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd -o x'.split())

    def test_nameInferrenceCanBeDisabled_forLongnames(self):
        class TestCommand(cmdstyle.Command):
            settings = cmdstyle.CommandSettings(
                    inferNamesFromAttrnames=False)
            opt = cmdstyle.Option(shortname='o')

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd --opt x'.split())

    def test_nameInferrenceCanBeDisabled_withoutDisablingShortnameInf(self):
        class TestCommand(cmdstyle.Command):
            settings = cmdstyle.CommandSettings(
                    inferNamesFromAttrnames=False)
            p = cmdstyle.Option(longname='opt')

        command = TestCommand()

        command.parse('prog cmd -o x'.split())

        self.assertEqual(command.p, 'x')

    def test_nameAndShortnameInferrenceCanBeDisabled(self):
        class TestCommand(cmdstyle.Command):
            settings = cmdstyle.CommandSettings(
                    inferNamesFromAttrnames=False,
                    inferShortnamesFromLongnames=False)
            o = cmdstyle.Option(longname='opt')

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd -o x'.split())

    def test_duplicateLongname_raisesError(self):
        with self.assertRaisesRegex(
                cmdstyle.DuplicateLongnameError,
                "Long name 'opt' can't be used by more than one option."
                ) as context:
            class TestCommand(cmdstyle.Command):
                opt1 = cmdstyle.Option(longname='opt', shortname='')
                opt2 = cmdstyle.Option(longname='opt', shortname='')

        self.assertEqual('opt', context.exception.name)

    def test_duplicateShortname_raisesError(self):
        with self.assertRaisesRegex(
                cmdstyle.DuplicateShortnameError,
                "Short name 'o' can't be used by more than one option. "
                "\\(This might be caused by the InferShortnamesFromLongnames "
                "setting.\\)"
                ) as context:
            class TestCommand(cmdstyle.Command):
                opt1 = cmdstyle.Option()
                opt2 = cmdstyle.Option()

        self.assertEqual('o', context.exception.name)


class CommandSettingTests(unittest.TestCase):
    def test_privateSettingsAttrAreIgnored(self):
        class TestCommand(cmdstyle.Command):
            _settings = cmdstyle.CommandSettings(
                    inferShortnamesFromLongnames=False)
            opt = cmdstyle.Option()

        command = TestCommand()

        command.parse('prog cmd -o x'.split())

        self.assertEqual(command.opt, 'x')

    def test_commandCantHaveMoreThanOneSettingsAttr(self):
        with self.assertRaisesRegex(
            TypeError,
            "Command can't have more than one CommandSettings."):
            class TestCommand(cmdstyle.Command):
                settings1 = cmdstyle.CommandSettings()
                settings2 = cmdstyle.CommandSettings()


class CommandTests(unittest.TestCase):

    def test_a_custom_parse_method_will_cause_an_exception(self):
        with self.assertRaisesRegex(
                TypeError,
                "Command can't define `parse`."):
            class TestCommand(cmdstyle.Command):
                def parse(self, args):
                    pass

    def test_a_custom_help_method_will_cause_an_exception(self):
        with self.assertRaisesRegex(
                TypeError,
                "Command can't define `help`."):
            class TestCommand(cmdstyle.Command):
                def help(self, args):
                    pass


class CommandParseTests(unittest.TestCase):

    def test_nonParamAttrsAreIgnored(self):
        #This shouldn't raise exceptions
        class TestCommand(cmdstyle.Command):
            x = 1

            def fn(self):
                pass

        command = TestCommand()
        command.parse('prog cmd'.split())


    def test_operand(self):
        class TestCommand(cmdstyle.Command):
            arg1 = cmdstyle.Operand()
            arg2 = cmdstyle.Operand()

        command = TestCommand()
        command.parse('prog cmd a b'.split())

        self.assertEqual(command.arg1, 'a')
        self.assertEqual(command.arg2, 'b')

    def test_operand_areParsedInDeclarationOrder(self):
        class TestCommand(cmdstyle.Command):
            argZ = cmdstyle.Operand()
            argA = cmdstyle.Operand()
            argB = cmdstyle.Operand()

        command = TestCommand()
        command.parse('prog cmd a b c'.split())

        self.assertEqual(command.argZ, 'a')
        self.assertEqual(command.argA, 'b')
        self.assertEqual(command.argB, 'c')

    def test_listOperand_collectsMultipleArgs(self):
        class TestCommand(cmdstyle.Command):
            args = cmdstyle.ListOperand()

        command = TestCommand()
        command.parse('prog cmd a b c'.split())
        self.assertListEqual(command.args, ['a', 'b', 'c'])

    def test_listOperand_moreThanOneIsntAllowed(self):
        with self.assertRaisesRegex(
                TypeError,
                "Command can't have more than one ListOperand"):
            class TestCommand(cmdstyle.Command):
                args1 = cmdstyle.ListOperand()
                args2 = cmdstyle.ListOperand()

    def test_listOperand_operandsBeforeAreAssignedArgs(self):
        class TestCommand(cmdstyle.Command):
            arg1 = cmdstyle.Operand()
            args = cmdstyle.ListOperand()

        command = TestCommand()
        command.parse('prog cmd a b c'.split())
        self.assertEqual(command.arg1, 'a')
        self.assertListEqual(command.args, ['b', 'c'])

    def test_listOperand_operandsAfterAreAssignedArgs(self):
        class TestCommand(cmdstyle.Command):
            args = cmdstyle.ListOperand()
            arg1 = cmdstyle.Operand()
            arg2 = cmdstyle.Operand()

        command = TestCommand()
        command.parse('prog cmd a b c d'.split())
        self.assertListEqual(command.args, ['a', 'b'])
        self.assertEqual(command.arg1, 'c')
        self.assertEqual(command.arg2, 'd')

    def test_listOperand_canBeEmptyAfterOtherOperandsAreAssignedArgs(self):
        class TestCommand(cmdstyle.Command):
            args = cmdstyle.ListOperand()
            arg1 = cmdstyle.Operand()
            arg2 = cmdstyle.Operand()

        command = TestCommand()
        command.parse('prog cmd a b'.split())
        self.assertListEqual(command.args, [])
        self.assertEqual(command.arg1, 'a')
        self.assertEqual(command.arg2, 'b')

    def test_operand_assignedDefaultIfUnspecified(self):
        class TestCommand(cmdstyle.Command):
            arg = cmdstyle.Operand(default='default')

        command = TestCommand()
        command.parse('prog cmd'.split())
        self.assertEqual(command.arg, 'default')

    def test_option_assignedDefaultIfUnspecified(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option(default='default')

        command = TestCommand()
        command.parse('prog cmd'.split())

        self.assertEqual(command.opt, 'default')

    def test_option_parsedInShortNotation(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd -o x'.split())

        self.assertEqual(command.o, 'x')

    def test_flag_assignedFalseIfUnspecified(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag()

        command = TestCommand()
        command.parse('prog cmd'.split())

        self.assertEqual(command.f, False)

    def test_flag_assignedTrueIfSpecified(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag()

        command = TestCommand()
        command.parse('prog cmd -f'.split())

        self.assertEqual(command.f, True)

    def test_flags_areParsedInGroupNotation(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag()
            g = cmdstyle.Flag()

        command = TestCommand()
        command.parse('prog cmd -fg'.split())

        self.assertEqual(command.f, True)
        self.assertEqual(command.g, True)

    def test_groupedNotation_parsesOptionArgFollowingGroup(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag()
            o = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd -fo a'.split())

        self.assertEqual(command.f, True)
        self.assertEqual(command.o, 'a')

    def test_option_inShortNotation_takesValueImmediatelyFollowing(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag()
            o = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd -of'.split())

        self.assertEqual(command.o, 'f')
        self.assertEqual(command.f, False)

    def test_option_groupedWithFlagBefore_takesValImmediatelyFollowing(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag()
            o = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd -foa'.split())

        self.assertEqual(command.f, True)
        self.assertEqual(command.o, 'a')

    def test_flag_parsedInLongNotation(self):
        class TestCommand(cmdstyle.Command):
            flag = cmdstyle.Flag()

        command = TestCommand()
        command.parse('prog cmd --flag'.split())

        self.assertEqual(command.flag, True)

    def test_doubleDash_endsOptionParsing(self):
        class TestCommand(cmdstyle.Command):
            flag = cmdstyle.Flag()
            arg = cmdstyle.Operand()

        command = TestCommand()
        command.parse('prog cmd -- -f'.split())

        self.assertEqual(command.flag, False)
        self.assertEqual(command.arg, '-f')

    def test_doubleDash_asShortOptionValueDoesntStopParsing(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option()
            p = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd -o -- -p x'.split())

        self.assertEqual(command.o, '--')
        self.assertEqual(command.p, 'x')

    def test_doubleDash_asLongOptionValueDoesntStopParsing(self):
        class TestCommand(cmdstyle.Command):
            opt1 = cmdstyle.Option(shortname='')
            opt2 = cmdstyle.Option(shortname='')

        command = TestCommand()
        command.parse('prog cmd --opt1 -- --opt2 x'.split())

        self.assertEqual(command.opt1, '--')
        self.assertEqual(command.opt2, 'x')

    def test_dash_parsedAsShortOptionValue(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd -o -'.split())

        self.assertEqual(command.o, '-')

    def test_dash_parsedAsLongOptionValue(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option()

        command = TestCommand()
        command.parse('prog cmd --opt -'.split())

        self.assertEqual(command.opt, '-')

    def test_tooManyArguments_raisesException(self):
        class TestCommand(cmdstyle.Command):
            pass

        command = TestCommand()

        with self.assertRaises(cmdstyle.TooManyArgsError):
            command.parse('prog cmd a'.split())

    def test_tooManyArguments_afterDoubleDash_raisesException(self):
        class TestCommand(cmdstyle.Command):
            pass

        command = TestCommand()

        with self.assertRaises(cmdstyle.TooManyArgsError):
            command.parse('prog cmd -- a'.split())

    def test_unknownLongOption_raisesException(self):
        class TestCommand(cmdstyle.Command):
            pass

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd --opt'.split())

    def test_unknownShortOption_raisesException(self):
        class TestCommand(cmdstyle.Command):
            pass

        command = TestCommand()

        with self.assertRaises(cmdstyle.UnknownOptionError):
            command.parse('prog cmd -o'.split())

    def test_longOption_atEnd_missingParameter_raisesException(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option()

        command = TestCommand()

        with self.assertRaises(cmdstyle.OptMissingArgError):
            command.parse('prog cmd --opt'.split())

    def test_longOption_inMiddle_missingParameter_raisesException(self):
        class TestCommand(cmdstyle.Command):
            opt1 = cmdstyle.Option(shortname='')
            opt2 = cmdstyle.Option(shortname='')

        command = TestCommand()

        with self.assertRaises(cmdstyle.OptMissingArgError):
            command.parse('prog cmd --opt1 --opt2 a'.split())

    def test_shortOption_atEnd_missingParameter_raisesException(self):
        class TestCommand(cmdstyle.Command):
            p = cmdstyle.Option()

        command = TestCommand()

        with self.assertRaises(cmdstyle.OptMissingArgError):
            command.parse('prog cmd -p'.split())

    def test_shortOption_inMiddle_missingParameter_raisesException(self):
        class TestCommand(cmdstyle.Command):
            o = cmdstyle.Option()
            p = cmdstyle.Option()

        command = TestCommand()

        with self.assertRaises(cmdstyle.OptMissingArgError):
            command.parse('prog cmd -o -p a'.split())


class CommandHelpTests(unittest.TestCase):

    def setUp(self):
        self.output = []
        pass

    def out(self, text):
        self.output.append(text)

    def test_summary_ComesFromDocstringFirstLine(self):
        class TestCommand(cmdstyle.Command):
            """Just a test command."""

        TestCommand().help('_name_', self.out)

        self.assertEqual(
            self.output[0],
            '_name_: Just a test command.')

    def test_summaryWhenNoDocstring(self):
        class TestCommand(cmdstyle.Command):
            pass

        TestCommand().help('_name_', self.out)

        self.assertEqual(self.output[0], '_name_')

    def test_explanation_ComesFromDocstringBody(self):
        class TestCommand(cmdstyle.Command):
            """Just a test command.

            With a detailed
            multiline
            explanation.
            """

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[2:7],
            ["",
             "  With a detailed",
             "  multiline",
             "  explanation.",
             ""])

    def test_usage_commandWithoutParams(self):
        class TestCommand(cmdstyle.Command):
            pass

        TestCommand().help('_name_', self.out)

        self.assertEqual(
            self.output[1],
            'usage: _name_')

    def test_usage_commandWithParams(self):
        class TestCommand(cmdstyle.Command):
            arg1 = cmdstyle.Operand()

        TestCommand().help('_name_', self.out)

        self.assertEqual(
            self.output[1],
            'usage: _name_ ARG1')

    def test_usage_paramNameSet(self):
        class TestCommand(cmdstyle.Command):
            foo = cmdstyle.Operand()

        TestCommand().help('_name_', self.out)

        self.assertEqual(
            self.output[1],
            'usage: _name_ FOO')

    def test_optionListing_optionsWithoutDescriptions(self):
        class TestCommand(cmdstyle.Command):
            force = cmdstyle.Flag()
            recursive = cmdstyle.Flag()

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-4:],
            ['Options:',
             '',
             '-f --force',
             '-r --recursive'])

    def test_optionListing_optionsWithDescriptions(self):
        class TestCommand(cmdstyle.Command):
            force = cmdstyle.Flag(description='Forces things.')
            recursive = cmdstyle.Flag(description='Do things recursively.')

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-4:],
            ['Options:',
             '',
             '-f --force      Forces things.',
             '-r --recursive  Do things recursively.'])

    def test_optionListing_someOptionsOnlyHaveLongNames(self):
        class TestCommand(cmdstyle.Command):
            force = cmdstyle.Flag(shortname='')
            recursive = cmdstyle.Flag()

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-4:],
            ['Options:',
            '',
            '   --force',
            '-r --recursive'])

    def test_optionListing_someOptionsOnlyHaveShortNames(self):
        class TestCommand(cmdstyle.Command):
            force = cmdstyle.Flag()
            r = cmdstyle.Flag()

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-4:],
            ['Options:',
             '',
             '-f --force',
             '-r'])

    def test_optionListing_noOptionsHaveShortNames(self):
        class TestCommand(cmdstyle.Command):
            force = cmdstyle.Flag(shortname='')
            recursive = cmdstyle.Flag(shortname='')

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-4:],
            ['Options:',
             '',
             '--force',
             '--recursive'])

    def test_optionListing_noOptionsHaveLongNames(self):
        class TestCommand(cmdstyle.Command):
            f = cmdstyle.Flag(description='description_f')
            r = cmdstyle.Flag(description='description_r')

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-4:],
            ['Options:',
             '',
             '-f  description_f',
             '-r  description_r'])

    def test_optionListing_argPlaceholdersAreShown(self):
        class TestCommand(cmdstyle.Command):
            output = cmdstyle.Option(shortname='')

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-3:],
            ['Options:',
             '',
             '--output ARG'])

    def test_optionListing_argPlaceholderUsesArgname(self):
        class TestCommand(cmdstyle.Command):
            output = cmdstyle.Option(shortname='', argname='PATH')

        TestCommand().help('_name_', self.out)

        self.assertListEqual(
            self.output[-3:],
            ['Options:',
             '',
             '--output PATH'])


class ProgramTests(unittest.TestCase):

    class SimpleCommand(cmdstyle.Command):
        def __init__(self, **args):
            self.called = False

        def __call__(self):
            self.called = True

    def setUp(self):
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.program = cmdstyle.Program(
            '_execname_', '_title_', '_description_',
            '_siteurl_', self.stdout, self.stderr)

    def test_no_command_given(self):
        class TestCommand():
            pass

        self.program.register(TestCommand())
        returnValue = self.program.run(['prog'])

        expected = 'Use `_execname_ help` for usage.' + eol
        self.assertEqual(self.stdout.getvalue(), expected)
        self.assertEqual(self.stderr.getvalue(), '')
        self.assertEqual(returnValue, 0)

    def test_help(self):
        class TestCommand():
            pass

        self.program.register(TestCommand())
        returnValue = self.program.run('prog help'.split())

        expected = eol.join(
            ['usage: _execname_ <command> [options] [args]',
             '',
             '_title_',
             '_description_',
             '',
             'Available commands:',
             '  test',
             '',
             'Use `_execname_ help <command>` '
             'for help on a specific command.',
             'See _siteurl_ for additional information.',
             ''])

        self.assertEqual(
            self.stdout.getvalue(),
            expected)

        self.assertEqual(self.stderr.getvalue(), '')
        self.assertEqual(returnValue, 0)

    def test_unknownCommand(self):
        class TestCommand():
            pass

        self.program.register(TestCommand())
        returnValue = self.program.run('prog unknown'.split())

        self.assertEqual(self.stdout.getvalue(), '')

        expected = eol.join([
            'Unknown command: `unknown`',
            'Use `_execname_ help` for usage.',
            ''])
        self.assertEqual(self.stderr.getvalue(), expected)

        self.assertEqual(returnValue, 1)

    def test_run_named_command_is_called(self):
        called = False

        class TestCommand(cmdstyle.Command):
            def __call__(self):
                nonlocal called
                called = True

        testCommand = TestCommand()
        self.program.register(testCommand)

        self.program.run('prog test'.split())

        self.assertTrue(called)

    def test_run_named_command_return_value_is_returned(self):
        RETURN_VALUE = 123

        class TestCommand(cmdstyle.Command):
            def __call__(self):
                return RETURN_VALUE

        self.program.register(TestCommand())

        returnValue = self.program.run('prog test'.split())

        self.assertEqual(returnValue, RETURN_VALUE)

    def test_register_withoutName(self):
        class Foo(ProgramTests.SimpleCommand):
            pass
        foo = Foo()

        self.program.register(foo)
        self.program.run('prog foo'.split())

        self.assertTrue(foo.called)

    def test_register_withoutName_classNameEndsInCommand(self):
        class TestCommand(ProgramTests.SimpleCommand):
            pass
        test = TestCommand()

        self.program.register(test)
        self.program.run('prog test'.split())

        self.assertTrue(test.called)

    def test_register_withoutName_classNameIsCommand(self):
        class Command(ProgramTests.SimpleCommand):
            pass
        command = Command()

        self.program.register(command)
        self.program.run('prog command'.split())

        self.assertTrue(command.called)

    def test_register_withName(self):
        class TestCommand(ProgramTests.SimpleCommand):
            pass
        command = TestCommand()

        self.program.register(command, 'foo')
        self.program.run('prog foo'.split())

        self.assertTrue(command.called)

    def test_register_withName_inferredNameIsNotUsed(self):
        class TestCommand(ProgramTests.SimpleCommand):
            pass
        command = TestCommand()

        self.program.register(command, 'foo')
        self.program.run('prog test'.split())

        self.assertTrue(not command.called)

    def test_register_withName_suppliedNameIsUsed(self):
        class TestCommand(ProgramTests.SimpleCommand):
            pass
        command = TestCommand()

        self.program.register(command, 'foo')
        self.program.run('prog foo'.split())

        self.assertTrue(command.called)

    def test_commandHelp_commandFound(self):
        class TestCommand(cmdstyle.Command):
            pass

        command = TestCommand()

        expected_help = ''

        def print_(text):
            nonlocal expected_help
            expected_help += text + eol
        command.help('test', print_)

        self.program.register(command)
        returnValue = self.program.run('prog help test'.split())

        self.assertEqual(self.stdout.getvalue(), expected_help)
        self.assertEqual(self.stderr.getvalue(), '')
        self.assertEqual(returnValue, 0)

    def test_commandHelp_unknownCommand(self):
        returnValue = self.program.run('prog help xxx'.split())

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(
            self.stderr.getvalue(),
            eol.join(['Unknown command: `xxx`', '']))
        self.assertEqual(returnValue, 1)

    def test_commandError_tooMangArgs(self):
        class TestCommand(cmdstyle.Command):
            def __call__(self):
                pass

        command = TestCommand()

        self.program.register(command)
        returnValue = self.program.run('prog test 1 2 3'.split())

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(
            self.stderr.getvalue(),
            eol.join(
            ['Error: Too many arguments for `test`.',
             'Use `_execname_ help test` for command usage.',
             '']))
        self.assertEqual(returnValue, 1)

    def test_commandError_unknownOption(self):
        class TestCommand(cmdstyle.Command):
            def __call__(self):
                pass

        command = TestCommand()

        self.program.register(command)
        returnValue = self.program.run('prog test --opt x'.split())

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(
            self.stderr.getvalue(),
            eol.join(
            ['Error: Unknown option for `test`.',
             'Use `_execname_ help test` for command usage.',
             '']))
        self.assertEqual(returnValue, 1)

    def test_commandError_optMissingArgError(self):
        class TestCommand(cmdstyle.Command):
            opt = cmdstyle.Option()

            def __call__(self):
                pass

        command = TestCommand()

        self.program.register(command)
        returnValue = self.program.run('prog test --opt'.split())

        self.assertEqual(self.stdout.getvalue(), '')
        self.assertEqual(
            self.stderr.getvalue(),
            eol.join(
            ['Error: No argument given for option `test`.',
             'Use `_execname_ help test` for command usage.',
             '']))
        self.assertEqual(returnValue, 1)


if __name__ == '__main__':
    unittest.main()
