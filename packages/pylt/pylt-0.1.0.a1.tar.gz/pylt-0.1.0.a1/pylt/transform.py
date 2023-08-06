"""transform module

Transform one or more files in one format to another format.  The
source and target locations can be different from one another.

"""

__all__ = (
        "Error",
        "TransformFailedError",
        "UnknownTargetFormatError",

        "Transform",
        "FSTransform",
        )


import abc


class Error(Exception):
    pass

class TransformFailedError(Error):
    pass

class UnknownTargetFormatError(TransformFailedError):
    pass


class Transform(metaclass=abc.ABCMeta):
    """Transform a named resource from one format to another.

    The named resources are pulled from data stores.  It's up to each
    Transform class to determine the interface the stores must provide.

    """

    SOURCE_STORE = None
    SOURCE_FORMAT = None
    TARGET_STORE = None
    TARGET_FORMAT = None
    INTERMEDIATE_FORMATS = ()

    VALID_OVERRIDES = ("source_store", "source_format",
                       "target_store", "target_format")

    def __init__(self, overrides=None):

        self.args = {
                name: getattr(self, name.upper())
                for name in self.VALID_OVERRIDES}
        self.args.update({
                name: overrides.pop(name)
                for name in overrides 
                if name in self.VALID_OVERRIDES})
        if overrides:
            raise TypeError("Unknown overrides: {}".format(overrides))

    def transform(self, name, overrides=None, save=False):
        """Extract the named resource and transform.

          name - the name of the resource in the source store to
                transform.
          overrides - provides a means to override the default settings
                of the Transform object.
          save - save the transformed data to the target store.  Either
                way, the data will be returned.

        The data resulting from the transformation will be returned.

        """

        # incorporate the overrides
        kwargs = self.args.copy()
        kwargs.update({
                name: overrides.pop(name)
                for name in overrides 
                if name in self.VALID_OVERRIDES})
        if overrides:
            raise TypeError("Unknown overrides: {}".format(overrides))

        source = kwargs.pop("source_store")
        source_format = kwargs.pop("source_format")
        target = kwargs.pop("target_store")
        target_format = kwargs.pop("target_format")

        # do the work
        data = self.load(name, source, source_format)
        result = self.transform_data(name, data, source_format, target_format)
        if save:
            self.save(result, name, target, target_format)
        return result

    @abc.abstractmethod
    def load(self, name, source_store, source_format):
        """Get the data from the source_store.

        The data will be returned in the source_format.

        """

    @abc.abstractmethod
    def save(self, data, name, target_store, target_format):
        """Save the data to the store as a named resource.

        """

    @abc.abstractmethod
    def transform_data(self, data, name, source_format, target_format):
        """Perform the transform on the source data.
        
        The data will be returned in the target format. 

        """

        if source_format not in self.INTERMEDIATE_FORMATS:
            raise UnknownFormatError(source_format)
        if target_format not in self.INTERMEDIATE_FORMATS:
            raise UnknownFormatError(target_format)
        if (self.INTERMEDIATE_FORMATS.find(source_format)
                > self.INTERMEDIATE_FORMATS.find(target_format)):
            raise TransformFailedError("Target format precedes source format")

        if source_format == target_format:
            return data


class FSTransform(Transform):
    """A Transform with stores on the filesystem.

    """

    SOURCE_PATH = None
    TARGET_PATH = None

    @property
    def SOURCE_STORE(self):
        return self.SOURCE_PATH

    @property
    def TARGET_STORE(self):
        return self.TARGET_PATH




