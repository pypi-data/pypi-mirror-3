# -*- test-case-name: modules.test.test_modules -*-
# Copyright (c) 2006-2010 Twisted Matrix Laboratories.
# See LICENSE for details.

"""
This module aims to provide a unified, object-oriented view of Python's
runtime hierarchy.

Python is a very dynamic language with wide variety of introspection utilities.
However, these utilities can be hard to use, because there is no consistent
API.  The introspection API in python is made up of attributes (__name__,
__module__, func_name, etc) on instances, modules, classes and functions which
vary between those four types, utility modules such as 'inspect' which provide
some functionality, the 'imp' module, the "compiler" module, the semantics of
PEP 302 support, and setuptools, among other things.

At the top, you have "PythonPath", an abstract representation of sys.path which
includes methods to locate top-level modules, with or without loading them.
The top-level exposed functions in this module for accessing the system path
are "walkModules", "iterModules", and "getModule".

From most to least specific, here are the objects provided::

                  PythonPath  # sys.path
                      |
                      v
                  PathEntry   # one entry on sys.path: an importer
                      |
                      v
                 PythonModule # a module or package that can be loaded
                      |
                      v
                 PythonAttribute # an attribute of a module (function or class)
                      |
                      v
                 PythonAttribute # an attribute of a function or class
                      |
                      v
                     ...

Here's an example of idiomatic usage: this is what you would do to list all of
the modules outside the standard library's python-files directory::

    import os
    stdlibdir = os.path.dirname(os.__file__)

    from exocet._modules import iterModules

    for modinfo in iterModules():
        if (modinfo.pathEntry.filePath.path != stdlibdir
            and not modinfo.isPackage()):
            print 'unpackaged: %s: %s' % (
                modinfo.name, modinfo.filePath.path)
"""

__metaclass__ = type

# let's try to keep path imports to a minimum...
from os.path import dirname, split as splitpath

import sys
import zipimport
import inspect
import warnings
import re
try:
    import ast
except ImportError:
    ast = None

from zope.interface import Interface, implements

from exocet._filepath import UnlistableError, FilePath
from exocet._zippath import  ZipArchive

from exocet._reflect import namedAny
from exocet._components import registerAdapter


_nothing = object()

PYTHON_EXTENSIONS = ['.py']
OPTIMIZED_MODE = __doc__ is None
if OPTIMIZED_MODE:
    PYTHON_EXTENSIONS.append('.pyo')
else:
    PYTHON_EXTENSIONS.append('.pyc')
PYTHON_EXTENSIONS.extend([".so", ".pyd"])

def _isPythonIdentifier(string):
    """
    cheezy fake test for proper identifier-ness.

    @param string: a str which might or might not be a valid python identifier.

    @return: True or False
    """
    if string == '':
        return True
    try:
        return re.match('[a-zA-Z_][a-zA-Z0-9_]*$', string) is not None
    except TypeError:
        return False


class NotLoadedError(Exception):
    """
    Attempt to access a value that hasn't been loaded yet.

    @since: 10.2
    """

def _isPackagePath(fpath):
    # Determine if a FilePath-like object is a Python package.  TODO: deal with
    # __init__module.(so|dll|pyd)?
    extless = fpath.splitext()[0]
    basend = splitpath(extless)[1]
    return basend == "__init__"



