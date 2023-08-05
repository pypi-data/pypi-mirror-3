# -*- coding: utf-8 -*-
from __future__ import with_statement

from shutil import rmtree, copytree
from os import system
from os.path import join, exists
import tempfile, threading, time

from logilab.common.decorators import classproperty

from cubicweb import Binary, QueryError, ValidationError, Unauthorized
from cubicweb import devtools # makes cubes importable
from cubes.vcsfile import entities, bridge

from utils import VCSFileTC, HERE

class VCSFileWriteTCMixin(object):

    @classproperty
    def test_db_id(cls):
        return cls.orig_repo_path + '-write'

    @classmethod
    def reset_fs_repo(cls):
        # .repo_path is an absolute path
        # (pathjoin done automatically from ._repo_path)
        destpath = str(cls.repo_path)
        if exists(destpath):
            rmtree(destpath)
        copytree(join(cls.datadir, str(cls.orig_repo_path)), destpath)

    @classmethod
    def pre_setup_database(cls, session, config):
        cls.reset_fs_repo()
        # don't use super, _WriteTC deleted to avoid unittest2 to try to run
        # it...
        VCSFileTC.pre_setup_database.im_func(cls, session, config)
        cls.grant_write_perm(session, 'managers')

    def setUp(self):
        VCSFileTC.setUp(self)
        self.reset_fs_repo()

    def tearDown(self):
        VCSFileTC.tearDown(self)
        rmtree(str(self.repo_path))

    def _test_new_revision(self, entity, vf, rev, revision):
        self.assertEqual(entity.content_for[0].eid, vf.eid)
        self.assertEqual(entity.description, u'add hôp')
        self.assertEqual(entity.author, 'syt')
        self.assertEqual(entity.data.getvalue(), 'hop\nhop\nhop\n')
        self.assertEqual(entity.data_encoding.lower(), self.repo_encoding)
        self.assertEqual(entity.data_format, 'text/plain')
        self.assertEqual(entity.rev.eid, rev.eid)
        self.assertEqual(entity.rev.revision, revision)
        if self.repo_type == u'mercurial':
            self.assertTrue(entity.rev.changeset)
        self.assertTrue(entity.rev.parent_revision)
        self.assertTrue(entity.rev.reverse_at_revision)

    def _new_toto_revision(self, data='hop\nhop\nhop\n', branch=entities._MARKER, req=None):
        if req is None:
            req = self.request()
        vf = req.execute('VersionedFile X WHERE X name "toto.txt"').get_entity(0, 0)
        self.vcsrepo.cw_clear_all_caches()
        self.vcsrepo._cw = req # XXX
        rev = self.vcsrepo.make_revision(msg=u'add hôp', author=u'syt', branch=branch)
        vc = req.execute('INSERT VersionContent X: X content_for VF, X from_revision R, '
                         'X data %(data)s WHERE VF eid %(vf)s, R eid %(r)s',
                         {'vf': vf.eid, 'r': rev.eid,
                          'data': Binary(data)}).get_entity(0, 0)
        return vf, rev, vc

    def _import_repository(self):
        try:
            session = self.repo.internal_session()
            bridge.import_content(session)
        finally:
            session.close()


class _WriteTC(VCSFileWriteTCMixin, VCSFileTC):
    _repo_path = u'testrepocopy' # must be unicode

    def test_new_revision(self):
        vf, rev, vc = self._new_toto_revision()
        self.commit()
        self._test_new_revision(vc, vf, rev, 8 + self.repo_rev_offset)
        self._import_repository()
        self.assertEqual(len(self.execute('Any X WHERE X revision %(r)s', {'r': rev.revision})), 1)

    def test_new_revision_security(self):
        self.execute('DELETE CWPermission X')
        self.commit()
        self.assertRaises(Unauthorized, self._new_toto_revision)

