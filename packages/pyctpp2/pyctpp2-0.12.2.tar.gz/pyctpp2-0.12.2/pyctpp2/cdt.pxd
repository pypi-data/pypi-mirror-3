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

from libc.stdint cimport uint32_t, int64_t
from string cimport const_char_ptr

cdef extern from "CDT.hpp" namespace "CTPP":
    cdef cppclass CDT:
        CDT()
        void PushBack(CDT &)
        CDT& operator[](const_char_ptr)

cdef extern from "pyctpp2/cdt_funcs.h" namespace "pyctpp2":
    cdef void CDTAssign(CDT *, int64_t)
    cdef void CDTAssign(CDT *, double)
    cdef void CDTAssign(CDT *, const_char_ptr)
    cdef void CreateListCDT(CDT *)
    cdef void CreateDictCDT(CDT *)
    cdef bint IsDictCDT(CDT &)