class _ModuleIteratorHelper:
    """
    This mixin provides common behavior between python module and path entries,
    since the mechanism for searching sys.path and __path__ attributes is
    remarkably similar.
    """

    def iterModules(self):
        """
        Loop over the modules present below this entry or package on PYTHONPATH.

        For modules which are not packages, this will yield nothing.

        For packages and path entries, this will only yield modules one level
        down; i.e. if there is a package a.b.c, iterModules on a will only
        return a.b.  If you want to descend deeply, use walkModules.

        @return: a generator which yields PythonModule instances that describe
        modules which can be, or have been, imported.
        """
        yielded = {}
        if not self.filePath.exists():
            return

        for placeToLook in self._packagePaths():
            try:
                children = placeToLook.children()
            except UnlistableError:
                continue

            children.sort()
            for potentialTopLevel in children:
                ext = potentialTopLevel.splitext()[1]
                potentialBasename = potentialTopLevel.basename()[:-len(ext)]
                if ext in PYTHON_EXTENSIONS:
                    # TODO: this should be a little choosier about which path entry
                    # it selects first, and it should do all the .so checking and
                    # crud
                    if not _isPythonIdentifier(potentialBasename):
                        continue
                    modname = self._subModuleName(potentialBasename)
                    if modname.split(".")[-1] == '__init__':
                        # This marks the directory as a package so it can't be
                        # a module.
                        continue
                    if modname not in yielded:
                        yielded[modname] = True
                        pm = PythonModule(modname, potentialTopLevel, self._getEntry())
                        assert pm != self
                        yield pm
                else:
                    if (ext or not _isPythonIdentifier(potentialBasename)
                        or not potentialTopLevel.isdir()):
                        continue
                    modname = self._subModuleName(potentialTopLevel.basename())
                    for ext in PYTHON_EXTENSIONS:
                        initpy = potentialTopLevel.child("__init__"+ext)
                        if initpy.exists():
                            yielded[modname] = True
                            pm = PythonModule(modname, initpy, self._getEntry())
                            assert pm != self
                            yield pm
                            break

    def walkModules(self, importPackages=False):
        """
        Similar to L{iterModules}, this yields self, and then every module in my
        package or entry, and every submodule in each package or entry.

        In other words, this is deep, and L{iterModules} is shallow.
        """
        yield self
        for package in self.iterModules():
            for module in package.walkModules(importPackages=importPackages):
                yield module

    def _subModuleName(self, mn):
        """
        This is a hook to provide packages with the ability to specify their names
        as a prefix to submodules here.
        """
        return mn

    def _packagePaths(self):
        """
        Implement in subclasses to specify where to look for modules.

        @return: iterable of FilePath-like objects.
        """
        raise NotImplementedError()

    def _getEntry(self):
        """
        Implement in subclasses to specify what path entry submodules will come
        from.

        @return: a PathEntry instance.
        """
        raise NotImplementedError()


    def __getitem__(self, modname):
        """
        Retrieve a module from below this path or package.

        @param modname: a str naming a module to be loaded.  For entries, this
        is a top-level, undotted package name, and for packages it is the name
        of the module without the package prefix.  For example, if you have a
        PythonModule representing the 'twisted' package, you could use::

            twistedPackageObj['python']['modules']

        to retrieve the Twisted-supplied version of this module.

        @raise: KeyError if the module is not found.

        @return: a PythonModule.
        """
        for module in self.iterModules():
            if module.name == self._subModuleName(modname):
                return module
        raise KeyError(modname)

    def __iter__(self):
        """
        Implemented to raise NotImplementedError for clarity, so that attempting to
        loop over this object won't call __getitem__.

        Note: in the future there might be some sensible default for iteration,
        like 'walkEverything', so this is deliberately untested and undefined
        behavior.
        """
        raise NotImplementedError()

if ast is not None:
    _iefBase = ast.NodeVisitor
else:
    _iefBase = object

