"""Simple utilities.

"""

__all__ = (
        "Object",

        "Attribute",
        "AbstractAttribute",

        "Constants",
        )


import itertools


# objects #######################################

class Object:
    """A bare object.

    The objects of the root object type are immutable.  This class
    provides mutability.  It's useful for when you want to just add
    some attributes to a bare object and use it.

    """


# attributes ####################################

class Attribute:
    """A class attribute (non-data descriptor).

    The class provides for an initial value and a docstring.  This
    replaces putting the information in the docstring of the class.

    """

    def __init__(self, value, doc=""):
        self.value = value
        self.docstring = doc
    def __get__(self, obj, cls):
        return self
    def __getattribute__(self, name):
        if name == "__doc__":
            return object.__getattribute__(self, "docstring")
        return object.__getattribute__(self, value)


class AbstractAttribute:
    """An abstract class attribute.

    Use this instead of an abstract property when you don't expect the
    attribute to be implemented by a property.

    """

    __isabstractmethod__ = True

    def __init__(self, doc=""):
        self.__doc__ = doc
    def __get__(self, obj, cls):
        return self


# constants #####################################

class Constants:
    """Add the passed "constants" as attributes.

    If morph is passed, use it to morph the iterable before binding.

    See the bind() staticmethod for an explanation of the remaining
    parameters.

    """

    def __init__(self, iterable, start=0, step=1, morph=None):

        self.original = self.__dict__.keys()[:]
        if morph:
            iterable = morph(iterable)
        self.bind(self, iterable, start, step)

    @property
    def names(self):
        """The names of the "constant" attributes.

        """

        return [name for name in self.__dict__
                if name not in self.original]

    @property
    def values(self):
        """The values of the "constant" attributes.

        """

        return [val for name, val in self.__dict__.items()
                if name not in self.original]

    def __add__(self, obj):
        result = self.__class__.__new__(self.__class__)
        for name in self.names:
            setattr(result, name, getattr(self, name))
        for name in obj.names:
            setattr(result, name, getattr(obj, name))
        return result

    def __iadd__(self, obj):
        for name in obj.names:
            setattr(self, name, getattr(obj, name))

    def __contains__(self, obj):
        return obj in self.values

    @staticmethod
    def morph_names(iterable):
        """Change the names that will be bound.

        This static method may be called before passing an iterable to
        Constants() or Constants.bind().

        """

        return iterable

    @staticmethod
    def step_binary(start, iterable):
        for i in it_mod.count(start, step):
            yield 2**i

    @staticmethod
    def step_lower(start, iterable):
        for name in iterable:
            yield name.lower()

    @staticmethod
    def step_echo(start, iterable):
        return iter(iterable)

    @staticmethod
    def bind(obj, iterable, start=0, step=1):
        """Bind the iterable's names to the object.

          obj - where to bind the names.
          iterable - the mapping or sequence for the constant's names.
          start - the value with which to start; used for sequences.
          step - the step value or step generator; used for sequences.

        If obj is a mapping, the iterable will be used to update the
        mapping.  Otherwise the iterable will be used to set attributes
        on the object.

        If the iterable is a mapping, the keys are bound to the values
        in the Constants object's namespace.  If a sequence, the names
        from the sequence are likewise bound, but to the values derived
        from the start and step arguments.

        If the step is an integer, the names will be bound to
        corresponding values from the range starting at start and
        stepping the step value.

        Otherwise step must be a callable that takes an integer start
        value and the iterable. The callable must return an iterable
        with the value to use at each step.

        """

        cls = obj.__class__
        try:
            setter = cls.__setitem__
        except AttributeError:
            setter = cls.__setattr__

        # handle mappings
        if hasattr(iterable, "items"):
            for name, value in iterable.items():
                setter(obj, name, value)
            return

        # compose the step function:
        if isinstance(step, int):
            val_iter = itertools.count(start, step)
        else:
            val_iter = step(start, iterable)

        # handle sequences
        for name in iterable:
            setter(obj, name, next(val_iter))


