#
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

"""The primary interface to oopses stored on disk - the DateDirRepo."""

__metaclass__ = type

__all__ = [
    'DateDirRepo',
    ]

import datetime
import os
import stat

from pytz import utc

import serializer_rfc822
from uniquefileallocator import UniqueFileAllocator


class DateDirRepo:
    """Publish oopses to a date-dir repository."""

    def __init__(self, error_dir, instance_id):
        self.log_namer = UniqueFileAllocator(
            output_root=error_dir,
            log_type="OOPS",
            log_subtype=instance_id,
            )

    def publish(self, report, now=None):
        """Write the report to disk.

        :param now: The datetime to use as the current time.  Will be
            determined if not supplied.  Useful for testing.
        """
        if now is not None:
            now = now.astimezone(utc)
        else:
            now = datetime.datetime.now(utc)
        oopsid, filename = self.log_namer.newId(now)
        report['id'] = oopsid
        serializer_rfc822.write(report, open(filename, 'wb'))
        # Set file permission to: rw-r--r-- (so that reports from
        # umask-restricted services can be gathered by a tool running as
        # another user).
        wanted_permission = (
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        os.chmod(filename, wanted_permission)
        return report['id']
