# Copyright (C) 2012 Linaro Limited
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

"""
lava.fastmodels.models
======================

LAVA Wrappers around ARM Fast Models {Portfolio,Tools}
"""

import logging
import os
import shutil
import subprocess
import tempfile
import errno


from json_document.document import Document
from json_document.shortcuts import persistence
from json_document import bridge

from lava.builder.interface import (
    IBuild,
)
from lava.builder.simple import (
    BuildArtifact,
    BuildError,
    BuildResult,
)


class ModelMetaData(Document):
    """
    Meta data for a model in the model library
    """

    document_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "format": {
                "type": "string",
                "enum": ["LAVA Fast Model 1.0"],
            },
            "configuration": {
                "type": "string",
            },
            "project": {
                "type": "string",
            },
            "so_file": {
                "type": "string",
            },
        }
    }

    @bridge.readwrite
    def format(self):
        """
        Document format identifier
        """

    @bridge.readwrite
    def configuration(self):
        """
        The configuration value passed to simgen
        """

    @bridge.readwrite
    def project(self):
        """
        The project file passed to simgen
        """

    @bridge.readwrite
    def so_file(self):
        """
        Relative path to the shared object/library to load
        """


class Model(object):
    """
    Model in the model library

    This class bundles a bit of meta-data and a shared library used by the ARM
    model shell. The shared library encapsulates the machine (and core)
    specification. A model can be build from sources assuming correct libraries
    and toolchain is installed on the machine. To build a model see
    :class:`~lava.fastmodels.models.ModelBuildRecipe`
    """

    def __init__(self, pathname):
        """
        Create a model that is installed in the specified location. The
        pathname must point to a .model directory. The directory must store two
        files: the meta-data document info.json and a shared object file (the
        name of the so file is encoded in info.json). No precautions are made
        to select the binary that is compatible with the current system.
        """
        self._pathname = pathname
        self._meta = ModelMetaData({})
        self._meta_persistence = persistence(
            self._meta, os.path.join(self._pathname, "info.json"),
            ignore_missing=False)
        self._meta_persistence.load()
        self._meta.validate()

    @property
    def meta(self):
        """
        Return the meta data associated with this model.

        The result is an instance of :class:`~lava.fastmodels.models.ModelMetaData`
        """
        return self._meta

    @property
    def name(self):
        """
        Name of this model

        The name is the directory name without the .model suffix
        """
        name, ext = os.path.splitext(
            os.path.basename(self._pathname))
        return name


class ModelLibrary(object):
    """
    A library of models (:class:`~lava.fastmodels.model.Model`)

    Here the word library corresponds to a collection of models, not
    to the shared object of a model (commonly referred to as a 'library')
    """
    
    def __init__(self, path):
        """
        Construct a library that will look at a particular directory
        """
        self._path = path

    def _load_model_by_name(self, name):
            pathname = os.path.join(self._path, name + ".model")
            if os.path.exists(pathname) and os.path.isdir(pathname):
                return self._load_model(pathname)

    def _load_model(self, pathname):
        try:
            model = Model(pathname)
            model.meta.validate()
            return model
        except ValueError as exc:
            logging.exception("Unable to load model: %s", pathname)

    @property
    def models(self):
        """
        Generate an unsorted list of models available in the library
        """
        names = []
        try:
            names.extend([
                os.path.splitext(name)[0]
                for name in os.listdir(self._path)
                if name.endswith(".model")])
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                logging.warning("Unable to enumerate directory: %s", self._path)
        for name in names:
            model = self._load_model_by_name(name)
            if model:
                yield model

    def __getitem__(self, name):
        model = self._load_model_by_name(name)
        if model:
            return model
        raise KeyError(name)

    def copy_to_library(self, model_dir):
        """
        """
        # XXX: There is no need to check if the model currently exists in this
        # library filesystem access is inheriently racy and since there is no
        # way to lock everyone out we just try to do our best
        shutil.copytree(
            model_dir, os.path.join(
                self._path, os.path.basename(model_dir)))


class ModelBuild(IBuild):
    """
    Recipe for building fast machine models
    using sgproj from their .sgproj description files
    and a build configuration (which toolchain to use)
    """

    def __init__(self, name, project, configuration):
        self._name = name
        self._project = project 
        self._configuration = configuration
        self._scratch_dir = tempfile.mkdtemp(suffix='.lava-fastmodels.build')

    @property
    def name(self):
        """
        Name of the model

        The name is arbitrary, usually it helps to identify the model in a
        simple manner (as in A15x1) without having to consult build
        configuration and the project file.
        """
        return self._name

    @property
    def project(self):
        """
        Pathname of the project file
        """
        return self._project

    @property
    def configuration(self):
        """
        Name of the build configuration
        """
        return self._configuration

    @property
    def _build_dir(self):
        """
        Directory where we'll build the model library (shared object)
        """
        return os.path.join(self._scratch_dir, "build")

    def _build_model_lib(self):
        """
        Build the model library (shared object)
        """
        # Create a build directory
        os.mkdir(self._build_dir)
        # Compose the build command
        build_cmd = [
            # Using simgen
            'simgen',
            # take this project file
            '--project-file', self.project,
            # and build it in this directory
            '--build-dir', self._build_dir,
            # using this toolchain
            '--configuration', self.configuration,
            # we want a binary build please
            '--build'
        ]
        # Build the model library
        proc = subprocess.Popen(
            build_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        # Crash if the model fails to build somehow
        if proc.returncode:
            raise BuildError(stderr)

    def _find_cadi_system(self):
        """
        Find the cadi_system*.so file in the model build directory
        """
        for name in os.listdir(self._build_dir):
            if name.startswith("cadi_system") and name.endswith(".so"):
                return os.path.join(self._build_dir, name)

    @property
    def _model_dir(self):
        """
        Directory where the new model is constructed
        """
        return os.path.join(self._scratch_dir, self._name + ".model")

    def _package_model(self):
        """
        Package the model library (shared object) as a .model directory
        """
        # Create a directory for the model
        model_dir = self._model_dir
        os.mkdir(model_dir)
        # Find the model binary
        so_pathname = self._find_cadi_system()
        # Get the name of the .so file
        so_file = os.path.basename(so_pathname)
        # Copy the library to the model directory
        shutil.copy(so_pathname, os.path.join(model_dir, so_file)) 
        # Create model meta data
        meta = ModelMetaData({
            'format': "LAVA Fast Model 1.0",
            'configuration': self.configuration,
            'project': self.project,
            'so_file': so_file
        })
        meta.validate()
        # Save it
        persistence(meta, os.path.join(model_dir, "info.json")).save()

    def run(self, sandbox):
        """
        Run the build process.

        This compiles the model library (shared object) and
        then wraps it in a format suitable for LAVA model library
        """
        try:
            with sandbox:
                self._build_model_lib()
                self._package_model()
                artifacts = [
                    BuildArtifact(self._model_dir, "Constructed model")
                ]
                return BuildResult(artifacts, self)
        except:
            self.clean()
            raise

    def clean(self):
        """
        Remove the build directory
        """
        shutil.rmtree(self._scratch_dir)
