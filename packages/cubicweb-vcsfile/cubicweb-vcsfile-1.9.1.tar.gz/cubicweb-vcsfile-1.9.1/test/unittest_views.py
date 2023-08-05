"""vcsfile.views module tests"""

import re
from os import remove
from os.path import exists

from cubicweb.web.views import actions, primary, idownloadable

from utils import VCSFileTC, remove_eid # import first to setup import machinery
from cubes.vcsfile import entities
from cubes.vcsfile.views import primary as svnfviews, actions as vcsactions



class VCViewsTC(VCSFileTC):

    def test_entity(self):
        v1 = self.execute('Any X WHERE X from_revision R, R revision 1, X content_for VF, VF name "toto.txt"').get_entity(0, 0)
        self.assertIsInstance(v1, entities.VersionContent)
        self.assertEqual(v1.file.path, "toto.txt")
        self.assertEqual(v1.is_head(), False)
        self.assertEqual(v1.head.revision, 2)
        self.assertEqual(v1.cw_adapt_to('IPrevNext').previous_entity(), None)
        self.assertEqual(v1.cw_adapt_to('IPrevNext').next_entity().revision, 2)
        v2 = self.execute('Any X WHERE X from_revision R, R revision 2, X content_for VF, VF name "toto.txt"').get_entity(0, 0)
        self.assertIsInstance(v2, entities.VersionContent)
        self.assertEqual(v2.file.path, "toto.txt")
        self.assertEqual(v2.is_head(), True)
        self.assertEqual(v2.head.revision, 2)
        self.assertEqual(v2.cw_adapt_to('IPrevNext').previous_entity().revision, 1)
        self.assertEqual(v2.cw_adapt_to('IPrevNext').next_entity(), None)
        v3 = self.execute('Any X WHERE X from_revision R, R revision 3').get_entity(0, 0)
        self.assertIsInstance(v3, entities.DeletedVersionContent)
        self.assertFalse(isinstance(v3, entities.VersionContent)) # VersionContent(DeletedVersionContent)
        self.assertEqual(v3.file.path, "dir1/data.bin.gz")
        self.assertEqual(v3.head.revision, 3)
        self.assertEqual(v3.is_head(), True)
        self.assertEqual(v3.cw_adapt_to('IPrevNext').previous_entity().revision, 1)
        self.assertEqual(v3.cw_adapt_to('IPrevNext').next_entity(), None)

    def test_possible_actions(self):
        req = self.request()
        v1rset = req.execute('Any X WHERE X from_revision R, R revision 1, X content_for VF, VF name "toto.txt"')
        self.assertEqual(self.pactions(req, v1rset),
                          [('managepermission', actions.ManagePermissionsAction),
                           ('addrelated', actions.AddRelatedActions),
                           ('revhead', vcsactions.VCHeadRevisionAction),
                           ('revall', vcsactions.VCAllRevisionsAction),
#                           ('revnext', vcsactions.VCNextRevisionAction),
                           ('revfiles', vcsactions.VCRevisionModifiedFilesAction),
                           ('revallfiles', vcsactions.VCRevisionAllFilesAction)])
        v2rset = req.execute('Any X WHERE X from_revision R, R revision 2, X content_for VF, VF name "toto.txt"')
        self.assertEqual(self.pactions(req, v2rset),
                          [('managepermission', actions.ManagePermissionsAction),
                           ('addrelated', actions.AddRelatedActions),
                           ('revall', vcsactions.VCAllRevisionsAction),
#                           ('revprev', vcsactions.VCPreviousRevisionAction),
                           ('revfiles', vcsactions.VCRevisionModifiedFilesAction),
                           ('revallfiles', vcsactions.VCRevisionAllFilesAction)])
        v3rset = req.execute('Any X WHERE X from_revision R, R revision 3, X content_for VF, VF name "data.bin.gz"')
        self.assertEqual(self.pactions(req, v2rset),
                          [('managepermission', actions.ManagePermissionsAction),
                           ('addrelated', actions.AddRelatedActions),
                           ('revall', vcsactions.VCAllRevisionsAction),
#                           ('revprev', vcsactions.VCPreviousRevisionAction),
                           ('revfiles', vcsactions.VCRevisionModifiedFilesAction),
                           ('revallfiles', vcsactions.VCRevisionAllFilesAction)])

    def test_metadata_view(self):
        v1 = self.execute('Any X WHERE X from_revision R, R revision 1, X content_for VF, VF name "toto.txt"').get_entity(0, 0)
        self.assertMultiLineEqual(remove_eid(v1.view('metadata')),
                              '<div class="metadata">#EID - <span>revision 1 of</span> <span class="value">toto.txt</span>,&nbsp;<span>created on</span> <span class="value">2007/12/19 11:18</span>&nbsp;<span>by</span> <span class="value">syt</span></div>')
        v3 = self.execute('Any X WHERE X from_revision R, R revision 3').get_entity(0, 0)
        self.assertMultiLineEqual(remove_eid(v3.view('metadata')),
                          '<div class="metadata">#EID - <span>revision 3 of</span> <span class="value">dir1/data.bin.gz</span>,&nbsp;<span>created on</span> <span class="value">2008/01/08 15:56</span>&nbsp;<span>by</span> <span class="value">syt</span></div>')


    def test_primary_view(self):
        req = self.request()
        v1rset = req.execute('Any X WHERE X from_revision R, R revision 1, X content_for VF, VF name "toto.txt"')
        view = self.vreg['views'].select('primary', req, rset=v1rset)
        self.assertIsInstance(view, svnfviews.VCPrimaryView)
        view.render() # just check no error raised
        v3rset = req.execute('Any X WHERE X from_revision R, R revision 3')
        view = self.vreg['views'].select('primary', req, rset=v3rset)
        self.assertIsInstance(view, svnfviews.DVCPrimaryView)
        view.render() # just check no error raised


