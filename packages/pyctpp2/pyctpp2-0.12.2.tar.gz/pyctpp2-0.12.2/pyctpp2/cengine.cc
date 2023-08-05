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

#include "pyctpp2/cengine.h"
#include "pyctpp2/ctemplate.h"

#include <CTPP2Util.hpp>
#include <CTPP2VMSyscall.hpp>
#include <CTPP2SyscallFactory.hpp>
#include <CTPP2VM.hpp>
#include <CTPP2VMExecutable.hpp>
#include <CTPP2VMMemoryCore.hpp>
#include <CTPP2VMSTDLib.hpp>
#include <CTPP2FileSourceLoader.hpp>
#include <CTPP2Compiler.hpp>
#include <CTPP2Parser.hpp>
#include <CTPP2Exception.hpp>
#include <CTPP2ParserException.hpp>

#define __STDC_FORMAT_MACROS
#include <inttypes.h>

#include <dlfcn.h>
#include <stdio.h>

#include <limits>

using std::string;
using std::pair;
using std::vector;
using std::exception;
using std::runtime_error;
using std::bad_alloc;

using CTPP::CTPPException;
using CTPP::CTPPParserException;

namespace pyctpp2 {

CEngine::CEngine() : syscall_factory_(NULL) {}

CEngine::~CEngine() throw() {
  CTPP::STDLibInitializer::DestroyLibrary(*syscall_factory_);

  ExtraFnMap::iterator it = extra_fn_.begin();
  for (; it != extra_fn_.end(); ++it) {
    syscall_factory_->RemoveHandler(it->second.handler->GetName());
    delete it->second.handler;
  }

  delete syscall_factory_;
}

bool CEngine::Init(uint32_t arg_stack_size,
                   uint32_t code_stack_size,
                   uint32_t steps_limit,
                   uint32_t max_func) {
  arg_stack_size_ = arg_stack_size;
  code_stack_size_ = code_stack_size;
  steps_limit_ = steps_limit;
  try {
    syscall_factory_ = new CTPP::SyscallFactory(max_func);
    CTPP::STDLibInitializer::InitLibrary(*syscall_factory_);

    gettext_.InitSTDLibFunction(*syscall_factory_);

  } catch (...) {
    if (syscall_factory_ != NULL)
    {
      CTPP::STDLibInitializer::DestroyLibrary(*syscall_factory_);
      delete syscall_factory_;
    }
    last_error_type_ = kSystemErrorType;
    last_error_message_ = "Failed to init CEngine";
    return false;
  }

  return true;
}

bool CEngine::set_include_dirs(const std::vector<std::string> &dirs) {
  try {
    include_dirs_.clear();
    std::copy(dirs.begin(), dirs.end(), std::back_inserter(include_dirs_));
  } catch (exception &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = e.what();
    return false;
  }
  return true;
}


bool CEngine::LoadBytecode(const char *filename, CTemplate **tmpl) {
  try {
    *tmpl = new CTemplate(filename, kBytecodeSourceType, include_dirs_,
                         arg_stack_size_, code_stack_size_,
                         steps_limit_, syscall_factory_, &gettext_);
  } catch (bad_alloc) {
    last_error_type_ = kNoMemoryErrorType;
    last_error_message_ = "";
    return false;
  } catch (CTPPException &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = e.what();
    return false;
  } catch (exception &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = e.what();
    return false;
  } catch (...) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = "unknown error occured";
    return false;
  }

  return true;
}

bool CEngine::Parse(const char *filename, CTemplate **tmpl) {
  try {
    *tmpl = new CTemplate(filename, kFileSourceType, include_dirs_,
                         arg_stack_size_, code_stack_size_, steps_limit_,
                         syscall_factory_, &gettext_);
  } catch (bad_alloc) {
    last_error_type_ = kNoMemoryErrorType;
    last_error_message_ = "";
    return false;
  } catch (CTPPParserException &e) {
    const size_t len = std::numeric_limits<uint32_t>::digits10 + 1;
    char buf[len] = { '\0' };
    string line;
    string pos;

    int res = snprintf(buf, len, "%"PRIu32, static_cast<uint32_t>(e.GetLine()));
    if (!(res < 0 || static_cast<size_t>(res) == len)) {
      line = string(buf);
    }

    memset(buf, 0, len);
    res = snprintf(buf, len, "%"PRIu32, static_cast<uint32_t>(e.GetLinePos()));
    if (!(res < 0 || static_cast<size_t>(res) == len)) {
      pos = string(buf);
    }

    last_error_type_ = kSyntaxErrorType;
    last_error_message_ = string(e.what()) + ": " + filename +
        ", line " + line + ", position " + pos;
    return false;
  } catch (CTPPException &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = string(e.what()) + ": " + filename;
    return false;
  } catch (exception &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = string(e.what()) + ": " + filename;
    return false;
  } catch (...) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = string("unknown error occured: ") + filename;
    return false;
  }

  return true;
}

