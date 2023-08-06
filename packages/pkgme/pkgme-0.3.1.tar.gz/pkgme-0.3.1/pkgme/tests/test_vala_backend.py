#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
#
# © 2010 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors: Michael Terry <michael.terry@canonical.com>
# =====================================================================

import os

from fixtures import TestWithFixtures
from testtools import TestCase

from pkgme.backend import ExternalHelpersBackend, get_backend_dir
from pkgme.testing import CommandRequiredTestCase, TempdirFixture


backend_dir = get_backend_dir(__file__, 'vala')


class ValaBackendTests(TestCase, TestWithFixtures, CommandRequiredTestCase):

    def setUp(self):
        super(ValaBackendTests, self).setUp()
        self.tempdir = self.useFixture(TempdirFixture())

    def get_backend(self):
        return ExternalHelpersBackend("vala", backend_dir)

    def get_info(self):
        backend = self.get_backend()
        return backend.get_info(self.tempdir.path)

    def test_want_zero_deep(self):
        self.tempdir.create_file("configure.ac", "")
        self.tempdir.create_file("main.vala", "")
        backend = self.get_backend()
        self.assertEqual((20, None), backend.want(self.tempdir.path))

    def test_want_one_deep(self):
        self.tempdir.create_file("configure.ac", "")
        self.tempdir.create_file(os.path.join("one", "main.vala"), "")
        backend = self.get_backend()
        self.assertEqual((20, None), backend.want(self.tempdir.path))

    def test_want_two_deep(self):
        self.tempdir.create_file("configure.ac", "")
        self.tempdir.create_file(
            os.path.join("one", "two", "main.vala"), "")
        backend = self.get_backend()
        self.assertEqual((0, None), backend.want(self.tempdir.path))

    def test_want_without_configure_ac(self):
        self.tempdir.create_file("main.vala", "")
        backend = self.get_backend()
        self.assertEqual((0, None), backend.want(self.tempdir.path))

    def test_want_with_configure_in(self):
        self.tempdir.create_file("configure.in", "")
        self.tempdir.create_file("main.vala", "")
        backend = self.get_backend()
        self.assertEqual((20, None), backend.want(self.tempdir.path))

    def test_architecture(self):
        info = self.get_info()
        self.assertEqual(
            {"architecture": "any"}, info.get_all(["architecture"]))

    def test_buildsystem(self):
        info = self.get_info()
        self.assertEqual(
            {"buildsystem": "autoconf"}, info.get_all(["buildsystem"]))

    def test_build_depends(self):
        self.skipTestIfCommandNotExecutable('vala-dep-scanner')
        self.tempdir.create_file("main.vala", "Gtk.Window win;")
        info = self.get_info()
        self.assertEqual(
            {"build_depends": "libgtk3.0-dev, valac"},
            info.get_all(["build_depends"]))

    def test_depends(self):
        info = self.get_info()
        self.assertEqual(
            {"depends": "${shlibs:Depends}"}, info.get_all(["depends"]))

    def test_homepage(self):
        self.tempdir.create_file(
            "configure.ac",
            "AC_INIT([Example Project],[1.0],[http://bugs.example.com/],"
            "[example-project], [http://example.com/] )")
        info = self.get_info()
        self.assertEqual(
            {"homepage": "http://example.com/"}, info.get_all(["homepage"]))

    def test_homepage_none(self):
        self.tempdir.create_file(
            "configure.ac",
            "AC_INIT([Example Project],[1.0],[http://bugs.example.com/],"
            "[example-project])")
        info = self.get_info()
        self.assertEqual(
            {"homepage": ""}, info.get_all(["homepage"]))

    def test_package_name(self):
        self.tempdir.create_file(
            "configure.ac",
            "AC_INIT([GNU Example Project],[1.0],[http://bugs.example.com/],"
            "[co ol-proj],[http://example.com/])")
        info = self.get_info()
        self.assertEqual(
            {"package_name": "co ol-proj"}, info.get_all(["package_name"]))

    def test_package_name_none(self):
        self.tempdir.create_file(
            "configure.ac",
            "AC_INIT( [GNU Example Project] , [1.0],"
            "[http://bugs.example.com/])")
        info = self.get_info()
        self.assertEqual(
            {"package_name": "example-project"}, info.get_all(["package_name"]))
