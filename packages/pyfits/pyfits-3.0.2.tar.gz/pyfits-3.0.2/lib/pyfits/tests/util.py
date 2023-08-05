"""Test utility functions."""

import sys
import warnings

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from io import BytesIO
except ImportError:
    BytesIO = StringIO


class CaptureStdout(object):
    """A simple context manager for redirecting stdout to a StringIO buffer."""

    def __init__(self):
        self.io = StringIO()

    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = self.io
        return self.io

    def __exit__(self, *args, **kwargs):
        sys.stdout = self._original_stdout
        self.io.close()


if hasattr(warnings, 'catch_warnings'):
    catch_warnings = warnings.catch_warnings
else:
    # For Python2.5, backport the catch_warnings context manager
    class WarningMessage(object):

        """Holds the result of a single showwarning() call."""

        _WARNING_DETAILS = ("message", "category", "filename", "lineno",
                            "file", "line")

        def __init__(self, message, category, filename, lineno, file=None,
                        line=None):
            local_values = locals()
            for attr in self._WARNING_DETAILS:
                setattr(self, attr, local_values[attr])
            self._category_name = category.__name__ if category else None

        def __str__(self):
            return ("{message : %r, category : %r, filename : %r, lineno : %s,"
                    " line : %r}" % (self.message, self._category_name,
                                     self.filename, self.lineno, self.line))
    class catch_warnings(object):

        """A context manager that copies and restores the warnings filter upon
        exiting the context.

        The 'record' argument specifies whether warnings should be captured by
        a custom implementation of warnings.showwarning() and be appended to a
        list returned by the context manager. Otherwise None is returned by the
        context manager. The objects appended to the list are arguments whose
        attributes mirror the arguments to showwarning().

        The 'module' argument is to specify an alternative module to the module
        named 'warnings' and imported under that name. This argument is only
        useful when testing the warnings module itself.

        """

        def __init__(self, record=False, module=None):
            """Specify whether to record warnings and if an alternative module
            should be used other than sys.modules['warnings'].

            For compatibility with Python 3.0, please consider all arguments to
            be keyword-only.

            """
            self._record = record
            self._module = (sys.modules['warnings']
                            if module is None else module)
            self._entered = False

        def __repr__(self):
            args = []
            if self._record:
                args.append("record=True")
            if self._module is not sys.modules['warnings']:
                args.append("module=%r" % self._module)
            name = type(self).__name__
            return "%s(%s)" % (name, ", ".join(args))

        def __enter__(self):
            if self._entered:
                raise RuntimeError("Cannot enter %r twice" % self)
            self._entered = True
            self._filters = self._module.filters
            self._module.filters = self._filters[:]
            self._showwarning = self._module.showwarning
            if self._record:
                log = []
                def showwarning(*args, **kwargs):
                    log.append(WarningMessage(*args, **kwargs))
                self._module.showwarning = showwarning
                return log
            else:
                return None

        def __exit__(self, *exc_info):
            if not self._entered:
                raise RuntimeError("Cannot exit %r without entering first" %
                                   self)
            self._module.filters = self._filters
            self._module.showwarning = self._showwarning