bool CEngine::ParseText(const char *text, CTemplate **tmpl) {
  try {
    *tmpl = new CTemplate(text, kTextSourceType, include_dirs_,
                         arg_stack_size_, code_stack_size_, steps_limit_,
                         syscall_factory_, &gettext_);
  } catch (std::bad_alloc) {
    last_error_type_ = kNoMemoryErrorType;
    last_error_message_ = "";
    return false;
  } catch (CTPPParserException &e) {
    const size_t len = std::numeric_limits<uint32_t>::digits10 + 1;
    char buf[len] = { '\0' };
    string line;
    string pos;

    int res = snprintf(buf, len, "%"PRIu32, static_cast<uint32_t>(e.GetLine()));
    if (!(res < 0 || static_cast<size_t>(res) == len)) {
      line = string(buf);
    }

    memset(buf, 0, len);
    res = snprintf(buf, len, "%"PRIu32, static_cast<uint32_t>(e.GetLinePos()));
    if (!(res < 0 || static_cast<size_t>(res) == len)) {
      pos = string(buf);
    }

    last_error_type_ = kSyntaxErrorType;
    last_error_message_ =
        string(e.what()) + ": line " + line + ", position " + pos;
    return false;
  } catch (CTPPException &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = e.what();
    return false;
  } catch (exception &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = e.what();
    return false;
  } catch (...) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = "unknown error occured";
    return false;
  }

  return true;
}

bool CEngine::AddUserFunction(const char *libname, const char *instance) {
  ExtraFnMap::iterator it = extra_fn_.find(string(instance));
  if (it != extra_fn_.end() || !syscall_factory_->GetHandlerByName(instance)) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ =
        string("user function `") + instance + "` already present";
    return false;
  }

  void *library = dlopen(libname, RTLD_NOW | RTLD_GLOBAL);
  if (!library) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = string("can't load library `") +
        libname + "`: `" + dlerror() + "`";
    return false;
  }

  // Init String
  const char *kInitSymPrefix =  "_init";
  size_t len = strlen(instance);
  char *init_str =
      reinterpret_cast<char *>(malloc(sizeof(char) *
                                      (len + sizeof(kInitSymPrefix) + 1)));
  if (!init_str) {
    last_error_type_ = kNoMemoryErrorType;
    last_error_message_ = "";
    return false;
  }
  memcpy(init_str, instance, len + 1);
  memcpy(init_str + len, kInitSymPrefix, sizeof(kInitSymPrefix));
  init_str[len + sizeof(kInitSymPrefix)] = '\0';

  // This is UGLY hack to avoid stupid gcc warnings
  // this code violates C++ Standard
  // InitPtr initPtr = (InitPtr)dlsym(library, initStr);
  void *ptr = dlsym(library, init_str);
  free(init_str);

  if (!ptr) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = string("in `") +
        libname + "`: cannot find user function `" + instance + "`";
    return false;
  }

  // This is UGLY hack to avoid stupid gcc warnings
  InitPtr init_ptr = NULL;
  // and this code - is correct C++ code
  memcpy(&init_ptr, &ptr, sizeof(void *));

  CTPP::SyscallHandler *handler =
      reinterpret_cast<CTPP::SyscallHandler *>(((*init_ptr)()));

  LoadableUserFunction loadable;

  loadable.filename = libname;
  loadable.func_name = instance;
  loadable.handler = handler;

  extra_fn_.insert(pair<string, LoadableUserFunction>(instance, loadable));

  syscall_factory_->RegisterHandler(handler);

  return true;
}

bool CEngine::AddTranslation(const char *filename, const char *domain,
                             const char *language) {

  try {
    gettext_.AddTranslation(filename, domain, language);
  } catch (CTPPException &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = e.what();
    return false;
  } catch (exception &e) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = e.what();
    return false;
  } catch (...) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = "unknown error occured";
    return false;
  }
  return true;
}

void CEngine::SetDefaultDomain(const char *domain) {
      gettext_.SetDefaultDomain(domain);
}

}  // namespace pyctpp2

