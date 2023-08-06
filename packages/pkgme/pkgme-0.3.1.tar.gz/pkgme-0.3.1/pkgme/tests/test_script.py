import json
import os
import pkg_resources
from StringIO import StringIO

from fixtures import (
    EnvironmentVariableFixture,
    MonkeyPatch,
    )
from testtools import TestCase
from testtools.matchers import (
    DirContains,
    DirExists,
    Not,
    )

from pkgme.backend import (
    BackendSelector,
    StaticBackend,
    )
from pkgme.bin.main import get_all_info
from pkgme.info_elements import (
    PackageName,
    )
from pkgme.project_info import DictInfo
from pkgme.testing import (
    TempdirFixture,
    )


class ScriptTests(TestCase):
    """Smoke tests for the top-level pkgme script."""

    def setUp(self):
        super(ScriptTests, self).setUp()
        # The DEBEMAIL environment variable is consulted when the
        # pacakging is written, so set it to a known value for proper
        # isolation
        debemail = 'Dude <dude@example.com>'
        self.useFixture(EnvironmentVariableFixture('DEBEMAIL', debemail))

    def run_script(self, cwd, argv=None):
        if argv is None:
            argv = []
        ep = pkg_resources.load_entry_point(
            "pkgme", "console_scripts", "pkgme")
        stderr = StringIO()
        stdout = StringIO()
        with MonkeyPatch('sys.stdout', stdout):
            with MonkeyPatch('sys.stderr', stderr):
                try:
                    ep(argv=argv, target_dir=cwd, interactive=False)
                except SystemExit:
                    # If the script exits due to a failure, we don't want to exit
                    # the whole test suite.
                    pass
        self.assertEqual('', stderr.getvalue())
        return stdout.getvalue()

    def create_marker_file(self, tempdir, prefix=None):
        """Create the file that triggers the dummy backend for testing."""
        path = "is_pkgme_test"
        if prefix is not None:
            path = os.path.join(prefix, path)
        tempdir.create_file(path, "")

    def test_writes_files(self):
        tempdir = self.useFixture(TempdirFixture())
        self.create_marker_file(tempdir)
        self.run_script(tempdir.path)
        self.assertThat(tempdir.abspath("debian"), DirExists())

    def test_builds_source_package(self):
        tempdir = self.useFixture(TempdirFixture())
        self.create_marker_file(tempdir, prefix="foo")
        self.run_script(tempdir.abspath('foo'))
        self.assertThat(tempdir.path, DirContains(
            ["foo_0.0.0.orig.tar.gz",
             "foo_0.0.0.debian.tar.gz",
             "foo_0.0.0.dsc",
             "foo_0.0.0_source.build",
             "foo_0.0.0_source.changes",
             "foo",
             ]))

    def test_nobuild_doesnt_builds_source_package(self):
        tempdir = self.useFixture(TempdirFixture())
        self.create_marker_file(tempdir, prefix="foo")
        self.run_script(tempdir.abspath('foo'), ['--nobuild'])
        self.assertThat(tempdir.path, DirContains(["foo"]))

    def test_which_backends(self):
        tempdir = self.useFixture(TempdirFixture())
        self.create_marker_file(tempdir)
        output = self.run_script(tempdir.path, ['--which-backends'])
        self.assertEqual('dummy (100)\n', output)
        self.assertThat(tempdir.abspath("debian"), Not(DirExists()))

    def test_dump(self):
        tempdir = self.useFixture(TempdirFixture())
        self.create_marker_file(tempdir)
        all_info = get_all_info(tempdir.path)
        clean_info = json.loads(json.dumps(all_info))
        output = self.run_script(tempdir.path, ['--dump'])
        self.assertEqual(clean_info, json.loads(output))
        self.assertThat(tempdir.abspath("debian"), Not(DirExists()))

    def test_nosign(self):
        tempdir = self.useFixture(TempdirFixture())
        self.create_marker_file(tempdir, prefix='foo')
        self.run_script(tempdir.abspath('foo'), ['--nosign'])
        changes_file = os.path.join(tempdir.path,
                                    "foo_0.0.0_source.changes")
        signature = open(changes_file)
        sig_text = signature.readlines()
        signature.close()
        self.assertNotIn(sig_text, "-----BEGIN PGP SIGNATURE-----\n")

class GetAllInfoTests(TestCase):

    def test_eligible_backends(self):
        info = DictInfo({})
        backend1 = StaticBackend(self.getUniqueString(), 5, info)
        backend2 = StaticBackend(self.getUniqueString(), 10, info)
        selector = BackendSelector([backend1, backend2])
        path = self.getUniqueString()
        info = get_all_info(path, selector)
        self.assertEqual(
            [(10, backend2.name), (5, backend1.name)], info['eligible_backends'])

    def test_selected_backend(self):
        info = DictInfo({})
        backend1 = StaticBackend(self.getUniqueString(), 5, info)
        backend2 = StaticBackend(self.getUniqueString(), 10, info)
        selector = BackendSelector([backend1, backend2])
        path = self.getUniqueString()
        info = get_all_info(path, selector)
        self.assertEqual(backend2.name, info['selected_backend'])

    def test_all_info(self):
        info = {PackageName.name: self.getUniqueString()}
        backend = StaticBackend(self.getUniqueString(), 5, DictInfo(info))
        selector = BackendSelector([backend])
        path = self.getUniqueString()
        all_info = get_all_info(path, selector)
        del all_info['eligible_backends']
        del all_info['selected_backend']
        self.assertEqual(info, all_info)
