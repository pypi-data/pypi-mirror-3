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

#include "pyctpp2/ctemplate.h"

#include <CTPP2Util.hpp>
#include <CTPP2VMSyscall.hpp>
#include <CTPP2SyscallFactory.hpp>
#include <CTPP2VM.hpp>
#include <CDT.hpp>
#include <CTPP2VMExecutable.hpp>
#include <CTPP2VMMemoryCore.hpp>
#include <CTPP2VMSTDLib.hpp>
#include <CTPP2JSONParser.hpp>
#include <CTPP2StringOutputCollector.hpp>
#include <CTPP2Logger.hpp>
#include <CTPP2FileSourceLoader.hpp>
#include <CTPP2VMOpcodeCollector.hpp>
#include <CTPP2Compiler.hpp>
#include <CTPP2Parser.hpp>
#include <CTPP2VMDumper.hpp>
#include <CTPP2GetText.hpp>

#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <stdio.h>
#include <locale.h>
#include <stdlib.h>

#include <stdexcept>

using std::string;
using std::runtime_error;

namespace {

class PyLogger: public CTPP::Logger {
 public:
  ~PyLogger() throw() { ;; }
 private:

  int WriteLog(const uint32_t, const char *, const uint32_t) { return true; }
};

class TextLoader: public CTPP::CTPP2SourceLoader {
 public:
  TextLoader() {}

  ~TextLoader() throw() {}

  int32_t LoadTemplate(const char *text) {
    text_ = text;
    return 0;
  }

  const char * GetTemplate(uint32_t &size) {
    size = text_.size();
    return text_.data();
  }

  CTPP::CTPP2SourceLoader * Clone() { return new TextLoader; }

 private:
  std::string text_;
};

}  // namespace

namespace pyctpp2 {

CTemplate::CTemplate(const char *src, SourceType type,
                    const std::vector<std::string> &include_dirs,
                    uint32_t arg_stack_size,
                    uint32_t code_stack_size,
                    uint32_t steps_limit,
                    CTPP::SyscallFactory *syscall_factory,
                    CTPP::CTPP2GetText *gettext) :
    core_(NULL),
    vm_mem_core_(NULL),
    arg_stack_size_(arg_stack_size),
    code_stack_size_(code_stack_size),
    steps_limit_(steps_limit),
    syscall_factory_(syscall_factory),
    gettext_(gettext) {

  if (type == kBytecodeSourceType) {
    struct stat st;

    if (stat(src, &st) == 1) {
      throw runtime_error(string("No such file ") + src);
    } else {
      struct stat st;
      if (stat(src, &st) == -1) {
        string msg("Can't get size of bytecode ");
        msg.append(src);
        msg.append(":");
        throw CTPP::CTPPUnixException(msg.c_str(), errno);
      }

      core_size_ = st.st_size;
      if (!core_size_) {
        string msg("Can't get size of file ");
        msg.append(src);
        throw CTPP::CTPPLogicError(msg.c_str());
      }

      FILE *F = fopen(src, "r");
      if (!F) {
        string msg("Can't open file ");
        msg.append(src);
        msg.append(":");
        throw CTPP::CTPPUnixException(msg.c_str(), errno);
      }

      core_ = reinterpret_cast<CTPP::VMExecutable *>(malloc(core_size_));
      fread(core_, core_size_, 1, F);
      fclose(F);

      if (core_->magic[0] == 'C' &&
          core_->magic[1] == 'T' &&
          core_->magic[2] == 'P' &&
          core_->magic[3] == 'P') {
        vm_mem_core_ = new CTPP::VMMemoryCore(core_);
      } else {
        free(core_);

        string msg(src);
        msg.append(" is not an CTPP bytecode file");
        throw CTPP::CTPPLogicError(msg.c_str());
      }
    }
  } else {
    CTPP::CTPP2FileSourceLoader file_loader;
    file_loader.SetIncludeDirs(include_dirs);
    TextLoader txt_loader;

    CTPP::CTPP2SourceLoader *src_loader = &file_loader;
    if (type == kTextSourceType) src_loader = &txt_loader;

    src_loader->LoadTemplate(src);

    CTPP::VMOpcodeCollector  vm_op_collector;
    CTPP::StaticText         syscalls;
    CTPP::StaticData         static_data;
    CTPP::StaticText         static_txt;
    CTPP::HashTable          hash_tbl;
    CTPP::CTPP2Compiler compiler(vm_op_collector, syscalls,
                           static_data, static_txt, hash_tbl);

    CTPP::CTPP2Parser parser(src_loader, &compiler,
                       (type == kTextSourceType) ? "direct source" : src);

    parser.Compile();

    uint32_t code_size = 0;
    const CTPP::VMInstruction *vm_instr = vm_op_collector.GetCode(code_size);

    CTPP::VMDumper dumper(code_size, vm_instr, syscalls,
                    static_data, static_txt, hash_tbl);
    const CTPP::VMExecutable *prg_core = dumper.GetExecutable(core_size_);

    core_ = reinterpret_cast<CTPP::VMExecutable *>(malloc(core_size_));
    memcpy(core_, prg_core, core_size_);
    vm_mem_core_ = new CTPP::VMMemoryCore(core_);

    if (type == kFileSourceType) name_ = file_loader.GetTemplateName();
  }
}

CTemplate::~CTemplate() throw() {
  delete vm_mem_core_;
  free(core_);
}

bool CTemplate::Render(CTPP::CDT *params, const char *language,
                       std::string *result) {
  uint32_t i_pointer = 0;
  std::string res;

  std::string tmp;
  if (language != NULL) {
    tmp.assign(language);
    gettext_->SetLanguage(*syscall_factory_, language);
  }

  try {
    CTPP::StringOutputCollector out_collector(*result);
    PyLogger logger;

    CTPP::VM vm(const_cast<CTPP::SyscallFactory *>(syscall_factory_),
                arg_stack_size_, code_stack_size_, steps_limit_);
    vm.Init(vm_mem_core_, &out_collector, &logger);
    vm.Run(vm_mem_core_, &out_collector, i_pointer, *params, &logger);
  } catch (CTPP::CTPPException &e) {
    last_error_type_ = kIOErrorType;
    last_error_message_ = string(e.what()) + ": " + name_;
    return false;
  } catch (std::exception &e) {
    last_error_type_ = kIOErrorType;
    last_error_message_ = string(e.what()) + ": " + name_;
    return false;
  } catch (...) {
    last_error_type_ = kSystemErrorType;
    last_error_message_ = string("Unknown error occured") + ": " + name_;
    return false;
  }

  return true;
}

bool CTemplate::SaveBytecode(const char *filename) {
  FILE *file = fopen(filename, "a");
  if (!file) {
    last_error_type_ = kIOErrorType;
    last_error_message_ =
        string("Can't save bytecode: ") + strerror(errno) + ": " + filename;
    return false;
  }

  fwrite(core_, core_size_, 1, file);
  fclose(file);

  return true;
}

}  // namespace pyctpp2

