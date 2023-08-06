# Copyright 2012 Canonical Ltd.  All rights reserved.
#
# This file is part of lazr.json
#
# lazr.json is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# lazr.json is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lazr.json.  If not, see <http://www.gnu.org/licenses/>.

"""The lazr.json package."""


import pkg_resources
__version__ = pkg_resources.resource_string(
    "lazr.json", "version.txt").strip()


__all__ = [
    'custom_type_decoder',
    'CustomTypeEncoder',
    'register_serialisable_type',
]

from lazr.json._serialisation import (
    custom_type_decoder,
    CustomTypeEncoder,
    register_serialisable_type,
    )
