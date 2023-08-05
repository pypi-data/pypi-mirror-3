# -*- coding: utf-8 -*-
import os.path as osp
import logging
logging.basicConfig(level=logging.CRITICAL)

from logilab.common.testlib import unittest_main

from cubicweb import ValidationError
from cubicweb.devtools.testlib import CubicWebTC

from cubes.vcsfile import bridge

from utils import VCSFileTC

class SVNRepoTC(VCSFileTC):
    repo_type = u'subversion'
    _repo_path = u'testrepo'
    repo_encoding = u'utf-8'

    def test_base(self):
        res = self.execute('Revision X')
        self.assertEqual(len(res), 7)
        res = self.execute('VersionedFile X')
        self.assertEqual(len(res), 5)
        res = self.execute('VersionContent X')
        self.assertEqual(len(res), 6)
        res = self.execute('DeletedVersionContent X')
        self.assertEqual(len(res), 2)

    def _test_advanced_rev_query(self, res):
        self.assertEqual(res[0], [1, 'revision 1', '2007-12-19 11:18', u'syt', None, None])
        self.assertEqual(res[1], [2, 'revision 2: modif toto.txt', '2007-12-19 11:18', u'syt', None, None])
        self.assertEqual(res[2], [3, 'delete binary file', '2008-01-08 15:56', u'syt', None, None])
        self.assertEqual(res[3], [4, 'hop', '2008-01-09 18:11', u'syt', None, None])

    def _test_advanced_vc_query(self, res):
        self.assertEqual(res[0], ['__hg_needs_a_file__', 5, None, u'application/octet-stream',
                                   'the file hg needs\n'])
        self.assertEqual(res[1], ['data.bin.gz', 1, u'gzip', u'application/octet-stream',
                                   '\x1f\x8b\x08\x00\xde\x17YG\x00\x03\x0b\xc9\xc8,V\x00\xa2D\x85\x92\xd4\xe2\x12.\x00\x8c-\xc0\xfa\x0f\x00\x00\x00'])
        self.assertEqual(res[2], [u'm\xe9', 7, None, u'application/octet-stream', ''])
        self.assertEqual(res[3], ['toto.txt', 1, self.repo_encoding, u'text/plain',
                                   'hop\n'])
        self.assertEqual(res[4], ['toto.txt', 2, self.repo_encoding, u'text/plain',
                                   'hop\nhop\n'])
        self.assertEqual(res[5], ['tutu.txt', 4, self.repo_encoding, u'text/plain',
                                   'coucou\n'])

    def _test_advanced_dvc_query(self, res):
        self.assertEqual(res[0], [u'__hg_needs_a_file__', 6])
        self.assertEqual(res[1], [u'data.bin.gz', 3])

    def test_advanced(self):
        res = self.execute('Any X,D,N ORDERBY D,N WHERE X is VersionedFile, X directory D, X name N')
        self.assertEqual(len(res), 5)
        self.assertEqual(res[0][1:], [u'', u'm\xe9'])
        self.assertEqual(res[1][1:], [u'', u'toto.txt'])
        self.assertEqual(res[2][1:], [u'dir1', 'data.bin.gz'])
        self.assertEqual(res[3][1:], [u'dir1', 'tutu.txt'])
        self.assertEqual(res[4][1:], [u'dir1/ghostdir', '__hg_needs_a_file__'])
        res = self.execute('Any R,C,D,A,CS,B ORDERBY R '
                           'WHERE X revision R, X description C, '
                           'X creation_date D, X author A, X changeset CS, X branch B')
        for row in res:
            row[2] = row[2].strftime('%Y-%m-%d %H:%M')
        self.assertEqual(len(res), 7)
        self._test_advanced_rev_query(res)
        res = self.execute('Any P,R,E,F,DA ORDERBY P,R '
                           'WHERE X content_for Y, Y name P, X from_revision REV, '
                           'REV revision R, X data_encoding E, X data_format F, '
                           'X data DA')
        for row in res:
            row[-1] = row[-1].getvalue()
        self.assertEqual(len(res), 6)
        self._test_advanced_vc_query(res)
        res = self.execute('Any P,R ORDERBY P,R '
                           'WHERE X content_for Y, Y name P, X from_revision REV, '
                           'REV revision R, X is DeletedVersionContent')
        self.assertEqual(len(res), 2)
        self._test_advanced_dvc_query(res)

    def test_revision_parent(self):
        res = self.execute('Any R,P ORDERBY REV WHERE R revision REV, R parent_revision P?')
        self.assertEqual(len(res), 7)
        self.assertEqual(res[0][1], None)
        latestrev = res[0][0]
        for i, (rev, parent) in enumerate(res[1:]):
            self.assertEqual(parent, latestrev)
            latestrev = rev

    first_revision = 1
    def test_revision_search(self):
        res = self.execute('Any P ORDERBY P WHERE X from_revision R, R revision %s, '
                           'X content_for VF, VF name P' % self.first_revision)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], [u'data.bin.gz'])
        self.assertEqual(res[1], [u'toto.txt'])

    author = 'syt'
    def test_author_search(self):
        res = self.execute('DISTINCT Any P ORDERBY P WHERE X from_revision R, '
                           'R author %(author)s, X content_for VF, VF name P',
                           {'author': self.author})
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0], [u'data.bin.gz'])
        self.assertEqual(res[1], [u'toto.txt'])
        self.assertEqual(res[2], [u'tutu.txt'])

    def test_anon_access_data(self):
        bridge._REPOHDLRS.clear()
        self.login('anon')
        res = self.execute('VersionContent X LIMIT 1').get_entity(0, 0)
        self.assertTrue(res.data)
        self.assertTrue(res.data.getvalue())


