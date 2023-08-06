from fixtures import TestWithFixtures
from testtools import TestCase

from pkgme.backend import ExternalHelpersBackend, get_backend_dir
from pkgme.testing import TempdirFixture


backend_dir = get_backend_dir(__file__, 'python')


class PythonBackendTests(TestCase, TestWithFixtures):

    def test_want_with_setup_py(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('setup.py')
        backend = ExternalHelpersBackend("python", backend_dir)
        self.assertEqual((20, None), backend.want(tempdir.path))

    def test_want_without_setup_py(self):
        tempdir = self.useFixture(TempdirFixture())
        backend = ExternalHelpersBackend("python", backend_dir)
        self.assertEqual(
            (0, "Couldn't find a setup.py"), backend.want(tempdir.path))

    def test_all_info(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.create_file('setup.py', """from distutils.core import setup

setup(name="foo")
""")
        backend = ExternalHelpersBackend("python", backend_dir)
        info = backend.get_info(tempdir.path)
        self.assertEqual(
            {"package_name": "foo"}, info.get_all(["package_name"]))
