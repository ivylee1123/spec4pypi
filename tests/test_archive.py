import os

from tarfile import TarFile
from zipfile import ZipFile

import pytest

from flexmock import flexmock

from pyp2rpm.archive import Archive

tests_dir = os.path.split(os.path.abspath(__file__))[0]

class TestArchive(object):
    td_dir = '{0}/test_data/'.format(tests_dir)

    def setup_method(self, method):
        # create fresh archives for every test

        self.a = [Archive('{0}plumbum-0.9.0.tar.gz'.format(self.td_dir)),
                  Archive('{0}pytest-2.2.3.zip'.format(self.td_dir)),
                  Archive('{0}restsh-0.1.tar.gz'.format(self.td_dir)),
                  Archive('{0}Sphinx-1.1.3-py2.6.egg'.format(self.td_dir)),
                  Archive('{0}unextractable-1.tar'.format(self.td_dir)),
                  Archive('{0}bitarray-0.8.0.tar.gz'.format(self.td_dir)),]

    @pytest.mark.parametrize(('i', 'expected'), [
        (0, TarFile),
        (1, ZipFile),
        (2, TarFile),
        (3, ZipFile),
        (4, TarFile),
    ])
    def test_extractor_cls(self, i, expected):
        assert self.a[i].extractor_cls == expected

    @pytest.mark.parametrize(('i', 'n', 'abs', 'expected'), [
        (0, 'setup.cfg', False, '[egg_info]\r\ntag_build = \r\ntag_date = 0\r\ntag_svn_revision = 0\r\n\r\n'),
        (1, 'requires.txt', False, 'py>=1.4.7.dev2'),
        (1, 'pytest-2.2.3/pytest.egg-info/requires.txt', True, 'py>=1.4.7.dev2'),
        (2, 'does_not_exist.dne', False,  None),
        (4, 'in_unextractable', False, None),
    ])
    def test_get_content_of_file_from_archive(self, i, n, abs, expected):
        with self.a[i] as a:
            assert a.get_content_of_file(n, abs) == expected

    def test_find_list_argument_not_present(self):
        flexmock(self.a[4]).should_receive('get_content_of_file').with_args('setup.py').and_return('install_requires=["spam",\n"eggs"]')
        assert self.a[4].find_list_argument('setup_requires') == []

    def test_find_list_argument_present(self):
        flexmock(self.a[4]).should_receive('get_content_of_file').with_args('setup.py').and_return('install_requires=["beans",\n"spam"]\nsetup_requires=["spam"]')
        assert self.a[4].find_list_argument('install_requires') == ['beans', 'spam']

    def test_find_list_argument_not_evaluable(self):
        flexmock(self.a[4]).should_receive('get_content_of_file').with_args('setup.py').and_return('install_requires=[some_function()]')
        assert self.a[4].find_list_argument('install_requires') == []

    def test_find_list_argument_unopenable_file(self):
        flexmock(self.a[4]).should_receive('get_content_of_file').with_args('setup.py').and_return(None)
        assert self.a[4].find_list_argument('install_requires') == []

    @pytest.mark.parametrize(('i', 'suf', 'expected'), [
        (0, ['.spamspamspam'],  False),
        (1, '.py', True),
        (4, ['.eggs'], False),
    ])
    def test_has_file_with_suffix(self, i, suf, expected):
        with self.a[i] as a:
            assert a.has_file_with_suffix(suf) == expected

    @pytest.mark.parametrize(('i', 'r', 'f', 'c', 'expected'), [
        (0, r'PKG-INFO', False, False, ['plumbum-0.9.0/PKG-INFO', 'plumbum-0.9.0/plumbum.egg-info/PKG-INFO']),
        (0, r'[a-z]/PKG-INFO', True, False, ['plumbum-0.9.0/plumbum.egg-info/PKG-INFO']),
        (0, r'[a-z]/pKg-InfO', True, True, ['plumbum-0.9.0/plumbum.egg-info/PKG-INFO']),
        (0, r'spam/PKG-INFO', True, False, []),
        (0, r'plumbum-0.9.0$', True, False, []), # should ignore directory in tarfile
    ])
    def test_get_files_re(self, i, r, f, c, expected):
        with self.a[i] as a:
            assert set(a.get_files_re(r, f, c)) == set(expected)

    @pytest.mark.parametrize(('i', 'r', 'f', 'c', 'expected'), [
        (0, r'plumbum.*', False, False, ['plumbum-0.9.0', 'plumbum-0.9.0/plumbum.egg-info', 'plumbum-0.9.0/plumbum']),
        (0, r'[0-9]/plumbum$', True, False, ['plumbum-0.9.0/plumbum']),
        (0, r'[0-9]/pLuMbUm$', True, True, ['plumbum-0.9.0/plumbum']),
        (0, r'spam/plumbum.*', True, False, []),
        (0, r'setup.py', True, False, []), # should ignore file
        # test for zipfile separately - some more logic going on there...
        (1, r'pytest.*', False, False, ['pytest-2.2.3', 'pytest-2.2.3/pytest.egg-info', 'pytest-2.2.3/_pytest']),
        (1, r't/assertion$', True, False, ['pytest-2.2.3/_pytest/assertion']),
        (1, r'[0-9]/_pYtEsT$', True, True, ['pytest-2.2.3/_pytest']),
        (1, r'spam/.*_pytest.*', True, False, []),
        (1, r'setup.py', True, False, []), # should ignore file
    ])
    def test_get_directories_re(self, i, r, f, c, expected):
        with self.a[i] as a:
            assert set(a.get_directories_re(r, f, c)) == set(expected)

    @pytest.mark.parametrize(('i', 'arg', 'expected'), [
        (0, 'name', True),
        (0, 'classifiers', True),
        (0, 'version', True),
        (0, 'spam', False),
        (0, 'lassifiers', False),
    ])
    def test_has_argument(self, i, arg, expected):
        with self.a[i] as a:
            assert a.has_argument(arg) == expected