class SVNPartRepoTC(VCSFileTC):
    repo_type = u'subversion'
    _repo_path = u'testrepo'
    repo_encoding = u'latin1'
    repo_subpath = u'dir1'

    def test_base(self):
        res = self.execute('Revision X')
        self.assertEqual(len(res), 7)
        res = self.execute('VersionedFile X')
        self.assertEqual(len(res), 3)
        res = self.execute('VersionContent X')
        self.assertEqual(len(res), 3)
        res = self.execute('DeletedVersionContent X')
        self.assertEqual(len(res), 2)

class SVNNoContentPartRepoTC(VCSFileTC):
    repo_type = u'subversion'
    _repo_path = u'testrepo'
    repo_encoding = u'latin1'
    repo_subpath = u'dir1'
    repo_import_revision_content = False

    def test_base(self):
        res = self.execute('Revision X')
        self.assertEqual(len(res), 7)
        res = self.execute('VersionedFile X')
        self.assertEqual(len(res), 0)
        res = self.execute('VersionContent X')
        self.assertEqual(len(res), 0)
        res = self.execute('DeletedVersionContent X')
        self.assertEqual(len(res), 0)


class HGRepoTC(SVNRepoTC):
    repo_type = u'mercurial'
    _repo_path = u'testrepohg'
    repo_encoding = u'latin1'

    first_revision = 0
    author = 'Sylvain Thenault <sylvain.thenault@logilab.fr>'

    def _test_advanced_rev_query(self, res):
        self.assertEqual(res[0], [0, 'revision 1', '2008-08-19 13:37',
                                   u'Sylvain Thenault <sylvain.thenault@logilab.fr>',  u'1a4a39caf4fe', 'default'])
        self.assertEqual(res[1], [1, 'revision 2: modif toto.txt', '2008-08-19 13:37',
                                   u'Sylvain Thenault <sylvain.thenault@logilab.fr>', u'295b01eaded6', 'default'])
        self.assertEqual(res[2], [2, u'delete binary file', '2008-08-19 13:38',
                                   u'Sylvain Thenault <sylvain.thenault@logilab.fr>', u'9b1d7e2c028e', 'default'])
        self.assertEqual(res[3], [3, 'hop', '2008-08-19 13:38',
                                   u'Sylvain Thenault <sylvain.thenault@logilab.fr>', u'45e1887b0167', 'default'])

    def _test_advanced_vc_query(self, res):
        self.assertEqual(res[1], ['data.bin.gz', 0, u'gzip', u'application/octet-stream',
                                   '\x1f\x8b\x08\x08\xed\x93\xaaH\x00\x03data.bin\x00\x93\xef\xe6\xe0\xd81y\x95\x07\x03sI~I\xbe^IE\t\xc3\xe9\x13\xfa\x0f\x1e110\xb8\xbesbe``\x00\x00\x85\xb3]\x01"\x00\x00\x00'])
        self.assertEqual(res[2], [u'm\xe9', 6, None, u'application/octet-stream', ''])
        self.assertEqual(res[3], ['toto.txt', 0, u'latin1', u'text/plain',
                                   'hop\n\n'])
        self.assertEqual(res[4], ['toto.txt', 1, u'latin1', u'text/plain',
                                   'hop\nhop\n\n'])
        self.assertEqual(res[5], ['tutu.txt', 3, u'latin1', u'text/plain',
                                   'coucou\n\n'])

    def _test_advanced_dvc_query(self, res):
        self.assertEqual(res[1], [u'data.bin.gz', 2])


    def test_error_update_repo(self):
        self.assertRaises(ValidationError,
                          self.execute, 'SET X type "subversion" WHERE X is Repository')