# XXX unable to do this, we need to get the associated VersionedFile in source.add_entity...
#     def test_two_steps_new_revision(self):
#         vf = self.execute('VersionedFile X WHERE X name "toto.txt"')
#         eid = self.execute('INSERT VersionContent X: X description %(msg)s, X author %(author)s, '
#                            'X data %(data)s', {'msg': u'add hôp', 'author': u'syt',
#                                                'data': Binary('hop\nhop\nhop\n')})[0][0]
#         self.execute('SET X content_for VF WHERE X eid %(x)s, VF eid %(vf)s',
#                      {'vf': vf[0][0], 'x': eid}, ('vf', 'x'))
#         self.commit()
#         self._test_new_revision(vf, eid)

    def test_rollback_new_revision(self):
        vf, rev, vc = self._new_toto_revision()
        self.rollback()
        # fail due to a bug in pysqlite, see
        # http://oss.itsystementwicklung.de/trac/pysqlite/ticket/219
        # http://www.sqlite.org/cvstrac/tktview?tn=2765,3
        # http://www.initd.org/pub/software/pysqlite/doc/usage-guide.html#controlling-transactions
        #rset = self.execute('Any X WHERE X eid %(x)s', {'x': rev.eid})
        #self.assertFalse(rset)
        rset = self.execute('Any X WHERE X eid %(x)s', {'x': vc.eid})
        self.assertFalse(rset)
        rset = self.execute('VersionContent X WHERE X content_for VF, VF eid %(vf)s', {'vf': vf.eid})
        self.assertEqual(len(rset), 2)
        # XXX check actually not in the repository

    def test_error_new_revision(self):
        # can't specify revision number
        self.assertRaises(QueryError, self.execute,
                          'INSERT Revision X: X from_repository R, '
                           'X description %(msg)s, X author %(author)s, X revision 2 '
                           'WHERE R eid %(r)s',
                           {'r': self.vcsrepo.eid, 'msg': u'add hôp', 'author': u'syt'})
        # missing from_repository
        self.assertRaises(ValidationError, self.execute,
                          'INSERT Revision X: '
                           'X description %(msg)s, X author %(author)s '
                           'WHERE R eid %(r)s',
                           {'r': self.vcsrepo.eid, 'msg': u'add hôp', 'author': u'syt'})
        self.rollback()
        # OK
        self.execute('INSERT Revision X: X from_repository R, '
                     'X description %(msg)s, X author %(author)s '
                     'WHERE R eid %(r)s',
                     {'r': self.vcsrepo.eid, 'msg': u'add hôp', 'author': u'syt'})
        # try to create another revision
        self.assertRaises(QueryError, self.execute,
                          'INSERT Revision X: X from_repository R, '
                          'X description %(msg)s, X author %(author)s '
                          'WHERE R eid %(r)s',
                          {'r': self.vcsrepo.eid, 'msg': u'add hôp', 'author': u'syt'})
        # commit while nothing changed in the revision
        self.assertRaises(QueryError, self.commit)

    def test_error_new_version_content(self):
        vfeid = self.execute('VersionedFile X WHERE X name "toto.txt"')[0][0]
        badreveid = self.execute('Revision X WHERE X revision 1')[0][0]
        # no revision transaction
        self.assertRaises(QueryError, self.execute,
                          'INSERT VersionContent X: X content_for VF, X from_revision R, '
                           'X data %(data)s WHERE VF eid %(vf)s, R eid %(r)s',
                          {'vf': vfeid, 'r': badreveid,
                           'data': Binary('hop\nhop\nhop\n')})
        # missing content_for relation
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.vcsrepo.eid, 'msg': u'add hôp', 'author': u'syt'})[0][0]
        self.assertRaises(ValidationError, self.execute,
                          'INSERT VersionContent X: X from_revision R, '
                           'X data %(data)s WHERE R eid %(r)s',
                          {'r': reveid,
                           'data': Binary('hop\nhop\nhop\n')})
        self.rollback()
        # missing data attribute
        self.assertRaises(ValidationError, self.execute,
                          'INSERT VersionContent X: X content_for VF, X from_revision R '
                           'WHERE VF eid %(vf)s, R eid %(r)s',
                          {'vf': vfeid, 'r': badreveid})
        self.rollback()
        # missing from_revision relation
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.vcsrepo.eid, 'msg': u'add hôp', 'author': u'syt'})[0][0]
        self.execute('INSERT VersionContent X: X content_for VF, '
                     'X data %(data)s WHERE VF eid %(vf)s',
                     {'vf': vfeid, 'data': Binary('hop\nhop\nhop\n')})
        self.assertRaises(ValidationError, self.commit)
        self.rollback()
        # bad from_revision relation
        reveid = self.execute('INSERT Revision X: X from_repository R, '
                              'X description %(msg)s, X author %(author)s '
                              'WHERE R eid %(r)s',
                              {'r': self.vcsrepo.eid, 'msg': u'add hôp', 'author': u'syt'})[0][0]
        self.execute('INSERT VersionContent X: X content_for VF, X from_revision R, '
                     'X data %(data)s WHERE VF eid %(vf)s, R eid %(r)s',
                     {'vf': vfeid, 'r': badreveid,
                      'data': Binary('hop\nhop\nhop\n')})
        self.assertRaises(QueryError, self.commit)

    def test_new_file(self):
        vfeid = self.execute('INSERT VersionedFile X: X from_repository R, '
                          'X directory %(dir)s, X name %(name)s WHERE R eid %(repo)s',
                          {'repo': self.vcsrepo.eid, 'dir': u'dir1', 'name': u'tutu.png'})[0][0]
        reveid = self.vcsrepo.make_revision(msg=u'new file', author=u'syt').eid
        eid = self.execute('INSERT VersionContent X: X content_for %(vf)s, X from_revision %(r)s, '
                           'X data %(data)s',
                           {'vf': vfeid, 'r': reveid, 'msg': u'new file', 'author': u'syt',
                            'data': Binary('zoubî')})[0][0]
        self.commit()
        entity = self.execute('Any X WHERE X eid %(x)s', {'x': eid}).get_entity(0, 0)
        vf = entity.content_for[0]
        self.assertEqual(vf.from_repository[0].eid, self.vcsrepo.eid)
        self.assertEqual(vf.directory, 'dir1')
        self.assertEqual(vf.name, 'tutu.png')
        self.assertEqual(entity.description, 'new file')
        self.assertEqual(entity.author, 'syt')
        self.assertEqual(entity.data.getvalue(), 'zoubî')
        self.assertEqual(entity.data_encoding, None)
        self.assertEqual(entity.data_format, 'image/png')

    def test_error_new_file(self):
        vfeid = self.execute('INSERT VersionedFile X: X directory %(dir)s, X name %(name)s WHERE R eid %(repo)s',
                     {'repo': self.vcsrepo.eid, 'dir': u'dir1', 'name': u'tutuu.txt'})[0][0]
        with self.assertRaises(ValidationError) as cm:
            self.commit()
        self.assertEqual(cm.exception.errors,
                         {'from_repository': u'at least one relation from_repository is required on VersionedFile (%s)' % vfeid})
        self.execute('INSERT VersionedFile X: X directory %(dir)s, X name %(name)s, X from_repository R '
                     'WHERE R eid %(repo)s', {'repo': self.vcsrepo.eid, 'dir': u'dir1', 'name': u'tutuu.txt'})
        with self.assertRaises(QueryError) as cm:
            self.commit()
        self.assertEqual(str(cm.exception),
                         'no transaction in progress for repository %s' % self.vcsrepo.eid)

    def test_multiple_changes_and_deletion(self):
        reveid = self.vcsrepo.make_revision(msg=u'add hop', author=u'syt').eid
        vf1 = self.execute('VersionedFile X WHERE X name "toto.txt"')
        eid1 = self.execute('INSERT VersionContent X: X content_for %(vf)s, X from_revision %(r)s, '
                            'X data %(data)s',
                            {'vf': vf1[0][0], 'r': reveid,
                             'data': Binary('hop\nhop\nhop\n')})[0][0]
        vf2 = self.execute('INSERT VersionedFile X: X from_repository R, '
                           'X directory %(dir)s, X name %(name)s WHERE R eid %(repo)s',
                           {'repo': self.vcsrepo.eid, 'dir': u'dir1', 'name': u'tutuu.txt'})
        eid2 = self.execute('INSERT VersionContent X: X content_for %(vf)s, X from_revision %(r)s, '
                           'X data %(data)s',
                            {'vf': vf2[0][0], 'r': reveid,
                             'data':Binary('zoubî')})[0][0]
        self.commit()
        entity1 = self.execute('Any X WHERE X eid %(x)s', {'x': eid1}).get_entity(0, 0)
        self.assertEqual(entity1.content_for[0].eid, vf1[0][0])
        self.assertEqual(entity1.description, 'add hop')
        self.assertEqual(entity1.author, 'syt')
        self.assertEqual(entity1.data.getvalue(), 'hop\nhop\nhop\n')
        entity2 = self.execute('Any X WHERE X eid %(x)s', {'x': eid2}).get_entity(0, 0)
        vf2 = entity2.content_for[0]
        self.assertEqual(vf2.from_repository[0].eid, self.vcsrepo.eid)
        self.assertEqual(vf2.directory, 'dir1')
        self.assertEqual(vf2.name, 'tutuu.txt')
        self.assertEqual(entity2.description, 'add hop')
        self.assertEqual(entity2.author, 'syt')
        self.assertEqual(entity2.data.getvalue(), 'zoubî')
        # deletion
        tmpdir = tempfile.mkdtemp()
        try:
            self.checkout(tmpdir)
            self.assertTrue(exists(join(tmpdir, 'dir1', 'tutuu.txt')))
            self.assertTrue(exists(join(tmpdir, 'toto.txt')))
        finally:
            rmtree(tmpdir)
        self.vcsrepo.cw_clear_all_caches()
        reveid = self.vcsrepo.make_revision(msg=u'kill file', author=u'auc').eid
        vf1 = self.execute('VersionedFile X WHERE X name "toto.txt"')
        # let's delete toto by linking its vf to DeletedVersionContent
        eid1 = self.execute('INSERT DeletedVersionContent X: X content_for %(vf)s, X from_revision %(r)s',
                           {'vf': vf1[0][0], 'r': reveid})[0][0]
        self.commit()
        entity1 = self.execute('Any X WHERE X eid %(x)s', {'x': eid1}).get_entity(0, 0)
        self.assertEqual(entity1.content_for[0].eid, vf1[0][0])
        self.assertEqual(entity1.description, 'kill file')
        self.assertEqual(entity1.author, 'auc')
        tmpdir = tempfile.mkdtemp()
        try:
            self.checkout(tmpdir)
            self.assertTrue(exists(join(tmpdir, 'dir1', 'tutuu.txt')))
            self.assertFalse(exists(join(tmpdir, 'toto.txt')))
            self.assertFalse(exists(join(tmpdir, 'dir1', 'subdir')))
        finally:
            rmtree(tmpdir)
        oddfile = self.execute('VersionedFile F WHERE F name "__hg_needs_a_file__"').get_entity(0,0)
        content = vf1.get_entity(0,0).reverse_content_for
        self.assertEqual(len(content), 4)
        self.assertIsInstance(content[0], entities.DeletedVersionContent)
        content = oddfile.reverse_content_for
        self.assertEqual(len(content), 2)
        self.assertIsInstance(content[0], entities.DeletedVersionContent)


