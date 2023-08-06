# Copyright (c) 2010, 2011, Canonical Ltd
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
