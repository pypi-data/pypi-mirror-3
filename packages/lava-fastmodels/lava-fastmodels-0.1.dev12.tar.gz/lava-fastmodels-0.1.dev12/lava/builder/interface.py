"""
lava.build.interface
====================

Interface classes for the build service.

You can use those classes to reason about the API of various objects you will
interact with as well as to provide compatible implementations in your own modules.

There are three classes here: the sandbox, the build recipe and the build
artifact. The idea is that you setup your sandbox, get a build recipe, run the
build, get build results and do whatever you want with the artifacts. Finally
you clean the build result and you are done.
"""

from lava.utils.interface import Interface, abstractmethod, abstractproperty


class ISandbox(Interface):
    """
    A container for running untrusted code in a sandbox.
    
    The actual sandbox is defined by the implementation, a no-security sandbox
    is also permitted so to reason about the way untrusted code will operate do
    inspect the actual runtime sandbox instance.

    .. note::

        The model of entering and exiting the sandbox has been copied from
        python context managers. It is still unclear if that is sufficient to
        provide enough API for a real sandbox such as a capability/namespace
        jail (Linux), virtual machine or other similar *container*. As such
        this API is **unstable** and may be changed.
    """

    @abstractmethod
    def __enter__(self):
        """
        Run the rest of the code with the container locks in place.
        """

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Disable the container locks.
        """


class IBuildResult(Interface):
    """
    Result of building something.

    Allows to examine build artifacts. Since this class is a context manager it
    also ensures build itself is wiped (by calling
    :meth:`~lava.builder.interface.IBuild.clean()` when the caller code is done
    interacting with the artifacts.
    """

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager.

        This also calls the clean method on the associated IBuild instance.
        """

    @abstractproperty
    def artifacts(self):
        """
        A list of build artifacts
        """

class IBuild(Interface):
    """
    Wrapper for the effects of building something.
    Created by IBuildRecipe.build()
    """

    @abstractmethod
    def run(self, sandbox):
        """
        Run the build in the provided sandbox

        This may raise IBuildError
        This returns IBuildResult
        """

    @abstractmethod
    def clean(self):
        """
        Remove filesystem effects of this build.
       
        Wipe the build tree, do whatever that is needed to clean up
        properly. Once this method is called accessing artifacts is
        no longer permitted.
        """


class IBuildError(Interface):
    """
    An exception that encapuslates build failure data.
    """


class IBuildArtifact(object):
    """
    Build artifact (a small leftover from building something)
    """
    
    @abstractproperty
    def pathname(self):
        """
        Pathname of the build artifact. This partname may be relative or
        absolute, it should be only usef for informative purpose or to call one
        of the copy methods from shutil module.
        """

    @abstractproperty
    def description(self):
        """
        A human readable description of the build artifact. It may be None
        """
