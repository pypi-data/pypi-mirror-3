import json
import sys

from fixtures import TestWithFixtures
from testtools import TestCase

from pkgme.project_info import (
    DictInfo,
    FallbackInfo,
    MultipleExternalHelpersInfo,
    SingleExternalHelperInfo,
    )
from pkgme.run_script import (
    ScriptFailed,
    ScriptPermissionDenied,
    )
from pkgme.testing import (
    ExecutableFileFixture,
    FileFixture,
    TempdirFixture,
    )


class DictInfoTests(TestCase):

    def test_get_one(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info = DictInfo({key: value})
        self.assertEqual({key: value}, info.get_all([key]))

    def test_get_multiple(self):
        key1 = self.getUniqueString()
        value1 = self.getUniqueString()
        key2 = self.getUniqueString()
        value2 = self.getUniqueString()
        info = DictInfo({key1: value1, key2: value2})
        self.assertEqual(
            {key1: value1, key2: value2}, info.get_all([key1, key2]))

    def test_get_missing(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info = DictInfo({key: value})
        self.assertEqual({}, info.get_all(self.getUniqueString()))

    def test_get_one_missing(self):
        key1 = self.getUniqueString()
        value1 = self.getUniqueString()
        key2 = self.getUniqueString()
        info = DictInfo({key1: value1})
        self.assertEqual(
            {key1: value1}, info.get_all([key1, key2]))


class FallbackInfoTests(TestCase):

    def test_uses_first(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info1 = DictInfo({key: value})
        info2 = DictInfo({})
        info = FallbackInfo(info1, info2)
        self.assertEqual({key: value}, info.get_all([key]))

    def test_falls_back_to_second(self):
        key = self.getUniqueString()
        value = self.getUniqueString()
        info1 = DictInfo({})
        info2 = DictInfo({key: value})
        info = FallbackInfo(info1, info2)
        self.assertEqual({key: value}, info.get_all([key]))

    def test_uses_first_when_second_present(self):
        key = self.getUniqueString()
        value1 = self.getUniqueString()
        value2 = self.getUniqueString()
        info1 = DictInfo({key: value1})
        info2 = DictInfo({key: value2})
        info = FallbackInfo(info1, info2)
        self.assertEqual({key: value1}, info.get_all([key]))


class MultipleExternalHelpersInfoTests(TestCase, TestWithFixtures):

    def test_missing_helper(self):
        tempdir = self.useFixture(TempdirFixture())
        info = MultipleExternalHelpersInfo(tempdir.path, tempdir.path)
        key = self.getUniqueString()
        self.assertEqual({key: None}, info.get_all([key]))

    def test_uses_output(self):
        tempdir = self.useFixture(TempdirFixture())
        script_name = self.getUniqueString()
        script_path = tempdir.abspath(script_name)
        value = self.getUniqueString()
        script = "#!/bin/sh\necho %s\n" % value
        self.useFixture(ExecutableFileFixture(script_path, script))
        info = MultipleExternalHelpersInfo(tempdir.path, tempdir.path)
        self.assertEqual({script_name: value}, info.get_all([script_name]))

    def test_script_error(self):
        tempdir = self.useFixture(TempdirFixture())
        script_name = self.getUniqueString()
        script_path = tempdir.abspath(script_name)
        script = "#!/bin/sh\nexit 1\n"
        self.useFixture(ExecutableFileFixture(script_path, script))
        info = MultipleExternalHelpersInfo(tempdir.path, tempdir.path)
        self.assertRaises(
            ScriptFailed, info.get_all, [script_name])

    def test_script_permission_denied(self):
        """Check the exception raised when the info script isn't executable."""
        tempdir = self.useFixture(TempdirFixture())
        script_name = self.getUniqueString()
        script_path = tempdir.abspath(script_name)
        script = "#!/bin/sh\nexit 0\n"
        self.useFixture(FileFixture(script_path, script))
        info = MultipleExternalHelpersInfo(tempdir.path, tempdir.path)
        self.assertRaises(
            ScriptPermissionDenied, info.get_all, [script_name])

    def test_correct_working_directory(self):
        script_tempdir = self.useFixture(TempdirFixture())
        cwd_tempdir = self.useFixture(TempdirFixture())
        script_name = self.getUniqueString()
        script_path = script_tempdir.abspath(script_name)
        script = "#!%s\nimport os\nprint os.getcwd()\n" % sys.executable
        self.useFixture(ExecutableFileFixture(script_path, script))
        info = MultipleExternalHelpersInfo(
            script_tempdir.path, cwd_tempdir.path)
        self.assertEqual(
            {script_name: cwd_tempdir.path}, info.get_all([script_name]))


class SingleExternalHelperInfoTests(TestCase, TestWithFixtures):

    def test_uses_output(self):
        tempdir = self.useFixture(TempdirFixture())
        script_name = self.getUniqueString()
        script_path = tempdir.abspath(SingleExternalHelperInfo.INFO_SCRIPT_NAME)
        value = self.getUniqueString()
        script = '#!%s\nimport json\nprint json.dumps(%s)\n' % (
            sys.executable, json.dumps({script_name: value}))
        self.useFixture(ExecutableFileFixture(script_path, script))
        info = SingleExternalHelperInfo(tempdir.path, tempdir.path)
        self.assertEqual({script_name: value}, info.get_all([script_name]))

    def test_when_script_gives_invalid_json_output(self):
        """Test when the script doesn't produce valid JSON.

        As this is a problem with the backend we expect an AssertionError
        with an intelligible message.
        """
        tempdir = self.useFixture(TempdirFixture())
        script_path = tempdir.abspath(SingleExternalHelperInfo.INFO_SCRIPT_NAME)
        value = self.getUniqueString()
        script = '#!%s\nprint "}Nonsense"' % (sys.executable, )
        self.useFixture(ExecutableFileFixture(script_path, script))
        info = SingleExternalHelperInfo(tempdir.path, tempdir.path)
        e = self.assertRaises(AssertionError, info.get_all, [])
        self.assertEquals("%s didn't return valid JSON: '}Nonsense\\n'"
                % (script_path, ), str(e))

    def test_passes_input(self):
        tempdir = self.useFixture(TempdirFixture())
        script_name = self.getUniqueString()
        script_path = tempdir.abspath(SingleExternalHelperInfo.INFO_SCRIPT_NAME)
        value = self.getUniqueString()
        script = """#!%s
import json
import sys

raw_input = sys.stdin.read()
input = json.loads(raw_input)
if input != ["%s"]:
    print json.dumps({"%s": "Did not pass correct input: %%s" %% raw_input})
else:
    print json.dumps({"%s": "%s"})
""" % (sys.executable, script_name, script_name, script_name, value)
        self.useFixture(ExecutableFileFixture(script_path, script))
        info = SingleExternalHelperInfo(tempdir.path, tempdir.path)
        self.assertEqual({script_name: value}, info.get_all([script_name]))

    def test_correct_working_directory(self):
        script_tempdir = self.useFixture(TempdirFixture())
        cwd_tempdir = self.useFixture(TempdirFixture())
        script_name = self.getUniqueString()
        script_path = script_tempdir.abspath(SingleExternalHelperInfo.INFO_SCRIPT_NAME)
        script = """#!%s
import os
import json
print json.dumps({"%s": os.getcwd()})
""" % (sys.executable, script_name)
        self.useFixture(ExecutableFileFixture(script_path, script))
        info = SingleExternalHelperInfo(
            script_tempdir.path, cwd_tempdir.path)
        self.assertEqual(
            {script_name: cwd_tempdir.path}, info.get_all([script_name]))