class _ImportExportFinder(_iefBase):
    """
    Find names of imports and exports (via __all__).

    @ivar imports: A set of (source, name) pairs describing an
                   imported name. if the source is None, the name
                   is an import from the top level.

    @ivar exports: A list of names defined in __all__ in this
                   module, or None if the module has no __all__
                   attribute.

    @ivar definedNames: A set of names created by assignment,
                        class definitions, or function definitions
                        at the top level of this module.
    """

    def __init__(self):
        self.imports = set()
        self.exports = None
        self.definedNames = set()


    def visit_Import(self, node):
        """
        Collect names for all import statements.
        """
        for alias in node.names:
            self.imports.add((None, alias.name))


    def visit_ImportFrom(self, node):
        """
        Collect names and source modules from "import x from y" statements.
        """
        if node.names[0].name == "*":
            raise SyntaxError("Code containing 'import *' cannot be statically analyzed.")
        for name in node.names:
            self.imports.add((node.module, name.name))


    def visit_Module(self, node):
        """
        Look for top-level name bindings and __all__ in a module.
        """
        def collectNames(target, value):
            if isinstance(target, ast.Name):
                collectSingleName(value, target.id)
            if isinstance(target, (ast.List, ast.Tuple)):
                if not (isinstance(value, (ast.List, ast.Tuple))
                        and len(value.elts) == len(target.elts)):
                    value = None
                nameNodes = target.elts
                for (i, n) in enumerate(nameNodes):
                    if value is not None:
                        v = value.elts[i]
                    else:
                        v = None
                    collectNames(n, v)

        def collectSingleName(value, name):
            if name == '__all__':
                checkAll(value)
            else:
                self.definedNames.add(name)

        def checkAll(allval):
            if self.exports is not None:
                    raise SyntaxError("__all__ can only be defined once")
            try:
                self.exports = set(ast.literal_eval(allval))
            except ValueError:
                raise SyntaxError("__all__ must only contain literal Python identifier strings")
            for exp in self.exports:
                if not _isPythonIdentifier(exp):
                    raise SyntaxError("__all__ must only contain literal Python identifier strings")
        for stmt in node.body:
            self.visit(stmt)
            if isinstance(stmt, ast.Assign):
                collectNames(stmt.targets[0], stmt.value)
            elif isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
                self.definedNames.add(stmt.name)

class PythonAttribute:
    """
    I represent a function, class, or other object that is present.

    @ivar name: the fully-qualified python name of this attribute.

    @ivar onObject: a reference to a PythonModule or other PythonAttribute that
    is this attribute's logical parent.

    @ivar name: the fully qualified python name of the attribute represented by
    this class.
    """
    def __init__(self, name, onObject, loaded, pythonValue):
        """
        Create a PythonAttribute.  This is a private constructor.  Do not construct
        me directly, use PythonModule.iterAttributes.

        @param name: the FQPN
        @param onObject: see ivar
        @param loaded: always True, for now
        @param pythonValue: the value of the attribute we're pointing to.
        """
        self.name = name
        self.onObject = onObject
        self._loaded = loaded
        self.pythonValue = pythonValue

    def __repr__(self):
        return 'PythonAttribute<%r>'%(self.name,)

    def isLoaded(self):
        """
        Return a boolean describing whether the attribute this describes has
        actually been loaded into memory by importing its module.
        """
        return self._loaded

    def load(self, default=_nothing):
        """
        Load the value associated with this attribute.

        @return: an arbitrary Python object, or 'default' if there is an error
        loading it.
        """
        if not self.isLoaded():
            mod = self.onObject.load()
            self.pythonValue = getattr(mod, self.name.split('.')[-1], default)
            self._loaded = True
        return self.pythonValue


    def iterAttributes(self):
        """
        Iterate over the attributes of the value named by this
        object. Only works when the module is loaded.

        @raise NotImplementedError: when the module is not loaded.
        """
        if not self.isLoaded():
            raise NotImplementedError("Static inspection of attributes doesn't"
                                      " go beyond the top level of the module.")
        for name, val in inspect.getmembers(self.load()):
            yield PythonAttribute(self.name + '.' + name, self, True, val)