class SVNSourceWriteTC(_WriteTC):
    orig_repo_path = 'testrepo'
    repo_type = u'subversion'
    repo_rev_offset = 0

    def checkout(self, tmpdir):
        svncmd = 'svn co file://%s %s >/dev/null 2>&1' % (self.repo_path, tmpdir)
        if system(svncmd):
            raise Exception('can not check out %s' % self.repo_path)


class HGSourceWriteTC(_WriteTC):
    orig_repo_path = 'testrepohg'
    repo_type = u'mercurial'
    repo_encoding = u'latin1'
    repo_rev_offset = -1

    def checkout(self, tmpdir):
        svncmd = 'hg clone %s %s >/dev/null 2>&1' % (self.repo_path, join(tmpdir, self.orig_repo_path))
        if system(svncmd):
            raise Exception('can not check out %s' % self.repo_path)
        system('mv %s %s' % (join(tmpdir, self.orig_repo_path, '*'), tmpdir))
        system('mv %s %s' % (join(tmpdir, self.orig_repo_path, '.hg'), tmpdir))

    def test_branches_from_app(self):
        vf, rev, vc = self._new_toto_revision(data='branch 1.2.3 content',
                                              branch=u'1.2.3')
        self.commit()
        hgdir = self.repo_path
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'hop\nhop\n\n')
        system('cd %s; hg up 1.2.3 >/dev/null 2>&1' % hgdir)
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'branch 1.2.3 content')
        # create new changeset in the default branch
        vf, rev, vc = self._new_toto_revision(data='branch default content')
        self.commit()
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'branch default content')
        # create new changeset in the 1.2.3 branch
        vf, rev, vc = self._new_toto_revision(data='branch 1.2.3 new content',
                                              branch=u'1.2.3')
        self.commit()
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        self.assertEqual(file(join(hgdir, 'toto.txt')).read(),
                          'branch default content')
        # delete file from both branches
        vf.vcs_rm(branch=u'default', author=u'titi')
        self.commit()
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        self.assertFalse(exists((join(hgdir, 'toto.txt'))))
        vf.vcs_rm(branch=u'1.2.3', author=u'toto')
        self.commit()
        system('cd %s; hg up 1.2.3 >/dev/null 2>&1' % hgdir)
        self.assertFalse(exists((join(hgdir, 'toto.txt'))))
        vf.cw_clear_all_caches()
        with self.assertRaises(QueryError) as cm:
            vf.vcs_rm(branch=u'1.2.3', author=u'toto')
        self.assertEqual(str(cm.exception), 'toto.txt is already deleted from the vcs')

    def test_strip(self):
        self.assertEqual(self.vcsrepo.latest_known_revision(), 6)
        vcrset = self.execute('Any X WHERE X from_revision R, R revision 6')
        system('cd %s; hg --config extensions.hgext.mq= strip 6 1>/dev/null 2>/dev/null' % self.repo_path)
        try:
            session = self.repo.internal_session()
            bridge.import_content(session)
        finally:
            session.close()
        self.commit()
        self.assertEqual(self.vcsrepo.latest_known_revision(), 5)
        for eid, in vcrset:
            self.assertFalse(self.execute('Any X WHERE X eid %(x)s', {'x': eid}))

    def test_branches_from_hg(self):
        self.assertEqual(self.execute('Any COUNT(R) WHERE R is Revision').rows, [[7]])
        hgdir = self.repo_path
        system('cd %s; hg up default >/dev/null 2>&1' % hgdir)
        system('cd %s; hg branch newbranch >/dev/null 2>&1' % hgdir)
        system('cd %s; hg tag newbranch -m "opening newbranch"' % hgdir)
        try:
            session = self.repo.internal_session()
            bridge.import_content(session)
        finally:
            session.close()
        self.commit()
        hgtags = self.execute('VersionContent V WHERE V content_for VF,  '
                              'VF name ".hgtags"').get_entity(0,0)
        self.assertEqual(hgtags.from_revision[0].branch, u'newbranch')
        self.assertEqual(hgtags.from_revision[0].revision, 7)
        self.assertEqual(self.execute('Any COUNT(R) WHERE R is Revision').rows, [[8]])



