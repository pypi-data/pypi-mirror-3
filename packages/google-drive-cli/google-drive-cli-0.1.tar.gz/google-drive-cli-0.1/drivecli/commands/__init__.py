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

from drivecli.commands.last import LastCommand
from drivecli.commands.recent import RecentCommand
from drivecli.commands.ls import LsCommand
from drivecli.commands.cd import CdCommand
from drivecli.commands.put import PutCommand
from drivecli.commands.log import LogCommand
from drivecli.commands.changes import ChangesCommand
from drivecli.commands.permit import PermitCommand
from drivecli.commands.about import AboutCommand
from drivecli.commands.fetch import FetchCommand
from drivecli.commands.permissions import PermissionsCommand


all_commands = [LastCommand, RecentCommand, LsCommand, CdCommand, PutCommand,
                LogCommand, ChangesCommand, PermitCommand, AboutCommand,
                FetchCommand, PermissionsCommand]
