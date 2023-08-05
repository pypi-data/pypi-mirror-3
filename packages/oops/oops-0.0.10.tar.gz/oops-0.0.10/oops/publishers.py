# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

"""Generic publisher support and utility code."""

__metaclass__ = type

__all__ = [
    'publish_new_only',
    ]

def publish_new_only(publisher):
    """Wraps a publisher with a check that the report has not had an id set.
    
    This permits having fallback publishers that only publish if the earlier
    one failed.

    For instance:

      >>> config.publishers.append(amqp_publisher)
      >>> config.publishers.append(publish_new_only(datedir_repo.publish))
    """
    def result(report):
        if report.get('id'):
            return None
        return publisher(report)
    return result
