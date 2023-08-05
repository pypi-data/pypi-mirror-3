// Copyright (c) 2012 Volvox Development Team
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//
// Author: Konstantin Lepa <konstantin.lepa@gmail.com>

#ifndef PYCTPP2_CDT_FUNCS_H_
#define PYCTPP2_CDT_FUNCS_H_

#include <stdint.h>
#include <CDT.hpp>

namespace pyctpp2 {

template<typename T>
void CDTAssign(CTPP::CDT *cdt, const T &value) { cdt->operator=(value); }

void CreateListCDT(CTPP::CDT *cdt) { *cdt = CTPP::CDT(CTPP::CDT::ARRAY_VAL); }

void CreateDictCDT(CTPP::CDT *cdt) { *cdt = CTPP::CDT(CTPP::CDT::HASH_VAL); }

bool IsDictCDT(const CTPP::CDT &cdt) {
  return cdt.GetType() == CTPP::CDT::HASH_VAL;
}

}  // namespace pyctpp2

#endif  // PYCTPP2_CDT_FUNCS_H_

