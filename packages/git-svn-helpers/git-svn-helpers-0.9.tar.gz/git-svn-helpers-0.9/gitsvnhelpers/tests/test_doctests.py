from gitsvnhelpers import testing


class TestGitify(testing.DocFileCase):
    path = 'test_gitify.txt'


class TestGitifyUp(testing.DocFileCase):
    path = 'test_gitify_up.txt'


class TestGitifyFetch(testing.DocFileCase):
    path = 'test_gitify_fetch.txt'


class TestSymlinkMigration(testing.DocFileCase):
    path = 'test_symlink_migration.txt'


class TestSvnSwitch(testing.DocFileCase):
    path = 'test_svn_switch.txt'


