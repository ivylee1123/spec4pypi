import os

from tarfile import TarFile
from zipfile import ZipFile

import pytest

from pyp2rpmlib.metadata_extractors import *

tests_dir = os.path.split(os.path.abspath(__file__))[0]

class TestMetadataExtractor(object):
    td_dir = '%s/test_data/' % tests_dir

    def setup_method(self, method):
        # create fresh extractors for every test

        self.e = [MetadataExtractor('%splumbum-0.9.0.tar.gz' % self.td_dir, 'plumbum', '0.9.0'),
                  MetadataExtractor('%spytest-2.2.3.zip' % self.td_dir, 'pytest', '2.2.3'),
                  MetadataExtractor('%srestsh-0.1.tar.gz' % self.td_dir, 'restsh', '0.1'),
                  MetadataExtractor('%sSphinx-1.1.3-py2.6.egg' % self.td_dir, 'Sphinx', '1.1.3'),
                  MetadataExtractor('%sunextractable-1.tar' % self.td_dir, 'unextractable', '1'),
                 ]

    @pytest.mark.parametrize(('i', 's', 'expected'), [
        (0, '.gz',  TarFile),
        (1, '.zip', ZipFile),
        (2, '.gz', TarFile),
        (3, '.egg', ZipFile),
        (4, '.tar', TarFile),
    ])
    def test_get_extractor_cls(self, i, s, expected):
        assert self.e[i].get_extractor_cls(s) == expected

    @pytest.mark.parametrize(('i', 'n', 'expected'), [
        (0, 'setup.cfg', '[egg_info]\r\ntag_build = \r\ntag_date = 0\r\ntag_svn_revision = 0\r\n\r\n'),
        (1, 'requires.txt', 'py>=1.4.7.dev2'),
        (2, 'does_not_exist.dne', None),
        (4, 'in_unextractable', None),
    ])
    def test_get_content_of_file_from_archive(self, i, n, expected):
        assert self.e[i].get_content_of_file_from_archive(n) == expected