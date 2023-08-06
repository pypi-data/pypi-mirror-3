import os
import sys

from fixtures import TestWithFixtures
from testtools import TestCase

from pkgme.backend import (
    Backend,
    BackendSelector,
    EXTERNAL_BACKEND_PATHS,
    ExternalHelpersBackend,
    ExternalHelpersBackendLoader,
    get_default_loader,
    get_default_selector,
    get_info_for,
    NoBackend,
    NoEligibleBackend,
    StaticBackend,
    StaticLoader,
    WantError,
    )
from pkgme.project_info import (
    MultipleExternalHelpersInfo,
    SingleExternalHelperInfo,
    )
from pkgme.run_script import ScriptUserError
from pkgme.testing import (
    ExecutableFileFixture,
    FileFixture,
    StaticLoaderFixture,
    TempdirFixture,
    )


class TestBackend(TestCase):

    def test_describe(self):
        # The default describe() just returns the name.
        backend = Backend(self.getUniqueString())
        self.assertEqual(backend.name, backend.describe())


class ExternalHelpersBackendTests(TestCase, TestWithFixtures):

    def make_want_script(self, script, executable=True):
        tempdir = self.useFixture(TempdirFixture())
        script_name = ExternalHelpersBackend.WANT_SCRIPT_NAME
        script_path = os.path.join(tempdir.path, script_name)
        if executable:
            cls = ExecutableFileFixture
        else:
            cls = FileFixture
        self.useFixture(cls(script_path, script))
        return tempdir

    def test_describe(self):
        backend = ExternalHelpersBackend(
            self.getUniqueString(), self.getUniqueString())
        self.assertEqual(
            "%s (%s)" % (backend.name, backend.basepath), backend.describe())

    def test_want_runs_script(self):
        script = "#!/bin/sh\necho 10\n"
        tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(self.getUniqueString(), tempdir.path)
        self.assertEqual((10, None), backend.want(tempdir.path))

    def test_empty_want_script(self):
        script = "#!/bin/sh\n"
        tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(self.getUniqueString(), tempdir.path)
        e = self.assertRaises(WantError, backend.want, tempdir.path)
        self.assertEqual(
            "Backend %s (%s) returned invalid JSON from 'want' script: ''"
            % (backend.name, tempdir.path),
            str(e))

    def test_want_script_with_reason(self):
        reason = self.getUniqueString()
        script = (
            "#!/usr/bin/python\n"
            "import json\n"
            "print json.dumps({'score': 10, 'reason': %r})"
            % (reason,))
        tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(self.getUniqueString(), tempdir.path)
        self.assertEqual((10, reason), backend.want(tempdir.path))

    def test_want_script_with_reason_and_bad_score(self):
        reason = self.getUniqueString()
        script = (
            "#!/usr/bin/python\n"
            "import json\n"
            "print json.dumps({'score': 'foo', 'reason': '%s'})"
            % (reason,))
        name = self.getUniqueString()
        tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(WantError, backend.want, tempdir.path)
        self.assertEqual(
            "Backend %s (%s) returned non-integer score from '%s' "
            "script: u'foo'"
            % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME),
            str(e))

    def test_want_script_with_no_score(self):
        reason = self.getUniqueString()
        script = (
            "#!/usr/bin/python\n"
            "import json\n"
            "print json.dumps({'reason': '%s'})"
            % (reason,))
        name = self.getUniqueString()
        tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(WantError, backend.want, tempdir.path)
        self.assertEqual(
            "Backend %s (%s) did not return a score from '%s' script: %s"
            % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME,
               "{u'reason': u'%s'}" % (reason,)),
            str(e))

    def test_want_script_with_valid_meaningless_json(self):
        script = (
            "#!/usr/bin/python\n"
            "import json\n"
            "print json.dumps(['what', 'could', 'this', 'mean'])")
        name = self.getUniqueString()
        tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(WantError, backend.want, tempdir.path)
        self.assertEqual(
            "Backend %s (%s) returned invalid score from '%s' script: "
            "[u'what', u'could', u'this', u'mean']"
            % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME),
            str(e))

    def test_want_script_with_missing_reason(self):
        script = (
            "#!/usr/bin/python\n"
            "import json\n"
            "print json.dumps({'score': 10})")
        tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(self.getUniqueString(), tempdir.path)
        self.assertEqual((10, None), backend.want(tempdir.path))

    def test_missing_want_script(self):
        tempdir = self.useFixture(TempdirFixture())
        name = self.getUniqueString()
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(AssertionError, backend.want, tempdir.path)
        self.assertEqual(
            "Backend %s (%s) has no '%s' script"
            % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME),
            str(e))

    def test_want_script_not_executable(self):
        """Check the message when the want script isn't executable."""
        script = "#!/bin/sh\necho foo\n"
        tempdir = self.make_want_script(script, executable=False)
        name = self.getUniqueString()
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(AssertionError, backend.want, tempdir.path)
        self.assertEqual(
            "Backend %s (%s) has no usable '%s' script: permission denied "
            "trying to execute %s/want, is it executable?"
            % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME,
                tempdir.path),
            str(e))

    def test_want_script_returns_non_integer(self):
        script = "#!/bin/sh\necho foo\n"
        tempdir = self.make_want_script(script)
        name = self.getUniqueString()
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(WantError, backend.want, tempdir.path)
        self.assertEqual(
            "Backend %s (%s) returned invalid JSON from '%s' script: 'foo'"
            % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME),
            str(e))

    def test_want_script_returns_user_error(self):
        script = "#!/bin/sh\necho foo\nexit %s" % (
            ScriptUserError.RETURN_CODE,)
        tempdir = self.make_want_script(script)
        name = self.getUniqueString()
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(ScriptUserError, backend.want, tempdir.path)
        self.assertEqual("foo\n", str(e))

    def test_want_script_returns_list(self):
        script = (
            "#!/usr/bin/python\n"
            "import json\n"
            "print json.dumps([1, 2, 3])")
        tempdir = self.make_want_script(script)
        name = self.getUniqueString()
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(WantError, backend.want, tempdir.path)
        self.assertEqual(
            ("Backend %s (%s) returned invalid score "
             "from '%s' script: [1, 2, 3]"
             % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME)),
            str(e))

    def test_want_script_returns_null(self):
        script = (
            "#!/usr/bin/python\n"
            "import json\n"
            "print json.dumps(None)")
        tempdir = self.make_want_script(script)
        name = self.getUniqueString()
        backend = ExternalHelpersBackend(name, tempdir.path)
        e = self.assertRaises(WantError, backend.want, tempdir.path)
        self.assertEqual(
            ("Backend %s (%s) returned invalid score "
             "from '%s' script: None"
             % (name, tempdir.path, ExternalHelpersBackend.WANT_SCRIPT_NAME)),
            str(e))

    def test_want_script_run_in_correct_dir(self):
        cwd_tempdir = self.useFixture(TempdirFixture())
        script = """#!%s
import os
if os.getcwd() != '%s':
    print "Backend was called in %%s rather than %%s" %% (os.getcwd(), '%s')
else:
    print 10
""" % (sys.executable, cwd_tempdir.path, cwd_tempdir.path)
        backend_tempdir = self.make_want_script(script)
        backend = ExternalHelpersBackend(
            self.getUniqueString(), backend_tempdir.path)
        self.assertEqual((10, None), backend.want(cwd_tempdir.path))

    def test_get_info_with_multiple(self):
        helpers_path = self.getUniqueString()
        cwd_path = self.getUniqueString()
        backend = ExternalHelpersBackend(self.getUniqueString(), helpers_path)
        project_info = backend.get_info(cwd_path)
        self.assertIsInstance(project_info, MultipleExternalHelpersInfo)
        self.assertEqual(helpers_path, project_info.basepath)
        self.assertEqual(cwd_path, project_info.cwd)

    def test_get_info_with_single(self):
        helpers_tempdir = self.useFixture(TempdirFixture())
        info_script_path = os.path.join(
            helpers_tempdir.path,
            SingleExternalHelperInfo.INFO_SCRIPT_NAME)
        with open(info_script_path, "w"):
            pass
        cwd_path = self.getUniqueString()
        backend = ExternalHelpersBackend(
            self.getUniqueString(), helpers_tempdir.path)
        project_info = backend.get_info(cwd_path)
        self.assertIsInstance(project_info, SingleExternalHelperInfo)
        self.assertEqual(helpers_tempdir.path, project_info.basepath)
        self.assertEqual(cwd_path, project_info.cwd)


