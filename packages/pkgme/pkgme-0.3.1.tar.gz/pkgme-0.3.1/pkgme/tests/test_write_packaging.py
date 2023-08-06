import os

from testtools import TestCase

from pkgme import write_packaging
from pkgme.backend import StaticBackend
from pkgme.info_elements import (
    Architecture,
    Description,
    Maintainer,
    PackageName,
    Version,
    )
from pkgme.package_files import Control, DEBIAN_DIR
from pkgme.project_info import DictInfo
from pkgme.testing import (
    ControlSourceStanzaHasField,
    StaticLoaderFixture,
    TempdirFixture,
    )


class WritePackagingTests(TestCase):

    def assert_control_has_source_name(self, name, tempdir):
        control_path = os.path.join(
            tempdir.path, DEBIAN_DIR, Control.filename)
        with open(control_path) as f:
            control_contents = f.read()
        self.assertThat(
            control_contents,
            ControlSourceStanzaHasField("Source", name))

    def make_info(self, name):
        info = DictInfo(
            {
                PackageName.name: name,
                Maintainer.name: self.getUniqueString(),
                Architecture.name: "all",
                Description.name: self.getUniqueString(),
                Version.name: "1",
            })
        return info

    def test_write_packaging(self):
        name = PackageName.clean(self.getUniqueString())
        info = self.make_info(name)
        tempdir = self.useFixture(TempdirFixture())
        backend = StaticBackend(
            self.getUniqueString(), 10, info, expected_path=tempdir.path)
        self.useFixture(StaticLoaderFixture([backend]))
        write_packaging(tempdir.path)
        self.assert_control_has_source_name(name, tempdir)

    def test_write_packaging_passes_allowed_backend_names(self):
        name = PackageName.clean(self.getUniqueString())
        other_name = name+"WRONG"
        info1 = self.make_info(name)
        info2 = self.make_info(other_name)
        tempdir = self.useFixture(TempdirFixture())
        backend1 = StaticBackend(
            self.getUniqueString(), 10, info1, expected_path=tempdir.path)
        backend2 = StaticBackend(
            self.getUniqueString(), 20, info2)
        self.useFixture(StaticLoaderFixture(
            [backend1, backend2]))
        write_packaging(tempdir.path,
                allowed_backend_names=[backend1.name])
        self.assert_control_has_source_name(name, tempdir)