class HGPartRepoTC(SVNPartRepoTC):
    repo_type = u'mercurial'
    _repo_path = u'testrepohg'
    repo_encoding = u'latin1'

class HGNoContentPartRepoTC(SVNNoContentPartRepoTC):
    repo_type = u'mercurial'
    _repo_path = u'testrepohg'
    repo_encoding = u'latin1'


class HGCopyAndRenameTC(VCSFileTC):
    _repo_path = u'testrepohg_renaming'
    repo_type = u'mercurial'

    def test_copy(self):
        rset = self.execute('Any F1, R1, F2, R2 WHERE VC1 vc_copy VC2,'
                            'VC1 content_for VF1, VF1 name F1, VC1 from_revision REV1, REV1 revision R1,'
                            'VC2 content_for VF2, VF2 name F2, VC2 from_revision REV2, REV2 revision R2'
                            )
        self.assertEqual(rset.rows,
                          [[u'tete.txt', 3, u'tata.txt', 2]])

    def test_rename(self):
        rset = self.execute('Any F1, R1, F2, R2 WHERE VC1 vc_rename VC2,'
                            'VC1 content_for VF1, VF1 name F1, VC1 from_revision REV1, REV1 revision R1,'
                            'VC2 content_for VF2, VF2 name F2, VC2 from_revision REV2, REV2 revision R2'
                            )
        self.assertEqual(rset.rows,
                          [[u'tata.txt', 2, u'toto.txt', 0]])

class HGCachedRepoTC(VCSFileTC):
    repo_type = u'mercurial'
    _repo_path = u'testrepohg'
    repo_encoding = u'latin1'

    @classmethod
    def _create_repo(cls, session):
        return session.create_entity('Repository', type=cls.repo_type,
                                     source_url='file://' + cls.repo_path,
                                     encoding=cls.repo_encoding)

    def test_cache_mgmt(self):
        self.skipTest('need update to deal with pre_setup')
        self.session.repo = self.repo
        self.assertFalse(osp.isabs(self.vcsrepo.local_cache))
        cachedir = osp.join(self.config['local-repo-cache-root'],
                            self.vcsrepo.local_cache)
        self.assertTrue(osp.isabs(cachedir))
        self.assertTrue(osp.isdir(cachedir))
        self.execute('DELETE Repository R WHERE R eid %(r)s', {'r': self.vcsrepo.eid})
        self.commit()
        self.assertFalse(osp.isdir(cachedir))

if __name__ == '__main__':
    unittest_main()
