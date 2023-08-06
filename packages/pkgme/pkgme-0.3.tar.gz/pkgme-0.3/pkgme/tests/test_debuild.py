import os
import tarfile

from testtools import TestCase

from pkgme.debuild import (
    _find_binary_files_in_dir,
    build_debian_source_include_binaries_content,
    build_orig_tar_gz,
    )
from pkgme.testing import (
    TempdirFixture,
    )


class DebianTempDirFixture(TempdirFixture):
    """A temp directory with a "testpkg" directory that contains
       a skeleton dir debian/ structure
    """

    def setUp(self, with_binary_data=False):
        super(DebianTempDirFixture, self).setUp()
        self.pkgdir = os.path.join(self.path, "testpkg")
        self.icon_path = os.path.join(self.pkgdir, "debian", "icons")
        self.debian_source_path = os.path.join(self.pkgdir, "debian", "source")
        # setup fake env
        os.makedirs(self.icon_path)
        os.makedirs(self.debian_source_path)


class BuildTarTestCase(TestCase):

    def test_build_orig_tar_gz(self):
        tempdir = self.useFixture(DebianTempDirFixture())
        changelog_path = os.path.join(tempdir.pkgdir, "debian", "changelog")
        with open(changelog_path, "w") as f:
            f.write("""
testpkg (0.1) unstable; urgency=low

  * some changes

 -- Some Guy <foo@example.com>  Thu, 19 Apr 2012 10:53:30 +0200
""")
        with open(os.path.join(tempdir.pkgdir, "canary"), "w") as f:
            f.write("pieep")
        # build it
        result_path = build_orig_tar_gz(tempdir.pkgdir)
        # verify
        self.assertEqual(
            "testpkg_0.1.orig.tar.gz", os.path.basename(result_path))
        with tarfile.open(result_path) as f:
            self.assertEqual(
                ["testpkg-0.1", "testpkg-0.1/canary"], 
                [m.name for m in f.getmembers()])


class BuildIncludeBinariesTestCase(TestCase):

    def _make_icons(self, tempdir):
        for icon_name in ["foo.png", "bar.png"]:
            with open(os.path.join(tempdir.icon_path, icon_name), "w") as f:
                f.write("x\0x")

    def test_find_binary_files(self):
        tempdir = self.useFixture(DebianTempDirFixture())
        self._make_icons(tempdir)
        bin_files = _find_binary_files_in_dir(os.path.join(
                tempdir.pkgdir, "debian"))
        self.assertEqual(
            ["icons/foo.png", "icons/bar.png"], bin_files)

    def test_build_debian_source_include_binaries_content(self):
        tempdir = self.useFixture(DebianTempDirFixture())
        self._make_icons(tempdir)
        build_debian_source_include_binaries_content(tempdir.pkgdir)
        self.assertEqual(
            "debian/icons/foo.png\ndebian/icons/bar.png", 
            open(os.path.join(tempdir.debian_source_path, "include-binaries")).read())

