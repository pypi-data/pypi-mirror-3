"""Build scripting framework

Barabash is a build scripting framework.
It takes some concepts from GNU make, CMake and SCons.
"""

import os
import os.path
import re
import inspect
import glob
import argparse
import subprocess
import string
import sys
import tempfile
import collections

__all__ = [
    "run", "run_target", "define_map_op", "define_reduce_op", "define_ops_chain", "include", "set_env",
    "Files", "Operation", "MapOp", "ReduceOp", "Command"]

# TODO:
# - auto-clean, i.e. clean auto-detects all outputs and deletes them
# - license headings in source files
# - func for coloured tracing BB
# - add support for custom clean to ops
# - referencing deps by name (additionaly to by reference to object)
# - build configurations
# - PhonyOp - always executed
# - TransiOp - does not modify files?
# - add test for missing output
# - side outputs
# - redir to file reorder BB traces to the end
# - prepare mod help (docstrings)
# DONE:
# + generation of additional deps for sources (indirect deps)
# + run scripts in one process
# + break on error
# + operations chaining (Compile+Link)
# + function actions (beside script actions)
# + env with variables
# + includes for modularity
# + define real-life operations:
#   - Compile
#   - LinkStaticLib
#   - LinkSharedLib
#   - LinkProgram
#   - BuildStaticLib
#   - BuildSharedLib
#   - BuildProgram
# + add __all__

# store for all deps
g_deps = {}

g_env = {"CC": "gcc",
         "AR": "ar",
         "RANLIB": "ranlib"}

g_basedir = None
g_basedir = os.path.dirname(inspect.getabsfile(inspect.stack()[-1][0]))
#print "g_basedir", g_basedir

