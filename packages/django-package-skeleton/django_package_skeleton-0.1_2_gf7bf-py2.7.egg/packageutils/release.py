#!/usr/bin/env python
# vim: set fileencoding=utf8:
"""
Distribute ReleaseCommand module


AUTHOR:
    lambdalisue[Ali su ae] (lambdalisue@hashnote.net)
    
Copyright:
    Copyright 2011 Alisue allright reserved.

License:
    Licensed under the Apache License, Version 2.0 (the "License"); 
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unliss required by applicable law or agreed to in writing, software
    distributed under the License is distrubuted on an "AS IS" BASICS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__AUTHOR__ = "lambdalisue (lambdalisue@hashnote.net)"
import re
import os
import commands
from setuptools import Command

class Controller(object):
    def get_status(self):
        """return list of unstaged and untracked files"""
        raise NotImplementedError
    def bump_version(self, version):
        """bump version"""
        raise NotImplementedError

class GitController(Controller):
    name = 'git'
    unstaged_pattern = re.compile(r'^ M\s(?P<path>.+)$', re.M)
    untracked_pattern = re.compile(r'^\?\?\s(?P<path>.+)$', re.M)

    def _get_unstaged_files(self, output):
        _iter = self.unstaged_pattern.finditer(output)
        return [m.group(1) for m in _iter]
    def _get_untracked_files(self, output):
        _iter = self.untracked_pattern.finditer(output)
        return [m.group(1) for m in _iter]
    def get_status(self):
        status, output = commands.getstatusoutput('git status -s')
        unstaged = []
        untracked = []
        if status == 0:
            unstaged = self._get_unstaged_files(output)
            untracked = self._get_untracked_files(output)
        return unstaged, untracked
            
    def bump_version(self, version):
        # create new tag
        print commands.getoutput('git tag -a %s -m "Bump version"' % version)
        # push
        print commands.getoutput('git push & git push origin ref/tags/%s' % version)

class ReleaseCommand(Command):
    description = "test the package and upload sdist, egg and docs to PyPI when test success"
    user_options = list(tuple())

    def initialize_options(self): pass
    def finalize_options(self): pass

    def _get_controller(self):
        if os.path.exists('.git'):
            return GitController()
        return None

    def run_version_controller_status_check(self, ignore_unstaged=False, ignore_untracked=False):
        # check version control status first
        unstaged, untracked = self.controller.get_status()

        print 'Unstaged', unstaged
        print 'Untracked', untracked

        def print_list(lst):
            for line in lst:
                print "-", line
        if not ignore_unstaged and unstaged:
            print
            print "Error: The following files are unstaged. Stage these files first"
            print_list(unstaged)
            exit(1)
        if not ignore_untracked and untracked:
            print
            print "Error: The following files are untracked. Track these files first"
            print_list(untracked)
            exit(1)

    def run_tests(self):
        self.reinitialize_command('test', inplace=0)
        try:
            self.run_command('test')
        except SystemExit, e:
            if e.code != 0:
                print
                print "Test failed. You have to fix these issue before release."
                raise e
            pass

    def bump_version(self):
        from version import get_git_version
        from pkg_resources import parse_version

        old_version = get_git_version()

        print
        while True:
            new_version = raw_input('Please input new version (current="%s"): '%old_version)

            if parse_version(old_version) >= parse_version(new_version):
                result = raw_input('New version "%s" is actually lower than old version. Are you sure to continue? (y/N)' % new_version)
                if result in ('y', 'Y', 'yes', 'Yes', 'YES'):
                    break
            else:
                break

        # Version Controller
        if self.controller:
            self.controller.bump_version(new_version)

    def upload_pypi(self):
        self.reinitialize_command('sdist', inplace=0)
        self.run_command('sdist')
        self.reinitialize_command('bdist_egg', inplace=0)
        self.run_command('bdist_egg')
        self.reinitialize_command('upload', inplace=0)
        self.run_command('upload')
        self.reinitialize_command('upload_docs', inplace=0, upload_dir='docs/_build/html')
        
    def run(self):
        # get version controller
        self.controller = self._get_controller()

        # Check version controller status first
        self.run_version_controller_status_check()

        # Check whether test fail or not
        self.run_tests()

        # Bump version
        self.bump_version()

        # Upload to PyPI
        self.upload_pypi()
