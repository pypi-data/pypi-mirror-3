# Copyright 2005-2011 Canonical Ltd.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from datetime import (
    date,
    datetime,
    )
import os
import urllib

from fixtures import TempDir
from oops_datedir_repo.serializer_bson import write as write_bson
from oops_datedir_repo.serializer_rfc822 import write
from pytz import utc
from testtools import TestCase

from oopstools.oops import helpers
from oopstools.oops.dboopsloader import (
    _find_dirs,
    OopsLoader,
    )
from oopstools.oops.models import (
    DBOopsRootDirectory,
    Oops,
    parsed_oops_to_model_oops,
    )


def create_directory_structure(root, structure):
    for directory in structure:
        os.makedirs(os.path.join(root, directory))


class TestDirFinder(TestCase):

    def _getExpectedDirs(self, root, dirs):
        return [os.path.join(root, directory) for directory in dirs]

    def setUp(self):
        super(TestDirFinder, self).setUp()
        self.root_dir = self.useFixture(TempDir()).path

    def test_find_dirs_no_matches(self):
        # Directories containing no subdirectories by date are not
        # considered as OOPS directories.
        create_directory_structure(self.root_dir, [
            'no-oopses/test',
            ])
        self.assertEqual([], _find_dirs([self.root_dir]))

    def test_find_dirs_matches(self):
        # Directories with subdirectories named YYYY-MM-DD are considered
        # to contain OOPSes.
        create_directory_structure(self.root_dir, [
            'oopses/2011-02-02',
            'more/deeper/2009-12-12',
            ])
        self.assertEqual(
            set(self._getExpectedDirs(self.root_dir,
                                      ['oopses', 'more/deeper'])),
            set(_find_dirs([self.root_dir])))

    def test_find_dirs_combined(self):
        # Directories with subdirectories named YYYY-MM-DD and other
        # subdirectories are considered to contain OOPSes, and their
        # non-date subdirectories can also contain OOPSes.
        create_directory_structure(self.root_dir, [
            'oopses/2011-02-02',
            'oopses/deeper/2009-12-12',
            ])
        self.assertEqual(
            set(self._getExpectedDirs(self.root_dir,
                                      ['oopses', 'oopses/deeper'])),
            set(_find_dirs([self.root_dir])))

    def test_find_dirs_symbolic_links_ignored(self):
        # Symbolic links are ignored.
        create_directory_structure(self.root_dir, [
            'oopses/2011-02-02',
            ])
        os.symlink(os.path.join(self.root_dir, 'oopses'),
                   os.path.join(self.root_dir, 'symlink'))
        self.assertEqual(
            self._getExpectedDirs(self.root_dir, ['oopses']),
            _find_dirs([self.root_dir]))

    def test_find_dirs_notexist(self):
        # Empty list is returned when requested root directory
        # does not exist.
        self.assertEqual(
            [],
            _find_dirs([self.root_dir + '/path/which/does/not/exist']))


class TestIncrementalLoading(TestCase):

    def test_nonsequential_filenames(self):
        # The new lock-free writer code makes no warranty about the order of
        # filenames on disk.
        helpers._today = date(2008, 01, 13)
        self.root_dir = self.useFixture(TempDir()).path
        os.mkdir(self.root_dir + '/2008-01-13')
        # Write and import a file.
        python_oops = {'id': 'OOPS-824S101', 'reporter': 'edge',
            'type': 'ValueError', 'value': 'a is not an int',
            'time': datetime(2008, 1, 13, 23, 14, 23, 00, utc)}
        with open(self.root_dir + '/2008-01-13/OOPS-824', 'wb') as output:
            write(python_oops, output)
        # Add our test dir to the db.
        oopsrootdir = DBOopsRootDirectory(
            root_dir=self.root_dir, last_date=None, last_oops=None)
        oopsrootdir.save()
        self.addCleanup(oopsrootdir.delete)
        loader = OopsLoader()
        self.assertEqual(1, len(loader.oopsdirs))
        start_date = date(2008, 01, 13)
        list(loader.find_oopses(start_date))
        # Should have loaded the oops.
        self.assertNotEqual(None, Oops.objects.get(oopsid='OOPS-824S101'))
        # Now we add a new oops with a disk path that sorts lower, but it
        # should still be picked up. For added value (we expect this to happen)
        # we make the new oops a bson oops.
        python_oops['id'] = 'OOPS-123S202'
        with open(self.root_dir + '/2008-01-13/OOPS-123', 'wb') as output:
            write_bson(python_oops, output)
        loader = OopsLoader()
        list(loader.find_oopses(start_date))
        self.assertNotEqual(None, Oops.objects.get(oopsid='OOPS-123S202'))


class TestParsedToModel(TestCase):

    def test_url_handling(self):
        unicode_url = u'http://example.com/foo\u2019s asset'
        report = { 'url': unicode_url, 'id': 'testurlhandling'}
        expected_url = urllib.quote(unicode_url.encode('utf8'))
        oops = parsed_oops_to_model_oops(report, 'test_url_handling')
        self.assertEqual(expected_url, oops.url)

    def test_no_topic_pageid_empty_bug_880641(self):
        report = { 'url': 'foo', 'id': 'testnotopichandling'}
        oops = parsed_oops_to_model_oops(report, 'bug_880641')
        self.assertEqual('', oops.pageid)

    def test_broken_url_handling(self):
        # This URL is not a valid URL - URL's are a subset of ASCII.
        broken_url = '/somep\xe1th'
        report = { 'url': broken_url, 'id': 'testbrokenurl'}
        # We handle such URL's by url quoting them, failing to do so being a
        # (not uncommon) producer mistake.
        expected_url = urllib.quote(broken_url)
        oops = parsed_oops_to_model_oops(report, 'test_broken_url_handling')
        self.assertEqual(expected_url, oops.url)

