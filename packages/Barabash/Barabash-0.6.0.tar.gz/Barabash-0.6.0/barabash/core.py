"""
Core of Barabash build scripting framework
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
import atexit
try:
    import pygraphviz as pgv
except:
    pgv = None


__all__ = [
    "run", "run_target", "define_map_op", "define_reduce_op", "define_ops_chain", "add_dependency", "include", "set_env", "project", "patsubst",
    "Files", "Operation", "MapOp", "ReduceOp", "Command"]

# TODO:
# - port to Py3k
# - license headings in source files
# - add support for custom clean to ops
# - referencing deps by name (additionaly to by reference to object)
# - add test for missing output
# - side outputs
# - add user help to operations
# - add (optional) dependency on python-pygraphviz in setpy.py; or at least add trace that it is missing and how to install it
# - make execution in 2 turns: first establish outputs then generate outputs
# - fix printing targets help when add_dependency is used
# - command for displaying deps for given output
# - verbose/files in help command
# DONE:
# + prepare modules help (docstrings)
# + build configurations
# + generation of additional deps for sources (indirect deps)
# + run scripts in one process
# + break on error
# + operations chaining (Compile+Link)
# + function actions (beside script actions)
# + env with variables
# + includes for modularity
# + auto-clean, i.e. clean auto-detects all outputs and deletes them
# + fix problem when MapOp has deps that generate outputs that should not be included as inputs in MapOp (see render-website and pygmentize-examples)
# + add name to barabash script project (like in cmake), use it in graph generator
# + eliminate run(), people forgets it (use atexit)
# + func for coloured tracing BB
# + add testing to build.py
# + redirecting to file (>) causes reordering BB traces to the end of output
# + define real-life operations:
#   - Compile
#   - LinkStaticLib
#   - LinkSharedLib
#   - LinkProgram
#   - BuildStaticLib
#   - BuildSharedLib
#   - BuildProgram
# + add __all__
# + add indirect_deps as files, see "add dep on base.html"

# store for all deps
g_deps = {}

g_env = {"CC": "gcc",
         "AR": "ar",
         "RANLIB": "ranlib"}


g_basedir = None
for s in inspect.stack():
    l = s[4][0]
    if "import" in l and "barabash" in l:
        g_basedir = os.path.dirname(inspect.getabsfile(s[0]))
        break

g_additional_deps = {}

g_project = "Some Project"

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

def _print(txt):
    print txt
    sys.stdout.flush()

def _print_error(err_type, msg):
    _print(bcolors.BRED + bcolors.YELLOW + "BB(" + err_type + "):" + bcolors.ENDC + " " + bcolors.RED + msg + bcolors.ENDC)

def _print_exe(short, msg=""):
    _print(bcolors.BLUE + "BB(" + bcolors.ENDC + short + bcolors.BLUE + "):" + bcolors.ENDC + msg)

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
    #_print(s)
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
        e = ExecutionError("Operation failed")
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
    """A named set of files.

    :param name: a name of the set of files, it can be referenced in deps in :class:`Operation`
    :param files: a list of files
    :param glob_: a glob rule that matches a set of files, alternative to files parameter
    :param regex: a regex rule that matches a set of files, alternative to files parameter
    :param recursive: TBD, unused

    Example:

    >>> src_js = Files("src_js", ["a.js", "b.js"])
    """
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
    """An operation that has input dependencies and generates outputs according to action.

    Operation class is a core element in Barabash that allows building a graph of dependencies.

    :param name: a name of operation, it can be referenced in other :class:`Operation` as dep
    :param deps: a dependency or a list of dependencies, a dependecy can be a :class:`Files` or other :class:`Operation`
    :param op_type: an operation type, it can be ``"map"`` (:class:`MapOp`) or ``"reduce"`` (:class:`ReduceOp`) or ``"cmd"`` (:class:`Command`).
    :param output: a rule that defines how output is named, it depends on ``op_type``
    :param action: a python function or a Bash script that will be executed in operation
    :param indirect_deps: an additional set of dependent elemets (files and :class:`Operation`) that is not treated as inputs, e.g. header files in C compilation
    """
    def __init__(self, name, deps, op_type, output, action=None, indirect_deps=[]):
        if isinstance(deps, list):
            deps = deps
        else:
            deps = [deps]
        self.deps = []
        for d in deps:
            if isinstance(d, basestring):
                d = Files(d, [d])
            self.deps.append(d)

        if isinstance(indirect_deps, basestring):
            self._indirect_deps = [indirect_deps]
        else:
            self._indirect_deps = indirect_deps

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

    def indirect_deps(self, env):
        """Return indirect dependencies.

        Override this function in subclass to return list of additional dependencies for the operation.
        It can be used to bring additional deps as for example header files from C source files.

        See example usage in :class:`barabash.ops.Compile` class.
        """
        return []

    def run_script(self, script, env):
        """Run Bash script.

        :param script: a Bash script
        :param env: variables that can be used in the script

        This is helper function for running shell script.
        Any variables in the script are substituted with values before running.
        This function can be used in action function also overriden in this class.
        """
        script = script.format(**env)
        _run_script(script)


class MapOp(Operation):
    """A map operation.

    :param name: a name of operation, it can be referenced in other :class:`Operation` as dep
    :param deps: a dependency or a list of dependencies, a dependecy can be a :class:`Files` or other :class:`Operation`
    :param output: a mapping rule like in GNU make
    :param action: a python function or a Bash script that will be executed in operation
    :param indirect_deps: an additional set of dependent elemets (files and :class:`Operation`) that is not treated as inputs, e.g. header files in C compilation

    Example:

    >>> objects = MapOp("objects", src_c, "%.o:%.c", "{CC} -c {in} -o {out}")
    """
    def __init__(self, name, deps, output, action, indirect_deps=[]):
        super(MapOp, self).__init__(name, deps, "map", output, action, indirect_deps)

class ReduceOp(Operation):
    """A reduce operation.

    :param name: a name of operation, it can be referenced in other :class:`Operation` as dep
    :param deps: a dependency or a list of dependencies, a dependecy can be a :class:`Files` or other :class:`Operation`
    :param output: an output file name, optional
    :param action: a python function or a Bash script that will be executed in operation

    Example:

    >>> js_tar_gz = ReduceOp("js.tar.gz", src_js, "tar -C {srcdir} -zcvf {out} {in.basename}")
    """
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
    """A command operation.

    :param name: a name of operation, it can be referenced in other :class:`Operation` as dep
    :param deps: a dependency or a list of dependencies, a dependecy can be a :class:`Files` or other :class:`Operation`
    :param action: a python function or a Bash script that will be executed in operation

    Example:

    >>> build_pkg = Command("build-pkg", "python setup.py sdist")
    """
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
    """Define a new map operation.

    :param output: a mapping definition that maps inputs to outputs, works as rules in GNU make, e.g. %.o: %.c - it maps for example main.c to main.o
    :param action: a Bash script or Python function

    Example:

    >>> Pygmentize = define_map_op("%.html:%.py", "pygmentize -O -f html -o {out} {in}")
    """
    class MapOp2(Operation):
        def __init__(self, name, deps, output2=None):
            if not output2:
                output2 = output
            super(MapOp2, self).__init__(name, deps, "map", output2, action)
    return MapOp2

def define_reduce_op(action):
    """Define a new reduce operation.

    :param action: a Bash script or Python function

    Example:

    >>> Tar = define_reduce_op("tar -C {srcdir} -zcvf {out} {in.basename}")
    """
    class ReduceOp2(Operation):
        def __init__(self, name, deps, output=None):
            if not output:
                output = name
            super(ReduceOp2, self).__init__(name, deps, "reduce", output, action)
    return ReduceOp2

def define_ops_chain(*actions):
    """Define a chain of operations.

    :param actions: a list of operations

    Example:

    >>> CompileAndLink = define_ops_chain(Compile, Link)
    """
    class ChainOp(object):
        def __init__(self, name, deps):
            interm = actions[0](name + actions[0].__name__, deps)
            for a in actions[1:-1]:
                interm = a(name + a.__name__, interm)
            actions[-1](name, interm, name)
    return ChainOp

def add_dependency(fname, operation):
    """Add dependency for given file on a given operation.

    :param fname: a file name
    :param operation: an operation that file depends on

    Example:

    >>> add_dependency("www/examples.html", pygmentize_examples)
    """
    g_additional_deps[os.path.abspath(fname)] = operation

def project(name):
    """Define a project name.

    :param name: a name of project

    Example:

    >>> project("Sample Project")
    """
    global g_project
    g_project = name

def include(path):
    """Include submodule to Barabash script.

    :param path: a relative or absolute path to Barabsh script submodule

    Example:

    >>> lib = include("lib/lib.py")
    """
    for s in inspect.stack():
        if "include(" in s[4][0]:
            subdir = os.path.dirname(s[1])
    sys.path.append(os.path.join(subdir, os.path.dirname(path)))
    mod = __import__(os.path.basename(path[:-3]))
    return mod

def set_env(var, val):
    """Set Barabash script environment variable.

    :param var: a name of variable
    :param val: a value of variable

    Example:

    >>> set_env("CC", "/usr/bin/gcc")
    """
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
    """Substitute string in files according to pattern.

    :param in_ptrn: a pattern for input files
    :param out_ptrn: an output pattern for output files
    :param files: a list of files
    :returns: a list of converted file names

    Example:

    >>> patsubst("%.c", "%.o", ["src/main.c"])
    ["src/main.o"]
    """
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
            raise Exception("no match for %s for %s (out: %s, files: %s)" % (f, in_ptrn, out_ptrn, files))
        output = out_left + m.group(1) + out_right
        outs.append(output)
    if single:
        return outs[0]
    else:
        return outs

class Barabash(object):
    def __init__(self, cmd_line_env=[]):
        self.top_objectives = []
        self.src_root_dir = g_basedir
        self.bld_root_dir = os.getcwd()

        self._load_env(cmd_line_env)

    def _load_env(self, cmd_line_env):
        for s in inspect.stack():
            if "run()" in s[4][0] or ".run_target(" in s[4][0]:
                frame = s[0]
                break
        for var, val in frame.f_locals.iteritems():
            if (isinstance(val, basestring) or isinstance(val, int)) and not var.startswith("_"):
                #print var, "=", val
                set_env(var, val)

        global g_env
        env = os.environ.copy()
        env.update(g_env)
        #del env[' ']
        g_env = env

        for p in cmd_line_env:
            try:
                var, val = p.split("=")
            except:
                continue
            var = var.strip()
            val = val.strip()
            set_env(var, val)

    def _analyze(self):
        for target, dep in g_deps.iteritems():
            for d in dep.deps:
                d.required_by.append(dep)

        for target, dep in g_deps.iteritems():
            if len(dep.required_by) == 0:
                self.top_objectives.append(dep)

    def _invoke_action(self, action, env):
        if isinstance(action, collections.Callable):
            ret = action(env)
            if ret != 0:
                e = ExecutionError()
                e.retcode = ret
                raise e
        else:
            script = action.format(**env)
            _run_script(script)

    def _trace_stack(self, stack):
        arrow = bcolors.BLUE + " -> " + bcolors.ENDC
        stack_str = arrow.join([ bcolors.CYAN + o.name + bcolors.ENDC for o in stack ])
        _print_exe(stack_str)

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
                if isinstance(v, basestring) and "{" in v and not "{ " in v:
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

                if output in g_additional_deps:
                    self._execute_op(g_additional_deps[output], stack + [operation])

                if self.target == "clean":
                    if os.path.exists(output):
                        _print_exe("clean", output)
                        os.unlink(output)
                else:
                    if not os.path.exists(outdir):
                        os.mkdir(outdir)
                    variables["in"] = File(i)
                    variables["out"] = File(output)
                    all_deps = [i]
                    all_deps.extend(operation._indirect_deps)
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
                    _print_exe("clean", output)
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
                    _print_error("Execution error", str(e))
                    return e.retcode
                return 0
        _print("target %s not found")
        return 1

    def clean(self):
        self.target = "clean"
        self._analyze()
        for dep in self.top_objectives:
            self._execute_op(dep, [])

    def _node_color(self, op):
        if op.op_type == "map":
            return 'blue'
        elif op.op_type == "reduce":
            return 'red'
        return 'black'

    def _node_text(self, op):
        if op.output is None:
            return op.name
        return "<" + op.name + "<BR/><FONT POINT-SIZE=\"10\" COLOR=\"#aaaaaa\">" + op.output + "</FONT>>"

    def _show_targets_recur(self, gr, parent, indent):
        if not isinstance(parent, Operation):
            return
        for d in parent.deps:
            if not isinstance(d, Operation):
                continue
            if pgv:
                gr.add_node(d.name, color=self._node_color(d), label=self._node_text(d))
                gr.add_edge(parent.name, d.name, dir="back")
            _print(indent + " " + d.name)
            self._show_targets_recur(gr, d, indent + "\t")

    def show_targets(self, graph=False):
        if pgv:
            gr = pgv.AGraph(directed=True)
            gr.node_attr.update(shape='box')
            gr.graph_attr.update(label="Barabash script graph for %s" % g_project)

        self._analyze()
        for d in self.top_objectives:
            if pgv:
                gr.add_node(d.name, color=self._node_color(d), label=self._node_text(d))
            _print(d.name)
            self._show_targets_recur(gr, d, "\t")

        if graph and pgv:
            gr.layout('dot') # layout with default (neato)
            gr.draw('barabash.png') # draw png

    def show_env(self):
        for var, val in sorted(g_env.iteritems()):
            print "%30s   %s"% (var, val)

def _print_header():
    _print(bcolors.BLUE + "Barabash script for " + bcolors.CYAN + g_project + bcolors.ENDC)

g_was_run = False

def run():
    """Run Barabash script.

    It scans command line parameters and executes accordingly.
    If there is a target in command line then it is executed.
    """
    global g_was_run
    g_was_run = True

    parser = argparse.ArgumentParser(description='Barabash Build Script.')
    parser.add_argument('target', help='a target or help to get list of available targets')
    parser.add_argument('-g', '--graph', help='generate a graph image of all operations dependencies to barabash.png file', action="store_true")

    args, other = parser.parse_known_args()

    bb = Barabash(other)

    _print_header()

    if args.target == "help":
        _print("Barabash Help:")
        bb.show_targets(args.graph)
    elif args.target == "env":
        _print("Barabash Environment:")
        bb.show_env()
    elif args.target == "clean":
        bb.clean()
    else:
        targets = [ n for p, n in g_deps.iterkeys() ]
        if args.target in targets:
            retcode = bb.execute(args.target)
            exit(retcode)
        else:
            _print_error("Run error", "unknown target '%s'. Select one from:" % args.target)
            bb.show_targets()
            exit(1)

def run_target(target):
    """Run specified target in Barabash script.

    :param target: a name of target defined in Barabash script
    """
    global g_was_run
    g_was_run = True

    bb = Barabash()

    targets = [ n for p, n in g_deps.iterkeys() ]
    if target in targets:
        retcode = bb.execute(target)
        return retcode
    _print_error("Run error", "unknown target '%s'. Select one from:" % target)
    bb.show_targets()
    exit(1)

def run_at_exit():
    if not g_was_run:
        _print_error("Definition error", "missing run() or run_target() function call at then end of main Barabash script")
atexit.register(run_at_exit)