class PythonModule(_ModuleIteratorHelper):
    """
    Representation of a module which could be imported from sys.path.

    @ivar name: the fully qualified python name of this module.

    @ivar filePath: a FilePath-like object which points to the location of this
    module.

    @ivar pathEntry: a L{PathEntry} instance which this module was located
    from.

    @ivar _finder: an L{_ImportExportFinder}, or None. Used to
    discover names used and defined in a module by inspecting its AST.
    """

    def __init__(self, name, filePath, pathEntry):
        """
        Create a PythonModule.  Do not construct this directly, instead inspect a
        PythonPath or other PythonModule instances.

        @param name: see ivar
        @param filePath: see ivar
        @param pathEntry: see ivar
        """
        assert not name.endswith(".__init__")
        self.name = name
        self.filePath = filePath
        self.parentPath = filePath.parent()
        self.pathEntry = pathEntry

        self._finder = None


    def _getEntry(self):
        return self.pathEntry

    def __repr__(self):
        """
        Return a string representation including the module name.
        """
        return 'PythonModule<%r>' % (self.name,)


    def isLoaded(self):
        """
        Determine if the module is loaded into sys.modules.

        @return: a boolean: true if loaded, false if not.
        """
        return self.pathEntry.pythonPath.moduleDict.get(self.name) is not None


    def _maybeLoadFinder(self):
        """
        Scan a module for imports, exports, and attributes.
        """
        if self._finder is None:
            try:
                tree = ast.parse(self.filePath.getContent())
            except TypeError:
                raise ValueError("Static analysis of module attributes can only be done on Python source.")
            self._finder = _ImportExportFinder()
            self._finder.visit(tree)


    def iterAttributes(self):
        """
        List all the attributes defined in this module.

        On Python 2.6 and later this method can list attributes on a
        module without loading it, via AST inspection. On earlier
        Python versions, they must be loaded. This method will use
        inspect.getmembers on all Python versions if the module is loaded.

        @raise NotImplementedError: if this module is not loaded and
        AST inspection is not possible.

        @return: a generator yielding PythonAttribute instances describing the
        attributes of this module.
        """
        if not self.isLoaded():
            if ast is None:
                raise NotImplementedError("Static analysis of module attributes"
                                          " requires the 'ast' module,"
                                          " found in Python 2.6 or later.")
            self._maybeLoadFinder()
            if self._finder.exports:
                attrs = (set([x[1] for x in self._finder.imports]) | self._finder.definedNames) & self._finder.exports
            else:
                attrs = self._finder.definedNames
            for name in attrs:
                yield PythonAttribute(self.name + '.' + name, self, False, _nothing)
        else:
            for name, val in inspect.getmembers(self.load()):
                yield PythonAttribute(self.name + '.' + name, self, True, val)


    def iterImportNames(self):
        """
        List all the fully-qualified names imported in this module.

        @raise NotImplementedError: if this module is not loaded and
        AST inspection is not possible.

        @return: a generator yielding fully qualified name strings for
                 each name imported into this module.

        @since: 10.2
        """
        if ast is None:
            raise NotImplementedError("Static analysis of module attributes"
                                      " requires the 'ast' module, found in"
                                      " Python 2.6 or later.")

        self._maybeLoadFinder()
        for (origin, name) in self._finder.imports:
            if origin is not None:
                yield origin+ '.' + name
            else:
                yield name


    def iterExportNames(self):
        """
        List all the names exported by this module. If the module
        defines __all__ as a list of literal strings, those names will
        be treated as the module's exports. Otherwise, all names
        defined at the top level of the module will be regarded as
        exports.

        @raise NotImplementedError: if this module is not loaded and
        AST inspection is not possible.

        @return: an iterable of names of attributes of this module.

        @since: 10.2
        """
        if ast is None:
            raise NotImplementedError("Static analysis of module attributes"
                                      " requires the 'ast' module, found in"
                                      " Python 2.6 or later.")
        self._maybeLoadFinder()
        return self._finder.exports or self._finder.definedNames


    def isPackage(self):
        """
        Returns true if this module is also a package, and might yield something
        from iterModules.
        """
        return _isPackagePath(self.filePath)

    def load(self, default=_nothing):
        """
        Load this module.

        @param default: if specified, the value to return in case of an error.

        @return: a genuine python module.

        @raise: any type of exception.  Importing modules is a risky business;
        the erorrs of any code run at module scope may be raised from here, as
        well as ImportError if something bizarre happened to the system path
        between the discovery of this PythonModule object and the attempt to
        import it.  If you specify a default, the error will be swallowed
        entirely, and not logged.

        @rtype: types.ModuleType.
        """
        try:
            return self.pathEntry.pythonPath.moduleLoader(self.name)
        except:                 # this needs more thought...
            if default is not _nothing:
                return default
            raise

    def __eq__(self, other):
        """
        PythonModules with the same name are equal.
        """
        if not isinstance(other, PythonModule):
            return False
        return other.name == self.name

    def __ne__(self, other):
        """
        PythonModules with different names are not equal.
        """
        if not isinstance(other, PythonModule):
            return True
        return other.name != self.name

    def walkModules(self, importPackages=False):
        if importPackages and self.isPackage():
            self.load()
        return super(PythonModule, self).walkModules(importPackages=importPackages)

    def _subModuleName(self, mn):
        """
        submodules of this module are prefixed with our name.
        """
        return self.name + '.' + mn

    def _packagePaths(self):
        """
        Yield a sequence of FilePath-like objects which represent path segments.
        """
        if not self.isPackage():
            return
        if self.isLoaded():
            load = self.load()
            if hasattr(load, '__path__'):
                for fn in load.__path__:
                    if fn == self.parentPath.path:
                        # this should _really_ exist.
                        assert self.parentPath.exists()
                        yield self.parentPath
                    else:
                        smp = self.pathEntry.pythonPath._smartPath(fn)
                        if smp.exists():
                            yield smp
        else:
            yield self.parentPath


