from utils import VCSFileTC

class HooksTC(VCSFileTC):
    test_db_id = 'vcsfile_hooks'
    @classmethod
    def pre_setup_database(cls, session, config):
        session.create_entity('Tag', name=u'dir1')
        session.create_entity('Folder', name=u'dir1')
        super(HooksTC, cls).pre_setup_database(session, config)

    def test_auto_classification(self):
        toto = self.execute('Any X WHERE X name "toto.txt"').get_entity(0, 0)
        self.assertFalse(toto.reverse_tags)
        self.assertFalse(toto.filed_under)
        tutu = self.execute('Any X WHERE X name "tutu.txt"').get_entity(0, 0)
        self.assertTrue(tutu.reverse_tags)
        self.assertTrue(tutu.filed_under)


class AtRevisionHooksTC(VCSFileTC):
    _repo_path = u'testrepohg_branches'
    repo_type = u'mercurial'

    def test_at_revision_is_set(self):
        self.assertTrue(self.execute('Any X WHERE X at_revision Y'))
        def files(revnum):
            rev = self.execute('Revision X WHERE X revision %(rev)s', {'rev': revnum}).get_entity(0, 0)
            return sorted((x.file.name, x.revision) for x in rev.reverse_at_revision)
        self.assertEqual(files(0), [(u'README', 0), (u'file.txt', 0)])
        self.assertEqual(files(1), [(u'README', 1), (u'file.txt', 0)])
        self.assertEqual(files(2), [(u'README', 1), (u'file.txt', 2)])
        self.assertEqual(files(3), [(u'README', 1), (u'file.txt', 2), (u'otherfile.txt', 3)])
        self.assertEqual(files(4), [(u'README', 1), (u'file.txt', 4), (u'otherfile.txt', 4)])

        self.assertEqual(files(9), [(u'README', 1),
                                    (u'andagain.txt', 9),
                                    (u'file.txt', 4),
                                    (u'oneagain.txt', 9),
                                    (u'otherfile.txt', 4)])

        self.assertEqual(files(12), [(u'README', 11),
                                     (u'andagain.txt', 9),
                                     (u'file.txt', 12),
                                     (u'oneagain.txt', 9),
                                     (u'otherfile.txt', 4)])

    def test_vf_creation_date(self):
        vf = self.vcsrepo.versioned_file('', 'file.txt')
        self.assertFalse(vf.creation_date == vf.modification_date)
        rev = vf.branch_head().rev
        self.assertEqual(vf.modification_date, rev.creation_date)

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()

