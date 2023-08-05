import os
import tempfile
from socket import getfqdn
import shutil
from cubicweb import devtools # setup import machinery
from cubes.narval.testutils import NarvalBaseTC
from narvalbot import main

HOSTNAME = getfqdn()
TEMP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

def create_tmp_file(dir=TEMP_DIR):
    file_desc, file_path = tempfile.mkstemp(dir=dir, suffix='.tmp')
    handler = open(file_path, "w")
    handler.write("This is a test for Narval move")
    handler.close()
    os.close(file_desc)
    return file_path

class ActionCpMoveFile(NarvalBaseTC):
    """Test for cp/mv operation recipes (single file)"""

    def setUp(self):
        super(ActionCpMoveFile, self).setUp()
        self.src_path = create_tmp_file()
        self.dest_path = tempfile.mkdtemp(dir=TEMP_DIR)

    def tearDown(self):
        if os.path.exists(self.src_path):
            os.remove(self.src_path)
        if os.path.exists(self.dest_path):
            shutil.rmtree(self.dest_path)

    def assert_copy_recipe(self, recipe):
        dest_file = os.path.join(self.dest_path, os.path.basename(self.src_path))
        self.assertFalse(os.path.exists(dest_file))
        self.run_recipe(recipe)
        self.assertTrue(os.path.exists(self.src_path))
        self.assertTrue(os.path.exists(dest_file))

    def assert_move_recipe(self, recipe):
        dest_file = os.path.join(self.dest_path, os.path.basename(self.src_path))
        self.assertFalse(os.path.exists(dest_file))
        self.run_recipe(recipe)
        self.assertFalse(os.path.exists(self.src_path))
        self.assertTrue(os.path.exists(dest_file))

    def _move_cp_recipe(self, action, arguments):
        recipe = self.req.create_entity('Recipe', name=u'action.%s' % action)
        action = recipe.add_step(u'action', action, initial=True, final=True,
                                 arguments=arguments)
        action.add_input(u'path_src', u'elmt.type == "package"')
        action.add_input(u'path_dest', u'elmt.type == "repo"')
        return recipe

    def do_test(self, action, src_host='', dest_host=''):
        if os.environ.get('APYCOT_ROOT') and (src_host or dest_host):
            self.skipTest('not executed under apycot')
        if src_host:
            file_src = 'FilePath("%s", host="%s", type="package")' % (self.src_path, src_host)
        else:
            file_src = 'FilePath("%s", type="package")' % self.src_path
        if dest_host:
            file_dest = 'FilePath("%s", host="%s", type="repo")' % (self.dest_path, dest_host)
        else:
            file_dest = 'FilePath("%s", type="repo")' % self.dest_path
        recipe = self._move_cp_recipe(u'basic.%s' % action,
                                      u'%s\n%s' % (file_src, file_dest))
        getattr(self, "assert_%s_recipe" % action)(recipe)

    def test_action_copy_local2local(self):
        self.do_test("copy")

    def test_action_copy_local2distant(self):
        self.do_test("copy", dest_host=HOSTNAME)

    def test_action_copy_distant2distant(self):
        self.do_test("copy", src_host=HOSTNAME, dest_host=HOSTNAME)

    def test_action_copy_distant2local(self):
        self.do_test("copy", src_host=HOSTNAME)

    def test_action_move_local2local(self):
        self.do_test("move")

    def test_action_move_local2distant(self):
        self.skipTest("unable to remove distant file(s)")
        self.do_test("move", dest_host=HOSTNAME)

    def test_action_move_distant2distant(self):
        self.skipTest("unable to remove distant file(s)")
        self.do_test("move", src_host=HOSTNAME, dest_host=HOSTNAME)

    def test_action_move_distant2local(self):
        self.skipTest("unable to remove distant file(s)")
        self.do_test("move", src_host=HOSTNAME)


class ActionCpMoveFiles(ActionCpMoveFile):
    """Test for cp/mv operation recipes (using glob)"""

    def setUp(self):
        NarvalBaseTC.setUp(self)
        self.dest_path = tempfile.mkdtemp(dir=TEMP_DIR)
        self.src_paths = [create_tmp_file() for __i in xrange(3)]
        self.src_path = os.path.join(TEMP_DIR, '*.tmp')

    def tearDown(self):
        for src_path in self.src_paths:
            if os.path.exists(self.src_path):
                os.remove(self.src_path)
        if os.path.exists(self.dest_path):
            shutil.rmtree(self.dest_path)

    def assert_copy_recipe(self, recipe):
        dest_files = [os.path.join(self.dest_path, os.path.basename(src_path))
                      for src_path in self.src_paths]
        for dest_file in dest_files:
            self.assertFalse(os.path.exists(dest_file))
        self.run_recipe(recipe)
        for src_file in self.src_paths:
            self.assertTrue(os.path.exists(src_path))
        for dest_file in dest_files:
            self.assertTrue(os.path.exists(dest_file))


    def assert_move_recipe(self, recipe):
        dest_files = [os.path.join(self.dest_path, os.path.basename(src_path))
                      for src_path in self.src_paths]
        for dest_file in dest_files:
            self.assertFalse(os.path.exists(dest_file))
        self.run_recipe(recipe)
        for src_file in self.src_paths:
            self.assertFalse(os.path.exists(src_path))
        for dest_file in dest_files:
            self.assertTrue(os.path.exists(dest_file))

class ActionCpMoveFromDir(ActionCpMoveFile):
    """Test for cp/mv operation recipes (using glob and directories)"""

    def setUp(self):
        NarvalBaseTC.setUp(self)
        self.src_folder = tempfile.mkdtemp(dir=TEMP_DIR, suffix='.d')
        self.dest_path = tempfile.mkdtemp(dir=TEMP_DIR)
        # simple files
        self.src_paths = [create_tmp_file(dir=self.src_folder)
                          for __i in xrange(3)]
        self.src_path = os.path.join(TEMP_DIR, 'tmp*.d')

    def assert_copy_recipe(self, recipe):
        dest_files = [os.path.join(self.dest_path,
                                   os.path.basename(self.src_folder),
                                   os.path.basename(src_path))
                      for src_path in self.src_paths]
        for dest_file in dest_files:
            self.assertFalse(os.path.exists(dest_file))
        self.run_recipe(recipe)
        for src_file in self.src_paths:
            self.assertTrue(os.path.exists(src_path))
        for dest_file in dest_files:
            self.assertTrue(os.path.exists(dest_file))

    def assert_move_recipe(self, recipe):
        dest_files = [os.path.join(self.dest_path,
                                   os.path.basename(self.src_folder),
                                   os.path.basename(src_path))
                      for src_path in self.src_paths]
        for dest_file in dest_files:
            self.assertFalse(os.path.exists(dest_file))
        self.run_recipe(recipe)
        for src_file in self.src_paths:
            self.assertFalse(os.path.exists(src_path))
        for dest_file in dest_files:
            self.assertTrue(os.path.exists(dest_file))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
