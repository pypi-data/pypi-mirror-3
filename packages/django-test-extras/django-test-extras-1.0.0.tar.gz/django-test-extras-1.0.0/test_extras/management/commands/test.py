# -*- coding: utf-8 -*-
# (c) 2012 Bright Interactive Limited. All rights reserved.
# http://www.bright-interactive.com | info@bright-interactive.com

from django.conf import settings
from test_extras.testrunners import CoverageTestSuiteWrapper, PdbTestSuiteMixin, XmlTestSuiteMixin, ProfileTestSuiteWrapper, TagTestSuiteMixin
from django.core.management.commands.test import Command as CoreCommand

from optparse import make_option
import os
import sys


class Command(CoreCommand):
    """
    Similar to Django's standard 'test' management command,
    except that it also adds support for:

    --coverage
    --pdb
    --xmlreports
    --profile
    --tags
    """

    option_list = CoreCommand.option_list + (
        make_option('-c', '--coverage', action='store',
                    dest='coverage', default=None,
            type='choice', choices=['text', 'html', 'xml'],
            help='Coverage report; One of \'text\', \'html\', \'xml\''),
        make_option('-p', '--pdb', action='store_true', dest='pdb',
                    default=False,
                    help='Drop into pdb on test failure.'),
        make_option('-x', '--xmlreports', action='store_true',
                    dest='xmlreports', default=False,
                    help='Tells Django to store xml reports of the tests for Jenkins to use.'),
        make_option('-f', '--profile', action='store_true',
                    dest='profile', default=False,
                    help='Profile tests.'),
        make_option('-t', '--tags', action='store', dest='tags', default=None,
            help='Comma separated list of tags to be tested. '
                 'Only tests that meet at least one of those tags will be run.')
        )

    def handle(self, *test_labels, **options):
        from django.test.utils import get_runner

        TestRunner = get_runner(settings)

        self.south_patch()

        if options['pdb'] and options['xmlreports']:
            from optparse import OptionError
            raise OptionError("--pdb, -x", "cannot have pdb and xmlreports specified")

        if options['pdb']:
            TestRunner = self.pdb_wrap(TestRunner)

        if options['tags']:
            TestRunner = self.tag_wrap(TestRunner, options['tags'])

        if options['xmlreports']:
            TestRunner = self.xml_wrap(TestRunner)

        if options['coverage']:
            TestRunner = self.coverage_wrap(TestRunner, options['coverage'])

        if options['profile']:
            TestRunner = self.profile_wrap(TestRunner)

        self._core_handle(TestRunner, *test_labels, **options)

    def south_patch(self):
        try:
            from south.management.commands import patch_for_test_db_setup
        except ImportError:
            pass
        else:
            patch_for_test_db_setup()

    def profile_wrap(self, Runner):
        class ProfileTestSuiteRunner(ProfileTestSuiteWrapper):
            def __init__(self, *args, **kwargs):
                subject = Runner(*args, **kwargs)
                super(ProfileTestSuiteRunner, self).__init__(subject, *args, **kwargs)
        return ProfileTestSuiteRunner

    def coverage_wrap(self, Runner, report_type):
        class CoverageTestSuiteRunner(CoverageTestSuiteWrapper):
            def __init__(self, *args, **kwargs):
                subject = Runner(*args, **kwargs)
                super(CoverageTestSuiteRunner, self).__init__(subject, report_type, *args, **kwargs)
        return CoverageTestSuiteRunner

    def pdb_wrap(self, Runner):
        class PdbTestSuiteRunner(PdbTestSuiteMixin, Runner):
            pass
        return PdbTestSuiteRunner

    def xml_wrap(self, Runner):
        class XmlTestSuiteRunner(XmlTestSuiteMixin, Runner):
            pass
        return XmlTestSuiteRunner

    def tag_wrap(self, Runner, test_tags):
        class TagTestRunner(TagTestSuiteMixin, Runner):
            tags = test_tags.split(',')
        return TagTestRunner

    def _core_handle(self, TestRunner, *test_labels, **options):
        """ Copied from django.core.management.commands.test (1.4)"""
        options['verbosity'] = int(options.get('verbosity'))

        if options.get('liveserver') is not None:
            os.environ['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = options['liveserver']
            del options['liveserver']

        test_runner = TestRunner(**options)
        failures = test_runner.run_tests(test_labels)

        if failures:
            sys.exit(bool(failures))
