# -*- coding: utf-8 -*-
#Copyright (C) 2012 Red Hat, Inc.
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the "Software"), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
import yamlish
import logging

PASS = 0
SKIP = 1
TBD = 2  #IGNORE:W0511
FAIL = 3
ERROR = 4

__docformat__ = 'reStructuredText'
__version__ = "0.6"
__author__ = u"Matěj Cepl <mcepl_at_redhat_dot_com>"

class TAPGenerator(object):
    def __init__(self):
        self.translate_msg = {
            PASS: self._pass,
            SKIP: self._skip,
            TBD: self._tbd,
            FAIL: self._fail,
            ERROR: self._error,
        }

    def _indent(self, instr, indent="\t"):
        return "\n".join(indent + line
                     for line in instr.split("\n"))

    def _format_string(self, result, reason, name, data):
        out_str = result
        if name is not None:
            out_str += " - %s" % name
        if reason:
            out_str += "\t# %s" % reason
        if data:
            logging.debug("data:\n%s", data)
            yamlish_str = yamlish.dumps(data)
            logging.debug("yamlish_str:\n%s", yamlish_str)
            line_str = self._indent(yamlish_str, "  ")
            logging.debug("line_str:\n%s", line_str)
            out_str += "\n%s" % line_str.rstrip()
        return out_str

    def _pass(self, name, desc, data):
        return self._format_string("ok", desc, name, data)

    def _skip(self, name, desc, data):
        skip_msg = "SKIP"
        if desc is not None:
            skip_msg += " " + desc
        return self._format_string("ok", skip_msg, name, data)

    def _tbd(self, name, desc, data):
        return self._format_string("todo", desc, name, data)

    def _fail(self, name, desc, data):
        return self._format_string("not ok", "FAIL " + desc, name, data)

    def _error(self, name, desc, data):
        return self._format_string("not ok", "ERROR " + desc, name, data)

    def format_TAP_msg(self, result, name, desc="", data=None):
        return self.translate_msg[result](name, desc, data)


if __name__ == '__main__':
    pass