class VFViewsTC(VCSFileTC):

    def test_entity(self):
        toto = self.execute('VersionedFile X WHERE X name %(name)s', {'name': 'toto.txt'}).get_entity(0, 0)
        self.assertIsInstance(toto, entities.VersionedFile)
        self.assertEqual(toto.name, "toto.txt")
        self.assertEqual(toto.directory, "")
        self.assertEqual(toto.path, "toto.txt")
        self.assertEqual(toto.head.revision, 2)
        self.assertTrue(toto.repository.path.endswith('testrepo'))
        tutu = self.execute('VersionedFile X WHERE X name %(name)s', {'name': 'tutu.txt'}).get_entity(0, 0)
        self.assertIsInstance(tutu, entities.VersionedFile)
        self.assertEqual(tutu.name, "tutu.txt")
        self.assertEqual(tutu.directory, "dir1")
        self.assertEqual(tutu.path, "dir1/tutu.txt")
        self.assertEqual(tutu.head.revision, 4)
        self.assertTrue(tutu.repository.path.endswith('testrepo'))
        self.assertEqual(tutu.deleted_in_branch(), False)
        data = self.execute('VersionedFile X WHERE X name %(name)s', {'name': 'data.bin.gz'}).get_entity(0, 0)
        self.assertEqual(data.head.revision, 3)
        self.assertEqual(data.deleted_in_branch(), True)

    def test_possible_actions(self):
        req = self.request()
        totorset = req.execute('VersionedFile X WHERE X name %(name)s', {'name': 'toto.txt'})
        self.assertEqual(self.pactions(req, totorset),
                          # XXX because we've some editable relation
                          #     check we actually want this
                          [('edit', actions.ModifyAction),
                           ('managepermission', actions.ManagePermissionsAction),
                           ('addrelated', actions.AddRelatedActions),
                           ('vfnewrevaction', vcsactions.VFPutUpdateAction),
                           ('vcsrmaction', vcsactions.VFRmAction),
                           ('revhead', vcsactions.VFHEADRevisionAction),
                           ('revall', vcsactions.VFAllRevisionsAction),
                           ('addrevision', vcsactions.VFAddRevisionAction)])


    def test_primary_view(self):
        req = self.request()
        totorset = req.execute('VersionedFile X WHERE X name %(name)s', {'name': 'toto.txt'})
        view = self.vreg['views'].select('primary', req, rset=totorset)
        self.assertIsInstance(view, primary.PrimaryView)
        view.render() # just check no error raised
        datarset = req.execute('VersionedFile X WHERE X name %(name)s', {'name': 'data.bin.gz'})
        view = self.vreg['views'].select('primary', req, rset=datarset)
        self.assertIsInstance(view, primary.PrimaryView)
        view.render() # just check no error raised


class UtilsTC(VCSFileTC):

    def test_rql_revision_content(self):
        repoeid = self.vcsrepo.eid
        rset = self.execute(*entities.rql_revision_content(repoeid, 1))
        self.assertEqual([(x.file.path, x.revision) for x in rset.entities()],
                          [('toto.txt', 1), ('dir1/data.bin.gz', 1)])
        rset = self.execute(*entities.rql_revision_content(repoeid, 2))
        self.assertEqual([(x.file.path, x.revision) for x in rset.entities()],
                          [('toto.txt', 2), ('dir1/data.bin.gz', 1)])
        rset = self.execute(*entities.rql_revision_content(repoeid, 3))
        self.assertEqual([(x.file.path, x.revision) for x in rset.entities()],
                          [('toto.txt', 2), ('dir1/data.bin.gz', 3)])
        rset = self.execute(*entities.rql_revision_content(repoeid, 4))
        self.assertEqual([(x.file.path, x.revision) for x in rset.entities()],
                          [('toto.txt', 2), ('dir1/tutu.txt', 4)])


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
