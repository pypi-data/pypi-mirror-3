"""The pylt module.

pylt ("Python Language Transformations") is a system for source-to-source
transformations...and more.

To activate the pylt system, simply import pylt.activate.

Once a transform is registered, it will be used during import to
transform the module's source if the tag and file suffix match.

You can also use import_module() to transform a module directly, or
transform() to transform source directly.

some_transform(source, [tag, [suffix]], **kwargs)

"""

__all__ = [
        'get_tags',
        'get_transforms',
        'transform',
        'register',
        'SourceTransformLoader',
        ]


__version__ = (0, 1, 0, "a1")


import sys
import re
import itertools
from importlib.machinery import FileFinder

from ._importing import SourceFileLoader


"""
Example:

def transform(*args, **kwargs):
    source, args = args[0], args[1:]
    tag, args = None, args if not args else args[0], args[1:]
    suffix, = args

    ...

"""



# XXX activate()
# XXX register_for_pyc(transform)
# XXX import_engine
# XXX transforms (catalog of "built in" transforms)
# XXX transforms['inline_pylt'] (pragma or fake context manager, a la pwang)
# XXX Policy (for registration collisions, etc.)
# XXX Transform (base class) or helper functions

# XXX warning when pylt actually changes the source
# XXX transform type based on transform strategy (handle each differently)
# XXX compare with def_from and given statenemt

# XXX "policy":
# registration collisions/duplicate keys
# order
# constraints

# XXX Hook API:
# activate()
# deactivate()
# is_activated()
# activated()  (context manager)
# deactivated()  (context manager)

# XXX Registry API:
# register()
# unregister()
# is_registered()
# registered()   (context manager)
# unregistered()   (context manager)

# XXX possible approaches for "inlined" transforms
#
# applies to the block (with the "with" clause removed and proper indent)
#   with pylt.transformed(tag, sufficx, ...):
#       ...
#
# applies to the block (with proper indentation)
#   # pylt: tag, suffix, ...
#       ...
#
# applies just to the statement:
#   # pylt: tag, suffix, ...
#   <statement>

# XXX import system considerations:
# - multiple path entry finders for a single path entry
# - path hook to make that work
# - different path entry finder for each file suffix

"""
Targetable artifacts:
- source
- token stream (from tokenization)
- AST (from parsing)
- bytecode (from compiling)

Transform strategies:
- do string replace on source before tokenization
- do regex replace on source before tokenization
- do token replace on token stream before parsing
- do AST replace on AST before compilation
- do bytecode replacement

Existing AST hacks and peephole optimizer in CPython...

"""


_TAG = r"(?:\w+)"
_KWARG = r"(?:\w+=\S+)"
_KWARGS = r"(?:{kwarg}(?:\s+{kwarg})*)".format(kwarg=_KWARG)
TAG_RE = re.compile(
        "#\s*pylt: (?P<tag>{})\s*\((?P<kwargs>{})\)\s*$".format(_TAG, _KWARGS))


_transforms = {}


def get_tags(source):
    """Get any pylt tags found at the top of the source."""
    lines = []
    tags = {}
    for line in source_bytes:
        lines.append(line)
        match = TAG_RE.match(line)
        if not match:
            break
        tag, kwargs = match.groups()
        tags[tag] = kwargs
    return tags, itertools.chain(lines, source_bytes)


def get_transforms(tags, suffix):
    """Yield (transform, tag) for each matching transform."""
    for transform, keys in _transforms.items():
        for tag, kwargs in tags:
            if (tag, suffix) in keys:
                yield transform, tag, kwargs
            elif (tag, None) in keys:
                yield transform, tag, kwargs
        if (None, suffix) in keys:
            yield transform, None, {}
        elif (None, None) in keys:
            yield transform, None, {}


class SourceTransformLoader(SourceFileLoader):

    def source_to_code(self, source_bytes, source_path):
        """Return the code object for the module's source."""
        suffix = os.path.splitext(source_path)[-1]
        tags, source_bytes = get_tags(source_bytes)
        for transform, tag, kwargs in get_transforms(tags, suffix):
            source_bytes = transform(source_bytes, tag, suffix, **kwargs)
        return super().source_to_code(source_bytes, source_path)


def _get_default_path_hook():
    found = None
    for path_hook in sys.path_hooks:
        if path_hook.__name__ == "path_hook_for_FileFinder":
            if found:
                raise NotImplementedError
            found = path_hook
    if not found:
        raise NotImplementedError
    return found


_path_hook = _get_default_path_hook()
_details = (SourceTransformLoader, [], True)


def _add_suffix_hook(suffix):
    # XXX automatically handle all SOURCE_SUFFIXES when any is passed?

    imp.acquire_lock()
    try:
        if suffix not in _details[1]:
            details[1].append(suffix)
        sys.path_importer_cache.clear()

        # make sure _details is in play
        loaders = list(_path_hook.__closure__[1].cell_contents)
        if _details not in loaders:
            loaders.insert(0, _details)
            index = sys.path_hooks.index(_path_hook)
            _path_hook = FileFinder.path_hook(*loaders)
            sys.path_hooks[index] = _path_hook
    finally:
        imp.release_lock()


def register(transform=None, *, tag=None, suffix='.py'):
    """Register a transform with pylt.

    May be used as a decorator.

    """
    # handle the decorator factory case
    if transform is None:
        return lambda transform: register(transform, tag, suffix)

    _transforms.setdefault(transform, []).append((tag, suffix))
    _add_suffix_hook(suffix)
    return transform


# XXX What should "source" be?  Should this be similar to
# importlib.abc.Loader.get_source().  Whatever it is, transform() should
# return the same structure.
#
# Here are the possibilities:
#   string
#   list of strings (lines)
#   iterator of strings (lines)
#   file-like object containing lines
#   "readlines"
#   filename
#
# For reference, tokenize() takes "readlines".

def transform(source, *, tag=None, suffix='.py', kwargs=None):
    """Return the transformed source."""
    kwargs = kwargs or {}
    for transform, tag, kwargs in get_transforms([tag], suffix):
        source = transform(source, tag, suffix, **kwargs)
    return source


def build_transform(*args):
    """Return a new transform that satisfies the passed directives.

    A transform directive is a tuple of (target, command, args).  For
    example:

    transform = build_transform(
            (SOURCE, str_replace, ("...", "...")),
            (SOURCE, regex_replace, ("...", "...")),
            (TOKENS, token_replace, (..., ...)),
            (AST, ast_replace, (..., ...)),
            (BYTECODE, bytecode_replace, (..., ...)),
            )

    """
    raise NotImplementedError
