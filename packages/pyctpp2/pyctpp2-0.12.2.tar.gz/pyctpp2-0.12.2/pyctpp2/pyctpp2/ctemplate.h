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

#ifndef PYCTPP2_TEMPLATE_H_
#define PYCTPP2_TEMPLATE_H_

#include "pyctpp2/error_type.h"

#include <stdint.h>
#include <string>
#include <vector>

namespace CTPP {
class SyscallFactory;
class VMExecutable;
class VMMemoryCore;
class CTPP2GetText;
class CDT;
}  // namespace CTPP

namespace pyctpp2 {

enum SourceType { kBytecodeSourceType, kFileSourceType, kTextSourceType };

class CTemplate {
 public:
  CTemplate(const char *src, SourceType type,
           const std::vector<std::string> &include_dirs,
           uint32_t arg_stack_size,
           uint32_t code_stack_size,
           uint32_t steps_limit,
           CTPP::SyscallFactory *syscall_factory,
           CTPP::CTPP2GetText *gettext);

  ~CTemplate() throw();

  bool SaveBytecode(const char *filename);

  bool Render(CTPP::CDT *params, const char *language, std::string *result);

  std::string last_error_message() const { return last_error_message_; }

  ErrorType last_error_type() const { return last_error_type_; }

  std::string name() const { return name_; }

 private:
  CTemplate();
  CTemplate(const CTemplate &rhs);
  CTemplate & operator=(const CTemplate &rhs);

  CTPP::VMExecutable *core_;
  uint32_t core_size_;
  CTPP::VMMemoryCore *vm_mem_core_;

  const uint32_t arg_stack_size_;
  const uint32_t code_stack_size_;
  const uint32_t steps_limit_;

  CTPP::SyscallFactory *syscall_factory_;
  CTPP::CTPP2GetText *gettext_;

  ErrorType last_error_type_;
  std::string last_error_message_;

  std::string name_;
};

}  // namespace pyctpp2

#endif  // PYCTPP2_TEMPLATE_H_