class PathEntry(_ModuleIteratorHelper):
    """
    I am a proxy for a single entry on sys.path.

    @ivar filePath: a FilePath-like object pointing at the filesystem location
    or archive file where this path entry is stored.

    @ivar pythonPath: a PythonPath instance.
    """
    def __init__(self, filePath, pythonPath):
        """
        Create a PathEntry.  This is a private constructor.
        """
        self.filePath = filePath
        self.pythonPath = pythonPath

    def _getEntry(self):
        return self

    def __repr__(self):
        return 'PathEntry<%r>' % (self.filePath,)

    def _packagePaths(self):
        yield self.filePath

class IPathImportMapper(Interface):
    """
    This is an internal interface, used to map importers to factories for
    FilePath-like objects.
    """
    def mapPath(self, pathLikeString):
        """
        Return a FilePath-like object.

        @param pathLikeString: a path-like string, like one that might be
        passed to an import hook.

        @return: a L{FilePath}, or something like it (currently only a
        L{ZipPath}, but more might be added later).
        """

class _DefaultMapImpl:
    """ Wrapper for the default importer, i.e. None.  """
    implements(IPathImportMapper)
    def mapPath(self, fsPathString):
        return FilePath(fsPathString)
_theDefaultMapper = _DefaultMapImpl()

class _ZipMapImpl:
    """ IPathImportMapper implementation for zipimport.ZipImporter.  """
    implements(IPathImportMapper)
    def __init__(self, importer):
        self.importer = importer

    def mapPath(self, fsPathString):
        """
        Map the given FS path to a ZipPath, by looking at the ZipImporter's
        "archive" attribute and using it as our ZipArchive root, then walking
        down into the archive from there.

        @return: a L{zippath.ZipPath} or L{zippath.ZipArchive} instance.
        """
        za = ZipArchive(self.importer.archive)
        myPath = FilePath(self.importer.archive)
        itsPath = FilePath(fsPathString)
        if myPath == itsPath:
            return za
        # This is NOT a general-purpose rule for sys.path or __file__:
        # zipimport specifically uses regular OS path syntax in its pathnames,
        # even though zip files specify that slashes are always the separator,
        # regardless of platform.
        segs = itsPath.segmentsFrom(myPath)
        zp = za
        for seg in segs:
            zp = zp.child(seg)
        return zp

