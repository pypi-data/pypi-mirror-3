# a shim until source_to_code is supported natively

import importlib.machinery
from importlib._bootstrap import *


class SourceFileLoader(importlib.machinery.SourceFileLoader):

    def source_to_code(self, source_bytes, source_path):
        """Return the code object for the module's source."""
        code_object = _call_with_frames_removed(compile,
                          source_bytes, source_path, 'exec',
                          dont_inherit=True)
        return code_object

    def get_code(self, fullname):
        """Concrete implementation of InspectLoader.get_code.

        Reading of bytecode requires path_stats to be implemented. To write
        bytecode, set_data must also be implemented.

        """
        source_path = self.get_filename(fullname)
        source_mtime = None
        try:
            bytecode_path = cache_from_source(source_path)
        except NotImplementedError:
            bytecode_path = None
        else:
            try:
                st = self.path_stats(source_path)
            except NotImplementedError:
                pass
            else:
                source_mtime = int(st['mtime'])
                try:
                    data = self.get_data(bytecode_path)
                except IOError:
                    pass
                else:
                    try:
                        bytes_data = self._bytes_from_bytecode(fullname, data,
                                                               bytecode_path,
                                                               st)
                    except (ImportError, EOFError):
                        pass
                    else:
                        _verbose_message('{} matches {}', bytecode_path,
                                        source_path)
                        found = marshal.loads(bytes_data)
                        if isinstance(found, _code_type):
                            _imp._fix_co_filename(found, source_path)
                            _verbose_message('code object from {}',
                                            bytecode_path)
                            return found
                        else:
                            msg = "Non-code object in {}"
                            raise ImportError(msg.format(bytecode_path),
                                              name=fullname, path=bytecode_path)
        source_bytes = self.get_data(source_path)
        code_object = self.source_to_code(source_bytes)
        _verbose_message('code object from {}', source_path)
        if (not sys.dont_write_bytecode and bytecode_path is not None and
            source_mtime is not None):
            data = bytearray(_MAGIC_BYTES)
            data.extend(_w_long(source_mtime))
            data.extend(_w_long(len(source_bytes)))
            data.extend(marshal.dumps(code_object))
            try:
                self.set_data(bytecode_path, data)
                _verbose_message('wrote {!r}', bytecode_path)
            except NotImplementedError:
                pass
        return code_object
