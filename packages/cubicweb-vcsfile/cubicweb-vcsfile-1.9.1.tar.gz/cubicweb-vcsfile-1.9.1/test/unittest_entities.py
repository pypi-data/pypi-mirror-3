from os.path import join, abspath

from logilab.common.decorators import clear_cache

from cubicweb import ValidationError
from cubicweb.devtools.testlib import TestCase, CubicWebTC

from cubes.vcsfile.entities import remove_authinfo
from utils import VCSFileTC, HERE


class RemoveAuthInfoTC(TestCase):
    def test(self):
        self.assertEqual(remove_authinfo('http://www.logilab.org/src/cw'),
                          'http://www.logilab.org/src/cw')
        self.assertEqual(remove_authinfo('http://toto:1223@www.logilab.org/src/cw'),
                          'http://***@www.logilab.org/src/cw')


def get_parent_revisions(head):
    return [head.revision] + [vc.revision for vc in head.iter_parent_versions()]

def get_following_revisions(initial):
    revs = []
    todo = [initial]
    while todo:
        initial = todo.pop(0)
        if initial.revision in revs:
            continue
        revs.append(initial.revision)
        for child in initial.next_versions():
            if not child.revision in revs:
                todo.append(child)
    return revs

class BranchesTC(VCSFileTC):
    _repo_path = u'testrepohg_branches'
    repo_type = u'mercurial'

    def head(self, file, *args):
        return self.vcsrepo.versioned_file('', file).branch_head(*args)

    def initial(self, file, *args):
        return self.vcsrepo.versioned_file('', file).revisions[-1]

    def rev(self, file, *args):
        return self.head(file, *args).revision

    def test_vcsrm(self):
        self.grant_write_perm(self.session, 'managers', self.vcsrepo.eid)
        vf = self.vcsrepo.versioned_file('', 'README')
        vf.vcs_rm()
        self.commit()
        clear_cache(vf, 'branch_head')
        clear_cache(vf, 'version_content')
        self.assertTrue(vf.deleted_in_branch())
        # ensure parent_revision has been properly set
        self.assertTrue(vf.head.rev.parent_revision)
        # ensure at_revision has been properly set, expect 5 files referenced by
        # the revision
        self.assertEqual(len(vf.head.rev.reverse_at_revision), 5,
                          vf.head.rev.reverse_at_revision)

    def test_branch_head_no_arg(self):
        self.assertEqual(self.rev('README'), 11)
        self.assertEqual(self.rev('file.txt'), 12)
        self.assertEqual(self.rev('otherfile.txt'), 4)

    def test_branch_head_default(self):
        self.assertEqual(self.rev('README', 'default'), 11)
        self.assertEqual(self.rev('file.txt', 'default'), 12)
        self.assertEqual(self.rev('otherfile.txt', 'default'), 4)

    def test_branch_head_branch1(self):
        self.assertEqual(self.rev('README', 'branch1'), 1)
        self.assertEqual(self.rev('file.txt', 'branch1'), 2)
        self.assertEqual(self.rev('otherfile.txt', 'branch1'), 3)

    def test_previous_versions(self):
        self.assertEqual(get_parent_revisions(self.head('README')),
                         [11, 1, 0])
        self.assertEqual(get_parent_revisions(self.head('file.txt')),
                         [12, 10, 4, 2, 0])
        self.assertEqual(get_parent_revisions(self.head('file.txt', 'branch1')),
                         [2, 0])
        self.assertEqual(get_parent_revisions(self.head('otherfile.txt')),
                         [4, 3])
        self.assertEqual(get_parent_revisions(self.head('oneagain.txt')),
                         [9, 7, 6, 5])
        self.assertEqual(get_parent_revisions(self.head('andagain.txt')),
                         [9, 8])

    def test_next_versions(self):
        self.assertEqual(get_following_revisions(self.initial('README')),
                         [0, 1, 11])
        self.assertEqual(get_following_revisions(self.initial('file.txt')),
                         [0, 2, 4, 10, 12])
        self.assertEqual(get_following_revisions(self.initial('otherfile.txt')),
                         [3, 4])
        self.assertEqual(get_following_revisions(self.initial('oneagain.txt')),
                         [5, 6, 7, 9])
        self.assertEqual(get_following_revisions(self.initial('andagain.txt')),
                         [8, 9])


class RepositoryTC(CubicWebTC):
    def test_repo_path_security(self):
        req = self.request()
        path = unicode(abspath(join(HERE, 'whatever')))
        vcsrepo = req.create_entity('Repository',
                                    path=path, type=u'mercurial')
        req.cnx.commit()
        self.assertEqual(vcsrepo.dc_title(),
                          u'mercurial:%s' % path)
        self.login('anon')
        req = self.request()
        vcsrepo = req.execute('Repository X').get_entity(0, 0)
        self.assertEqual(vcsrepo.dc_title(), 'mercurial repository #%s' % vcsrepo.eid)

    def test_unmodifiable_attrs(self):
        req = self.request()
        self.assertRaises(ValidationError, req.create_entity, 'Repository',
                          source_url=u"http://myrepo.ru",
                          type=u'mercurial')
        req.cnx.rollback()
        req = self.request()
        repo = req.create_entity('Repository', type=u'mercurial',
                                 path=unicode(abspath(join(HERE, 'whatever'))))
        req.cnx.commit()
        self.assertRaises(ValidationError, repo.set_attributes, path=u'new')
        self.assertRaises(ValidationError, repo.set_attributes, type=u'mercurial')
        self.assertRaises(ValidationError, repo.set_attributes, source_url=u'http://myrepo.fr')

    def test_source_url_format(self):
        req = self.request()
        self.assertRaises(ValidationError, req.create_entity, 'Repository',
                          path=u'whatever', type=u'mercurial')
        self.assertRaises(ValidationError, req.create_entity, 'Repository',
                          source_url=u'whatever', type=u'mercurial')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
