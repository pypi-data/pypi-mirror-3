from __future__ import print_function

from distutils.cmd import Command
from distutils.spawn import spawn
import os
from commands.util import configure_error, is_osx

JAVA_HOME = os.environ.get('JAVA_HOME')
MAC_JAVA_HOME = '/System/Library/Frameworks/JavaVM.framework'

def get_java_home():
    global JAVA_HOME
    if JAVA_HOME and os.path.exists(JAVA_HOME):
        return JAVA_HOME

    # mac's JAVA_HOME is predictable, just use that if we can
    if is_osx() and os.path.exists(MAC_JAVA_HOME):
        JAVA_HOME = MAC_JAVA_HOME
        return JAVA_HOME

    configure_error("Please set JAVA_HOME to a path containing the JDK.")

def get_java_include():
    """
    Locate the Java include folder containing jni.h.
    """
    inc_name = 'include'
    if is_osx():
        inc_name = 'Headers'
    inc = os.path.join(JAVA_HOME, inc_name)
    if not os.path.exists(inc):
        configure_error("Include folder should be at '{0}' but doesn't exist. " \
                        "Please check you've installed the JDK properly.".format(inc))
    jni = os.path.join(inc, "jni.h")
    if not os.path.exists(jni):
        configure_error("jni.h should be in '{0}' but doesn't exist. " \
                        "Please check you've installed the JDK properly.".format(jni))
    return inc

def get_java_lib():
    lib_name = 'lib'
    if is_osx():
        lib_name = 'Libraries'
    lib = os.path.join(JAVA_HOME, lib_name)
    if not os.path.exists(lib):
        configure_error("Lib folder should be at '{0}' but doesn't exist. " \
                        "Please check you've installed the JDK properly.".format(lib))
    return lib

def get_java_linker_args():
    if is_osx():
        return ['-framework JavaVM']

class build_java(Command):
    outdir = None

    user_options = [
        ('javac=', None, 'use javac (default: JAVA_HOME/bin/javac)'),
    ]

    def initialize_options(self):
        build_java.outdir = os.path.join('build', 'java')
        if not os.path.exists(build_java.outdir):
            os.makedirs(build_java.outdir)

        self.java_files = []
        if is_osx():
            self.javac = os.path.join(get_java_home(), 'Commands', 'javac')
        else:
            self.javac = os.path.join(get_java_home(), 'bin', 'javac')

    def finalize_options(self):
        self.java_files = self.distribution.java_files

    def build(self, *jclasses):
        spawn([self.javac, '-deprecation', '-d', build_java.outdir, '-classpath', 'src/'] + list(*jclasses))

    def run(self):
        self.build(self.java_files)


class build_jar(Command):
    outdir = None

    user_options = [
        ('jar=', None, 'use javac (default: JAVA_HOME/bin/jar)'),
    ]

    def initialize_options(self):
        build_java.outdir = os.path.join('build', 'java')
        if not os.path.exists(build_java.outdir):
            os.makedirs(build_java.outdir)

        self.java_files = []
        if is_osx():
            self.jar = os.path.join(get_java_home(), 'Commands', 'jar')
        else:
            self.jar = os.path.join(get_java_home(), 'bin', 'jar')

    def finalize_options(self):
        pass

    def build(self):
        spawn([self.jar, '-cfe', 'build/java/jep.jar', 'jep.Run', '-C', 'build/java/', 'jep'])

    def run(self):
        self.build()

class build_javah(Command):
    outdir = None

    user_options = [
        ('javah=', None, 'use javah (default: JAVA_HOME/bin/javah)'),
    ]

    def initialize_options(self):
        build_javah.outdir = os.path.join('build', 'include')
        if not os.path.exists(build_javah.outdir):
            os.mkdir(build_javah.outdir)

        if is_osx():
            self.javah = os.path.join(get_java_home(), 'Commands', 'javah')
        else:
            self.javah = os.path.join(get_java_home(), 'bin', 'javah')
        self.javah_files = []

    def finalize_options(self):
        self.javah_files = self.distribution.javah_files

    def build(self, jclass, header):
        spawn([self.javah, '-classpath', build_java.outdir, '-o', os.path.join(build_javah.outdir, header), jclass])

    def run(self):
        for jclass, header in self.javah_files:
            self.build(jclass, header)
