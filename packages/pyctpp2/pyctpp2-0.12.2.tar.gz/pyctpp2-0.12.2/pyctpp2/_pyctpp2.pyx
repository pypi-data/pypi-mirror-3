# encoding: utf-8
# Copyright (c) 2012 Volvox Development Team
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

from cengine cimport CEngine
from ctemplate cimport CTemplate
from cdt cimport CDT, CDTAssign, CreateListCDT, CreateDictCDT, IsDictCDT
cimport error_type as err
from libc.stdint cimport uint32_t, int64_t
from string cimport string, const_char_ptr
from cpython cimport exc
from cython.operator cimport dereference as deref
from libcpp.vector cimport vector
from libintl cimport bindtextdomain, textdomain

include "pyversion.pxi"

cdef int MAX_LEVEL = 10

IF PYTHON_VERSION >= 3:
    ctypedef str StringType
    cdef str string_type_to_str():
        return str(str)
    cdef bytes str_to_bytes(StringType s):
        cdef bytes tmp = s.encode('UTF-8')
        return tmp
    cdef StringType c_str_to_str(const_char_ptr c):
        return c.decode('UTF-8', 'strict')
    cdef bint isunicode(s):
        return isinstance(s, str)
ELSE:
    from cpython cimport unicode

    ctypedef bytes StringType
    cdef bytes string_type_to_str():
        return str(unicode)
    cdef bytes str_to_bytes(StringType s):
        return s
    cdef StringType c_str_to_str(const_char_ptr c):
        return c
    cdef bint isunicode(s):
        return isinstance(s, unicode)

cdef raise_error(err.ErrorType etype, string message_):
    cdef const_char_ptr c_str = message_.c_str()
    cdef StringType message = c_str_to_str(c_str)
    if etype == err.kNoErrorType:
        raise Exception(message)
    elif etype == err.kSyntaxErrorType:
        raise SyntaxError(message)
    elif etype == err.kNoMemoryErrorType:
        exc.PyErr_NoMemory()
    elif etype == err.kSystemErrorType:
        raise SystemError(message)
    elif etype == err.kIOErrorType:
        raise IOError(message)

cdef class Template

cdef class Engine:
    """CTPP2 Engine class."""
    cdef CEngine *thisptr
    cdef object include_dirs

    property path:
        """Template path."""

        def __get__(self):
            return self.include_dirs

        def __set__(self, value):
            cdef vector[string] dirs
            cdef char *c_str
            cdef string s_str
            cdef bytes bt_str

            self.include_dirs = value
            for v in self.include_dirs:
                if isunicode(v):
                    bt_str = str_to_bytes(v)
                elif isinstance(v, bytes):
                    bt_str = v
                else:
                    raise ValueError("It has invalid value type")
                c_str = bt_str
                s_str.clear()
                s_str.append(c_str)
                dirs.push_back(s_str)
            self.thisptr.set_include_dirs(dirs)

        def __del__(self):
            cdef vector[string] dirs
            self.include_dirs = list()
            self.thisptr.set_include_dirs(dirs)


    def __cinit__(self):
        self.thisptr = new CEngine()

    def __dealloc__(self):
        del self.thisptr

    def __init__(self,
            uint32_t arg_stack_size=10240,
            uint32_t code_stack_size=10240,
            uint32_t steps_limit=1048576,
            uint32_t max_func=1024):
        """x.__init__(arg_stack_size=10240,
                      code_stack_size=10240,
                      steps_limit=1048576,
                      max_func=1024) --

        'arg_stack_size'  - Max. size of stack of arguments
        'code_stack_size' - Max. stack size
        'max_func'        - Max. number of functions in CTPP standard library

        Normally you should now change these parameters, to explanation please
        refer to CTPP library documentation.

        'steps_limit' - template execution limit (in steps). Default value
        is 1 048 576 (1024*1024). You can limit template execution time by
        specifying this parameter [default: 1048576].

        Note, if execution limit is reached, template engine generates error
        and you should use try/except to catch it.
        """

        cdef string err_msg
        if not self.thisptr.Init(arg_stack_size, code_stack_size,
                steps_limit, max_func):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);

    def load_bytecode(self, str filename):
        """x.load_bytecode(filename) -- load precompiled template from
        specified file.

        ATTENTION: you should specify FULL path to precompiled file,
        CTPP DOES NOT uses include_dirs to search bytecode!
        """
        cdef CTemplate *tmpl
        cdef string err_msg
        cdef bytes filename_bt = str_to_bytes(filename)
        if not self.thisptr.LoadBytecode(filename_bt, &tmpl):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);
        return self.create_template(tmpl)

    def parse(self, str filename, str encoding="UTF-8"):
        """x.parse(filename, encoding="UTF-8") -- compile source code of
        template to CTPP bytecode.
        """

        cdef CTemplate *tmpl
        cdef string err_msg
        cdef bytes filename_bt = str_to_bytes(filename)
        if not self.thisptr.Parse(filename_bt, &tmpl):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);
        return self.create_template(tmpl, encoding)

    def parse_text(self, str text):
        """x.parse_text(text) -- compile text of template to CTPP bytecode."""
        cdef CTemplate *tmpl
        cdef string err_msg
        cdef bytes text_bt = str_to_bytes(text)
        if not self.thisptr.ParseText(text_bt, &tmpl):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);
        return self.create_template(tmpl)

    def add_translation(self,
            str filename,
            str domain,
            str language):
        """x.add_translation(filename, domain, language) -- add translation."""
        if not self.thisptr.AddTranslation(filename, domain, language):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);

    def set_default_domain(self, str domain):
        """x.set_default_domain(domain) -- set default i18n domain."""
        self.thisptr.SetDefaultDomain(domain)

    def add_user_function(self, str libname, str instance):
        """x.add_user_function(libname, instance) -- add user-defined function
        from external storage.

        If you have a shared library wich contains compiled user-defined
        functions, you may load it by calling method add_user_function().
        Please refer to documentation to explain, how you can write
        user-defined CTPP functions in C++.
        """

        cdef string err_msg
        if not self.thisptr.AddUserFunction(libname, instance):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);

    cdef Template create_template(self, CTemplate *template, str encoding="UTF-8"):
        cdef Template tmpl
        tmpl = Template.__new__(Template)
        tmpl.thisptr = template
        tmpl.engine = self
        tmpl.encoding = encoding
        return tmpl


