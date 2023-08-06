# Copyright (C) 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of LAVA Fast Models
#
# LAVA Fast Models is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License version 3
# as published by the Free Software Foundation
#
# LAVA Fast Models is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with LAVA Fast Models.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

import os
import sys

from lava_tool.interface import Command, SubCommand, LavaCommandError
from lava.builder.interface import IBuildError
from lava.builder.simple import NoSandbox
from lava.fastmodels.models import ModelBuild, ModelLibrary


class FastModelCommand(SubCommand):
    """
    Interact with ARM Fast Models
    """

    namespace = "lava.fastmodels.commands"

    @classmethod
    def register_arguments(cls, parser):
        super(FastModelCommand, cls).register_arguments(parser)
        parser.add_argument(
            "-P", "--library-path",
            default="/var/lib/lava/fastmodels/models/",
            help="Location of the model library (default: %(default)s)")

    @classmethod
    def get_name(cls):
        return "fastmodel"

    def invoke(self):
        print("burp?")


class ListCommand(Command):
    """
    Display a list of available models
    """

    @classmethod
    def get_name(self):
        return "list"

    def invoke(self):
        library = ModelLibrary(self.args.library_path)
        models = list(library.models)
        if models:
            print("Available models:")
            models.sort(key=lambda model: (model.meta.project, model.meta.configuration))
            for model in models: 
                print(" {model.name}: {model.meta.project} built using "
                      "{model.meta.configuration}".format(model=model))
        else:
            print("There are no models in the library yet")
            print("You can build a model from source using")
            print("$ lava fastmodel build")


class BuildCommand(Command):
    """
    Build a fast model instance suitable for running on the local computer
    """

    @classmethod
    def get_name(cls):
        return "build"

    @classmethod
    def register_arguments(cls, parser):
        super(BuildCommand, cls).register_arguments(parser)
        parser.add_argument(
            "name",
            metavar="NAME",
            help="Name of the model (user defined)")
        parser.add_argument(
            '-p', '--project',
            metavar="PROJECT",
            required=True,
            help="Path to a project fileo compatible with simgen (.sgproj)"),
        parser.add_argument(
            '-c', '--configuration',
            default="Linux-Release-GCC-4.1",
            metavar="CONFIG",
            help="Configuration name (default: %(default)s)")

    def invoke(self):
        library = ModelLibrary(self.args.library_path)
        # Check if model name conflicts
        for model in library.models:
            if model.name == self.args.name:
                raise LavaCommandError("A model with this name already exists in the library")
        # Get a build environment
        build = ModelBuild(self.args.name, self.args.project, self.args.configuration)
        # Get a trusted sandbox
        sandbox = NoSandbox()
        # Build it!
        print("Building: {args.project} using configuration "
              "{args.configuration}".format(args=self.args))
        try:
            with build.run(sandbox) as result:
                # Get our model artifact
                artifact = result.artifacts[0]
                # And copy it to our library
                print("Adding model to the libary")
                library.copy_to_library(artifact.pathname)
        except IBuildError as exc:
            raise LavaCommandError("Unable to build model: %r" % exc)
        # Finally add the new model to the library
        print("Done")
