# Copyright (C) 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'afshar@google.com (Ali Afshar)'

import os
import cmd
import readline
import atexit

# Constants for shell appearance
PS1 = u'\u25b3'
INTRO = """Google Drive command line client
(for a list of commands try the help command)"""

# History file will contain previous commands.
# TODO(afshar), make the history path configurable.
HISTORY_FILE = os.path.expanduser('~/.drivecli.history')


def SaveHistory():
  """Save the readline history."""
  readline.write_history_file(HISTORY_FILE)


# We have to register the history to be saved on exiting.
atexit.register(SaveHistory)


if os.path.exists(HISTORY_FILE):
  readline.read_history_file(HISTORY_FILE)


class DriveShell(cmd.Cmd):
  """User interface for the shell."""

  intro = INTRO

  @property
  def prompt(self):
    """Create a context-sensitive prompt to display.

    Returns:
      Prompt as a string.
    """
    cfd = self.boss.cft or '/'
    return (u' %s [%s]: ' % (PS1, cfd)).encode('utf8')

  def onecmd(self, line):
    """Handle a single command line.

    This is overriden here to provide magical handling for . and % commands,
    which cmd.Cmd can't cope with.

    Args:
      line: User-entered line.
    Returns:
      Response from the called command.
    """
    if line.startswith('.'):
      return self.do_last(line[1:])
    elif line.startswith('%'):
      return self.do_recent(line[1:])
    else:
      return cmd.Cmd.onecmd(self, line)

  def do_exit(self, line):
    """Command to exit the shell, and have a nice day."""
    return True

  def do_help(self, line):
    """Help needs no help. You do."""
    if not line or line in ['help', 'exit', 'EOF']:
      return cmd.Cmd.do_help(self, line)
    else:
      getattr(self, 'do_%s' % line)('--help')

  # do_EOF handles the EOF character, do the same thing as exit.
  do_EOF = do_exit


def GenerateShell(commands, boss):
  """Generate a shell instance from the available commands."""
  type_dict = {}
  for command_type in commands:
    command = command_type()
    command.boss = boss
    def do_command(self, line, c=command):
      c._Execute(line)
    do_command.__doc__ = command.__doc__
    type_dict['do_%s' % command.name] = do_command
  # This creates a new shell *class* with the commands bound.
  cmd_type = type('ActualDriveShell', (DriveShell, object), type_dict)
  cmd_type.boss = boss
  return cmd_type()