cdef class Template:
    """CTPP2 Template class."""
    cdef CTemplate *thisptr
    cdef Engine engine
    cdef str encoding

    property name:
        """Template text source filename."""

        def __get__(self):
            cdef const_char_ptr c_str
            cdef string s_str
            cdef bytes bt_str

            s_str = self.thisptr.name()
            c_str = s_str.c_str()
            bt_str = c_str_to_str(c_str)
            return bt_str

    def __cinit__(self):
        self.thisptr = NULL
        self.engine = None

    def __dealloc__(self):
        del self.thisptr

    def __init__(self):
        raise TypeError("This class cannot be instantiated from Python")

    def save_bytecode(self, str filename):
        """x.save_bytecode(filename) -- save precompiled template to
        specified file.
        """

        cdef string err_msg
        cdef bytes filename_bt = str_to_bytes(filename)
        if not self.thisptr.SaveBytecode(filename_bt):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);

    def render(self, args, language=None):
        """x.render(args, language=None) -- render with variables."""
        cdef CDT cdt
        cdef int idx
        CreateDictCDT(&cdt)
        traverse(args, &cdt)

        cdef string err_msg
        cdef string result
        cdef bytes bt_str
        cdef const_char_ptr c_str

        c_str = NULL
        if language is not None:
            bt_str = str_to_bytes(language)
            c_str = bt_str

        if not self.thisptr.Render(&cdt, c_str, &result):
            err_msg = self.thisptr.last_error_message()
            raise_error(self.thisptr.last_error_type(), err_msg);

        c_str = result.c_str()
        return c_str.decode(self.encoding, 'strict')


cdef traverse(obj, CDT *cdt, int level=0):
    cdef int idx
    cdef CDT inner_cdt
    cdef CDT dict_cdt
    cdef char *c_str
    cdef bytes bt_str
    cdef StringType key
    cdef int valid_key_type

    level += 1

    if isinstance(obj, (int, long, bool)):
        CDTAssign(cdt, <int64_t>obj)
    elif isinstance(obj, float):
        CDTAssign(cdt, <double>obj)
    elif isunicode(obj):
        bt_str = obj.encode('UTF-8')
        c_str = bt_str
        CDTAssign(cdt, c_str)
    elif isinstance(obj, bytes):
        bt_str = obj
        c_str = bt_str
        CDTAssign(cdt, c_str)
    elif isinstance(obj, dict) or hasattr(obj, '__dict__'):
        if hasattr(obj, '__dict__'):
            obj = obj.__dict__

        CreateDictCDT(cdt)
        dict_cdt = CDT()

        try:
            for key in obj:
                pass
            valid_key_type = True
        except TypeError:
            valid_key_type = False
            
        if valid_key_type:
            for key, value in obj.items():
                inner_cdt = CDT()
                if level > MAX_LEVEL:
                    raise Exception("Max level of recursion is exceed")

                traverse(value, &inner_cdt, level)
                IF PYTHON_VERSION >= 3:
                    bt_str = key.encode('UTF-8')
                    c_str = bt_str
                ELSE:
                    c_str = key
                (deref(cdt))[c_str] = inner_cdt

    elif hasattr(obj, '__iter__') and not hasattr(obj, 'read'):
        CreateListCDT(cdt)
        for elem in obj:
            inner_cdt = CDT()
            if level > MAX_LEVEL:
                raise Exception("Max level of recursion is exceed")
            traverse(elem, &inner_cdt, level)
            cdt.PushBack(inner_cdt)

