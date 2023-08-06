#!/usr/bin/python

import argparse
import json
import os
import sys

from pkgme import __version__, write_packaging
from pkgme.backend import (
    EXTERNAL_BACKEND_PATHS,
    get_backend_selector,
    get_default_loader,
    )
from pkgme.debuild import build_source_package
from pkgme.upload import (
    InvalidPPAName,
    parse_ppa_name,
    upload,
    )
from pkgme.errors import PkgmeError
from pkgme import trace


def build_package(target_dir, interactive, ppa=None, sign=None):
    """Where the magic happens."""
    trace.debug("Building source package for %s" % (target_dir,))
    if sign is not None:
        changes_file = build_source_package(target_dir, sign=sign)
    else:
        changes_file = build_source_package(target_dir, sign=interactive)
    trace.debug("Built source package for %s" % (target_dir,))
    if ppa:
        trace.debug('Uploading to PPA: %s => %s' % (changes_file, ppa))
        upload(changes_file, ppa)
        trace.debug('Uploaded to PPA: %s => %s' % (changes_file, ppa))


def make_arg_parser():
    def ppa_type(ppa_name):
        try:
            parse_ppa_name(ppa_name)
        except InvalidPPAName, e:
            raise argparse.ArgumentTypeError(str(e))
        return ppa_name
    parser = argparse.ArgumentParser(
        description='pkgme - A Debian packaging generation framework.')
    parser.add_argument(
        '-v', '--version', action='store_true',
        help='Print this version string and exit')
    parser.add_argument('-D', '--debug', action='store_true')
    parser.add_argument('--dump', action='store_true')
    parser.add_argument('--which-backends', action='store_true')
    parser.add_argument(
        '-d', '--distro',
        help="The distribution to upload to. e.g. 'oneiric' or 'unstable'.")
    parser.add_argument(
        'ppa', nargs='?', metavar='PPA', type=ppa_type,
        help='A PPA to upload to. e.g. ppa:user/ppa-name')
    parser.add_argument('--nosign', action='store_true', default=None,
                        help="Do not sign resulting source packages.")
    parser.add_argument('--nobuild', action='store_true', default=None,
                        help="Do not build a source packages.")
    return parser


def get_version_info(debug=False):
    version = 'pkgme %s' % (__version__,)
    if debug:
        ls = [version, '']
        ls.append('Backend paths: %s' % ', '.join(map(repr, EXTERNAL_BACKEND_PATHS)))
        ls.append("Available backends:")
        loader = get_default_loader()
        backends = loader.load()
        for backend in backends:
            ls.append(" %s" % backend.describe())
        version = '\n'.join(ls)
    return version


def get_eligible_backends(target_dir):
    """Return a string listing eligible backends for ``target_dir``."""
    selector = get_backend_selector()
    backends = selector.get_eligible_backends(target_dir)
    return ', '.join('%s (%s)' % (backend.name, score) for (score, backend) in backends)


def get_all_info(target_dir, selector=None):
    """Get all info for ``target_dir``.

    Here, "all info" means the list of eligible backends for ``target_dir``,
    the backend that was selected, and all of the info that backend returns.

    This is all collected together as a dict.
    """
    from pkgme.package_files import default_package_file_group
    if selector is None:
        selector = get_backend_selector()
    eligible = selector.get_eligible_backends(target_dir)
    backend = eligible[0][1]
    # XXX: This ignores ExtraFiles and ExtraFilesFromPaths because they aren't
    # in get_elements().
    elements = default_package_file_group.get_elements()
    keys = [element.name for element in elements]
    project_info = backend.get_info(target_dir)
    data = project_info.get_all(keys)
    data[u'selected_backend'] = backend.name
    data[u'eligible_backends'] = [(score, b.name) for (score, b) in eligible]
    return data


def main(argv=None, target_dir=None, interactive=True):
    if argv is None:
        argv = sys.argv[1:]
    parser = make_arg_parser()
    options = parser.parse_args(args=argv)
    if options.version:
        print get_version_info(options.debug)
        return 0
    if options.debug:
        trace.set_debug()
    if target_dir is None:
        target_dir = os.getcwd()
    try:
        if options.dump:
            json.dump(get_all_info(target_dir), sys.stdout,
                      sort_keys=True, indent=2)
        elif options.which_backends:
            print get_eligible_backends(target_dir)
        else:
            trace.debug("Writing packaging for %s" % (target_dir,))
            write_packaging(target_dir, distribution=options.distro)
            trace.debug("Wrote packaging for %s" % (target_dir,))
            if not options.nobuild:
                if options.nosign is None:
                    sign = None
                else:
                    sign = not options.nosign
                build_package(
                    target_dir, interactive=interactive, ppa=options.ppa,
                    sign=sign)
    except PkgmeError, e:
        if options.debug:
            raise
        else:
            sys.stderr.write("ERROR: %s\n" % (e,))
            return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
