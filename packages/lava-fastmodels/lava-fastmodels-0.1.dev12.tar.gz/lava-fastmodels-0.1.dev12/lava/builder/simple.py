"""
lava.build.simple
=================

Simple implementation of the build interface. This module may likely be split
up as the package matures.
"""

from lava.builder import interface


class NoSandbox(interface.ISandbox):
    """
    Sandbox that does not limit anything
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class BuildError(interface.IBuildError):
    """
    Simple build error
    """


class BuildArtifact(interface.IBuildArtifact):
    """
    Simple artifact from building something
    """

    def __init__(self, pathname, description=None):
        self._pathname = pathname
        self._description = description

    def __repr__(self):
        return "BuildArtifact({0!r}, {0!r})".format(
            self.pathname, self.description)

    @property
    def pathname(self):
        return self._pathname

    @property
    def description(self):
        return self._description


class BuildResult(object):
    """
    Result of building something
    """

    def __init__(self, artifacts, build):
        self._artifacts = artifacts
        self._build = build

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._build.clean()

    @property
    def artifacts(self):
        return self._artifacts
