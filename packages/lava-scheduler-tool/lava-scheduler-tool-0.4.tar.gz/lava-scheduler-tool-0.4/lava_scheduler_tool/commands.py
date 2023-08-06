# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Michael Hudson-Doyle <michael.hudson@linaro.org>
#
# This file is part of lava-scheduler-tool.
#
# lava-scheduler-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-scheduler-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-scheduler-tool.  If not, see <http://www.gnu.org/licenses/>.

import xmlrpclib

from lava_tool.authtoken import AuthenticatingServerProxy, KeyringAuthBackend
from lava.tool.command import Command, CommandGroup
from lava.tool.errors import CommandError
from lava.tool.commands import ExperimentalCommandMixIn


class scheduler(CommandGroup):
    """
    Interact with LAVA Scheduler
    """

    namespace = "lava.scheduler.commands"


class submit_job(ExperimentalCommandMixIn, Command):
    """
    Submit a job to lava-scheduler
    """

    @classmethod
    def register_arguments(cls, parser):
        super(submit_job, cls).register_arguments(parser)
        parser.add_argument("SERVER")
        parser.add_argument("JSON_FILE")

    def invoke(self):
        self.print_experimental_notice()
        server = AuthenticatingServerProxy(
            self.args.SERVER, auth_backend=KeyringAuthBackend())
        with open(self.args.JSON_FILE, 'rb') as stream:
            command_text = stream.read()
        try:
            job_id = server.scheduler.submit_job(command_text)
        except xmlrpclib.Fault, e:
            raise CommandError(str(e))
        else:
            print "submitted as job id:", job_id


class cancel_job(ExperimentalCommandMixIn, Command):

    @classmethod
    def register_arguments(self, parser):
        parser.add_argument("SERVER")
        parser.add_argument("JOB_ID", type=int)

    def invoke(self):
        self.print_experimental_notice()
        server = AuthenticatingServerProxy(
            self.args.SERVER, auth_backend=KeyringAuthBackend())
        server.scheduler.cancel_job(self.args.JOB_ID)
