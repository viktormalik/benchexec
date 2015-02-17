"""
BenchExec is a framework for reliable benchmarking.
This file is part of BenchExec.

Copyright (C) 2007-2015  Dirk Beyer
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import os

import benchexec.util as util
import benchexec.tools.template
import benchexec.result as result

class Tool(benchexec.tools.template.BaseTool):

    def executable(self):
        return util.find_executable('pblast.opt')


    def program_files(self, executable):
        executableDir = os.path.dirname(executable)
        return [executableDir]


    def working_directory(self, executable):
        return os.curdir


    def environment(self, executable):
        executableDir = os.path.dirname(executable)
        workingDir = self.working_directory(executable)
        return {"additionalEnv" : {'PATH' :  ':' + (os.path.relpath(executableDir, start=workingDir))}}


    def version(self, executable):
        return self._version_from_tool(executable)[6:11]


    def cmdline(self, blastExe, options, sourcefiles, propertyfile, rlimits):
        workingDir = self.working_directory(blastExe)
        ocamlExe = util.find_executable('ocamltune')
        return [os.path.relpath(ocamlExe, start=workingDir), os.path.relpath(blastExe, start=workingDir)] + options + sourcefiles


    def name(self):
        return 'BLAST'


    def determine_result(self, returncode, returnsignal, output, isTimeout):
        status = result.STATUS_UNKNOWN
        for line in output:
            if line.startswith('Error found! The system is unsafe :-('):
                status = result.STATUS_FALSE_REACH
            elif line.startswith('No error found.  The system is safe :-)'):
                status = result.STATUS_TRUE_PROP
            elif line.startswith('Fatal error: exception Out_of_memory'):
                status = 'OUT OF MEMORY'
            elif line.startswith('Error: label \'ERROR\' appears multiple times'):
                status = 'ERROR'
            elif (returnsignal == 9):
                status = 'TIMEOUT'
            elif 'Ack! The gremlins again!' in line:
                status = 'EXCEPTION (Gremlins)'
        return status