import os
import subprocess

from . import core


__all__ = ["Compile", "BuildSharedLib", "BuildStaticLib", "BuildProgram"]

class Compile(core.MapOp):
    """Compile input files."""

    def __init__(self, name, sources):
        super(Compile, self).__init__(name, sources, "%.o:%.c", "{CC} -c {in} -o {out}")

    def indirect_deps(self, vars):
        cmd = "{CC} -MM {in}".format(**vars)
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        deps = []
        ll = False
        for l in out.split("\n"):
            if not l:
                continue
            if not ll:
                l = l.split(":")[1]
                if l.endswith(" \\"):
                    ll = True
                    deps.append(l[:-2].strip())
                else:
                    deps.append(l.strip())
            else:
                ll = False
                deps.append(l.strip())
        return deps

class BuildSharedLib(core.ReduceOp):
    """Build a shared library."""
    def __init__(self, name, sources):
        objs = Compile(name+"_compile", sources)
        #   gcc -Wall -fPIC -c *.c
        #    gcc -shared -Wl,-soname,libctest.so.1 -o libctest.so.1.0   *.o
        super(BuildSharedLib, self).__init__(name, objs,
                                             """
                                             {CC} -shared -Wl,-soname,{out.dropext} -o {out} {in}
                                             ln -f -s {out} {out.dropext}
                                             ln -f -s {out} {out.dropext2}
                                             """)

class BuildStaticLib(core.ReduceOp):
    """Build a static library."""

    def __init__(self, name, sources):
        objs = Compile(name+"_compile", sources)
        super(BuildStaticLib, self).__init__(name, objs, "{AR} cru {out} {in}\n{RANLIB} {out}")

class BuildProgram(core.ReduceOp):
    """Build a program.

    name - name of program
    """

    def __init__(self, name, sources, static_libs=[], shared_libs=[], external_libs=[], compile_flags=[], link_flags=[]):
        self.objs = Compile(name+"_compile", sources)
        if not isinstance(static_libs, list):
            static_libs = [static_libs]
        self.static_libs = static_libs
        if not isinstance(shared_libs, list):
            shared_libs = [shared_libs]
        self.shared_libs = shared_libs
        self.external_libs = external_libs
        self.compile_flags = compile_flags
        self.link_flags = link_flags
        super(BuildProgram, self).__init__(name, [self.objs] + self.static_libs + self.shared_libs)

    def action(self, vars):
        shared_libs = [ os.path.basename(sl.outputs[0])[3:].split(".so")[0] for sl in self.shared_libs ]
        shared_libs_dirs = [ os.path.dirname(sl.outputs[0]) for sl in self.shared_libs ]
        script = "{CC} -o %s %s %s %s %s" % (self.outputs[0],
                                             " ".join(self.objs.outputs),
                                             " ".join([ sl.outputs[0] for sl in self.static_libs ]),
                                             " ".join([ "-L%s" % ld for ld in shared_libs_dirs ]),
                                             " ".join([ "-l%s" % l for l in shared_libs + self.external_libs ]))
        self.run_script(script, vars)