# 0	Reset all attributes
# 1	Bright
# 2	Dim
# 4	Underscore
# 5	Blink
# 7	Reverse
# 8	Hidden
#	Foreground Colours
# 30	Black
# 31	Red
# 32	Green
# 33	Yellow
# 34	Blue
# 35	Magenta
# 36	Cyan
# 37	White
#	Background Colours
# 40	Black
# 41	Red
# 42	Green
# 43	Yellow
# 44	Blue
# 45	Magenta
# 46	Cyan
# 47	White
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    BLUE = '\033[34m'
    OKGREEN = '\033[92m'
    GREEN = '\033[22m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    ENDC = '\033[0m'
    BRED = '\033[41m'
    YELLOW = '\033[33m'

    @classmethod
    def disable(cls):
        cls.HEADER = ''
        cls.OKBLUE = ''
        cls.BLUE = ''
        cls.OKGREEN = ''
        cls.GREEN = ''
        cls.WARNING = ''
        cls.FAIL = ''
        cls.RED = ''
        cls.CYAN = ''
        cls.ENDC = ''
        cls.BRED = ''
        cls.YELLOW = ''

if not sys.stdout.isatty():
    bcolors.disable()

def _generate_script(script):
    s = """#!/bin/bash
#set -e
set -u
#set -v
#set -x
#set -o errtrace
set -o pipefail
set -o functrace
set -o posix
#export SHELLOPTS:=errexit:pipefail
function error_handler {
    local err=$?
    if [ $err -ne 0 ]; then
        trap - DEBUG
        shift
#        echo "Error code $err returned in line '$@'"
        echo "Error code $err"
        exit 1
    fi
}
#LINE=0
#trap 'error_handler $LINENO $LINE' DEBUG
trap 'error_handler $LINENO' DEBUG
"""
    for l in script.split("\n"):
        l = l.strip()
        if not l:
            continue
#        s += "LINE='%s'\n" % l.replace("'", "\\'")
        s += "echo '%s'\n" % l.replace("'", "\"")
        s += l + "\n"
    s += "exit 0\n"
    #print s
    fd, path = tempfile.mkstemp()
    os.write(fd, s)
    os.close(fd)
    os.chmod(path, 0777)
    return path

class ExecutionError(Exception): pass
class DuplicatedObjectiveError(Exception): pass

def _run_script(script):
    script_path = _generate_script(script)
    retcode = subprocess.call(script_path, shell=True)
    if retcode != 0:
        e = ExecutionError("Recipe failed")
        e.retcode = retcode
        raise e
    os.unlink(script_path)

class Objective(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.dirname = os.path.dirname(path)
        self.target = (path, name)
        self.required_by = []

        # store new dep in g_deps
        global g_deps
        if self.target in g_deps:
            raise DuplicatedObjectiveError("Two identical deps defined: %s:%s" % (self.path, self.name))
        else:
            g_deps[self.target] = self

class Files(Objective):
    def __init__(self, name, files=None, glob_=None, regex=None, recursive=True):
        for s in inspect.stack():
            if s[3] != "__init__":
                path = os.path.abspath(s[1])
                break

        duplicated = False
        try:
            super(Files, self).__init__(name, path)
        except DuplicatedObjectiveError:
            duplicated = True

        if files:
            for f in files:
                fp = os.path.join(self.dirname, f)
                if not os.path.exists(fp):
                    raise Exception("File %s does not exists" % fp)
            self.files = files
        elif glob:
            self.files = glob.glob(glob_) # TODO: how to do recursive?
        elif regex:
            self.files = [] # TODO: how to do recursive?

        if duplicated:
            global g_deps
            d = g_deps[self.target]
            if isinstance(d, Files):
                if set(self.files).difference(set(d.files)):
                    raise DuplicatedObjectiveError("Two identical deps defined: %s:%s" % (self.path, self.name))

        self.deps = []

def _is_newer(a, b):
    if os.path.exists(a):
        at = os.path.getmtime(a)
        bt = os.path.getmtime(b)
        return at > bt
    else:
        return False

# generic operations
class Operation(Objective):
    def __init__(self, name, deps, op_type, output, action=None):
        if isinstance(deps, list):
            deps = deps
        else:
            deps = [deps]
        self.deps = []
        for d in deps:
            if isinstance(d, basestring):
                d = Files(d, [d])
            self.deps.append(d)
        self.output = output
        if action:
            self.action = action
        self.op_type = op_type

        for s in inspect.stack():
            if s[3] != "__init__":
                path = os.path.abspath(s[1])
                mod = inspect.getmodule(s[0])
                break

        setattr(mod, name, self)

        super(Operation, self).__init__(name, path)

    def run_script(self, script, vars):
        script = script.format(**vars)
        _run_script(script)


class MapOp(Operation):
    def __init__(self, name, deps, output, action):
        super(MapOp, self).__init__(name, deps, "map", output, action)

class ReduceOp(Operation):
    def __init__(self, name, deps, *args):
        if len(args) == 2:
            output, action = args
        elif len(args) == 1:
            output = name
            action, = args
        else:
            output = name
            action = None
        super(ReduceOp, self).__init__(name, deps, "reduce", output, action)

class Command(Operation):
    def __init__(self, name, *args):
        if len(args) == 2:
            deps, action = args
        elif len(args) == 1:
            deps = []
            action, = args
        else:
            deps = []
            action = None
        super(Command, self).__init__(name, deps, "cmd", None, action)

def define_map_op(output, action):
    class MapOp2(Operation):
        def __init__(self, name, deps, output2=None):
            if not output2:
                output2 = output
            super(MapOp2, self).__init__(name, deps, "map", output2, action)
    return MapOp2

def define_reduce_op(action):
    class ReduceOp2(Operation):
        def __init__(self, name, deps, output=None):
            if not output:
                output = name
            super(ReduceOp2, self).__init__(name, deps, "reduce", output, action)
    return ReduceOp2

def define_ops_chain(*actions):
    class ChainOp(object):
        def __init__(self, name, deps):
            interm = actions[0](name + actions[0].__name__, deps)
            for a in actions[1:-1]:
                interm = a(name + a.__name__, interm)
            actions[-1](name, interm, name)
    return ChainOp

def include(path):
    """Include submodule to barabash"""
    for s in inspect.stack():
        if "include(" in s[4][0]:
            subdir = os.path.dirname(s[1])
    sys.path.append(os.path.join(subdir, os.path.dirname(path)))
    mod = __import__(os.path.basename(path[:-3]))
    return mod

def set_env(var, val):
    global g_env
    g_env[var] = val

def dropext(path):
    return os.path.splitext(path)[0]

def dropext2(path):
    return os.path.splitext(os.path.splitext(path)[0])[0]

class File(object):
    def __init__(self, f):
        self.name = f

    def __str__(self):
        if isinstance(self.name, list):
            return " ".join(self.name)
        else:
            return self.name

    def __getattr__(self, item):
        if item == "dropext":
            m = dropext
        elif item == "dropext2":
            m = dropext2
        else:
            m = getattr(os.path, item)
        if isinstance(self.name, list):
            return " ".join([ m(n) for n in self.name ])
        else:
            return m(self.name)

def patsubst(in_ptrn, out_ptrn, files):
    single = False
    if not isinstance(files, list):
        files = [files]
        single = True
    out_left, out_right = out_ptrn.strip().split("%")
    in_ptrn = in_ptrn.strip().replace("%", "(.*?)")
    outs = []
    for f in files:
        m = re.search("^" + in_ptrn + "$", f)
        if not m:
            raise Exception("no match for %s for %s" % (i, in_ptrn))
        output = out_left + m.group(1) + out_right
        outs.append(output)
    if single:
        return outs[0]
    else:
        return outs

class Barabash(object):
    def __init__(self):
        self.top_objectives = []
        self.src_root_dir = g_basedir
        self.bld_root_dir = os.getcwd()

        self._load_env()

    def _load_env(self):
        for s in inspect.stack():
            if "run()" in s[4][0] or ".run_target(" in s[4][0]:
                frame = s[0]
                break
        for var, val in frame.f_locals.iteritems():
            if (isinstance(val, basestring) or isinstance(val, int)) and not var.startswith("_"):
                #print var, "=", val
                set_env(var, val)

    def _analyze(self):
        for target, dep in g_deps.iteritems():
            for d in dep.deps:
                d.required_by.append(dep)

        for target, dep in g_deps.iteritems():
            if len(dep.required_by) == 0:
                self.top_objectives.append(dep)

    def _invoke_action(self, action, vars):
        if isinstance(action, collections.Callable):
            ret = action(vars)
            if ret != 0:
                e = ExecutionError()
                e.retcode = ret
                raise e
        else:
            script = action.format(**vars)
            _run_script(script)

    def _trace_stack(self, stack):
        arrow = bcolors.BLUE + " -> " + bcolors.ENDC
        stack_str = arrow.join([ bcolors.CYAN + o.name + bcolors.ENDC for o in stack ])
        print bcolors.BLUE + "BB(" + bcolors.ENDC + stack_str + bcolors.BLUE + "):" + bcolors.ENDC

    def _execute_op(self, operation, stack):
        operation.outputs = []

        if isinstance(operation, Files):
            operation.outputs = [ os.path.join(operation.dirname, f) for f in operation.files ]
            return True

        statuses = []
        inputs = []
        for d in operation.deps:
            statuses.append(self._execute_op(d, stack + [operation]))
            inputs.extend(d.outputs)

        self._trace_stack(stack + [operation])

        # TODO: this is wrong because it does not create outpout if it does not exist
        #if operation.deps and not any(statuses):
        #    return True

        changed = False
        variables = g_env.copy()
        variables.update({"srcdir": operation.dirname,
                          "blddir": self.bld_root_dir})
        for i in xrange(4):
            variables2 = {}
            for n, v in variables.iteritems():
                if isinstance(v, basestring) and "{" in v:
                    v = v.format(**variables)
                variables2[n] = v
            variables = variables2

        if operation.op_type == "map":
            for i in inputs:
                out_ptrn, in_ptrn = operation.output.split(":")
                i2 = i.replace(operation.dirname + "/", "")
                output = patsubst(in_ptrn, out_ptrn, i2)
                output = output.format(**variables)
                outdir = operation.dirname.replace(self.src_root_dir, self.bld_root_dir)
                output = os.path.join(outdir, output)
                operation.outputs.append(output)
                if self.target == "clean":
                    if os.path.exists(output):
                        print bcolors.BLUE + "BB(" + bcolors.ENDC + "clean" + bcolors.BLUE + "):" + bcolors.ENDC + output
                        os.unlink(output)
                else:
                    if not os.path.exists(outdir):
                        os.mkdir(outdir)
                    variables["in"] = File(i)
                    variables["out"] = File(output)
                    all_deps = [i]
                    if hasattr(operation, "indirect_deps"):
                        ind = getattr(operation, "indirect_deps")
                        all_deps.extend(ind(variables))
                    if os.path.exists(output) and all((_is_newer(output, d) for d in all_deps)):
                        continue
                    self._invoke_action(operation.action, variables)
                    if not os.path.exists(output):
                        e = ExecutionError("Missing output %s" % output)
                        e.retcode = 1
                        raise e
                    changed = True
            return changed
        elif operation.op_type == "reduce":
            outdir = operation.dirname.replace(self.src_root_dir, self.bld_root_dir)
            output = os.path.join(outdir, operation.output)
            output = output.format(**variables)
            operation.outputs.append(output)
            if self.target == "clean":
                if os.path.exists(output):
                    print bcolors.BLUE + "BB(" + bcolors.ENDC + "clean" + bcolors.BLUE + "):" + bcolors.ENDC + output
                    os.unlink(output)
            else:
                if os.path.exists(output) and all((_is_newer(output, i) for i in inputs)):
                    return False
                variables["in"] = File(inputs)
                variables["out"] = File(output)
                self._invoke_action(operation.action, variables)
                if not os.path.exists(output):
                    e = ExecutionError("Missing output %s" % output)
                    e.retcode = 1
                    raise e
            return True
        elif operation.op_type == "cmd":
            if self.target != "clean":
                self._invoke_action(operation.action, variables)
            return True

        raise Exception("hmm")

    def execute(self, target):
        self.target = target
        self._analyze()
        for (path, name), dep in g_deps.iteritems():
            if target == name:
                try:
                    self._execute_op(dep, [])
                except ExecutionError, e:
                    print bcolors.BRED + bcolors.YELLOW + "BB(Execution error):" + bcolors.ENDC + " " + bcolors.RED + str(e) + bcolors.ENDC
                    return e.retcode
                return 0
        print "target %s not found"
        return 1

    def clean(self):
        self.target = "clean"
        self._analyze()
        for dep in self.top_objectives:
            self._execute_op(dep, [])

    def show_targets(self):
        self._analyze()
        for d1 in self.top_objectives:
            print d1.name
            for d2 in d1.deps:
                print "\t", d2.name
                for d3 in d2.deps:
                    print "\t\t", d3.name

def run():
    """Run Barabash.

    It scans command line parameters and executes accordingly.
    If there is a target in command line then it is executed.
    """
    parser = argparse.ArgumentParser(description='Barabash Build Script.')
    parser.add_argument('target', help='TODO')

    args = parser.parse_args()

    bb = Barabash()

    if args.target == "help":
        bb.show_targets()
    elif args.target == "clean":
        bb.clean()
    else:
        targets = [ n for p, n in g_deps.iterkeys() ]
        if args.target in targets:
            retcode = bb.execute(args.target)
            exit(retcode)
        else:
            print "Error: unknown target '%s'. Select one from:" % args.target
            bb.show_targets()
            exit(1)

def run_target(target):
    bb = Barabash()

    targets = [ n for p, n in g_deps.iterkeys() ]
    if target in targets:
        retcode = bb.execute(target)
        return retcode
    raise Exception("missing target")

