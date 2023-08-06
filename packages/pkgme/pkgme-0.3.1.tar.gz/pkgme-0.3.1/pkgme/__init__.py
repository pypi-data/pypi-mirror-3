# pkgme - A Debian packaging framework
#
# Copyright (C) 2010 Canonical Lt.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Package symbols."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    '__version__',
    'write_packaging',
    ]


__version__ = '0.3.1'


def write_packaging(path, distribution=None, allowed_backend_names=None):
    # Do these imports in the function to reduce the side-effects of importing
    # pkgme.   This avoids the need for setup.py of the tool being packaged
    # from having to find all the imported dependencies when running the
    # extension pkgme_info setup.py command.
    from pkgme.backend import get_info_for
    from pkgme.package_files import default_package_file_group
    from pkgme.write import Writer
    info = get_info_for(path, allowed_backend_names=allowed_backend_names)
    if distribution:
        from pkgme.info_elements import Distribution
        from pkgme.project_info import DictInfo, FallbackInfo
        info = FallbackInfo(DictInfo({Distribution.name: distribution}), info)
    files = default_package_file_group.get_files(info)
    Writer().write(files, path)
