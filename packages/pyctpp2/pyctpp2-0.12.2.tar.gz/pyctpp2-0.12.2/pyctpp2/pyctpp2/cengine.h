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

#ifndef PYCTPP2_ENGINE_H_
#define PYCTPP2_ENGINE_H_

#include "pyctpp2/error_type.h"

#include <stdint.h>
#include <strings.h>

#include <map>
#include <string>
#include <vector>
#include <CTPP2GetText.hpp>

namespace CTPP {
class SyscallHandler;
class SyscallFactory;
}  // namespace CTPP

namespace pyctpp2 {

class CTemplate;

class CEngine {
 public:
  CEngine();

  ~CEngine() throw();

  bool Init(uint32_t arg_stack_size, uint32_t code_stack_size,
            uint32_t steps_limit, uint32_t max_func);

  bool set_include_dirs(const std::vector<std::string> &dirs);

  bool LoadBytecode(const char *filename, CTemplate **tmpl);

  bool Parse(const char *filename, CTemplate **tmpl);

  bool ParseText(const char *text, CTemplate **tmpl);

  bool AddUserFunction(const char *libname, const char *instance);

  bool AddTranslation(const char *fname, const char *domain, const char *lang);

  void SetDefaultDomain(const char *domain);

  std::string last_error_message() const { return last_error_message_; }

  ErrorType last_error_type() const { return last_error_type_; }

 private:
  typedef CTPP::SyscallHandler *((*InitPtr)());

  CTPP::SyscallFactory *syscall_factory_;

  class HandlerSort:
      public std::binary_function<std::string, std::string, bool> {
   public:
    inline bool operator()(const std::string &x, const std::string &y) const {
      return (strcasecmp(x.c_str(), y.c_str()) > 0);
    }
  };

  struct LoadableUserFunction
  {
    std::string filename;
    std::string func_name;
    CTPP::SyscallHandler *handler;
  };

  typedef std::map<std::string, LoadableUserFunction, HandlerSort> ExtraFnMap;

  ExtraFnMap               extra_fn_;
  std::vector<std::string> include_dirs_;

  uint32_t arg_stack_size_;
  uint32_t code_stack_size_;
  uint32_t steps_limit_;

  ErrorType last_error_type_;
  std::string last_error_message_;

  CTPP::CTPP2GetText gettext_;
};

}  // namespace pyctpp2

#endif  // PYCTPP2_ENGINE_H_