class BackendSelectorTests(TestCase):

    def test_selects_highest_score(self):
        info1 = self.getUniqueString()
        info2 = self.getUniqueString()
        path = self.getUniqueString()
        backend1 = StaticBackend(
            self.getUniqueString(), 10, info1, expected_path=path)
        backend2 = StaticBackend(
            self.getUniqueString(), 20, info2, expected_path=path)
        backends = [backend1, backend2]
        selector = BackendSelector(backends)
        self.assertEqual(info2, selector.get_info(path))

    def test_no_backends(self):
        path = self.getUniqueString()
        selector = BackendSelector([])
        self.assertRaises(NoBackend, selector.get_info, path)

    def test_no_eligble(self):
        info = self.getUniqueString()
        path = self.getUniqueString()
        backend = StaticBackend(
            self.getUniqueString(), 0, info, expected_path=path)
        backends = [backend]
        selector = BackendSelector(backends)
        self.assertRaises(NoEligibleBackend, selector.get_info, path)

    def test_reasons_for_ineligbility(self):
        backend1 = StaticBackend('no-reason', 0, None)
        backend2 = StaticBackend(
            'a', 0, None, reason=self.getUniqueString())
        backend3 = StaticBackend(
            'b', 0, None, reason=self.getUniqueString())
        backends = [backend1, backend2, backend3]
        selector = BackendSelector(backends)
        e = self.assertRaises(
            NoEligibleBackend, selector.get_info, '/path')
        self.assertEqual(
            'No eligible backends for /path. Tried a (%s), b (%s), '
            'no-reason' % (backend2.reason, backend3.reason),
            str(e))

    def test_selects_first_name_in_tie(self):
        info1 = self.getUniqueString()
        info2 = self.getUniqueString()
        path = self.getUniqueString()
        backend1 = StaticBackend("a", 10, info1, expected_path=path)
        backend2 = StaticBackend("b", 10, info2, expected_path=path)
        backends = [backend1, backend2]
        selector = BackendSelector(backends)
        self.assertEqual(info1, selector.get_info(path))

    def test_rejects_non_allowable_backend(self):
        info1 = self.getUniqueString()
        info2 = self.getUniqueString()
        path = self.getUniqueString()
        backend1 = StaticBackend("a", 20, info1, expected_path=path)
        backend2 = StaticBackend("b", 10, info2, expected_path=path)
        backends = [backend1, backend2]
        allowed_backend_names = ["b"]
        selector = BackendSelector(backends,
                allowed_backend_names=allowed_backend_names)
        self.assertEqual(info2, selector.get_info(path))

    def test_error_contains_disallowed_backends(self):
        """The disallowed backends are part of the error.

        When backend restrictions are in effect, and
        no backend can be found, the error message
        includes an indication of backends that were disallowed.
        """
        info = self.getUniqueString()
        path = self.getUniqueString()
        backend = StaticBackend("b", 10, info, expected_path=path)
        backends = [backend]
        allowed_backend_names = ["a"]
        selector = BackendSelector(backends,
                allowed_backend_names=allowed_backend_names)
        e = self.assertRaises(NoEligibleBackend,
                selector.get_info, path)
        self.assertEqual(
            "No eligible backends for %s. Tried . The following backends "
            "were disallowed by policy: %s." % (path, backend.name),
            str(e))

    def test_list_backends_no_backends(self):
        # get_eligible_backends raises NoBackend when there are no backends found.
        path = self.getUniqueString()
        selector = BackendSelector([])
        self.assertRaises(NoBackend, selector.get_eligible_backends, path)

    def test_list_backends_no_eligible(self):
        # get_eligible_backends raises NoEligibleBackend when there are
        # backends found but none of them are eligible.
        info = self.getUniqueString()
        path = self.getUniqueString()
        backend = StaticBackend(
            self.getUniqueString(), 0, info, expected_path=path)
        backends = [backend]
        selector = BackendSelector(backends)
        self.assertRaises(NoEligibleBackend, selector.get_eligible_backends, path)

    def test_order_by_score(self):
        # get_eligible_backends returns backends sorted by score, descending.
        path = self.getUniqueString()
        backend1 = StaticBackend("a", 5, self.getUniqueString(), expected_path=path)
        backend2 = StaticBackend("b", 10, self.getUniqueString(), expected_path=path)
        backends = [backend1, backend2]
        selector = BackendSelector(backends)
        self.assertEqual(
            [(10, backend2), (5, backend1)],
            selector.get_eligible_backends(path))

    def test_order_by_name_after_score(self):
        # get_eligible_backends returns backends sorted by score, descending,
        # and then by name lexigraphically.
        path = self.getUniqueString()
        backend1 = StaticBackend("a", 5, self.getUniqueString(), expected_path=path)
        backend2 = StaticBackend("b", 10, self.getUniqueString(), expected_path=path)
        backend3 = StaticBackend("c", 10, self.getUniqueString(), expected_path=path)
        backends = [backend1, backend2, backend3]
        selector = BackendSelector(backends)
        self.assertEqual(
            [(10, backend2), (10, backend3), (5, backend1)],
            selector.get_eligible_backends(path))

    def test_ineligible_backends_excluded(self):
        # get_eligible_backends only returns backends with scores greater than zero.
        path = self.getUniqueString()
        backend1 = StaticBackend("a", 5, self.getUniqueString(), expected_path=path)
        backend2 = StaticBackend("b", 10, self.getUniqueString(), expected_path=path)
        backend3 = StaticBackend("c", 0, self.getUniqueString(), expected_path=path)
        backends = [backend1, backend2, backend3]
        selector = BackendSelector(backends)
        self.assertEqual(
            [(10, backend2), (5, backend1)],
            selector.get_eligible_backends(path))

    def test_excludes_non_allowed_backend(self):
        info1 = self.getUniqueString()
        info2 = self.getUniqueString()
        path = self.getUniqueString()
        backend1 = StaticBackend("a", 20, info1, expected_path=path)
        backend2 = StaticBackend("b", 10, info2, expected_path=path)
        backends = [backend1, backend2]
        allowed_backend_names = ["b"]
        selector = BackendSelector(backends,
                allowed_backend_names=allowed_backend_names)
        self.assertEqual(
            [(10, backend2)], selector.get_eligible_backends(path))


