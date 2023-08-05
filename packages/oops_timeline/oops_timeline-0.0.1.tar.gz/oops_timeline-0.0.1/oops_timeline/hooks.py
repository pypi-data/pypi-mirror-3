# Copyright (c) 2010, 2011, Canonical Ltd
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

"""oops creation and filtering hooks for working with timelines."""

__all__ = [
    'install_hooks',
    'flatten_timeline',
    ]


def install_hooks(config):
    """Install the default timeline hooks into config."""
    config.on_create.extend([flatten_timeline])


def flatten_timeline(report, context):
    """Flattens the timeline into a list of tuples as report['timeline'].

    Looks for the timeline in content['timeline'] and sets it in
    report['timeline'].
    """
    timeline = context.get('timeline')
    if timeline is None:
        return
    statements = []
    for action in timeline.actions:
        statements.append(action.logTuple())
    report['timeline'] = statements
