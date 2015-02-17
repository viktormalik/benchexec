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
    """
    This class serves as tool adaptor for ESBMC (http://www.esbmc.org/)
    """

    def executable(self):
        return util.find_executable('esbmc')


    def program_files(self, executable):
        executableDir = os.path.dirname(executable)
        return [executableDir]


    def working_directory(self, executable):
        executableDir = os.path.dirname(executable)
        return executableDir


    def environment(self, executable):
        return {"additionalEnv" : {'PATH' :  ':.'}}


    def version(self, executable):
        return self._version_from_tool(executable)

    def name(self):
        return 'ESBMC'


    def cmdline(self, executable, options, sourcefiles, propertyfile, rlimits):
        assert len(sourcefiles) == 1, "only one sourcefile supported"
        sourcefile = sourcefiles[0]
        workingDir = self.working_directory(executable)
        return [os.path.relpath(executable, start=workingDir)] + options + [os.path.relpath(sourcefile, start=workingDir)]



    def determine_result(self, returncode, returnsignal, output, isTimeout):
        output = '\n'.join(output)
        status = result.STATUS_UNKNOWN

        if self.allInText(['Violated property:',
                      'dereference failure: dynamic object lower bound',
                      'VERIFICATION FAILED'],
                      output):
            status = result.STATUS_FALSE_DEREF
        elif self.allInText(['Violated property:',
                      'Operand of free must have zero pointer offset',
                      'VERIFICATION FAILED'],
                      output):
            status = result.STATUS_FALSE_FREE
        elif self.allInText(['Violated property:',
                      'error label',
                      'VERIFICATION FAILED'],
                      output):
            status = result.STATUS_FALSE_REACH
        elif self.allInText(['Violated property:',
                      'assertion',
                      'VERIFICATION FAILED'],
                      output):
            status = result.STATUS_FALSE_REACH
        elif self.allInText(['Violated property:',
                      'dereference failure: forgotten memory',
                      'VERIFICATION FAILED'],
                      output):
            status = result.STATUS_FALSE_MEMTRACK
        elif 'VERIFICATION SUCCESSFUL' in output:
            status = result.STATUS_TRUE_PROP

        if status == result.STATUS_UNKNOWN:
            if isTimeout:
                status = 'TIMEOUT'
            elif output.endswith(('Z3 Error 9', 'Z3 Error 9\n')):
                status = 'ERROR (Z3 Error 9)'
            elif output.endswith(('error', 'error\n')):
                status = 'ERROR'
            elif 'Encountered Z3 conversion error:' in output:
                status = 'ERROR (Z3 conversion error)'

        return status


    def add_column_values(self, output, columns):
        """
        This method adds the values that the user requested to the column objects.
        If a value is not found, it should be set to '-'.
        If not supported, this method does not need to get overridden.
        """
        pass

    """ helper method """
    def allInText(self, words, text):
        """
        This function checks, if all the words appear in the given order in the text.
        """
        index = 0
        for word in words:
            index = text[index:].find(word)
            if index == -1:
                return False
        return True