registerAdapter(_ZipMapImpl, zipimport.zipimporter, IPathImportMapper)

def _defaultSysPathFactory():
    """
    Provide the default behavior of PythonPath's sys.path factory, which is to
    return the current value of sys.path.

    @return: L{sys.path}
    """
    return sys.path


class PythonPath:
    """
    I represent the very top of the Python object-space, the module list in
    sys.path and the modules list in sys.modules.

    @ivar _sysPath: a sequence of strings like sys.path.  This attribute is
    read-only.

    @ivar moduleDict: a dictionary mapping string module names to module
    objects, like sys.modules.

    @ivar sysPathHooks: a list of PEP-302 path hooks, like sys.path_hooks.

    @ivar moduleLoader: a function that takes a fully-qualified python name and
    returns a module, like twisted.python.reflect.namedAny.
    """

    def __init__(self,
                 sysPath=None,
                 moduleDict=sys.modules,
                 sysPathHooks=sys.path_hooks,
                 importerCache=sys.path_importer_cache,
                 moduleLoader=namedAny,
                 sysPathFactory=None):
        """
        Create a PythonPath.  You almost certainly want to use
        modules.theSystemPath, or its aliased methods, rather than creating a
        new instance yourself, though.

        All parameters are optional, and if unspecified, will use 'system'
        equivalents that makes this PythonPath like the global L{theSystemPath}
        instance.

        @param sysPath: a sys.path-like list to use for this PythonPath, to
        specify where to load modules from.

        @param moduleDict: a sys.modules-like dictionary to use for keeping
        track of what modules this PythonPath has loaded.

        @param sysPathHooks: sys.path_hooks-like list of PEP-302 path hooks to
        be used for this PythonPath, to determie which importers should be
        used.

        @param importerCache: a sys.path_importer_cache-like list of PEP-302
        importers.  This will be used in conjunction with the given
        sysPathHooks.

        @param moduleLoader: a module loader function which takes a string and
        returns a module.  That is to say, it is like L{namedAny} - *not* like
        L{__import__}.

        @param sysPathFactory: a 0-argument callable which returns the current
        value of a sys.path-like list of strings.  Specify either this, or
        sysPath, not both.  This alternative interface is provided because the
        way the Python import mechanism works, you can re-bind the 'sys.path'
        name and that is what is used for current imports, so it must be a
        factory rather than a value to deal with modification by rebinding
        rather than modification by mutation.  Note: it is not recommended to
        rebind sys.path.  Although this mechanism can deal with that, it is a
        subtle point which some tools that it is easy for tools which interact
        with sys.path to miss.
        """
        if sysPath is not None:
            sysPathFactory = lambda : sysPath
        elif sysPathFactory is None:
            sysPathFactory = _defaultSysPathFactory
        self._sysPathFactory = sysPathFactory
        self._sysPath = sysPath
        self.moduleDict = moduleDict
        self.sysPathHooks = sysPathHooks
        self.importerCache = importerCache
        self.moduleLoader = moduleLoader


    def _getSysPath(self):
        """
        Retrieve the current value of the module search path list.
        """
        return self._sysPathFactory()

    sysPath = property(_getSysPath)

    def _findEntryPathString(self, modobj):
        """
        Determine where a given Python module object came from by looking at path
        entries.
        """
        topPackageObj = modobj
        while '.' in topPackageObj.__name__:
            topPackageObj = self.moduleDict['.'.join(
                    topPackageObj.__name__.split('.')[:-1])]
        if _isPackagePath(FilePath(topPackageObj.__file__)):
            # if package 'foo' is on sys.path at /a/b/foo, package 'foo's
            # __file__ will be /a/b/foo/__init__.py, and we are looking for
            # /a/b here, the path-entry; so go up two steps.
            rval = dirname(dirname(topPackageObj.__file__))
        else:
            # the module is completely top-level, not within any packages.  The
            # path entry it's on is just its dirname.
            rval = dirname(topPackageObj.__file__)

        # There are probably some awful tricks that an importer could pull
        # which would break this, so let's just make sure... it's a loaded
        # module after all, which means that its path MUST be in
        # path_importer_cache according to PEP 302 -glyph
        if rval not in self.importerCache:
            warnings.warn(
                "%s (for module %s) not in path importer cache "
                "(PEP 302 violation - check your local configuration)." % (
                    rval, modobj.__name__),
                stacklevel=3)

        return rval

    def _smartPath(self, pathName):
        """
        Given a path entry from sys.path which may refer to an importer,
        return the appropriate FilePath-like instance.

        @param pathName: a str describing the path.

        @return: a FilePath-like object.
        """
        importr = self.importerCache.get(pathName, _nothing)
        if importr is _nothing:
            for hook in self.sysPathHooks:
                try:
                    importr = hook(pathName)
                except ImportError:
                    pass
            if importr is _nothing: # still
                importr = None
        return IPathImportMapper(importr, _theDefaultMapper).mapPath(pathName)

    def iterEntries(self):
        """
        Iterate the entries on my sysPath.

        @return: a generator yielding PathEntry objects
        """
        for pathName in self.sysPath:
            fp = self._smartPath(pathName)
            yield PathEntry(fp, self)


    def __getitem__(self, modname):
        """
        Get a python module by its given fully-qualified name.

        @param modname: The fully-qualified Python module name to load.

        @type modname: C{str}

        @return: an object representing the module identified by C{modname}

        @rtype: L{PythonModule}

        @raise KeyError: if the module name is not a valid module name, or no
            such module can be identified as loadable.
        """
        # See if the module is already somewhere in Python-land.
        moduleObject = self.moduleDict.get(modname)
        if moduleObject is not None:
            # we need 2 paths; one of the path entry and one for the module.
            pe = PathEntry(
                self._smartPath(
                    self._findEntryPathString(moduleObject)),
                self)
            path = inspect.getsourcefile(moduleObject)
            if path is None:
                path = moduleObject.__file__
            mp = self._smartPath(path)
            return PythonModule(modname, mp, pe)

        # Recurse if we're trying to get a submodule.
        if '.' in modname:
            pkg = self
            for name in modname.split('.'):
                pkg = pkg[name]
            return pkg

        # Finally do the slowest possible thing and iterate
        for module in self.iterModules():
            if module.name == modname:
                return module
        raise KeyError(modname)


    def __repr__(self):
        """
        Display my sysPath and moduleDict in a string representation.
        """
        return "PythonPath(%r,%r)" % (self.sysPath, self.moduleDict)

    def iterModules(self):
        """
        Yield all top-level modules on my sysPath.
        """
        for entry in self.iterEntries():
            for module in entry.iterModules():
                yield module

    def walkModules(self, importPackages=False):
        """
        Similar to L{iterModules}, this yields every module on the path, then every
        submodule in each package or entry.
        """
        for package in self.iterModules():
            for module in package.walkModules(importPackages=False):
                yield module

theSystemPath = PythonPath()

def walkModules(importPackages=False):
    """
    Deeply iterate all modules on the global python path.

    @param importPackages: Import packages as they are seen.
    """
    return theSystemPath.walkModules(importPackages=importPackages)

def iterModules():
    """
    Iterate all modules and top-level packages on the global Python path, but
    do not descend into packages.

    @param importPackages: Import packages as they are seen.
    """
    return theSystemPath.iterModules()

def getModule(moduleName):
    """
    Retrieve a module from the system path.
    """
    return theSystemPath[moduleName]
