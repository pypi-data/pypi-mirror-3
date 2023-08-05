from dexy.dexy_filter import DexyFilter
import subprocess
import time

### @export "clang-handler"
class ClangHandler(DexyFilter):
    """Compiles C code using clang compiler, then runs compiled program."""
    VERSION = "clang --version"
    EXECUTABLE = "clang"
    INPUT_EXTENSIONS = [".c"]
    OUTPUT_EXTENSIONS = [".txt"]
    ALIASES = ['clang']

    def process(self):
        self.artifact.generate_workfile()
        of = self.artifact.temp_filename(".o")
        wf = self.artifact.work_filename()
        command = "%s %s -o %s" % (self.EXECUTABLE, wf, of)
        self.log.debug(command)
        proc = subprocess.Popen(command, shell=True,
                                cwd=self.artifact.artifacts_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                )
        stdout, stderr = proc.communicate()
        self.artifact.stdout = stdout

        command = "./%s" % of
        self.log.debug(command)
        proc = subprocess.Popen(command, shell=True,
                                cwd=self.artifact.artifacts_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                )
        stdout, stderr = proc.communicate()
        self.artifact.data_dict['1'] = stdout
        self.artifact.stdout += stderr

### @export "clang-interactive-handler"
class ClangInteractiveHandler(DexyFilter):
    """Compiles C code using clang compiler, then runs compiled program, reading
    input from any input files."""
    VERSION = "clang --version"
    EXECUTABLE = "clang"
    INPUT_EXTENSIONS = [".c"]
    OUTPUT_EXTENSIONS = [".txt"]
    ALIASES = ['cint']

    def process(self):
        self.artifact.generate_workfile()
        of = self.artifact.temp_filename(".o")
        wf = self.artifact.work_filename()
        command = "%s %s -o %s" % (self.EXECUTABLE, wf, of)
        self.log.debug(command)
        proc = subprocess.Popen(command, shell=True,
                                cwd=self.artifact.artifacts_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                )
        stdout, stderr = proc.communicate()
        self.artifact.stdout = stdout

        command = "./%s" % of
        self.log.debug(command)
        for k, a in self.artifact.inputs().items():
            for s, t in a.data_dict.items():
                proc = subprocess.Popen(command, shell=True,
                                        cwd=self.artifact.artifacts_dir,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                       )
                stdout, stderr = proc.communicate(t)
                self.artifact.data_dict[s] = stdout
                self.artifact.stdout = self.artifact.stdout + "\n" + stderr

### @export "clang-timing-handler"
class ClangTimingHandler(DexyFilter):
    """Compiles C code using clang compiler, then runs compiled program N times
    reporting timings."""
    N = 10
    INPUT_EXTENSIONS = [".txt", ".c"]
    OUTPUT_EXTENSIONS = [".times"]
    ALIASES = ['ctime']
    EXECUTABLE = 'clang'
    VERSION = "clang --version"

    def process(self):
        self.artifact.generate_workfile()
        of = self.artifact.temp_filename(".o")
        wf = self.artifact.work_filename()
        command = "%s %s -o %s" % (self.EXECUTABLE, wf, of)
        self.log.debug(command)
        proc = subprocess.Popen(command, shell=True,
                                cwd=self.artifact.artifacts_dir,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                )
        stdout, stderr = proc.communicate()
        self.artifact.stdout = stdout

        command = "./%s" % of
        self.log.debug(command)
        times = []
        for i in xrange(self.N):
            start = time.time()
            proc = subprocess.Popen(command, shell=True,
                                    cwd=self.artifact.artifacts_dir,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    )
            stdout, stderr = proc.communicate()
            times.append("%s" % (time.time() - start))
        self.artifact.data_dict['1'] = "\n".join(times)

### @export "cpp-handler"
class CppHandler(ClangHandler):
    """Compiles and then runs C++ code."""
    VERSION = "c++ --version"
    EXECUTABLE ="c++"
    INPUT_EXTENSIONS = [".cpp"]
    OUTPUT_EXTENSIONS = [".txt"]
    ALIASES = ['cpp']

### @export "gcc-handler"
class CHandler(ClangHandler):
    """Compiles C code using gcc compiler, then runs compiled program."""
    VERSION = "gcc --version"
    EXECUTABLE = "gcc"
    INPUT_EXTENSIONS = [".c"]
    OUTPUT_EXTENSIONS = [".txt"]
    ALIASES = ['c', 'gcc']