class HGPostgresWriteTC(VCSFileWriteTCMixin, VCSFileTC):
    _repo_path = u'testrepocopy' # must be unicode
    orig_repo_path = 'testrepohg'
    repo_type = u'mercurial'
    repo_encoding = u'latin1'
    repo_rev_offset = -1

    @classmethod
    def setUpClass(cls):
        cls.config = devtools.ApptestConfiguration(
            'data', sourcefile='sources_postgres', apphome=cls.datadir)

    def test_new_revision_concurrency(self):
        self.create_user(self.request(), 'toto', ('managers',))
        head = self.vcsrepo.branch_head()
        self.cnx._txid = lambda *args: {'txid': 'tx1'}
        lock = threading.Lock()
        vf, rev, vc1 = self._new_toto_revision()
        def commit_later(cnx=self.cnx, session=self.session):
            time.sleep(.5)
            cnx.commit()
            lock.release()
        lock.acquire()
        t = threading.Thread(target=commit_later)
        t.start()
        cnx = self.login('toto')
        vf, rev, vc2 = self._new_toto_revision(req=cnx.request())
        lock.acquire()
        with self.assertRaises(ValidationError) as cm:
            cnx.commit()
        self.assertEqual(cm.exception.errors, {None: 'concurrency error, please re-upload the revision'})
        t.join()

del HGPostgresWriteTC # XXX comment out to run the test. Need to properly detect
                      # configuration and skip when necessary

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    del _WriteTC # otherwise it will be detected by unittest2
    unittest_main()