class ExternalHelpersBackendLoaderTests(TestCase, TestWithFixtures):

    def test_loads_no_backends(self):
        tempdir = self.useFixture(TempdirFixture())
        loader = ExternalHelpersBackendLoader([tempdir.path])
        self.assertEqual([], loader.load())

    def test_loads_from_one_dir(self):
        tempdir = self.useFixture(TempdirFixture())
        backend_name = self.getUniqueString()
        basepath = tempdir.mkdir(backend_name)
        loader = ExternalHelpersBackendLoader([tempdir.path])
        backends = loader.load()
        self.assertEqual(1, len(backends))
        self.assertIsInstance(backends[0], ExternalHelpersBackend)
        self.assertEqual(backend_name, backends[0].name)
        self.assertEqual(basepath, backends[0].basepath)

    def test_loads_from_two_dirs(self):
        tempdir1 = self.useFixture(TempdirFixture())
        tempdir2 = self.useFixture(TempdirFixture())
        backend_name1 = self.getUniqueString()
        backend_name2 = self.getUniqueString()
        tempdir1.mkdir(backend_name1)
        tempdir2.mkdir(backend_name2)
        loader = ExternalHelpersBackendLoader(
            [tempdir1.path, tempdir2.path])
        backends = loader.load()
        self.assertEqual(2, len(backends))

    def test_loads_only_one_instance_of_each_name(self):
        tempdir1 = self.useFixture(TempdirFixture())
        tempdir2 = self.useFixture(TempdirFixture())
        backend_name = self.getUniqueString()
        basepath1 = tempdir1.mkdir(backend_name)
        tempdir2.mkdir(backend_name)
        loader = ExternalHelpersBackendLoader(
            [tempdir1.path, tempdir2.path])
        backends = loader.load()
        self.assertEqual(1, len(backends))
        self.assertEqual(basepath1, backends[0].basepath)

    def test_loads_only_dirs(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch(self.getUniqueString())
        loader = ExternalHelpersBackendLoader([tempdir.path])
        self.assertEqual([], loader.load())

    def test_ignores_dotdirs(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.mkdir("." + self.getUniqueString())
        loader = ExternalHelpersBackendLoader([tempdir.path])
        self.assertEqual([], loader.load())

    def test_ignores_missing_dirs(self):
        self.useFixture(TempdirFixture())
        loader = ExternalHelpersBackendLoader([self.getUniqueString()])
        self.assertEqual([], loader.load())


class GetDefaultSelectorTests(TestCase):

    def test_returns_backend_selector(self):
        backend = self.getUniqueString()
        selector = get_default_selector([backend])
        self.assertIsInstance(selector, BackendSelector)
        self.assertEqual([backend], selector.backends)


class GetDefaultLoaderTests(TestCase):

    def test_returns_external_helpers_loader(self):
        loader = get_default_loader()
        self.assertIsInstance(loader, ExternalHelpersBackendLoader)

    def test_sets_default_paths(self):
        loader = get_default_loader()
        self.assertEqual(EXTERNAL_BACKEND_PATHS, loader.paths)


class TestSelector(BackendSelector):

    def get_info(self, path):
        return self.__class__.__name__


class GetInfoForTests(TestCase):

    def test_gets_correct_info(self):
        info = self.getUniqueString()
        path = self.getUniqueString()
        backend = StaticBackend(
            self.getUniqueString(), 10, info, expected_path=path)
        loader = StaticLoader([backend])
        self.assertEqual(info, get_info_for(path, loader=loader))

    def test_uses_selector_cls(self):
        info = self.getUniqueString()
        path = self.getUniqueString()
        backend = StaticBackend(
            self.getUniqueString(), 10, info, expected_path=path)
        loader = StaticLoader([backend])
        selector_cls = TestSelector
        self.assertEqual(
            selector_cls.__name__,
            get_info_for(path, loader=loader, selector_cls=selector_cls))

    def test_uses_default_loader(self):
        info = self.getUniqueString()
        path = self.getUniqueString()
        backend = StaticBackend(
            self.getUniqueString(), 10, info, expected_path=path)
        self.useFixture(StaticLoaderFixture([backend]))
        self.assertEqual(info, get_info_for(path))

    def test_passes_allowed_backend_names(self):
        info1 = self.getUniqueString()
        info2 = self.getUniqueString()
        path = self.getUniqueString()
        backend1 = StaticBackend(
            self.getUniqueString(), 10, info1, expected_path=path)
        backend2 = StaticBackend(
            self.getUniqueString(), 20, info2, expected_path=path)
        self.useFixture(StaticLoaderFixture(
            [backend1, backend2]))
        self.assertEqual(info1, get_info_for(path,
                allowed_backend_names=[backend1.name]))
