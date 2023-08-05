# Standard library imports
import unittest
import sys
from StringIO import StringIO
import os
import tempfile
import shutil

# Custom library imports
import simple
import list_participants
import marginal_prices


class ScriptSandbox(unittest.TestCase):
    def setUp(self):
        self._old_stdout = sys.stdout
        self._old_stderr = sys.stderr
        self._old_cwd = os.getcwd()

        self._tempdir = tempfile.mkdtemp()
        os.chdir(self._tempdir)
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        def errorhander(function, path, execinfo):
            raise OSError('Cannot delete tempfile at ' + path)

        stdout = sys.stdout
        stderr = sys.stderr

        sys.stdout = self._old_stdout
        sys.stderr = self._old_stderr
        os.chdir(self._old_cwd)

        # Delete temp directory
        shutil.rmtree(self._tempdir, onerror = errorhander)


class TestSimple(ScriptSandbox):
    def test_main(self):
        self.assertEquals(simple.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 50)


class TestListParticipants(ScriptSandbox):
    def test_main(self):
        self.assertEquals(list_participants.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 50)


class TestMarginalPrices(ScriptSandbox):
    def test_main(self):
        self.assertEquals(marginal_prices.main(), 0)

        self.assertTrue(len(sys.stdout.getvalue()) > 100)


if __name__ == '__main__':
    unittest.main()

