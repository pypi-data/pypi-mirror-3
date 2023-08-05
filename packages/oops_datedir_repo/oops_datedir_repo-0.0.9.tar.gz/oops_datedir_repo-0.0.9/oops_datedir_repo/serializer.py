# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Read from any known serializer.

Where possible using the specific known serializer is better as it is more
efficient and won't suffer false positives if two serializations happen to pun
with each other (unlikely though that is).

Typical usage:
    >>> fp = file('an-oops', 'rb')
    >>> report = serializer.read(fp)

See the serializer_rfc822 and serializer_bson modules for information about
serializing OOPS reports by hand. Generally just using the DateDirRepo.publish
method is all that is needed.
"""


__all__ = [
    'read',
    ]

from StringIO import StringIO

from oops_datedir_repo import (
    serializer_bson,
    serializer_rfc822,
    )


def read(fp):
    """Deserialize an OOPS from a bson or rfc822 message.
    
    The whole file is read regardless of the OOPS format.
    """
    # Deal with no-rewindable file pointers.
    content = fp.read()
    try:
        return serializer_bson.read(StringIO(content))
    except KeyError:
        return serializer_rfc822.read(StringIO(content))
